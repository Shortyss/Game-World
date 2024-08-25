from django.contrib import admin

from viewer.models import *
# Register your models here.


class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity')
    search_fields = ('name',)
    filter_horizontal = ('platform', 'genres', 'game_mode', 'developer', 'publisher')


admin.site.register(Game)
admin.site.register(Genre)
admin.site.register(GameMode)
admin.site.register(Developer)
admin.site.register(Platform)
admin.site.register(Publisher)
admin.site.register(Wishlist)
admin.site.register(DLC)
