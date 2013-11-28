from django.contrib import admin
from models import UserData, Quota
from django.contrib.auth.models import User


class QuotaInline(admin.StackedInline):
    model = Quota


class UserDataInline(admin.StackedInline):
    model = UserData


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [UserDataInline, QuotaInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Quota)
admin.site.register(UserData)