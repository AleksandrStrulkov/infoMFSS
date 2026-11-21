from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from html.parser import HTMLParser

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError, connection
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

from config.views import csrf_failure
from users.forms import RegisterForm
from users.services import (
    InvalidInvitation,
    InvitationLimitReached,
    active_invitations,
    create_invitation,
    redeem_invitation,
)


def create_test_user(email: str, password: str, **fields: str):
    user = get_user_model()(email=email, **fields)
    user.set_password(password)
    user.save()
    return user


@pytest.fixture
def inviter(db: object):
    user = create_test_user(
        email="inviter@example.test",
        password="Password123!",
        first_name="Мария",
        middle_name="Ивановна",
        last_name="Петрова",
    )
    return user


class FormStructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.form_depth = 0
        self.nested_forms = False
        self.csrf_inside_form = False
        self.submit_inside_form = False
        self.form_count = 0
        self.registration_form_count = 0
        self.registration_form_open = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "form":
            if self.form_depth:
                self.nested_forms = True
            self.form_depth += 1
            self.form_count += 1
            if attributes.get("id") != "logout-form":
                self.registration_form_count += 1
                self.registration_form_open = True
        elif tag == "input" and attributes.get("name") == "csrfmiddlewaretoken" and self.registration_form_open:
            self.csrf_inside_form = True
        elif tag == "button" and attributes.get("type") == "submit" and self.registration_form_open:
            self.submit_inside_form = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self.form_depth -= 1
            self.registration_form_open = False


def registration_data(email: str = "new@example.test") -> dict[str, str]:
    return {
        "last_name": "Иванов",
        "first_name": "Иван",
        "middle_name": "Иванович",
        "email": email,
        "phone": "+79991234567",
        "location_of_work": "Шахта",
        "post": "Инженер",
        "password1": "GoodPassword123!",
        "password2": "GoodPassword123!",
    }


def test_invitation_expiry_boundary(inviter):
    invitation = create_invitation(inviter)
    assert invitation.is_valid(invitation.expires_at - timedelta(microseconds=1))
    assert not invitation.is_valid(invitation.expires_at)
    assert not invitation.is_valid(invitation.expires_at + timedelta(seconds=1))


def test_invitation_limit_and_expiration(inviter):
    invitations = [create_invitation(inviter) for _ in range(5)]
    with pytest.raises(InvitationLimitReached):
        create_invitation(inviter)
    invitations[0].expires_at = timezone.now() - timedelta(seconds=1)
    invitations[0].save(update_fields=["expires_at"])
    assert active_invitations(inviter).count() == 4
    create_invitation(inviter)
    assert active_invitations(inviter).count() == 5


def test_invalid_token_cannot_create_user(inviter):
    user = RegisterForm(registration_data()).save(commit=False)
    with pytest.raises(InvalidInvitation):
        redeem_invitation("invalid", user)
    assert not get_user_model().objects.filter(email=user.email).exists()


def test_registration_form_contains_csrf_and_submit_in_one_form(client: Client, inviter: object) -> None:
    invitation = create_invitation(inviter)
    url = reverse("users:register", kwargs={"token": invitation.token})
    response = client.get(url)
    parser = FormStructureParser()
    parser.feed(response.content.decode())
    assert parser.form_count == 2  # Separate logout form in the site header.
    assert parser.registration_form_count == 1
    assert not parser.nested_forms
    assert parser.csrf_inside_form
    assert parser.submit_inside_form

    csrf_client = Client(enforce_csrf_checks=True)
    response = csrf_client.get(url)
    assert response.status_code == 200
    token = csrf_client.cookies["csrftoken"].value
    invalid_data = registration_data()
    invalid_data["phone"] = "bad"
    response = csrf_client.post(url, {**invalid_data, "csrfmiddlewaretoken": token})
    assert response.status_code == 200
    assert response.context["form"].errors


def test_csrf_failure_renders_recovery_page() -> None:
    response = csrf_failure(HttpRequest(), reason="secret diagnostics")
    assert response.status_code == 403
    assert "Не удалось проверить запрос" in response.content.decode()
    assert "secret diagnostics" not in response.content.decode()


def test_error_pages_render_without_request_context() -> None:
    for name in ("400.html", "403.html", "404.html", "500.html"):
        html = render_to_string(name)
        assert "На главную" in html


def test_http_success_and_inviter_history(client: Client, inviter):
    invitation = create_invitation(inviter)
    url = reverse("users:register", kwargs={"token": invitation.token})
    response = client.get(url)
    assert response.status_code == 200
    assert "Петрова" in response.content.decode()
    assert b'name="password1"' in response.content
    response = client.post(url, registration_data())
    assert response.status_code == 302
    assert response.url == reverse("mfss:home")
    assert response["Referrer-Policy"] == "no-referrer"
    assert response["Cache-Control"] == "private, no-store"
    user = get_user_model().objects.get(email="new@example.test")
    assert user.is_active and user.is_activated
    assert client.session["_auth_user_id"] == str(user.pk)
    invitation.refresh_from_db()
    assert invitation.registered_user == user
    assert invitation.used_at is not None
    assert len(mail.outbox) == 0
    assert client.get(url).templates[0].name == "users/registration_invalid.html"

    author_client = Client()
    author_client.force_login(inviter)
    profile = author_client.get(reverse("users:profile"))
    assert "Иванов" in profile.content.decode()
    assert invitation.token not in profile.content.decode()
    other = create_test_user(
        email="other@example.test", password="Password123!", first_name="Анна", middle_name="Игоревна"
    )
    other_client = Client()
    other_client.force_login(other)
    assert "Иванов" not in other_client.get(reverse("users:profile")).content.decode()


def test_guest_paths_and_invalid_registration(client: Client, inviter):
    home = client.get("/")
    assert home.status_code == 302
    assert reverse("users:login") == "/login/"
    assert home.url == "/login/?next=/"
    login = client.get(reverse("users:login"))
    assert login.status_code == 200
    assert reverse("mfss:contact") in login.content.decode()
    assert "Зарегистрироваться" not in login.content.decode()
    assert client.get(reverse("mfss:contact")).status_code == 200
    for url in (
        reverse("users:register_without_token"),
        reverse("users:register", kwargs={"token": "broken"}),
        "/users/accounts/register/" + "x" * 43 + "/",
    ):
        response = client.get(url)
        assert response.status_code == 200
        assert response.templates[0].name == "users/registration_invalid.html"
        assert reverse("mfss:contact") in response.content.decode()
    assert client.post(reverse("users:register_without_token"), registration_data()).status_code == 405
    assert client.post(reverse("users:invite_create")).status_code == 302
    assert not get_user_model().objects.filter(email="new@example.test").exists()
    assert client.get("/users/accounts/activate/old-sign").status_code == 404


def test_login_canonical_route_and_legacy_compatibility(client: Client, inviter):
    assert reverse("users:login") == "/login/"
    assert client.get("/users/").url == "/login/"
    assert client.get("/users/?next=/users/accounts/profile/").url == "/login/?next=/users/accounts/profile/"
    for unsafe in ("https://attacker.example/", "//attacker.example/", "\\\\attacker.example"):
        assert client.get("/users/", {"next": unsafe}).url == "/login/"
    assert client.post("/login/", {"username": inviter.email, "password": "Password123!"}).status_code == 302
    assert client.session["_auth_user_id"] == str(inviter.pk)

    safe_next_client = Client()
    assert safe_next_client.post(
        "/login/?next=/users/accounts/profile/",
        {"username": inviter.email, "password": "Password123!"},
    ).url == reverse("users:profile")
    unsafe_next_client = Client()
    assert unsafe_next_client.post(
        "/login/?next=https://attacker.example/",
        {"username": inviter.email, "password": "Password123!"},
    ).url == reverse("mfss:home")

    legacy_client = Client()
    assert legacy_client.post("/users/", {"username": inviter.email, "password": "Password123!"}).status_code == 302
    assert legacy_client.session["_auth_user_id"] == str(inviter.pk)


def test_activation_failure_template_points_to_access_request():
    html = render_to_string("users/activation_failed.html")
    assert reverse("mfss:contact") in html
    assert "Зарегистрироваться повторно" not in html


@override_settings(ALLOWED_HOSTS=["testserver", "info-mfss.ru"])
def test_invitation_link_uses_https_behind_proxy(client: Client, inviter):
    client.force_login(inviter)
    assert client.post(reverse("users:invite_create")).status_code == 302
    invitation = active_invitations(inviter).get()
    response = client.get(reverse("users:profile"), HTTP_HOST="info-mfss.ru", HTTP_X_FORWARDED_PROTO="https")
    assert response.status_code == 200
    assert (
        f"https://info-mfss.ru{reverse('users:register', kwargs={'token': invitation.token})}"
        in response.content.decode()
    )


def test_invite_issue_requires_post_and_profile_shows_active_link(client: Client, inviter):
    client.force_login(inviter)
    url = reverse("users:invite_create")
    assert client.get(url).status_code == 405
    assert client.post(url).status_code == 302
    invitation = active_invitations(inviter).get()
    profile = client.get(reverse("users:profile"))
    assert invitation.token in profile.content.decode()
    assert "Копировать" in profile.content.decode()


def test_form_errors_do_not_redeem(client: Client, inviter):
    invitation = create_invitation(inviter)
    url = reverse("users:register", kwargs={"token": invitation.token})
    bad_data = registration_data()
    bad_data["phone"] = "bad"
    response = client.post(url, bad_data)
    assert response.status_code == 200
    assert response.context["form"].errors
    invitation.refresh_from_db()
    assert invitation.is_valid()
    assert client.post(url, registration_data()).status_code == 302
    second = client.post(url, registration_data("another@example.test"))
    assert second.templates[0].name == "users/registration_invalid.html"
    assert second["Referrer-Policy"] == "no-referrer"
    assert second["Cache-Control"] == "private, no-store"
    assert get_user_model().objects.filter(email="another@example.test").count() == 0


def test_token_constraint_prevents_second_account(inviter):
    first = create_invitation(inviter)
    second = create_invitation(inviter)
    user = create_test_user(email="joined@example.test", password="Password123!")
    first.registered_user, first.used_at = user, timezone.now()
    first.save()
    second.registered_user, second.used_at = user, timezone.now()
    with pytest.raises(IntegrityError):
        second.save()


def test_password_reset_still_sends_email(client: Client, inviter):
    response = client.post(reverse("users:password_reset"), {"email": inviter.email})
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert reverse("users:password_reset_confirm", kwargs={"uidb64": "a", "token": "b"}).startswith(
        "/users/accounts/password-reset/"
    )


@pytest.mark.django_db(transaction=True)
def test_parallel_redemption_uses_only_one_account():
    if connection.vendor != "postgresql":
        pytest.skip("SELECT FOR UPDATE requires PostgreSQL")
    author = create_test_user(email="parallel-author@example.test", password="Password123!")
    invitation = create_invitation(author)
    url = reverse("users:register", kwargs={"token": invitation.token})

    def submit(email: str) -> tuple[int, str | None, str, str]:
        parallel_client = Client()
        response = parallel_client.post(url, registration_data(email))
        return (
            response.status_code,
            parallel_client.session.get("_auth_user_id"),
            response["Referrer-Policy"],
            response["Cache-Control"],
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(submit, ["first@example.test", "second@example.test"]))
    assert sorted(status for status, *_ in outcomes) == [200, 302]
    assert sum(user_id is not None for _, user_id, *_ in outcomes) == 1
    assert all(referrer == "no-referrer" and cache == "private, no-store" for _, _, referrer, cache in outcomes)
    assert get_user_model().objects.filter(email__in=["first@example.test", "second@example.test"]).count() == 1
    invitation.refresh_from_db()
    assert invitation.registered_user is not None


@pytest.mark.django_db(transaction=True)
def test_parallel_issuance_enforces_author_limit():
    if connection.vendor != "postgresql":
        pytest.skip("SELECT FOR UPDATE requires PostgreSQL")
    author = create_test_user(email="limit-author@example.test", password="Password123!")
    for _ in range(4):
        create_invitation(author)

    def issue(_: int) -> str:
        try:
            create_invitation(author)
        except InvitationLimitReached:
            return "limited"
        return "created"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(issue, range(2)))
    assert sorted(results) == ["created", "limited"]
    assert active_invitations(author).count() == 5
