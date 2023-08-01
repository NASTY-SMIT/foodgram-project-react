from django.contrib import admin

from . import models


@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
    search_fields = ['user__first_name', 'user__last_name', 'user__username']
