from django.contrib import admin
from .models import Child, Reward, Task, Mentor, Redemption, Shop
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'phone')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    def phone(self, instance):
        return instance.phone
    phone.short_description = 'Phone'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('user', 'identifier', 'points')
    search_fields = ('user__username', 'identifier')
    list_filter = ('points',)

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_required')
    search_fields = ('title',)
    list_filter = ('points_required',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'points', 'deadline', 'completed')
    search_fields = ('title',)
    list_filter = ('deadline', 'completed')

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ('child', 'points_used', 'date_redeemed', 'shop')
    search_fields = ('child__user__username', 'shop__name')
    list_filter = ('date_redeemed', 'shop')

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'max_points')
    search_fields = ('name', 'user__username')
