from django.contrib import admin
from .models import SiteProfile

# Register your models here.
admin.site.register(SiteProfile)

admin.site.site_header = "KrushComics Administration"
admin.site.site_title = "KrushComics Admin"
admin.site.index_title = "KrushComics Content Management"

