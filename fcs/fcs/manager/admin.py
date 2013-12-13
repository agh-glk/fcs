from django.contrib import admin
from models import User, Quota, Task, CrawlingType, ServiceUnitPrice, Service


class QuotaInline(admin.StackedInline):
    model = Quota


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    inlines = [QuotaInline]


admin.site.register(User, UserAdmin)
admin.site.register(Quota)
admin.site.register(Task)
admin.site.register(CrawlingType)
admin.site.register(ServiceUnitPrice)
admin.site.register(Service)