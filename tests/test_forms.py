import pytest

from infoMFSS.forms import EquipmentForm


@pytest.mark.django_db
def test_contact_form_valid(equipment_form_factory):
    form = EquipmentForm(data=equipment_form_factory())
    assert form.is_valid(), form.errors
