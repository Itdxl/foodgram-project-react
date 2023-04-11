from django.contrib import admin

from django.contrib.auth.models import Group, Permission
from django.db import models

# Переопределение модели Group
class MyGroup(Group):
    name = models.CharField(max_length=150, verbose_name="Имя группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

# Переопределение модели Permission
class MyPermission(Permission):
    name = models.CharField(max_length=255, verbose_name="Имя разрешения")

    class Meta:
        verbose_name = "Разрешение"
        verbose_name_plural = "Разрешения"