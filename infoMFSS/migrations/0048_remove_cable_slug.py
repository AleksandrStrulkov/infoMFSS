# Generated by Django 5.1.2 on 2025-03-01 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("infoMFSS", "0047_alter_cable_file_certificate_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cable",
            name="slug",
        ),
    ]
