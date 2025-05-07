import random

import factory
import faker

from infoMFSS.models import (Cable, Equipment, InclinedBlocks, NumberMine,
                             PointPhone, Subsystem, Tunnel)
from users.models import AllowedPerson, User

fake = faker.Faker("ru_RU")


def random_middle_name():
    bases = ["Иван", "Петр", "Максим", "Александр", "Владимир"]
    return random.choice(bases) + "ович"


class AllowedPersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AllowedPerson

    last_name = factory.Faker("last_name", locale="ru_RU")
    first_name = factory.Faker("first_name", locale="ru_RU")
    middle_name = factory.LazyFunction(lambda: random_middle_name())
    is_active = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    last_name = factory.Faker("last_name", locale="ru_RU")
    first_name = factory.Faker("first_name", locale="ru_RU")
    middle_name = factory.LazyFunction(lambda: random_middle_name())
    email = factory.Sequence(lambda n: f"user{n}@example.com")  # уникальный email
    phone = factory.LazyFunction(lambda: fake.msisdn()[:12])
    telegram_id = factory.Faker("uuid4")
    is_activated = False
    is_active = False
    location_of_work = factory.Faker("company", locale="ru_RU")
    post = factory.Faker("job", locale="ru_RU")


class NumberMineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NumberMine

    title = factory.Iterator(
        [
            "Нефтешахта №1",
            "Нефтешахта №2",
            "Нефтешахта №3",
            "Все шахты",
        ]
    )
    address_mine = factory.Faker("address")
    slug = factory.LazyFunction(lambda: fake.msisdn()[:15])


class SubsystemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subsystem

    title = factory.Faker("word")
    description = factory.Faker("text")
    slug = factory.Faker("slug")


class InclinedBlocksFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InclinedBlocks

    title = factory.Faker("word")
    number_mine = factory.SubFactory(NumberMineFactory)  # создаём связанную шахту
    description = factory.Faker("text")
    slug = factory.Faker("slug")


class TunnelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tunnel

    title = factory.Faker("word")
    number_mine = factory.SubFactory(NumberMineFactory)  # создаём связанную шахту
    inclined_blocks = factory.SubFactory(InclinedBlocksFactory)  # создаём связанный уклонный блок
    tuf_bool = True
    inclined_bool = False
    description = factory.Faker("text")
    name_slag = factory.Faker("slug")


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment

    title = factory.Faker("word")
    device_type = factory.Faker("word")
    description = factory.Faker("text")
    subsystem = factory.SubFactory(SubsystemFactory)
    slug = factory.Faker("slug")
    file_pdf = None
    file_passport = None
    file_certificate = None


class CableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cable

    title = factory.Faker("word")
    device_type = factory.Faker("word")
    description = factory.Faker("text")
    file_pdf = None
    file_passport = None
    file_certificate = None


class PointPhoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PointPhone

    title = factory.Faker("word")
    number_mine = factory.SubFactory(NumberMineFactory)
    tunnel = factory.SubFactory(TunnelFactory)
    inclined_blocks = factory.SubFactory(InclinedBlocksFactory)
    subscriber_number = factory.Faker("word")
    picket = factory.Faker("word")
    description = factory.Faker("text")
    slug = factory.Faker("slug")
    serial_number = factory.Faker("word")
    device_type = factory.Faker("word")


class EquipmentFormFactory(factory.Factory):
    class Meta:
        model = Equipment

    number_mine = factory.LazyAttribute(lambda o: NumberMineFactory(title="Все шахты").id)
    subsystems = factory.LazyAttribute(lambda o: SubsystemFactory(title="Все подсистемы").id)
    incl_blocks = factory.LazyAttribute(lambda o: InclinedBlocksFactory(title="Все уклонные блоки").id)
    equipment = factory.LazyFunction(lambda: EquipmentFactory(title="Все оборудование").id)
