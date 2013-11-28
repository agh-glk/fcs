from django.contrib import admin
from models import ClientData, Quota


class QuotaAdmin(admin.ModelAdmin):
    pass


class ClientDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(Quota, QuotaAdmin)
admin.site.register(ClientData, ClientDataAdmin)