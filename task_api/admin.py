from django.contrib import admin
from .models import *
# Register your models here.
class TasksAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'due_date')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_filter = ('due_date',)
    date_hierarchy = 'due_date'
    ordering = ('due_date',)
    readonly_fields = ('title', 'description', 'due_date')


admin.site.register(Tasks, TasksAdmin)
