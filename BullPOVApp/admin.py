from django.contrib import admin
from .models import *

admin.site.register(UserDetail)
admin.site.register(Stock)
admin.site.register(Trade)
admin.site.register(Contact)