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
def room_type(context):
    qs = Room.objects.filter(user_id__username=context, r_status='1')
    emptylist = []
    for q in qs:
        emptylist.append(q.r_type.rt_title)
    emptylist = set(emptylist)
    return emptylist

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
def room_owner_username(context):
    qs = RoomOwner.objects.get(user_id__username=context)
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
    return round(abs(value - arg))

@register.filter
def cond(x):
    value = x.paymentgenerate_set.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00
    arg = x.paymentpaid_set.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00
    if(value - arg > 0):
        return True
    else:
        return False

@register.filter
def total_due(pg, pp):
    return round(abs(pg - pp))

@register.filter
def total_add(pg, pp):
    return round(abs(pg + pp))

@register.filter
def due_cond(pg,pp):
    if (pg - pp > 0):
        return True
    else:
        return False

@register.filter
def sum_due(l):
    sum = 0
    for x in l:
        if cond(x):
            data = subtract(x)
            sum += data
        else:
            pass
    return sum

@register.filter
def sum_advance(l):
    sum = 0
    for x in l:
        if cond(x):
            pass
        else:
            data = subtract(x)
            sum += data
    return sum

@register.filter
def has_group(user,group_name):
    return user.groups.filter(name=group_name).exists()