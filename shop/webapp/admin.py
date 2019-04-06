from django.contrib import admin
from webapp.models import RegistrationToken, Category, Product, Photo, Order


class RegistrationTokenAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'created_at']
    readonly_fields = ['token']


def list_admin_with_pk(*fields):
    class PkListAdmin(admin.ModelAdmin):
        list_display = ['pk'] + list(fields)
    return PkListAdmin


admin.site.register(Category, list_admin_with_pk('name'))
admin.site.register(Product, list_admin_with_pk('name'))
admin.site.register(Photo, list_admin_with_pk('product'))
admin.site.register(Order, list_admin_with_pk('user', 'phone', 'address'))

admin.site.register(RegistrationToken, RegistrationTokenAdmin)
