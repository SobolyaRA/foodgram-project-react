import re

from django.core.exceptions import ValidationError


def username_validator_not_past_me(value):
    '''Проверка, что username не равно 'me' '''
    message = (
        'В сервисе запрещено использовать '
        'значение \"me\" как имя пользователя.'
    )
    if value == 'me':
        raise ValidationError(message)


def validate_username(value):
    '''Проверка, что username состоит из корректных символов'''
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в нике.'),
            params={'value': value},
        )
