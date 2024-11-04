# Generated by Django 5.1.2 on 2024-11-04 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Кабель')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'кабель',
                'verbose_name_plural': 'кабели',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Оборудование')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'оборудование',
                'verbose_name_plural': 'оборудования',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='InclinedBlocks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название уклонного блока')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'уклонный блок',
                'verbose_name_plural': 'уклонные блоки',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='NumberMine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('Нефтешахта №1', 'Нефтешахта №1'), ('Нефтешахта №2', 'Нефтешахта №2'), ('Нефтешахта №3', 'Нефтешахта №3')], max_length=15, verbose_name='Шахта')),
                ('address_mine', models.CharField(max_length=250, verbose_name='Адрес шахты')),
                ('slug', models.SlugField(blank=True, max_length=15, null=True, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'нефтешахта',
                'verbose_name_plural': 'нефтешахты',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Subsystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Подсистема')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'подсистема',
                'verbose_name_plural': 'подсистемы',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('м.', 'м.'), ('км.', 'км.'), ('шт.', 'шт.')], max_length=10, verbose_name='Краткое описание')),
                ('description', models.CharField(choices=[('метр', 'метр'), ('километр', 'километр'), ('штук', 'штук')], max_length=15, verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'единица измерения',
                'verbose_name_plural': 'единицы измерения',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='CableMagazine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(editable=False, max_length=61, verbose_name='Трасса от - до')),
                ('track_from', models.CharField(max_length=100, verbose_name='Начало трассы')),
                ('track_to', models.CharField(max_length=100, verbose_name='Конец трассы')),
                ('distance', models.PositiveIntegerField(verbose_name='Протяженность')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
                ('cable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipment_cables', to='infoMFSS.cable', verbose_name='Кабель')),
                ('inclined_blocks', models.ForeignKey(blank=True, default='Туффит', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incl_magazines', to='infoMFSS.inclinedblocks', verbose_name='Уклонный блок')),
                ('number_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_magazines', to='infoMFSS.numbermine', verbose_name='Шахта')),
                ('subsystem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_magazines', to='infoMFSS.subsystem', verbose_name='Подсистема')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_magazines', to='infoMFSS.unit', verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'отдельную позицию',
                'verbose_name_plural': 'кабельный журнал',
                'ordering': ['-name'],
            },
        ),
        migrations.CreateModel(
            name='EquipmentInstallation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picket', models.CharField(blank=True, max_length=100, null=True, verbose_name='Пикет')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='eq_installs', to='infoMFSS.equipment', verbose_name='Оборудование')),
                ('inclined_blocks', models.ForeignKey(blank=True, default='Туффит', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incl_installs', to='infoMFSS.inclinedblocks', verbose_name='Уклонный блок')),
                ('number_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_installs', to='infoMFSS.numbermine', verbose_name='Шахта')),
                ('subsystem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_installs', to='infoMFSS.subsystem', verbose_name='Подсистема')),
            ],
            options={
                'verbose_name': 'место установки оборудования',
                'verbose_name_plural': 'места установки оборудования',
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='inclinedblocks',
            name='number_mine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_bloxs', to='infoMFSS.numbermine', verbose_name='Шахта'),
        ),
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execution_bool', models.BooleanField(default=False, verbose_name='Установка выполнена')),
                ('date_start', models.DateField(blank=True, null=True, verbose_name='Дата начала')),
                ('date_end', models.DateField(blank=True, null=True, verbose_name='Дата завершения')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('cable_magazine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cable_executions', to='infoMFSS.cablemagazine', verbose_name='Кабельный журнал')),
                ('equipment_install', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='eq_executions', to='infoMFSS.equipmentinstallation', verbose_name='Оборудование')),
                ('inclined_blocks', models.ForeignKey(blank=True, default='Туффит', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incl_execution', to='infoMFSS.inclinedblocks', verbose_name='Уклонный блок')),
                ('number_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_executions', to='infoMFSS.numbermine', verbose_name='Шахта')),
                ('subsystem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_executions', to='infoMFSS.subsystem', verbose_name='Подсистема')),
            ],
            options={
                'verbose_name': 'выполнение работы',
                'verbose_name_plural': 'выполнения работы',
                'ordering': ['equipment_install'],
            },
        ),
        migrations.CreateModel(
            name='Tunnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Выработка')),
                ('tuf_bool', models.BooleanField(default=False, verbose_name='Признак туффитового горизонта')),
                ('inclined_bool', models.BooleanField(default=False, verbose_name='Признак уклонного блока')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
                ('inclined_blocks', models.ForeignKey(blank=True, default='Туффит', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incl_tunnels', to='infoMFSS.inclinedblocks', verbose_name='Уклонный блок')),
                ('number_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_tunnels', to='infoMFSS.numbermine', verbose_name='Шахта')),
            ],
            options={
                'verbose_name': 'выработка',
                'verbose_name_plural': 'выработки',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='PointPhone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Точка телефонии')),
                ('subscriber_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Абонентский номер')),
                ('picket', models.CharField(blank=True, max_length=100, null=True, verbose_name='Пикет')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
                ('inclined_blocks', models.ForeignKey(blank=True, default='Туффит', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='block_phones', to='infoMFSS.inclinedblocks', verbose_name='Уклонный блок')),
                ('number_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_phones', to='infoMFSS.numbermine', verbose_name='Шахта')),
                ('tunnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel_phones', to='infoMFSS.tunnel', verbose_name='Выработка')),
            ],
            options={
                'verbose_name': 'точка телефонии',
                'verbose_name_plural': 'точки телефонии',
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='equipmentinstallation',
            name='tunnel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel_installs', to='infoMFSS.tunnel', verbose_name='Выработка'),
        ),
        migrations.CreateModel(
            name='BranchesBox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('picket', models.CharField(blank=True, max_length=100, null=True, verbose_name='Пикет')),
                ('boolean_block', models.BooleanField(default=False, verbose_name='Признак уклонного блока')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Краткое описание')),
                ('slug', models.SlugField(blank=True, max_length=150, null=True, unique=True, verbose_name='slug')),
                ('inclined_blocks', models.ForeignKey(blank=True, default='Туффит', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='incl_boxs', to='infoMFSS.inclinedblocks', verbose_name='Уклонный блок')),
                ('number_mine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mine_boxs', to='infoMFSS.numbermine', verbose_name='Шахта')),
                ('subsystem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_boxs', to='infoMFSS.subsystem', verbose_name='Подсистема')),
                ('tunnel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tunnel_boxs', to='infoMFSS.tunnel', verbose_name='Выработка')),
            ],
            options={
                'verbose_name': 'распред.коробка',
                'verbose_name_plural': 'распред.коробки',
                'ordering': ['title'],
            },
        ),
    ]
