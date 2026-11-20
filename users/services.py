from __future__ import annotations

import re
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.utils import timezone

from users.models import Invitation, User


def send_new_password(email: str, new_password: str) -> None:
    """Preserve the existing notification helper for other callers."""
    send_mail(
        subject="Вы сменили пароль",
        message=f"Ваш новый пароль: {new_password}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )


MAX_ACTIVE_INVITATIONS = 5
INVITATION_LIFETIME = timedelta(hours=48)
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{43}\Z")


class InvitationLimitReached(Exception):
    """The author already has the maximum number of active invitations."""


class InvalidInvitation(Exception):
    """The invitation cannot be redeemed."""


def active_invitations(author: User) -> QuerySet[Invitation]:
    """Return unexpired and unused invitations owned by the author."""
    return Invitation.objects.filter(
        created_by=author, used_at__isnull=True, registered_user__isnull=True, expires_at__gt=timezone.now()
    ).order_by("-created_at")


def redeemed_invitations(author: User) -> QuerySet[Invitation]:
    """Return colleagues registered through this author's invitations."""
    return (
        Invitation.objects.filter(created_by=author, used_at__isnull=False)
        .select_related("registered_user")
        .order_by("-used_at")
    )


def get_valid_invitation(token: str) -> Invitation | None:
    """Find a valid invitation without exposing invalid token details."""
    if not TOKEN_PATTERN.fullmatch(token):
        return None
    invitation = Invitation.objects.select_related("created_by").filter(token=token).first()
    return invitation if invitation is not None and invitation.is_valid() else None


def create_invitation(author: User) -> Invitation:
    """Issue a token while serializing concurrent requests by this author."""
    with transaction.atomic():
        User.objects.select_for_update().get(pk=author.pk)
        if active_invitations(author).count() >= MAX_ACTIVE_INVITATIONS:
            raise InvitationLimitReached
        now = timezone.now()
        return Invitation.objects.create(
            token=secrets.token_urlsafe(32), created_by=author, created_at=now, expires_at=now + INVITATION_LIFETIME
        )


def redeem_invitation(token: str, user: User) -> User:
    """Create the account and redeem the token in one locked transaction."""
    if not TOKEN_PATTERN.fullmatch(token):
        raise InvalidInvitation
    try:
        with transaction.atomic():
            invitation = Invitation.objects.select_for_update().filter(token=token).first()
            if invitation is None or not invitation.is_valid():
                raise InvalidInvitation
            user.is_active = True
            user.is_activated = True
            user.save()
            invitation.used_at = timezone.now()
            invitation.registered_user = user
            invitation.save(update_fields=["used_at", "registered_user"])
    except IntegrityError as error:
        raise InvalidInvitation from error
    return user
