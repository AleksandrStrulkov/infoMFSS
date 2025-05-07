import pytest_factoryboy

from tests.factories import (AllowedPersonFactory, CableFactory,
                             EquipmentFactory, EquipmentFormFactory,
                             InclinedBlocksFactory, NumberMineFactory,
                             PointPhoneFactory, SubsystemFactory,
                             TunnelFactory, UserFactory)

pytest_factoryboy.register(AllowedPersonFactory)
pytest_factoryboy.register(UserFactory)
pytest_factoryboy.register(NumberMineFactory)
pytest_factoryboy.register(SubsystemFactory)
pytest_factoryboy.register(InclinedBlocksFactory)
pytest_factoryboy.register(TunnelFactory)
pytest_factoryboy.register(EquipmentFactory)
pytest_factoryboy.register(CableFactory)
pytest_factoryboy.register(PointPhoneFactory)
pytest_factoryboy.register(EquipmentFormFactory)
