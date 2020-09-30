from django.contrib import admin
from django.urls import path,include
from datawork import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="homepage"),
    path('user_register_renter/',views.user_register_renter,name="user_register_renter"),
    path('register_renter/',views.register_renter,name="register_renter"),
    path('renter_profile/',views.renter_profile,name="renter_profile"),
    path('user_register_owner/',views.user_register_owner,name="user_register_owner"),
    path('register_owner/',views.register_owner,name="register_owner"),
    path('owner_profile/',views.owner_profile,name="owner_profile"),
    path('owner_rooms/',views.owner_rooms,name="owner_rooms"),
    path('room_allot/',views.room_allot,name="room_allot"),
    path('logins/',views.logins,name="logins"),
    path('logouts/',views.logouts,name="logouts"),
    path('roomallot/active/<int:a_id>', views.allot_active,name="allot_active"),
    path('roomallot/pending/<int:p_id>', views.allot_pending,name="allot_pending"),
    path('roomallot/delete/<int:d_id>', views.allot_delete,name="allot_delete"),
    path('view_renter_profile/<str:rnt_id>', views.view_renter_profile,name="view_renter_profile"),
    path('room_view/<str:rm_id>', views.room_view,name="room_view"),

] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

