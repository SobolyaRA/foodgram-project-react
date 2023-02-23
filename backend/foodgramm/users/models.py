from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.db.models import UniqueConstraint

from .validators import username_validator_not_past_me, validate_username


class User(AbstractUser):
    """Кастомная модель пользователя
    """

    username = models.CharField(
        verbose_name='Username',
        max_length=150,
        unique=True,
        help_text=(
            'Необходимо использовать не более 150 символов.'
            'Разрешено использовать только буквы, цифры и @/./+/-/_'

        ),
        validators=[
            username_validator_not_past_me,
            validate_username
        ],
        error_messages={
            'unique': ('Пользователь с таким именем уже существует.')
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        blank=True,
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        validators=[validate_password],
    )
    subscribe = models.ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='self',
        symmetrical=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password',
    ]

    class Meta:
        ordering = ['username', ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.email


class Follow(models.Model):
    """Модель подписки на авторов
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['-author_id', ]
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            UniqueConstraint(
                name='unique_user_following',
                fields=['user', 'author'],
            ),
        ]

    def __str__(self) -> str:
        return (f'{self.user.username} подписан на {self.author.username}')
