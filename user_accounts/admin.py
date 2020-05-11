from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse

from django.contrib.auth.admin import UserAdmin
from user_accounts.models import User, Account, Transaction
from user_accounts.forms import CustomUserChangeForm, CustomUserCreationForm

# Register your models here.
# Admin Action Functions


def export_as_json(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response)
    return response


def make_users_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


def make_users_active(modeladmin, request, queryset):
    queryset.update(is_active=True)


# Action Descriptions
make_users_inactive.short_description = "Mark Selected Users as Inactive"
make_users_active.short_description = "Mark Selected Users as Active"
make_users_active.allowed_permissions = ('change',)
make_users_inactive.allowed_permissions = ('change',)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display_links = ('is_staff', 'first_name', 'last_name', 'username')
    list_display = [
        'phonenumber', 'username', 'wallet',
        'first_name', 'last_name', 'is_staff',
        'is_active', 'date_joined', 'last_login'
    ]
    search_fields = ('phonenumber', 'first_name',
                     'last_name', 'wallet__balance')
    list_filter = (
        ('is_staff', admin.BooleanFieldListFilter),
        ('is_superuser', admin.BooleanFieldListFilter),
        ('is_active', admin.BooleanFieldListFilter),
        ('is_producer', admin.BooleanFieldListFilter),
        ('is_secretary', admin.BooleanFieldListFilter),
    )
    actions = [make_users_inactive, make_users_active]


class AccountAdmin(admin.ModelAdmin):
    model = Account
    list_display = ['owner', 'balance', 'created_at']
    search_fields = [
        'owner__phonenumber',
        'owner__username',
        'balance',
    ]
    readonly_fields = ['owner', 'transactions', 'balance', 'created_at']


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    date_hierarchy = 'created_at'
    list_display = ('created_at', 'title', 'trans_type', 'account', 'amount')
    # search_fields = [
    #     'created_at', 'title', 'account__owner',
    #     'account__owner__phonenumber',
    #     'trans_type', 'account__balance', 'amount'
    # ]
    list_filter = ('created_at', 'title', 'trans_type')
    readonly_fields = ['amount', 'created_at', 'trans_type', 'account']

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.username.upper() != "TRALAHM":
            del actions['delete_selected']

        return actions


# Register your models here.
# admin.site.register(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Account)
admin.site.register(Transaction, TransactionAdmin)

# Admin site customization
# Admin site header
admin.site.site_header = "Uplift Studios Admin Dashboard"
admin.site.empty_value_display = "<NONE>"
admin.site.index_title = "Uplift Studios Management Portal"
admin.site.add_action(export_as_json)
