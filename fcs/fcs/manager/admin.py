from django.contrib import admin
from models import User, Quota, Task, CrawlingType


class QuotaInline(admin.StackedInline):
    model = Quota


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')
    search_fields = ('id', 'username', 'email')
    inlines = [QuotaInline]


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'max_links', 'priority', 'expire_date', 'created', 'last_data_download')
    search_fields = ('id', 'user', 'name', 'max_links', 'priority', 'expire_date', 'created', 'last_data_download')


admin.site.register(User, UserAdmin)
admin.site.register(Quota)
admin.site.register(Task, TaskAdmin)
admin.site.register(CrawlingType)
