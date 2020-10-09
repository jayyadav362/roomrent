from django import template
from datawork.models import *

register = template.Library()

@register.filter
def room_allot_count(context):
    qs = RoomAllot.objects.filter(ra_room_id=context,ra_status='1')
    if qs.exists():
        return qs.count()
    else:
        return 0

@register.filter
def room_count(context):
    qs = Room.objects.filter(user_id=context, r_status='1')
    if qs.exists():
        return qs.count()
    else:
        return 0

@register.filter
def room_owner_contact(context):
    qs = RoomOwner.objects.get(user_id=context)
    if qs:
        return qs.ro_contact
    else:
        return 0

@register.filter
def room_owner_house(context):
    qs = RoomOwner.objects.get(user_id=context)
    if qs:
        return qs.ro_house
    else:
        return 0

@register.filter
def room_owner_id(context):
    qs = RoomOwner.objects.get(user_id=context)
    if qs:
        return qs.ro_id
    else:
        return 0

@register.filter
def room_renter_contact(context):
    qs = RoomRenter.objects.get(user_id=context)
    if qs:
        return qs.rr_contact
    else:
        return 0
