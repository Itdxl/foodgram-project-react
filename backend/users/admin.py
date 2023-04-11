from django.contrib import admin
from django.db import models

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'email', 'first_name', 'last_name', 'password'
    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('user', 'author')



class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name="Группы")


class Token(models.Model):
    token = models.CharField(max_length=100, verbose_name="Токены")