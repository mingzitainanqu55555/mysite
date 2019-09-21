from django.contrib import admin
from .models import LikeCount,LikeRecond
# Register your models here.
@admin.register(LikeCount)
class LikeCountAdmin(admin.ModelAdmin):
    list_display = ('content_object','liked_num')

@admin.register(LikeRecond)
class LikeRecondAdmin(admin.ModelAdmin):
    list_display = ('content_object','user','liked_time')