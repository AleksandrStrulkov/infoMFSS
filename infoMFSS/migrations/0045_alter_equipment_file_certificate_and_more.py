# Generated by Django 5.1.2 on 2025-02-28 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("infoMFSS", "0044_alter_tunnel_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="equipment",
            name="file_certificate",
            field=models.FileField(blank=True, null=True, upload_to="Сертификат"),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="file_passport",
            field=models.FileField(blank=True, null=True, upload_to="Паспорт"),
        ),
        migrations.AlterField(
            model_name="equipment",
            name="file_pdf",
            field=models.FileField(blank=True, null=True, upload_to="Руководство по эксплуатации"),
        ),
    ]
