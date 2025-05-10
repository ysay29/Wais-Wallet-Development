from django.contrib import admin
from .models import Transaction, UserCategory
from savings.models import Saving

admin.site.register(Transaction)
admin.site.register(UserCategory)
admin.site.register(Saving)
