from django.db import models
from django.utils import formats
import locale

NULLABLE = {'blank': True, 'null': True}


class NumberMine(models.Model):
    """Номера шахт"""
    NAME = (
            ('Нефтешахта №1', 'Нефтешахта №1'),
            ('Нефтешахта №2', 'Нефтешахта №2'),
            ('Нефтешахта №3', 'Нефтешахта №3'),
            ('Все шахты', 'Все шахты')
    )

    title = models.CharField(max_length=15, verbose_name='Шахта', choices=NAME)
    address_mine = models.CharField(max_length=250, verbose_name='Адрес шахты')
    slug = models.SlugField(max_length=15, unique=True, verbose_name='slug', **NULLABLE)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'нефтешахта'
        verbose_name_plural = 'нефтешахты'
        ordering = ['title']


class InclinedBlocks(models.Model):
    """Уклонные блоки"""

    title = models.CharField(max_length=100, verbose_name='Название уклонного блока')
    number_mine = models.ForeignKey(
            NumberMine, related_name='mine_bloxs', on_delete=models.CASCADE,
            verbose_name='Шахта', **NULLABLE,
    )
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def __str__(self):
        if self.number_mine is None:
            return self.title
        return f'{self.title} {self.number_mine}'

    class Meta:
        verbose_name = 'уклонный блок'
        verbose_name_plural = 'уклонные блоки'
        ordering = ['number_mine']


class Tunnel(models.Model):
    """Выработка"""

    title = models.CharField(max_length=100, verbose_name='Выработка')
    number_mine = models.ForeignKey(NumberMine, related_name='mine_tunnels', on_delete=models.CASCADE,
                                    verbose_name='Шахта')
    inclined_blocks = models.ForeignKey(
        InclinedBlocks, related_name='incl_tunnels', on_delete=models.CASCADE,
        verbose_name='Уклонный блок', **NULLABLE, default='Туффит',
    )
    tuf_bool = models.BooleanField(verbose_name='Признак туффитового горизонта', default=False, **NULLABLE)
    inclined_bool = models.BooleanField(
            verbose_name='Признак уклонного блока',
            default=False, **NULLABLE
    )
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    name_slag = models.CharField(max_length=100, verbose_name='Генерация slag', **NULLABLE)
    # slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def save(self, *args, **kwargs):
        # Генерируем name перед сохранением
        if self.inclined_blocks is not None:
            self.name_slag = f"{self.title} {self.inclined_blocks}"
        else:
            self.name_slag = f"{self.title} {self.number_mine}"
        super().save(*args, **kwargs)

    def __str__(self):
        if self.inclined_blocks is not None:
            return f'{self.title} {self.inclined_blocks}'
        else:
            return f'{self.title} {self.number_mine}'

    class Meta:
        verbose_name = 'выработка'
        verbose_name_plural = 'выработки'
        ordering = ['title']


class Unit(models.Model):
    """Единица измерения количества"""
    NAME = (
        ('м.', 'м.'),
        ('км.', 'км.'),
        ('шт.', 'шт.')
    )
    DESCRIPTION = (
        ('метр', 'метр'),
        ('километр', 'километр'),
        ('штук', 'штук'),
    )

    title = models.CharField(max_length=10, verbose_name='Краткое описание', choices=NAME)
    description = models.CharField(max_length=15, verbose_name='Описание', choices=DESCRIPTION)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'единица измерения'
        verbose_name_plural = 'единицы измерения'
        ordering = ['title']


class Subsystem(models.Model):
    """Подсистема"""
    title = models.CharField(max_length=50, verbose_name='Подсистема')
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'подсистема'
        verbose_name_plural = 'подсистемы'
        ordering = ['id']


class Equipment(models.Model):
    """Перечень оборудования"""

    title = models.CharField(max_length=150, verbose_name='Оборудование')
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)
    file_pdf = models.FileField(upload_to='pdf')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'оборудование'
        verbose_name_plural = 'оборудования'
        ordering = ['-id']


class Cable(models.Model):
    """Перечень кабелей"""

    title = models.CharField(max_length=100, verbose_name='Кабель')
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'кабель'
        verbose_name_plural = 'кабели'
        ordering = ['title']


class PointPhone(models.Model):
    """Точка телефонии"""
    title = models.CharField(max_length=100, verbose_name='Точка телефонии')
    number_mine = models.ForeignKey(NumberMine, verbose_name='Шахта', related_name='mine_phones',
                                    on_delete=models.CASCADE)
    tunnel = models.ForeignKey(
        Tunnel, related_name='tunnel_phones', on_delete=models.CASCADE,
        verbose_name='Выработка'
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks, related_name='block_phones', on_delete=models.CASCADE,
        verbose_name='Уклонный блок', default='Туффит', **NULLABLE,
    )
    subscriber_number = models.CharField(max_length=10, verbose_name='Абонентский номер', unique=True,)
    picket = models.CharField(max_length=100, verbose_name='Пикет', **NULLABLE)
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def __str__(self):
        return f'{self.title}({self.tunnel}/{self.subscriber_number})'

    class Meta:
        verbose_name = 'точка телефонии'
        verbose_name_plural = 'точки телефонии'
        ordering = ['title']


class BranchesBox(models.Model):
    """Распределительные коробки"""

    title = models.CharField(max_length=100, verbose_name='Название')
    inclined_blocks = models.ForeignKey(
        InclinedBlocks, related_name='incl_boxs', on_delete=models.CASCADE,
        verbose_name='Уклонный блок', default='Туффит', **NULLABLE,
    )
    name_slag = models.CharField(max_length=100, verbose_name='Генерация slag', **NULLABLE)
    number_mine = models.ForeignKey(
        NumberMine, verbose_name='Шахта', related_name='mine_boxs',
        on_delete=models.CASCADE
    )
    tunnel = models.ForeignKey(
        Tunnel, related_name='tunnel_boxs', on_delete=models.CASCADE,
        verbose_name='Выработка'
    )
    subsystem = models.ForeignKey(
        Subsystem, related_name='sub_boxs', on_delete=models.CASCADE,
        verbose_name='Подсистема'
    )
    equipment = models.ForeignKey(
        'EquipmentInstallation', related_name='equipment_boxs', on_delete=models.CASCADE,
        verbose_name='Оборудование', **NULLABLE
    )
    picket = models.CharField(max_length=100, verbose_name='Пикет', **NULLABLE)
    boolean_block = models.BooleanField(verbose_name='Признак уклонного блока', default=False)
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)
    # slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)


    def save(self, *args, **kwargs):
        # Генерируем name перед сохранением
        self.name_slag = f"{self.title[0:2]}#{self.title[3:]}({self.number_mine.title[0]}" \
                         f"Ш{self.number_mine.title[-1]})"
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.title}({self.tunnel})'
        # return f'{self.title}({self.number_mine})'

    class Meta:
        verbose_name = 'распред.коробка'
        verbose_name_plural = 'распред.коробки'
        ordering = ['title']


class CableMagazine(models.Model):
    """Кабельный журнал"""

    cable = models.ForeignKey(
        Cable, related_name='equipment_cables', on_delete=models.CASCADE,
        verbose_name='Кабель', )
    name = models.CharField(max_length=61, editable=False, verbose_name='Трасса от - до')
    subsystem = models.ForeignKey(
        Subsystem, related_name='sub_magazines', on_delete=models.CASCADE,
        verbose_name='Подсистема'
    )
    number_mine = models.ForeignKey(
        NumberMine, related_name='mine_magazines', on_delete=models.CASCADE,
        verbose_name='Шахта'
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks, related_name='incl_magazines', on_delete=models.CASCADE,
        verbose_name='Уклонный блок', default='Туффит', **NULLABLE,
    )
    track_from_box = models.ForeignKey(
            BranchesBox, related_name='box_from', on_delete=models.CASCADE,
            verbose_name='От распределительной коробки', **NULLABLE,
    )
    track_from = models.CharField(max_length=100, verbose_name='Начало трассы', **NULLABLE,)
    track_to_box = models.ForeignKey(
            BranchesBox, related_name='box_to', on_delete=models.CASCADE,
            verbose_name='До распределительной коробки', **NULLABLE,
    )
    track_to_phone = models.ForeignKey(
            PointPhone, related_name='phone_to', on_delete=models.CASCADE,
            verbose_name='До телефонной точки', **NULLABLE,
    )
    track_to = models.CharField(max_length=100, verbose_name='Конец трассы', **NULLABLE,)
    distance = models.PositiveIntegerField(verbose_name='Протяженность')
    unit = models.ForeignKey(
        Unit, related_name='unit_magazines', on_delete=models.CASCADE, verbose_name='Единица '
                                                                                    'измерения'
    )
    slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    # @property
    # def get_name(self):
    #     return f'{self.track_from} - {self.track_to}'

    def save(self, *args, **kwargs):
        # Генерируем name перед сохранением
        if self.track_to_box is not None:
            self.name = f"{self.track_from_box.title} - {self.track_to_box.title}"
        else:
            self.name = f"{self.track_from_box.title} - {self.track_to_phone.title}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}: -{self.subsystem}-{self.number_mine}-{self.inclined_blocks}'

    class Meta:
        verbose_name = 'отдельную позицию'
        verbose_name_plural = 'кабельный журнал'
        ordering = ['-name']



class EquipmentInstallation(models.Model):
    """Место установки оборудования"""

    title = models.ForeignKey(
        Equipment, related_name='eq_installs', on_delete=models.CASCADE,
        verbose_name='Оборудование'
    )
    name = models.CharField(max_length=100, verbose_name='Обозначение в проекте', **NULLABLE)
    point_phone = models.ForeignKey(
        PointPhone, related_name='phones', on_delete=models.CASCADE,
        verbose_name='Точка телефонии', **NULLABLE,
    )
    branches_box = models.ForeignKey(
        BranchesBox, related_name='box_installs', on_delete=models.CASCADE,
        verbose_name='Распределительная коробка', **NULLABLE,
    )
    subsystem = models.ForeignKey(
        Subsystem, related_name='sub_installs', on_delete=models.CASCADE,
        verbose_name='Подсистема'
    )
    number_mine = models.ForeignKey(
        NumberMine, related_name='mine_installs', on_delete=models.CASCADE,
        verbose_name='Шахта', **NULLABLE,
    )
    tunnel = models.ForeignKey(
        Tunnel, related_name='tunnel_installs', on_delete=models.CASCADE,
        verbose_name='Выработка', **NULLABLE,
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks, related_name='incl_installs', on_delete=models.CASCADE,
        verbose_name='Уклонный блок', default="Туффит", **NULLABLE,
    )
    equipment_bool = models.ForeignKey('Execution', related_name='exe_bool', on_delete=models.SET_NULL,
                                       verbose_name='Выполнение',  **NULLABLE,)
    picket = models.CharField(max_length=100, verbose_name='Пикет', **NULLABLE)
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)

    def __str__(self):
        return f'{self.title}-({self.name})/{self.subsystem}/{self.tunnel}/' \
               f'ПК{self.picket}'

    class Meta:
        verbose_name = 'место установки оборудования'
        verbose_name_plural = 'места установки оборудования'
        ordering = ['title']


class Execution(models.Model):
    """Отчет выполнения работ"""

    equipment_install = models.ForeignKey(
        EquipmentInstallation, related_name='eq_executions', on_delete=models.CASCADE,
        verbose_name='Список оборудования', **NULLABLE
    )
    cable_magazine = models.ForeignKey(
        CableMagazine, related_name='cable_executions', verbose_name='Список трасс кабелей',
        on_delete=models.CASCADE, **NULLABLE
    )
    # subsystem = models.ForeignKey(
    #         Subsystem, related_name='sub_executions', on_delete=models.CASCADE,
    #         verbose_name='Подсистема', **NULLABLE
    # )
    # number_mine = models.ForeignKey(
    #         NumberMine, related_name='mine_executions', on_delete=models.CASCADE,
    #         verbose_name='Шахта', **NULLABLE
    # )
    # tunnel = models.ForeignKey(
    #         Tunnel, related_name='tunnel_executions', on_delete=models.CASCADE,
    #         verbose_name='Выработка'
    # )
    # inclined_blocks = models.ForeignKey(
    #         InclinedBlocks, related_name='incl_execution', on_delete=models.CASCADE, verbose_name='Уклонный блок',
    #         **NULLABLE, default='Туффит',
    # )
    # volume_total = models.PositiveIntegerField(verbose_name='Общий объем')
    # volume_used = models.PositiveIntegerField(verbose_name='Всего установлено', default=0)
    # volume_remaining = models.PositiveIntegerField(verbose_name='Остаток', default=0)
    execution_bool = models.BooleanField(verbose_name='Установка выполнена',
                                         default=False)
    # unit = models.ForeignKey(
    #         Unit, related_name='execution', on_delete=models.CASCADE, verbose_name='Единица '
    #                                                                                'измерения'
    # )
    date_start = models.DateField(verbose_name='Дата начала', **NULLABLE)
    date_end = models.DateField(verbose_name='Дата завершения', **NULLABLE)
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)

    # slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def __str__(self):
        return f'{self.equipment_install}-{self.cable_magazine}'

    class Meta:
        verbose_name = 'выполнение работы'
        verbose_name_plural = 'отчет выполнения работ'
        ordering = ['equipment_install']


class DateUpdate(models.Model):
    """Дата последнего изменения"""
    # update = models.DateField(default=timezone.now)
    update = models.DateTimeField(verbose_name='Дата обновления данных', auto_now=False, auto_now_add=False,
                                  **NULLABLE)
    description = models.TextField(verbose_name='Краткое описание', **NULLABLE)

    # def formatted_datetime(self):
    #     return formats.date_format(self.update, "H:M:s D, d/M/Y")

    def __str__(self) -> str:
        return self.update.strftime('%d.%m.%Y %H:%M',)

    class Meta:
        verbose_name = 'дата последнего изменения'
        verbose_name_plural = 'даты последнего изменения'
        ordering = ['-update']
