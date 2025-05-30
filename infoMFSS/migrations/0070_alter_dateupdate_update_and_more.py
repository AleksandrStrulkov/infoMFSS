# Generated by Django 5.1.2 on 2025-04-20 16:22

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("infoMFSS", "0069_beacon_subsystem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dateupdate",
            name="update",
            field=models.DateTimeField(
                blank=True,
                default=django.utils.timezone.now,
                null=True,
                verbose_name="Дата обновления данных",
            ),
        ),
        migrations.AlterField(
            model_name="numbermine",
            name="address_mine",
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name="Адрес шахты"),
        ),
    ]
