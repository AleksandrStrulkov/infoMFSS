import logging

from django.db import connection, models
from django.utils import timezone

logger = logging.getLogger(__name__)

NULLABLE = {"blank": True, "null": True}


class NumberMine(models.Model):
    """Номера шахт"""

    NAME = (
        ("Нефтешахта №1", "Нефтешахта №1"),
        ("Нефтешахта №2", "Нефтешахта №2"),
        ("Нефтешахта №3", "Нефтешахта №3"),
        ("Все шахты", "Все шахты"),
    )

    title = models.CharField(max_length=15, verbose_name="Шахта", choices=NAME)
    address_mine = models.CharField(max_length=250, verbose_name="Адрес шахты", **NULLABLE)
    slug = models.SlugField(max_length=15, unique=True, verbose_name="slug", **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "нефтешахта"
        verbose_name_plural = "нефтешахты"
        ordering = ["title"]

    @classmethod
    def truncate_table_restart_id(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"ALTER SEQUENCE infomfss_numbermine_id_seq RESTART WITH 1;")


class InclinedBlocks(models.Model):
    """Уклонные блоки"""

    title = models.CharField(max_length=100, verbose_name="Название уклонного блока")
    number_mine = models.ForeignKey(
        NumberMine,
        related_name="mine_bloxs",
        on_delete=models.CASCADE,
        verbose_name="Шахта",
        **NULLABLE,
    )
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name="slug", **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "уклонный блок"
        verbose_name_plural = "уклонные блоки"
        ordering = ["number_mine"]


class Tunnel(models.Model):
    """Выработка"""

    title = models.CharField(max_length=100, verbose_name="Выработка")
    number_mine = models.ForeignKey(
        NumberMine, related_name="mine_tunnels", on_delete=models.CASCADE, verbose_name="Шахта"
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks,
        related_name="incl_tunnels",
        on_delete=models.CASCADE,
        verbose_name="Уклонный блок",
        **NULLABLE,
        default="Туффит",
    )
    tuf_bool = models.BooleanField(verbose_name="Признак туффитового горизонта", default=False, **NULLABLE)
    inclined_bool = models.BooleanField(verbose_name="Признак уклонного блока", default=False, **NULLABLE)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    name_slag = models.CharField(max_length=100, verbose_name="Генерация slag", **NULLABLE)

    # slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)

    def save(self, *args, **kwargs):
        # Генерируем name перед сохранением
        if self.inclined_blocks is not None:
            self.name_slag = f"{self.title} {self.inclined_blocks} "
        else:
            self.name_slag = f"{self.title} {self.number_mine}"
        super().save(*args, **kwargs)

    def __str__(self):
        if self.inclined_blocks is not None:
            return f"{self.title} {self.inclined_blocks} (НШ-{self.number_mine.title[-1]})"
        else:
            return f"{self.title} (НШ-{self.number_mine.title[-1]})"

    class Meta:
        verbose_name = "выработка"
        verbose_name_plural = "выработки"
        ordering = ["number_mine"]


class Unit(models.Model):
    """Единица измерения количества"""

    NAME = (("м.", "м."), ("км.", "км."), ("шт.", "шт."))
    DESCRIPTION = (
        ("метр", "метр"),
        ("километр", "километр"),
        ("штук", "штук"),
    )

    title = models.CharField(max_length=10, verbose_name="Краткое описание", choices=NAME)
    description = models.CharField(max_length=15, verbose_name="Описание", choices=DESCRIPTION)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "единица измерения"
        verbose_name_plural = "единицы измерения"
        ordering = ["title"]


class Subsystem(models.Model):
    """Подсистема"""

    title = models.CharField(max_length=50, verbose_name="Подсистема")
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name="slug", **NULLABLE)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "подсистема"
        verbose_name_plural = "подсистемы"
        ordering = ["id"]


class Equipment(models.Model):
    """Перечень оборудования"""

    title = models.CharField(max_length=150, verbose_name="Оборудование", **NULLABLE)
    device_type = models.CharField(max_length=50, verbose_name="Тип", **NULLABLE)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    subsystem = models.ForeignKey(
        Subsystem, related_name="subsystem_equipment", on_delete=models.CASCADE, verbose_name="Подсистема", **NULLABLE
    )
    slug = models.SlugField(max_length=150, unique=True, verbose_name="slug", **NULLABLE)
    file_pdf = models.FileField(upload_to="pdf", **NULLABLE, verbose_name="Руководство по эксплуатации")
    file_passport = models.FileField(upload_to="pdf_passport", **NULLABLE, verbose_name="Паспорт")
    file_certificate = models.FileField(upload_to="pdf_certificate", **NULLABLE, verbose_name="Сертификат")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Создан новое оборудование: {self.title} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )

    class Meta:
        verbose_name = "оборудование"
        verbose_name_plural = "оборудования"
        ordering = ["-id"]


class Cable(models.Model):
    """Перечень кабелей"""

    title = models.CharField(max_length=100, verbose_name="Кабель")
    # subsystem = models.ForeignKey(
    #         Subsystem, related_name='subsystem_cable', on_delete=models.CASCADE,
    #         verbose_name='Подсистема', **NULLABLE
    # )
    device_type = models.CharField(max_length=50, verbose_name="Тип", **NULLABLE)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    # slug = models.SlugField(max_length=150, unique=True, verbose_name='slug', **NULLABLE)
    file_pdf = models.FileField(upload_to="pdf", **NULLABLE, verbose_name="Руководство по эксплуатации")
    file_passport = models.FileField(upload_to="pdf_passport", **NULLABLE, verbose_name="Паспорт")
    file_certificate = models.FileField(upload_to="pdf_certificate", **NULLABLE, verbose_name="Сертификат")

    def __str__(self):
        # if self.device_type is not None:
        #     return f"{self.title}-{self.device_type}"
        # else:
        return f"{self.device_type}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Создан новый кабель: {self.title} (ID: {self.id})", extra={"classname": self.__class__.__name__}
            )

    class Meta:
        verbose_name = "кабель"
        verbose_name_plural = "кабели"
        ordering = ["-id"]


class PointPhone(models.Model):
    """Точка телефонии"""

    title = models.CharField(max_length=100, verbose_name="Обозначение в проекте")
    number_mine = models.ForeignKey(
        NumberMine, verbose_name="Шахта", related_name="mine_phones", on_delete=models.CASCADE
    )
    tunnel = models.ForeignKey(
        Tunnel,
        related_name="tunnel_phones",
        on_delete=models.CASCADE,
        verbose_name="Выработка",
        **NULLABLE,
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks,
        related_name="block_phones",
        on_delete=models.CASCADE,
        verbose_name="Уклонный блок",
        **NULLABLE,
    )
    subscriber_number = models.CharField(
        max_length=10,
        verbose_name="Абонентский номер",
    )
    picket = models.CharField(max_length=100, verbose_name="Пикет", **NULLABLE)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    slug = models.SlugField(max_length=150, unique=True, verbose_name="slug", **NULLABLE)
    serial_number = models.CharField(max_length=50, verbose_name="Зав. №", **NULLABLE)
    device_type = models.CharField(max_length=50, verbose_name="Тип", **NULLABLE)

    def __str__(self):
        return f"{self.title}/{self.subscriber_number} (НШ-{self.number_mine.title[-1]})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Создан новая точка телефонии: {self.title} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )

    class Meta:
        verbose_name = "точка телефонии"
        verbose_name_plural = "точки телефонии"
        ordering = ["-id"]


class BranchesBox(models.Model):
    """Распределительные коробки"""

    title = models.CharField(max_length=100, verbose_name="Обозначение в проекте")
    inclined_blocks = models.ForeignKey(
        InclinedBlocks,
        related_name="incl_boxs",
        on_delete=models.CASCADE,
        verbose_name="Уклонный блок",
        **NULLABLE,
    )
    name_slag = models.CharField(max_length=100, verbose_name="Генерация slag", **NULLABLE)
    number_mine = models.ForeignKey(
        NumberMine, verbose_name="Шахта", related_name="mine_boxs", on_delete=models.CASCADE
    )
    tunnel = models.ForeignKey(
        Tunnel, related_name="tunnel_boxs", on_delete=models.CASCADE, verbose_name="Выработка", **NULLABLE
    )
    subsystem = models.ForeignKey(
        Subsystem, related_name="sub_boxs", on_delete=models.CASCADE, verbose_name="Подсистема", **NULLABLE
    )
    equipment = models.ForeignKey(
        "EquipmentInstallation",
        related_name="equipment_boxs",
        on_delete=models.CASCADE,
        verbose_name="Связанное оборудование",
        **NULLABLE,
    )
    picket = models.CharField(max_length=100, verbose_name="Пикет", **NULLABLE)
    boolean_block = models.BooleanField(verbose_name="Признак уклонного блока", default=False)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    ip_address = models.CharField(max_length=13, verbose_name="IP адрес", **NULLABLE)
    serial_number = models.CharField(max_length=50, verbose_name="Зав. №", **NULLABLE)
    device_type = models.CharField(max_length=50, verbose_name="Тип", **NULLABLE)

    def save(self, *args, **kwargs):
        # Генерируем name перед сохранением
        self.name_slag = (
            f"{self.title[0:2]}#{self.title[3:]}({self.number_mine.title[0]}" f"НШ{self.number_mine.title[-1]})"
        )
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Создан новая распред.коробка: {self.title} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )

    def __str__(self):
        return f"{self.title} (НШ-{self.number_mine.title[-1]})"
        # return f'{self.title}({self.number_mine})'

    class Meta:
        verbose_name = "распред.коробка"
        verbose_name_plural = "распред.коробки"
        ordering = ["title"]


class CableMagazine(models.Model):
    """Кабельный журнал"""

    cable = models.ForeignKey(
        Cable,
        related_name="equipment_cables",
        on_delete=models.CASCADE,
        verbose_name="Кабель",
    )
    name = models.CharField(max_length=61, editable=False, verbose_name="Трасса от - до")
    subsystem = models.ForeignKey(
        Subsystem, related_name="sub_magazines", on_delete=models.CASCADE, verbose_name="Подсистема"
    )
    number_mine = models.ForeignKey(
        NumberMine, related_name="mine_magazines", on_delete=models.CASCADE, verbose_name="Шахта"
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks,
        related_name="incl_magazines",
        on_delete=models.CASCADE,
        verbose_name="Уклонный блок",
        default="Туффит",
        **NULLABLE,
    )
    # track_from_box = models.ForeignKey(
    #     BranchesBox,
    #     related_name="box_from",
    #     on_delete=models.CASCADE,
    #     verbose_name="От распределительной коробки",
    #     **NULLABLE,
    # )
    track_from = models.ForeignKey(
        "EquipmentInstallation",
        related_name="track_from",
        on_delete=models.CASCADE,
        verbose_name="От оборудования",
        **NULLABLE,
    )
    # track_from = models.CharField(
    #     max_length=100,
    #     verbose_name="Начало трассы",
    #     **NULLABLE,
    # )
    # track_to_box = models.ForeignKey(
    #     BranchesBox,
    #     related_name="box_to",
    #     on_delete=models.CASCADE,
    #     verbose_name="До распределительной коробки",
    #     **NULLABLE,
    # )
    # track_to_phone = models.ForeignKey(
    #     PointPhone,
    #     related_name="phone_to",
    #     on_delete=models.CASCADE,
    #     verbose_name="До телефонной точки",
    #     **NULLABLE,
    # )
    track_to = models.ForeignKey(
        "EquipmentInstallation",
        related_name="track_to",
        on_delete=models.CASCADE,
        verbose_name="До оборудования",
        **NULLABLE,
    )
    # track_to = models.CharField(
    #     max_length=100,
    #     verbose_name="Конец трассы",
    #     **NULLABLE,
    # )
    distance = models.PositiveIntegerField(verbose_name="Протяженность")
    unit = models.ForeignKey(
        Unit, related_name="unit_magazines", on_delete=models.CASCADE, verbose_name="Единица измерения"
    )
    cable_bool = models.ForeignKey(
        "Execution",
        related_name="cable_bool",
        on_delete=models.SET_NULL,
        verbose_name="Выполнение",
        **NULLABLE,
    )
    slug = models.SlugField(max_length=150, unique=True, verbose_name="slug", **NULLABLE)

    def save(self, *args, **kwargs):
        # Генерируем name перед сохранением
        # if self.track_to is not None:
        self.name = f"{self.track_from.name}/{self.track_to.name}"
        # else:
        #     self.name = f"{self.track_from_box.title}/{self.track_to_phone.title}"
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Создана новая трасса кабеля: {self.name} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )

    def __str__(self):
        if self.inclined_blocks:
            return (
                f"{self.cable.title}-({self.name})-{self.subsystem}"
                f" {self.inclined_blocks} (НШ-{self.number_mine.title[-1]})"
            )
        else:
            return f"{self.cable.title}-({self.name})-{self.subsystem} (НШ-{self.number_mine.title[-1]})"

    class Meta:
        verbose_name = "отдельную позицию"
        verbose_name_plural = "кабельный журнал"
        ordering = ["-id"]


class EquipmentInstallation(models.Model):
    """Место установки оборудования"""

    title = models.ForeignKey(
        Equipment, related_name="eq_installs", on_delete=models.CASCADE, verbose_name="Оборудование"
    )
    name = models.CharField(max_length=100, verbose_name="Обозначение в проекте", **NULLABLE)
    point_phone = models.ForeignKey(
        PointPhone,
        related_name="phones",
        on_delete=models.CASCADE,
        verbose_name="Точка телефонии",
        **NULLABLE,
    )
    branches_box = models.ForeignKey(
        BranchesBox,
        related_name="box_installs",
        on_delete=models.CASCADE,
        verbose_name="Распределительная коробка",
        **NULLABLE,
    )
    subsystem = models.ForeignKey(
        Subsystem,
        related_name="sub_installs",
        on_delete=models.CASCADE,
        verbose_name="Подсистема",
        **NULLABLE,
    )
    number_mine = models.ForeignKey(
        NumberMine,
        related_name="mine_installs",
        on_delete=models.CASCADE,
        verbose_name="Шахта",
        **NULLABLE,
    )
    tunnel = models.ForeignKey(
        Tunnel,
        related_name="tunnel_installs",
        on_delete=models.CASCADE,
        verbose_name="Выработка",
        **NULLABLE,
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks,
        related_name="incl_installs",
        on_delete=models.CASCADE,
        verbose_name="Уклонный блок",
        default="Туффит",
        **NULLABLE,
    )
    equipment_bool = models.ForeignKey(
        "Execution",
        related_name="exe_bool",
        on_delete=models.SET_NULL,
        verbose_name="Выполнение",
        **NULLABLE,
    )
    picket = models.CharField(max_length=100, verbose_name="Пикет", **NULLABLE)
    ip_address = models.CharField(max_length=13, verbose_name="IP адрес", **NULLABLE)
    serial_number = models.CharField(max_length=50, verbose_name="Зав. №", **NULLABLE)
    device_type = models.CharField(max_length=50, verbose_name="Тип", **NULLABLE)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)
    file_graphics = models.FileField(upload_to="pdf_graphics", **NULLABLE)

    def __str__(self):
        return f"{self.title}-({self.name})/{self.subsystem}/{self.tunnel}"

    def save(self, *args, **kwargs):
        if self.point_phone is not None:
            self.name = self.point_phone.title
            self.number_mine = self.point_phone.number_mine
            self.tunnel = self.point_phone.tunnel
            self.picket = self.point_phone.picket
            self.serial_number = self.point_phone.serial_number
            self.device_type = self.point_phone.device_type
            self.subsystem = Subsystem.objects.get(title="АТС")
            if self.point_phone.inclined_blocks is not None:
                self.inclined_blocks = self.point_phone.inclined_blocks
        if self.branches_box is not None:
            self.name = self.branches_box.title
            self.number_mine = self.branches_box.number_mine
            self.tunnel = self.branches_box.tunnel
            self.subsystem = self.branches_box.subsystem
            self.picket = self.branches_box.picket
            self.ip_address = self.branches_box.ip_address
            self.serial_number = self.branches_box.serial_number
            self.device_type = self.branches_box.device_type
            if self.branches_box.inclined_blocks is not None:
                self.inclined_blocks = self.branches_box.inclined_blocks
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Добавлено новое место установки оборудования: {self.name} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )

    class Meta:
        verbose_name = "место установки оборудования"
        verbose_name_plural = "места установки оборудования"
        ordering = ["-id"]


class Execution(models.Model):
    """Отчет выполнения работ"""

    equipment_install = models.ForeignKey(
        EquipmentInstallation,
        related_name="eq_executions",
        on_delete=models.CASCADE,
        verbose_name="Список оборудования",
        **NULLABLE,
    )
    cable_magazine = models.ForeignKey(
        CableMagazine,
        related_name="cable_executions",
        verbose_name="Список трасс кабелей",
        on_delete=models.CASCADE,
        **NULLABLE,
    )
    execution_bool = models.BooleanField(verbose_name="Установка выполнена", default=False)
    date_start = models.DateField(verbose_name="Дата начала", **NULLABLE)
    date_end = models.DateField(verbose_name="Дата завершения", **NULLABLE)
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)

    def __str__(self):
        if self.equipment_install:
            return f"{self.equipment_install}"
        elif self.cable_magazine:
            return f"{self.cable_magazine}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if self.equipment_install and self.equipment_install.equipment_bool != self:
            EquipmentInstallation.objects.filter(pk=self.equipment_install.pk).update(equipment_bool=self)
        if is_new:
            if self.equipment_install:
                logger.info(
                    f"Добавлено новое выполнение работ: {self.equipment_install.title}",
                    extra={"classname": self.__class__.__name__},
                )
            elif self.cable_magazine:
                logger.info(
                    f"Добавлено новое выполнение работ: {self.cable_magazine.cable.title}",
                    extra={"classname": self.__class__.__name__},
                )

    class Meta:
        verbose_name = "выполнение работы"
        verbose_name_plural = "отчет выполнения работ"
        ordering = ["equipment_install"]


class DateUpdate(models.Model):
    """Дата последнего изменения"""

    # update = models.DateField(default=timezone.now)
    update = models.DateTimeField(
        verbose_name="Дата обновления данных", auto_now=False, auto_now_add=False, default=timezone.now, **NULLABLE
    )
    description = models.TextField(verbose_name="Краткое описание", **NULLABLE)

    # def formatted_datetime(self):
    #     return formats.date_format(self.update, "H:M:s D, d/M/Y")

    def __str__(self) -> str:
        local_time = timezone.localtime(self.update)
        return local_time.strftime("%d.%m.%Y %H:%M")

    class Meta:
        verbose_name = "дата последнего изменения"
        verbose_name_plural = "даты последнего изменения"
        ordering = ["-update"]


class Violations(models.Model):
    """Нарушения"""

    number_act = models.CharField(max_length=100, verbose_name="Номер акта", **NULLABLE)
    date_act = models.DateField(verbose_name="Дата проверки", **NULLABLE)
    issued_by_act = models.CharField(max_length=100, verbose_name="Кем выдано", **NULLABLE)
    number_mine = models.ForeignKey(
        NumberMine, verbose_name="Шахта", on_delete=models.CASCADE, related_name="mine_act"
    )
    title = models.TextField(verbose_name="Описание нарушения", **NULLABLE)
    execution_bool = models.BooleanField(verbose_name="Нарушение устранено", default=False)
    file_act = models.FileField(upload_to="pdf_act", **NULLABLE, verbose_name="Акт")
    file_notification = models.FileField(upload_to="pdf_notifications", **NULLABLE, verbose_name="Уведомление")

    def __str__(self):
        return f"{self.number_act} от {self.date_act}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Добавлено новое нарушение: {self.number_mine.title} " f"{self.title[:10]}",
                extra={"classname": self.__class__.__name__},
            )

    class Meta:
        verbose_name = "нарушение"
        verbose_name_plural = "нарушения"
        ordering = ["date_act"]


class Visual(models.Model):
    number_mine = models.ForeignKey(
        NumberMine, verbose_name="Шахта", related_name="mine_visual", on_delete=models.CASCADE, **NULLABLE
    )
    subsystem = models.ForeignKey(
        Subsystem, related_name="sub_visual", on_delete=models.CASCADE, verbose_name="Подсистема", **NULLABLE
    )
    equipment = models.ForeignKey(
        Equipment, related_name="equipment_visual", on_delete=models.CASCADE, verbose_name="Оборудование", **NULLABLE
    )
    cable = models.ForeignKey(
        Cable, related_name="cable_visual", on_delete=models.CASCADE, verbose_name="Кабель", **NULLABLE
    )
    file_pdf = models.FileField(upload_to="pdf_visual", **NULLABLE, verbose_name="Файл")
    data = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    def __str__(self):
        return f"{self.equipment} ({self.number_mine}, {self.subsystem})"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Проверяем, что объект новый
        super().save(*args, **kwargs)
        if is_new:
            logger.info(
                f"Добавлен новый файл pdf: {self.equipment} (ID: {self.id})",
                extra={"classname": self.__class__.__name__},
            )

    class Meta:
        verbose_name = "визуализация"
        verbose_name_plural = "визуализации"
        ordering = ["number_mine"]


class Beacon(models.Model):
    """Маячки"""

    designation = models.CharField(max_length=50, verbose_name="Обозн. в проекте", unique=True)
    subsystem = models.CharField(max_length=20, verbose_name="Подсистема", default="Позиционирование")
    number_mine = models.ForeignKey(
        NumberMine,
        verbose_name="Шахта",
        related_name="mine_beacons",
        on_delete=models.CASCADE,
    )
    tunnel = models.ForeignKey(
        Tunnel,
        verbose_name="Выработка",
        related_name="tunnel_beacons",
        on_delete=models.CASCADE,
        **NULLABLE,
    )
    inclined_blocks = models.ForeignKey(
        InclinedBlocks,
        verbose_name="Уклонный блок",
        related_name="incl_beacons",
        on_delete=models.CASCADE,
        default="Туффит",
        **NULLABLE,
    )
    picket = models.CharField(max_length=10, verbose_name="Пикет", **NULLABLE)
    mac_address = models.CharField(max_length=17, verbose_name="MAC-адрес", unique=True, default="")
    serial_number = models.CharField(max_length=10, verbose_name="Зав. №", unique=True, default="")
    minor = models.CharField(max_length=10, verbose_name="МИНОР", unique=True, default="")
    execution_bool = models.BooleanField(verbose_name="Установлен", default=False)
    data = models.DateField(verbose_name="Дата монтажа")

    def __str__(self):
        return f"{self.designation} ({self.number_mine.title})"

    class Meta:
        verbose_name = "бикон"
        verbose_name_plural = "биконы"
        ordering = ["number_mine"]
