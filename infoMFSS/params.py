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
