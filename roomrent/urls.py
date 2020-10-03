from django.contrib import admin
from django.urls import path,include
from datawork import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="homepage"),
    path('register_pending',views.register_pending,name="register_pending"),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'), # AJAX
    path('user_register_renter/',views.user_register_renter,name="user_register_renter"),
    path('register_renter/',views.register_renter,name="register_renter"),
    path('renter_profile/',views.renter_profile,name="renter_profile"),
    path('user_register_owner/',views.user_register_owner,name="user_register_owner"),
    path('register_owner/',views.register_owner,name="register_owner"),
    path('owner_profile/',views.owner_profile,name="owner_profile"),
    path('owner_rooms/',views.owner_rooms,name="owner_rooms"),
    path('room_allot/',views.room_allot,name="room_allot"),
    path('my_renter/',views.my_renter,name="my_renter"),
    path('room_allot_request/',views.room_allot_request,name="room_allot_request"),
    path('room_allot_pending/',views.room_allot_pending,name="room_allot_pending"),
    path('logins/',views.logins,name="logins"),
    path('logouts/',views.logouts,name="logouts"),
    path('roomallot/active/<int:a_id>', views.allot_active,name="allot_active"),
    path('roomallot/pending/<int:p_id>', views.allot_pending,name="allot_pending"),
    path('roomallot/delete/<int:d_id>', views.allot_delete,name="allot_delete"),
    path('view_renter_profile/<str:rnt_id>', views.view_renter_profile,name="view_renter_profile"),
    path('room_view/<str:rm_id>', views.room_view,name="room_view"),
    path('room_edit/<int:et_id>', views.room_edit,name="room_edit"),

] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

