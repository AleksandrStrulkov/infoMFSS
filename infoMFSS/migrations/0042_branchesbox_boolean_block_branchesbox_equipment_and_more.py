# Generated by Django 5.1.2 on 2025-01-08 16:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("infoMFSS", "0041_remove_branchesbox_boolean_block_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="branchesbox",
            name="boolean_block",
            field=models.BooleanField(default=False, verbose_name="Признак уклонного блока"),
        ),
        migrations.AddField(
            model_name="branchesbox",
            name="equipment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="equipment_boxs",
                to="infoMFSS.equipmentinstallation",
                verbose_name="Оборудование",
            ),
        ),
        migrations.AddField(
            model_name="branchesbox",
            name="inclined_blocks",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="incl_boxs",
                to="infoMFSS.inclinedblocks",
                verbose_name="Уклонный блок",
            ),
        ),
        migrations.AddField(
            model_name="branchesbox",
            name="picket",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="Пикет"),
        ),
        migrations.AddField(
            model_name="branchesbox",
            name="tunnel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tunnel_boxs",
                to="infoMFSS.tunnel",
                verbose_name="Выработка",
            ),
        ),
        migrations.AlterField(
            model_name="branchesbox",
            name="subsystem",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sub_boxs",
                to="infoMFSS.subsystem",
                verbose_name="Подсистема",
            ),
        ),
    ]
