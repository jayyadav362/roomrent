from django import template
from datawork.models import *

register = template.Library()
from django.db.models import Sum

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

@register.filter
def sum_pg_amount(x):
    total = x.paymentgenerate_set.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00
    return total

@register.filter
def sum_pp_amount(x):
    total = x.paymentpaid_set.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00
    return total

@register.filter
def subtract(x):
    value = x.paymentgenerate_set.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00
    arg = x.paymentpaid_set.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00
    return value - arg

@register.filter
def cond(x):
    value = x.paymentgenerate_set.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00
    arg = x.paymentpaid_set.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00
    if(value - arg > 0):
        return True
    else:
        return False