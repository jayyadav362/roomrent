from django.contrib import admin
from datawork.models import *
# Register your models here.
admin.site.register(State)
admin.site.register(City)
admin.site.register(RoomOwner)
admin.site.register(Room)
admin.site.register(RoomType)
admin.site.register(RoomAllot)
admin.site.register(RoomRenter)
admin.site.register(PaymentPaid)
admin.site.register(PaymentGenerate)
