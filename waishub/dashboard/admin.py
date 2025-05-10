from django.contrib import admin
from .models import Notification, Reminder

admin.site.register(Notification)
admin.site.register(Reminder)

from django.contrib import admin
from .models import Budget  

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'review_period', 'created_at')
    list_filter = ('category', 'review_period')
