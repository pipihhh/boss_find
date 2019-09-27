from django.contrib import admin
from core import models

# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Candidate)
admin.site.register(models.Provide)
admin.site.register(models.Position)
admin.site.register(models.Company)
admin.site.register(models.Select)
