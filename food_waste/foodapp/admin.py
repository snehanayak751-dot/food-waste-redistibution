from django.contrib import admin
# Update this line to import FoodItem instead of Food
from .models import FoodItem, NGO, Volunteer, FoodRequest, Profile
@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ('ngo_id', 'ngo_name', 'phone')
    readonly_fields = ('ngo_id',)

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('volunteer_id', 'city', 'phone')
    readonly_fields = ('volunteer_id',)

# Register your models here.
admin.site.register(FoodItem)


admin.site.register(FoodRequest)
admin.site.register(Profile)