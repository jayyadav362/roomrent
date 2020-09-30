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
