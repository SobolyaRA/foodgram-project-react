# Generated by Django 2.2.19 on 2023-02-20 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['-author_id'], 'verbose_name': 'Подписка на автора', 'verbose_name_plural': 'Подписки на авторов'},
        ),
    ]
