# Generated by Django 5.1.2 on 2025-03-02 07:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("infoMFSS", "0050_alter_pointphone_subscriber_number"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pointphone",
            options={"ordering": ["-id"], "verbose_name": "точка телефонии", "verbose_name_plural": "точки телефонии"},
        ),
        migrations.AlterField(
            model_name="branchesbox",
            name="equipment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="equipment_boxs",
                to="infoMFSS.equipmentinstallation",
                verbose_name="Подключенное оборудование",
            ),
        ),
    ]
