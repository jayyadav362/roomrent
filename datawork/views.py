from django.shortcuts import *
from .forms import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse,HttpResponse
from django.db.models import Q
from datetime import datetime
import json as simplejson
# Create your views here.
def home(r):
    data = {}
    return render(r,'home.html',data)

# AJAX
def load_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state__id=state_id).all()
    return render(request, 'city_dropdown_list_options.html', {'cities': cities})
    # return JsonResponse(list(cities.values('id', 'name')), safe=False)


def logins(r):
    mu = LoginForm(r.POST or None)
    if r.method == 'POST':
        if mu.is_valid:
            email = r.POST['email']
            password = r.POST['password']
            username = User.objects.get(email=email.lower()).username

            status = 0
            try:
                profile = RoomRenter.objects.get(user_id__username=username)
                status = 1
                r.session['name'] = 'renter'
            except ObjectDoesNotExist:
                profile = RoomOwner.objects.get(user_id__username=username)
                status = 2
                r.session['name'] = 'owner'

            u = profile.user_id.username
            user = authenticate(username=u,password=password)
            login(r, user)

            if status == 1:
                return redirect('renter_profile')
            elif status == 2:
                return redirect('owner_profile')
            else:
                return redirect('logins')

    data = {"form": mu}
    return render(r, 'logins.html', data)

def logouts(r):
    logout(r)
    return redirect('homepage')

# room renter -------------------------------------
def user_register_renter(r):
    u = RegisterForm(r.POST or None)
    if r.method == "POST":
        if u.is_valid():
            u.save()
            a = authenticate(username=u.cleaned_data['username'], password=u.cleaned_data['password1'])
            login(r, a)
            return redirect('register_renter')
    data = {"form":u}
    return render(r, 'user_register_renter.html', data)

@login_required(login_url=logins)
def register_renter(r):
    a = RegisterRenterForm(r.POST or None, r.FILES or None)
    if r.method == "POST":
        if a.is_valid():
            d = a.save(commit=False)
            user = User.objects.get(username=r.user)
            d.user_id = user
            d.save()
            return redirect('renter_profile')
    data = {"form": a,}
    return render(r, 'register_renter.html', data)

@login_required(login_url=logins)
def renter_profile(r):
    data = {
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomrenter/rr_profile.html',data)

# room owner -------------------------------------------------
def user_register_owner(r):
    u = RegisterForm(r.POST or None)
    if r.method == "POST":
        if u.is_valid():
            u.save()
            a = authenticate(username=r.POST.get('username'), password=r.POST.get('password1'))
            login(r, a)
            return redirect('register_owner')
    data = {"form":u}
    return render(r, 'user_register_owner.html', data)

@login_required(login_url=logins)
def register_owner(r):
    a = RegisterOwnerForm(r.POST or None, r.FILES or None)
    if r.method == "POST":
        if a.is_valid():
            d = a.save(commit=False)
            user = User.objects.get(username=r.user)
            d.user_id = user
            d.save()
            return redirect('owner_profile')
    data = {
        "form": a,
    }
    return render(r, 'register_owner.html', data)

@login_required(login_url=logins)
def owner_profile(r):
    data = {
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/ro_profile.html',data)

@login_required(login_url=logins)
def owner_rooms(r):
    rm = AddRoomForm(r.POST or None, r.FILES or None)
    if r.method == "POST":
        if rm.is_valid():
            d = rm.save(commit=False)
            user = User.objects.get(username=r.user)
            d.user_id = user
            d.slug = r.POST.get('r_title')
            d.save()
            return redirect('owner_rooms')
    data = {
        "form": rm,
        "rooms": Room.objects.filter(user_id__username=r.user),
        "rooms_al": RoomAllot.objects.filter(user_id__username=r.user),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_rooms.html', data)

@login_required(login_url=logins)
def room_allot(r):
    if r.is_ajax():
        term = r.GET.get('term')
        renter = User.objects.filter(roomrenter__rr_contact__exact=term)
        response_content = list(renter.values())
        return JsonResponse(response_content, safe=False)

    if r.method == "POST":
        d = RoomAllot()
        user = User.objects.get(username=r.user)
        d.user_id = user
        d.renter = User(r.POST.get('renter'))
        d.ra_room_id = Room(r.POST.get('ra_room_id'))
        d.slug = r.POST.get('rr_id')
        d.save()
        return redirect('room_allot')

        # check_renter_room = RoomAllot.objects.get(Q(ra_room_id=r.POST.get('ra_room_id')) & Q(renter=r.POST.get('renter')),ra_status='1')
        # check=0
        # try:
        #     check_renter_room
        #     print('Already allot this room!')
        #     check = 1
        # except ObjectDoesNotExist:
        #     d = RoomAllot()
        #     user = User.objects.get(username=r.user)
        #     d.user_id = user
        #     d.renter = User(r.POST.get('renter'))
        #     d.ra_room_id = Room(r.POST.get('ra_room_id'))
        #     d.ra_slug = r.POST.get('rr_id')
        #     d.save()
        #     check = 2
        #
        # if check == 1:
        #     return redirect('room_allot')
        # elif check == 2:
        #     return redirect('room_allot')
        # else:
        #     return redirect('owner_profile')

    data = {
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
        "renter": User.objects.all(),
        "room": Room.objects.filter(user_id__username=r.user,r_status='1'),
    }
    return render(r, 'roomowner/ro_room_allot.html', data)

@login_required(login_url=logins)
def my_renter(r):
    data = {
        "renters": RoomAllot.objects.filter(user_id__username=r.user, ra_status='1'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/ro_my_renter.html',data)

@login_required(login_url=logins)
def room_allot_request(r):
    data = {
        "roomallot_request": RoomAllot.objects.filter(user_id__username=r.user,ra_status='0'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_roomallot_request.html', data)

@login_required(login_url=logins)
def room_allot_pending(r):
    data = {
        "roomallot_pending": RoomAllot.objects.filter(user_id__username=r.user,ra_status='2'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_roomallot_pending.html', data)

@login_required(login_url=logins)
def allot_active(r,a_id):
    active = RoomAllot.objects.get(ra_id=a_id,ra_room_id__r_status='1')
    #check = RoomAllot.objects.get(Q(ra_room_id=active.ra_room_id) & Q(renter=active.renter))
    active.ra_status = '1'
    active.ra_doc = datetime.now()
    active.save()
    return redirect('room_allot')

@login_required(login_url=logins)
def allot_pending(r,p_id):
    pending = RoomAllot.objects.get(ra_id=p_id)
    pending.ra_status = '2'
    pending.ra_doc = datetime.now()
    pending.save()
    return redirect('room_allot_pending')

@login_required(login_url=logins)
def allot_delete(r,d_id):
    delete = RoomAllot.objects.get(ra_id=d_id)
    delete.delete()
    return redirect('room_allot')

@login_required(login_url=logins)
def view_renter_profile(r,rnt_id):
    data = {
        "renter_profile":RoomRenter.objects.get(user_id=rnt_id),
        "user_r": User.objects.get(roomrenter__user_id=rnt_id),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
        "room_al": RoomAllot.objects.filter(renter__id=rnt_id).filter(user_id__username=r.user)
    }
    return render(r,'roomowner/view_renter_profile.html',data)

@login_required(login_url=logins)
def room_view(r,rm_id):
    data = {
        "room_view": Room.objects.get(r_id=rm_id),
        "room_renter": RoomAllot.objects.filter(ra_room_id=rm_id,ra_status='1'),
        "room_renter_request": RoomAllot.objects.filter(ra_room_id=rm_id,ra_status='0'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/room_view.html',data)

@login_required(login_url=logins)
def room_edit(r,et_id):
    room = Room.objects.get(r_id=et_id)
    re = EditRoomForm(r.POST or None,instance=room)
    if r.method == "POST":
        if re.is_valid():
            re.save()
            return redirect("../room_view/"+str(room.r_id))
    data = {
        "form":re,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/room_edit.html',data)

#--------------------------------------------------------------------------




