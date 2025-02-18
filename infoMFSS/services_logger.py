import logging
from django.core.mail import mail_admins


logger = logging.getLogger(__name__)


class LoggingMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info(f'Запрос: {request.method} {request.path} {request.user.last_name}',
                        extra={'classname': self.__class__.__name__})
            return super().dispatch(request, *args, **kwargs)
        else:
            logger.info(f'Запрос: {request.method} {request.path} ANONYMOUS USER',
                        extra={'classname': self.__class__.__name__})
            return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        user = self.request.user
        user_info = f'{user.last_name} ({user.email})' if user.is_authenticated else 'Анонимный пользователь'
        error_message = f'Ошибка валидации формы: {form.errors}. Пользователь: {user_info}). ' \
                        f'Класс: {self.__class__.__name__}'

        # Логирование ошибки
        logger.error(error_message, extra={'classname': self.__class__.__name__})

        # Отправка email администратору
        mail_admins(
                subject='Ошибка валидации формы',
                message=error_message,
                fail_silently=True,
        )

        return super().form_invalid(form)


def logger_context(self):
    user = self.request.user
    if user.is_authenticated:
        return logger.info(f'Контекст обработан и выведен в шаблон. Пользователь: {user.last_name}',
                       extra={'classname': self.__class__.__name__})
    return logger.info(
        f'Контекст обработан и выведен в шаблон. Анонимный пользователь',
        extra={'classname': self.__class__.__name__}
        )

def logger_form_valid(self):
    user = self.request.user
    if user.is_authenticated:
        return logger.info(f'Форма успешно обработана. Пользователь: {user.last_name}',
                       extra={'classname': self.__class__.__name__})
    return logger.info(
            f'Контекст обработан и выведен в шаблон. Анонимный пользователь',
            extra={'classname': self.__class__.__name__}
    )