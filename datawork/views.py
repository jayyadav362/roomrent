from django.shortcuts import *
from .forms import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from datedelta import datedelta
from datetime import datetime
import string
import random
from django.db.models import Sum
from datawork.templatetags import template_tags
# Create your views here.

def create_txn_code(digit):
    return "".join(random.choices(string.digits,k=digit))

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def home(r):
    return render(r, 'home.html')

def city_search(r):
    if r.is_ajax():
        term = r.GET.get('term')
        city = City.objects.filter(name__icontains=term)[:5]
        response_content = list(city.values())
        return JsonResponse(response_content, safe=False)

    # if 'term' in r.GET:
    #     qs = City.objects.filter(name__icontains=r.GET.get('term'))[:5]
    #     titles = list()
    #     for city in qs:
    #         titles.append(city.name)
    #     return JsonResponse(titles, safe=False)

def search_room(r):
    if r.method == 'GET':
        house = RoomOwner.objects.filter(city__name=r.GET.get('city'))
        data = {
            "house": house,
            "type":RoomType.objects.all(),
        }
        return render(r,'search.html',data)

def room_type(r,rt_id):
    house = RoomOwner.objects.filter(Q(city__name=r.GET.get('city')) & Q(user_id__room__r_type__slug=rt_id) & Q(user_id__room__r_status='1'))
    data = {
        "house": house,
        "type": RoomType.objects.all(),
    }
    return render(r, 'search.html', data)

def house_view(r,h_id):
    owner = RoomOwner.objects.get(user_id__username=h_id)
    room_query = RoomQueryForm(r.POST or None)
    if r.method == 'POST':
        if room_query.is_valid:
            s = room_query.save(commit=False)
            s.user_id = User(owner.user_id_id)
            s.save()
            messages.success(r, "Room Query send successfully!")
            return redirect("../house_view/" + str(owner.user_id.username))
    data = {
        "form":room_query,
        "house":owner,
        "room":Room.objects.filter(user_id__username=owner.user_id.username,r_status='1')
    }
    return render(r,'house_view.html',data)

def room_view(r,r_id):
    room = Room.objects.get(slug=r_id)
    data = {
        "room_view": room,
        "room_owner": RoomOwner.objects.get(user_id__username=room.user_id),
    }
    return render(r,'room_view.html',data)

def logins(r):
    form = LoginForm(r.POST or None)
    if r.method == 'POST':
        if form.is_valid:
            email = r.POST['email']
            password = r.POST['password']
            try:
                username = User.objects.get(email=email.lower()).username
                user = authenticate(username=username,password=password)
                if user is not None:
                    login(r, user)
                else:
                    messages.error(r,"Your password is incorrect!")
                    return redirect('logins')

                if user.groups.filter(name='renter').exists():
                    return redirect('renter_profile')
                elif user.groups.filter(name='owner').exists():
                    return redirect('owner_profile')

            except User.DoesNotExist:
                messages.error(r,"The email address or password is incorrect. Please retry...")
                return redirect('logins')

    data = {"form": form}
    return render(r, 'registration/logins.html', data)

@login_required(login_url=logins)
def room_request(r,rq_id):
    request = RoomAllot()
    request.renter = r.user
    room = Room.objects.get(slug=rq_id)
    request.ra_room_id = Room(room.r_id)
    request.user_id = User(room.user_id_id)
    request.ra_status = '0'
    request.save()
    messages.success(r, "room request successfully!")
    return redirect('renter_profile')

def logouts(r):
    logout(r)
    return redirect('logins')

# AJAX
@login_required(login_url=logins)
def load_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state__id=state_id).all().order_by('name')
    return render(request, 'city_dropdown_list_options.html', {'cities': cities})

# room renter -------------------------------------
def user_register_renter(r):
    u = RegisterForm(r.POST or None)
    if r.method == "POST":
        if u.is_valid():
            c = u.save()
            group = Group.objects.get(name='renter')
            c.groups.add(group)
            a = authenticate(username=u.cleaned_data['username'], password=u.cleaned_data['password1'])
            login(r, a)
            return redirect('register_renter')
    data = {"form":u}
    return render(r, 'registration/user_register_renter.html', data)

@login_required(login_url=logins)
def register_renter(r):
    a = RegisterRenterForm(r.POST or None, r.FILES or None)
    if r.method == "POST":
        if a.is_valid():
            d = a.save(commit=False)
            d.user_id = r.user
            d.save()
            return redirect('renter_profile')
    data = {"form": a,}
    return render(r, 'registration/register_renter.html', data)

@login_required(login_url=logins)
def renter_profile(r):
    check = RoomRenter.objects.filter(user_id__username=r.user).count()
    if check == 0:
        return redirect('register_renter')

    allot = RoomAllot.objects.filter(renter__username=r.user, ra_status='1').filter(ra_room_id__r_status='1')
    for x in allot:
        doj = x.ra_doc
        doj = datetime(doj.year, doj.month, 2)
        while diff_month(datetime.now().date(), doj) >= 0:
            cond = Q(pg_month__month=doj.month, pg_month__year=doj.year) & Q(pg_allot_id=x.ra_id) & Q(
                user_id__username=x.renter)
            if PaymentGenerate.objects.filter(cond).exists() == False:
                p = PaymentGenerate()
                p.pg_txn = create_txn_code(8)
                p.pg_month = doj
                p.pg_amount = x.ra_room_id.r_rent / x.ra_room_id.roomallot_set.filter(ra_status='1').count()
                p.pg_allot_id = RoomAllot(x.ra_id)
                p.user_id = x.renter
                p.owner = x.user_id
                p.save()
            else:
                try:
                    p = PaymentGenerate.objects.get(
                        Q(pg_month__month=datetime.now().date().month, pg_month__year=datetime.now().date().year) & Q(
                            pg_allot_id=x.ra_id) & Q(user_id__username=x.renter))
                    p.pg_amount = x.ra_room_id.r_rent / x.ra_room_id.roomallot_set.filter(ra_status='1').count()
                    p.save()
                except ObjectDoesNotExist:
                    pass
            doj = datetime(doj.year, doj.month, 2) + datedelta(months=1)

    data = {
        "room_request": RoomAllot.objects.filter(renter__username=r.user, ra_status='0'),
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomrenter/rr_profile.html',data)

@login_required(login_url=logins)
def renter_update_image(r):
    room = RoomRenter.objects.get(user_id__username=r.user)
    if r.method == "POST":
        image = room
        image.rr_image = r.FILES['rr_image']
        image.save()
        return redirect("renter_profile")
    data = {
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_profile.html', data)

@login_required(login_url=logins)
def renter_update_profile(r):
    renter = RoomRenter.objects.get(user_id__username=r.user)
    profile = UpdateRenterForm(r.POST or None, instance=renter)
    up = UpdateProfile(r.POST or None,instance=r.user)
    if r.method == "POST":
        if up.is_valid():
            user = up.save(commit=False)
            profile.save()
            user.save()
            return redirect('renter_profile')
    else:
        up = UpdateProfile(instance=r.user)
        profile = UpdateRenterForm(instance=renter)
    data = {
        "form":up,
        "profile":profile,
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomrenter/renter_update_profile.html',data)

@login_required(login_url=logins)
def renter_update_id_proof(r):
    room = RoomRenter.objects.get(user_id__username=r.user)
    if r.method == "POST":
        image = room
        image.rr_id_proof = r.FILES['id_proof']
        image.save()
        return redirect("renter_profile")
    data = {
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomrenter/rr_profile.html', data)

@login_required(login_url=logins)
def request_delete(r,r_id):
    delete = RoomAllot.objects.get(slug=r_id)
    delete.delete()
    messages.error(r, "room request delete successfully!")
    return redirect('renter_profile')

@login_required(login_url=logins)
def password_change_renter(r):
    if r.method == 'POST':
        form = PasswordChangeForm(r.user, r.POST or None)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(r, user)  # Important!
            messages.success(r, 'Your password was successfully updated!')
            return redirect('password_change_renter')
        else:
            messages.error(r, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(r.user)
    data = {
        "form":form,
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomrenter/rr_password_change.html', data)

@login_required(login_url=logins)
def renter_rooms(r):
    data = {
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
        "rooms_a": RoomAllot.objects.filter(renter__username=r.user, ra_status='1'),
        "rooms_p": RoomAllot.objects.filter(renter__username=r.user, ra_status='2'),
    }
    return render(r,'roomrenter/rr_rooms.html',data)

@login_required(login_url=logins)
def renter_payment(r):
    data = {
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
        "room": RoomAllot.objects.filter(Q(renter__username=r.user, ra_status='1') | Q(renter__username=r.user, ra_status='2')),
    }
    return render(r,'roomrenter/rr_payment.html',data)

# room owner -------------------------------------------------
def user_register_owner(r):
    u = RegisterForm(r.POST or None)
    if r.method == "POST":
        if u.is_valid():
            c = u.save()
            group = Group.objects.get(name='owner')
            c.groups.add(group)
            a = authenticate(username=r.POST.get('username'), password=r.POST.get('password1'))
            login(r, a)
            return redirect('register_owner')
    data = {"form":u}
    return render(r, 'registration/user_register_owner.html', data)

@login_required(login_url=logins)
def register_owner(r):
    a = RegisterOwnerForm(r.POST or None, r.FILES or None)
    if r.method == "POST":
        if a.is_valid():
            d = a.save(commit=False)
            d.user_id = r.user
            d.save()
            return redirect('owner_profile')
    data = {
        "form": a,
    }
    return render(r, 'registration/register_owner.html', data)

@login_required(login_url=logins)
def owner_profile(r):
    check = RoomOwner.objects.filter(user_id__username=r.user).count()
    if check == 0:
        return redirect('register_owner')

    allot = RoomAllot.objects.filter(user_id__username=r.user, ra_status='1').filter(ra_room_id__r_status='1')
    for x in allot:
        doj = x.ra_doc
        doj = datetime(doj.year, doj.month, 2)
        while diff_month(datetime.now().date(), doj) >= 0:
            cond = Q(pg_month__month=doj.month, pg_month__year=doj.year) & Q(pg_allot_id=x.ra_id) & Q(
                user_id__username=x.renter)
            if PaymentGenerate.objects.filter(cond).exists() == False:
                p = PaymentGenerate()
                p.pg_txn = create_txn_code(8)
                p.pg_month = doj
                p.pg_amount = x.ra_room_id.r_rent / x.ra_room_id.roomallot_set.filter(ra_status='1').count()
                p.pg_allot_id = RoomAllot(x.ra_id)
                p.user_id = x.renter
                p.owner = x.user_id
                p.save()
            else:
                try:
                    p = PaymentGenerate.objects.get(
                        Q(pg_month__month=datetime.now().date().month, pg_month__year=datetime.now().date().year) & Q(
                            pg_allot_id=x.ra_id) & Q(user_id__username=x.renter))
                    p.pg_amount = x.ra_room_id.r_rent / x.ra_room_id.roomallot_set.filter(ra_status='1').count()
                    p.save()
                except ObjectDoesNotExist:
                    pass
            doj = datetime(doj.year, doj.month, 2) + datedelta(months=1)

    room = RoomOwner.objects.get(user_id__username=r.user)
    if r.method == "POST":
        house = room
        house.ro_house_image = r.FILES['house_image']
        house.save()
        return redirect("owner_profile")
    data = {
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/ro_profile.html',data)

@login_required(login_url=logins)
def owner_update_image(r):
    room = RoomOwner.objects.get(user_id__username=r.user)
    if r.method == "POST":
        image = room
        image.ro_image = r.FILES['ro_image']
        image.save()
        return redirect("owner_profile")
    data = {
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_profile.html', data)

@login_required(login_url=logins)
def owner_update_id_proof(r):
    room = RoomOwner.objects.get(user_id__username=r.user)
    if r.method == "POST":
        image = room
        image.ro_id_proof = r.FILES['id_proof']
        image.save()
        return redirect("owner_profile")
    data = {
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_profile.html', data)

@login_required(login_url=logins)
def owner_update_profile(r):
    owner = RoomOwner.objects.get(user_id__username=r.user)
    profile = UpdateOwnerForm(r.POST or None, instance=owner)
    up = UpdateProfile(r.POST or None,instance=r.user)
    if r.method == "POST":
        if up.is_valid():
            user = up.save(commit=False)
            profile.save()
            user.save()
            return redirect('owner_profile')
    else:
        up = UpdateProfile(instance=r.user)
        profile = UpdateOwnerForm(instance=owner)
    data = {
        "form":up,
        "profile":profile,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/owner_update_profile.html',data)

@login_required(login_url=logins)
def password_change_owner(r):
    if r.method == 'POST':
        form = PasswordChangeForm(r.user, r.POST or None)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(r, user)  # Important!
            messages.success(r, 'Your password was successfully updated!')
            return redirect('password_change_owner')
        else:
            messages.error(r, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(r.user)
    data = {
        "form":form,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_password_change.html', data)

@login_required(login_url=logins)
def owner_rooms(r):
    data = {
        "rooms_a": Room.objects.filter(user_id__username=r.user,r_status='1'),
        "rooms_p": Room.objects.filter(user_id__username=r.user,r_status='2'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_rooms.html', data)


@login_required(login_url=logins)
def add_room(r):
    rm = AddRoomForm(r.POST or None, r.FILES or None)
    if r.method == "POST":
        if rm.is_valid():
            d = rm.save(commit=False)
            d.user_id = r.user
            d.slug = str(r.user) + '-' + r.POST.get('r_title')
            d.save()
            messages.success(r, 'Room add was successfully!')
            return redirect('add_room')
    data = {
        "form": rm,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/add_room.html', data)

@login_required(login_url=logins)
def owner_room_view(r,rm_id):
    if r.method == "POST":
        room = Room.objects.get(slug=rm_id)
        room.r_image = r.FILES['r_image']
        room.save()
        return redirect("../owner_room_view/" + str(room.slug))
    data = {
        "room_view": Room.objects.get(slug=rm_id),
        "room_renter": RoomAllot.objects.filter(ra_room_id__slug=rm_id,ra_status='1'),
        "room_renter_request": RoomAllot.objects.filter(ra_room_id__slug=rm_id,ra_status='0'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_room_view.html', data)

@login_required(login_url=logins)
def owner_room_edit(r,et_id):
    room = Room.objects.get(slug=et_id)
    re = EditRoomForm(r.POST or None,instance=room)
    if r.method == "POST":
        if re.is_valid():
            re.save()
            return redirect("../owner_room_view/"+str(room.slug))
    else:
        re = EditRoomForm(instance=room)

    data = {
        "form":re,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_room_edit.html', data)

@login_required(login_url=logins)
def room_active(r,a_id):
    room = Room.objects.get(slug=a_id)
    room.r_status = '1'
    room.save()
    return redirect('owner_rooms')

@login_required(login_url=logins)
def room_pending(r,p_id):
    room = Room.objects.get(slug=p_id)
    room.r_status = '2'
    room.save()
    return redirect('owner_rooms')

@login_required(login_url=logins)
def room_allot(r):
    if r.is_ajax():
        term = r.GET.get('term')
        renter = User.objects.filter(roomrenter__rr_contact__exact=term)
        response_content = list(renter.values())
        return JsonResponse(response_content, safe=False)

    if r.method == "POST":
        try:
            try:
                # check renter room active-----------
                check = RoomAllot.objects.get(Q(ra_room_id=r.POST.get('ra_room_id')) & Q(renter=r.POST.get('renter')),ra_status='1')
                if check is not None:
                    messages.error(r,"this renter is already in this room!")
                    return redirect('room_allot')
            except ObjectDoesNotExist:
                # check renter room pending-----------
                check = RoomAllot.objects.get(Q(ra_room_id=r.POST.get('ra_room_id')) & Q(renter=r.POST.get('renter')),ra_status='2')
                if check is not None:
                    messages.error(r, "this renter is pending in this room!")
                    return redirect('room_allot')
        except ObjectDoesNotExist:
            d = RoomAllot()
            d.user_id = r.user
            d.renter = User(r.POST.get('renter'))
            d.ra_room_id = Room(r.POST.get('ra_room_id'))
            rm = Room.objects.filter(r_id=r.POST.get('ra_room_id'))
            rt = RoomRenter.objects.filter(user_id=r.POST.get('renter'))
            d.slug = rm[0].r_title+'-'+rt[0].user_id.username
            d.save()
            messages.success(r, "room alloting successfully!")
            return redirect('room_allot')

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
def room_request_active(r,al_id):
    active = RoomAllot.objects.get(slug=al_id, ra_room_id__r_status='1')
    try:
        # check room active-----------
        if active is not None:
            messages.error(r, "this room is in pending condition! please active first")
            return redirect('room_allot_request')
        try:
            # check renter room active-----------
            check = RoomAllot.objects.get(Q(ra_room_id=active.ra_room_id) & Q(renter=active.renter),ra_status='1')
            if check is not None:
                messages.error(r, "this renter is already in this room!")
                return redirect('room_allot_request')
        except ObjectDoesNotExist:
            # check renter room pending-----------
            check = RoomAllot.objects.get(Q(ra_room_id=active.ra_room_id) & Q(renter=active.renter),ra_status='2')
            if check is not None:
                messages.error(r, "this renter is pending in this room!")
                return redirect('room_allot_request')
    except ObjectDoesNotExist:
        active.ra_status = '1'
        active.ra_doc = datetime.now()
        active.save()
        messages.success(r, "room alloting active successfully!")
        return redirect('my_renter')

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
    active = RoomAllot.objects.get(slug=a_id, ra_room_id__r_status='1')
    try:
        try:
            # check room active-----------
            if active is not None:
                messages.error(r, "this room is in pending condition! please active first")
                return redirect('room_allot_pending')
        except ObjectDoesNotExist:
            check = RoomAllot.objects.get(Q(ra_room_id=active.ra_room_id) & Q(renter=active.renter),ra_status='1')
            if check is not None:
                messages.error(r, "this renter is already pending in this room!")
                return redirect('room_allot_pending')
    except ObjectDoesNotExist:
        active.ra_status = '1'
        active.ra_doc = datetime.now()
        active.save()
        messages.success(r, "room alloting active successfully!")
        return redirect('my_renter')

@login_required(login_url=logins)
def allot_pending(r,p_id):
    pending = RoomAllot.objects.get(slug=p_id)
    pending.ra_status = '2'
    pending.ra_doc = datetime.now()
    pending.save()
    return redirect('room_allot_pending')

@login_required(login_url=logins)
def allot_delete(r,d_id):
    delete = RoomAllot.objects.get(slug=d_id)
    delete.delete()
    return redirect('room_allot_request')

@login_required(login_url=logins)
def view_renter_profile(r,rnt_id):
    pay = RoomAllot.objects.filter(slug=r.POST.get('slug'))
    if r.method == "POST":
        p = PaymentPaid()
        p.pp_amount = r.POST.get('amount')
        p.renter_id = pay[0].renter
        p.owner_id = r.user
        p.pp_allot_id = RoomAllot(pay[0].ra_id)
        p.pp_txn = create_txn_code(8)
        p.save()
        return redirect("../view_renter_profile/" + str(pay[0].renter.username))
    data = {
        "renter_profile":RoomRenter.objects.get(user_id__username=rnt_id),
        "user_r": User.objects.get(roomrenter__user_id__username=rnt_id),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
        "room_al": RoomAllot.objects.filter(renter__username=rnt_id).filter(user_id__username=r.user),
        "room": RoomAllot.objects.filter(Q(renter__username=rnt_id, ra_status='1') | Q(renter__username=rnt_id, ra_status='2')).filter(user_id__username=r.user),
    }
    return render(r,'roomowner/view_renter_profile.html',data)

@login_required(login_url=logins)
def owner_room_query(r):
    data = {
        "query": RoomQuery.objects.filter(user_id__username=r.user),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/ro_room_query.html',data)

@login_required(login_url=logins)
def query_delete(r,q_id):
    query = RoomQuery.objects.get(m_id=q_id)
    query.delete()
    return redirect('owner_room_query')

@login_required(login_url=logins)
def owner_payment(r):
    total_paid = PaymentPaid.objects.filter(owner_id=r.user)
    total_gen = PaymentGenerate.objects.filter(owner=r.user)
    data = {
        "renter": RoomAllot.objects.filter(Q(user_id__username=r.user, ra_status='1') | Q(user_id__username=r.user, ra_status='2')),
        "total_paid":total_paid.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00,
        "total_gen":total_gen.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/owner_payment.html',data)

@login_required(login_url=logins)
def owner_payment_paid(r):
    if r.method == 'POST':
        date = r.POST.get('month')
        m = datetime.strptime(date, '%Y-%m').date()
        c_month = m.month
        c_year = m.year
    else:
        c_month = datetime.now().date().month
        c_year = datetime.now().date().year
        c_date = datetime.now().date()
        date = c_date.strftime('%Y-%m')

    pay = PaymentPaid.objects.filter(pp_doc__month=c_month,pp_doc__year=c_year).filter(owner_id=r.user)
    gen = PaymentGenerate.objects.filter(pg_doc__month=c_month,pg_doc__year=c_year).filter(owner=r.user)
    data = {
        "paid": pay.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00,
        "gen": gen.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00,
        "payment": pay,
        "date": date,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/owner_payment_paid.html',data)

@login_required(login_url=logins)
def owner_payment_gen(r):
    if r.method == 'POST':
        date = r.POST.get('month')
        m = datetime.strptime(date, '%Y-%m').date()
        c_month = m.month
        c_year = m.year
    else:
        c_month = datetime.now().date().month
        c_year = datetime.now().date().year
        c_date = datetime.now().date()
        date = c_date.strftime('%Y-%m')

    pay = PaymentPaid.objects.filter(pp_doc__month=c_month,pp_doc__year=c_year).filter(owner_id=r.user)
    gen = PaymentGenerate.objects.filter(pg_doc__month=c_month,pg_doc__year=c_year).filter(owner=r.user)
    data = {
        "paid": pay.aggregate(Sum('pp_amount'))['pp_amount__sum'] or 00.00,
        "gen": gen.aggregate(Sum('pg_amount'))['pg_amount__sum'] or 00.00,
        "payment": gen,
        "date": date,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/owner_payment_gen.html', data)

@login_required(login_url=logins)
def owner_payment_due(r):
    data = {
    "renter": RoomAllot.objects.filter(Q(user_id__username=r.user, ra_status='1') | Q(user_id__username=r.user, ra_status='2')),
    "user": RoomOwner.objects.filter(user_id__username=r.user),
    "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/owner_payment_due.html',data)

@login_required(login_url=logins)
def owner_payment_advance(r):
    data = {
    "renter": RoomAllot.objects.filter(Q(user_id__username=r.user, ra_status='1') | Q(user_id__username=r.user, ra_status='2')),
    "user": RoomOwner.objects.filter(user_id__username=r.user),
    "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/owner_payment_advance.html',data)

#--------------------------------------------------------------------------





