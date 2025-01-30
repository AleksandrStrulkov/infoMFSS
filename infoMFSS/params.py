# class FilterParams:
#     def __init__(self, request):
#         # Значения по умолчанию - "Все..."
#         self.mine = request.GET.get("mine")
#         self.subsystem = request.GET.get("subsystem")
#         self.incl_blocks = request.GET.get("incl_blocks")
#         self.equipment = request.GET.get("equipment")
#
#         # Проверяем, были ли переданы параметры формы
#         self.is_form_submitted = any(
#                 [
#                         self.mine is not None,
#                         self.subsystem is not None,
#                         self.incl_blocks is not None,
#                         self.equipment is not None
#                 ]
#         )
#
#     def to_dict(self):
#         return {
#                 "mine": self.mine,
#                 "subsystem": self.subsystem,
#                 "incl_blocks": self.incl_blocks,
#                 "equipment": self.equipment,
#         }

class FilterParams:
    def __init__(self, request):
        self.request = request
        self.params = request.GET

    def get(self, key, default=None):
        """Возвращает значение параметра по ключу."""
        return self.params.get(key, default)

    @property
    def is_form_submitted(self):
        """Проверяет, отправлена ли форма (есть хотя бы один параметр)."""
        return bool(self.params)
