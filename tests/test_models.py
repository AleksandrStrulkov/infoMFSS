import pytest
from django.urls import reverse

from tests.factories import CableFactory, UserFactory
from users.utilities import signer


@pytest.mark.django_db
def test_multiple_allowed_persons(allowed_person_factory):
    persons = allowed_person_factory.create_batch(5)
    assert len(persons) == 5
    for person in persons:
        assert person.is_active


@pytest.mark.django_db
def test_user_activation(client):
    # Создаём пользователя
    user = UserFactory()

    # Подписываем email
    signed_email = signer.sign(user.email)

    # Проверяем, что пользователь ещё не активирован
    assert not user.is_active
    assert not user.is_activated

    # Имитируем переход по ссылке активации
    response = client.get(reverse("users:activate", kwargs={"sign": signed_email}))

    user.refresh_from_db()

    assert user.is_active
    assert user.is_activated
    assert response.status_code == 200


@pytest.mark.django_db
def test_number_mine_str(number_mine):
    assert str(number_mine) == number_mine.title


@pytest.mark.django_db
def test_subsystem_str(subsystem):
    assert str(subsystem) == subsystem.title
    # assert subsystem.number_mine is not None  # Проверяем, что шахта связана


@pytest.mark.django_db
def test_inclined_block_str(inclined_blocks):
    # inclined_block = inclined_blocks_factory()
    assert str(inclined_blocks) == inclined_blocks.title
    assert inclined_blocks.number_mine is not None  # Проверяем, что шахта связана


@pytest.mark.django_db
def test_tunnel_str(tunnel):
    assert str(tunnel) == f"{tunnel.title} {tunnel.inclined_blocks} (НШ-{tunnel.number_mine.title[-1]})"
    assert tunnel.number_mine is not None  # Проверяем, что шахта связана


@pytest.mark.django_db
def test_equipment_str(equipment):
    assert str(equipment) == equipment.title
    assert equipment.subsystem is not None  # Проверяем, что подсистема связана


@pytest.mark.django_db
def test_cable_str(cable):
    assert str(cable) == f"{cable.title}-{cable.device_type}"


@pytest.mark.django_db
def test_cable_none_device_type_str():
    cable = CableFactory(
        title="Parlan",
        device_type=None,
        description="Многопарный кабель",
        file_pdf=None,
        file_passport=None,
        file_certificate=None,
    )
    assert str(cable) == "Parlan"


@pytest.mark.django_db
def test_point_phone_str(point_phone):
    assert (
        str(point_phone) == f"{point_phone.title}/{point_phone.subscriber_number} "
        f"(НШ-{point_phone.number_mine.title[-1]})"
    )
