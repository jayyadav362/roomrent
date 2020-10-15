from django.shortcuts import *
from .forms import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from datedelta import datedelta
from datetime import timedelta,datetime
from datawork.templatetags import template_tags
import string
import random
from django.db.models import Sum
# Create your views here.

def create_txn_code(digit):
    return "".join(random.choices(string.digits,k=digit))

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def home(r):
    renter = RoomRenter.objects.all()
    for rt in renter:
        allot = RoomAllot.objects.filter(renter=rt.user_id, ra_status='1')
        for x in range(allot.count()):
            doj = allot[x].ra_doc
            while diff_month(datetime.now().date(), doj) != 0:
                cond = Q(pg_month=doj) & Q(pg_allot_id=allot[x].ra_id) & Q(user_id__username=allot[x].renter)
                if PaymentGenerate.objects.filter(cond).exists() == True:
                    p = PaymentGenerate.objects.get(Q(pg_month=datetime.now().month) & Q(pg_allot_id=allot[x].ra_id) & Q(user_id__username=allot[x].renter))
                    p.pg_amount = allot[x].ra_room_id.r_rent / allot[x].ra_room_id.roomallot_set.filter(ra_status='1').count()
                    p.save()
                elif PaymentGenerate.objects.filter(cond).exists() == False:
                    p = PaymentGenerate()
                    p.pg_txn = create_txn_code(8)
                    p.pg_month = doj
                    p.pg_amount = allot[x].ra_room_id.r_rent / allot[x].ra_room_id.roomallot_set.filter(ra_status='1').count()
                    p.pg_allot_id = RoomAllot(allot[x].ra_id)
                    p.user_id = allot[x].renter
                    p.save()
                doj = doj + datedelta(months=1)
    return render(r, 'home.html')

def state_search(r):
    if 'term' in r.GET:
        qs = State.objects.filter(name__icontains=r.GET.get('term'))[:5]
        titles = list()
        for state in qs:
            titles.append(state.name)
        return JsonResponse(titles, safe=False)

def city_search(r):
    if 'term' in r.GET:
        qs = City.objects.filter(name__icontains=r.GET.get('term'))[:5]
        titles = list()
        for city in qs:
            titles.append(city.name)
        return JsonResponse(titles, safe=False)
    
def search_room(r):
    if r.method == 'GET':
        data = {
            "house":RoomOwner.objects.filter(Q(state__name=r.GET.get('state')) & Q(city__name=r.GET.get('city')))
        }
    else:
        data = {"house":RoomOwner.objects.all()}
        
    return render(r,'search.html',data)

def house_view(r,h_id):
    owner = RoomOwner.objects.get(ro_id=h_id)
    room_query = RoomQueryForm(r.POST or None)
    if r.method == 'POST':
        if room_query.is_valid:
            s = room_query.save(commit=False)
            s.user_id = User(owner.user_id_id)
            s.save()
            messages.success(r, "Room Query send successfully!")
            return redirect("../house_view/" + str(owner.ro_id))
    data = {
        "form":room_query,
        "house":owner,
        "room":Room.objects.filter(user_id__username=owner.user_id.username)
    }
    return render(r,'house_view.html',data)

def room_view(r,r_id):
    room = Room.objects.get(r_id=r_id)
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
            status = 0
            try:
                username = User.objects.get(email=email.lower()).username
                try:
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
                    if user is not None:
                        login(r, user)
                    else:
                        messages.error(r,"Your password is incorrect!")
                        return redirect('logins')


                    if status == 1:
                        return redirect('renter_profile')
                    elif status == 2:
                        return redirect('owner_profile')

                except ObjectDoesNotExist:
                    user = authenticate(username=username, password=password)
                    r.session['name'] = 'pending'
                    if user is not None:
                        login(r, user)
                        return render(r, 'pending.html')
                    else:
                        messages.error(r, "Your password is incorrect!")
                        return redirect('logins')

            except User.DoesNotExist:
                messages.error(r,"The email address or password is incorrect. Please retry...")
                return redirect('logins')

    data = {"form": form}
    return render(r, 'logins.html', data)

@login_required(login_url=logins)
def room_request(r,rq_id):
    request = RoomAllot()
    user = User.objects.get(username=r.user)
    request.renter = user
    room = Room.objects.get(r_id=rq_id)
    request.ra_room_id = Room(room.r_id)
    request.user_id = User(room.user_id_id)
    request.ra_status = '0'
    request.save()
    messages.success(r, "room request successfully!")
    return redirect('renter_profile')

def logouts(r):
    logout(r)
    return redirect('logins')

@login_required(login_url=logins)
def register_pending(r):
    return render(r,'pending.html')

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
            u.save()
            r.session['name'] = 'renter'
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
        "room_request": RoomAllot.objects.filter(renter__username=r.user, ra_status='0'),
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomrenter/rr_profile.html',data)

@login_required(login_url=logins)
def request_delete(r,r_id):
    delete = RoomAllot.objects.get(ra_id=r_id)
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
    room = RoomAllot.objects.filter(renter__username=r.user, ra_status='1')
    data = {
        "user": RoomRenter.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
        "room": room,
    }
    return render(r,'roomrenter/rr_payment.html',data)

# room owner -------------------------------------------------
def user_register_owner(r):
    u = RegisterForm(r.POST or None)
    if r.method == "POST":
        if u.is_valid():
            u.save()
            r.session['name'] = 'owner'
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
        try:
            # check renter room-----------
            check = RoomAllot.objects.get(Q(ra_room_id=r.POST.get('ra_room_id')) & Q(renter=r.POST.get('renter')),ra_status='1')
            if check is not None:
                messages.error(r,"this renter is already in this room!")
                return redirect('room_allot')
        except ObjectDoesNotExist:
            d = RoomAllot()
            user = User.objects.get(username=r.user)
            d.user_id = user
            d.renter = User(r.POST.get('renter'))
            d.ra_room_id = Room(r.POST.get('ra_room_id'))
            d.slug = r.POST.get('ra_room_id')
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
def room_allot_pending(r):
    data = {
        "roomallot_pending": RoomAllot.objects.filter(user_id__username=r.user,ra_status='2'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_roomallot_pending.html', data)

@login_required(login_url=logins)
def allot_active(r,a_id):
    active = RoomAllot.objects.get(ra_id=a_id, ra_room_id__r_status='1')
    try:
        check = RoomAllot.objects.get(Q(ra_room_id=active.ra_room_id) & Q(renter=active.renter),ra_status=1)
        if check is not None:
            messages.error(r, "this renter is already allot in this room!")
            return redirect('my_renter')
    except ObjectDoesNotExist:
        active.ra_status = '1'
        active.ra_doc = datetime.now()
        active.save()
        messages.success(r, "room alloting active successfully!")
        return redirect('my_renter')

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
def owner_room_view(r,rm_id):
    data = {
        "room_view": Room.objects.get(r_id=rm_id),
        "room_renter": RoomAllot.objects.filter(ra_room_id=rm_id,ra_status='1'),
        "room_renter_request": RoomAllot.objects.filter(ra_room_id=rm_id,ra_status='0'),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_room_view.html', data)

@login_required(login_url=logins)
def owner_room_edit(r,et_id):
    room = Room.objects.get(r_id=et_id)
    re = EditRoomForm(r.POST or None,instance=room)
    if r.method == "POST":
        if re.is_valid():
            re.save()
            return redirect("../ro_room_view/"+str(room.r_id))
    else:
        re = EditRoomForm(instance=room)

    data = {
        "form":re,
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r, 'roomowner/ro_room_edit.html', data)

def owner_room_query(r):
    data = {
        "query": RoomQuery.objects.filter(user_id__username=r.user),
        "user": RoomOwner.objects.filter(user_id__username=r.user),
        "userdata": User.objects.filter(username=r.user),
    }
    return render(r,'roomowner/ro_room_query.html',data)

def query_delete(r,q_id):
    query = RoomQuery.objects.get(m_id=q_id)
    query.delete()
    return redirect('owner_room_query')

#--------------------------------------------------------------------------




