from django.contrib import admin
from django.urls import path,include
from datawork import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="homepage"),
    path('room_request/<int:rq_id>', views.room_request, name="room_request"),
    path('state_search',views.state_search,name="state_search"),
    path('city_search',views.city_search,name="city_search"),
    path('search_room',views.search_room,name="search_room"),
    path('house_view/<str:h_id>', views.house_view,name="house_view"),
    path('room_view/<str:r_id>', views.room_view,name="room_view"),
    path('logins/',views.logins,name="logins"),
    path('logouts/',views.logouts,name="logouts"),
    path('register_pending',views.register_pending,name="register_pending"),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'), # AJAX
    #room renter--------------------------------
    path('user_register_renter/',views.user_register_renter,name="user_register_renter"),
    path('register_renter/',views.register_renter,name="register_renter"),
    path('renter_profile/',views.renter_profile,name="renter_profile"),
    path('renter_rooms/',views.renter_rooms,name="renter_rooms"),
    path('renter_payment/',views.renter_payment,name="renter_payment"),
    path('request_delete/<int:r_id>', views.request_delete,name="request_delete"),
    path('password_change_renter/',views.password_change_renter,name="password_change_renter"),
    # room owner------------------------------
    path('user_register_owner/',views.user_register_owner,name="user_register_owner"),
    path('register_owner/',views.register_owner,name="register_owner"),
    path('owner_profile/',views.owner_profile,name="owner_profile"),
    path('owner_rooms/',views.owner_rooms,name="owner_rooms"),
    path('room_allot/',views.room_allot,name="room_allot"),
    path('owner_payment/',views.owner_payment,name="owner_payment"),
    path('password_change_owner/',views.password_change_owner,name="password_change_owner"),
    path('my_renter/',views.my_renter,name="my_renter"),
    path('room_allot_request/',views.room_allot_request,name="room_allot_request"),
    path('room_request_active/',views.room_request_active,name="room_request_active"),
    path('room_allot_pending/',views.room_allot_pending,name="room_allot_pending"),
    path('roomallot/active/<int:a_id>', views.allot_active,name="allot_active"),
    path('roomallot/pending/<int:p_id>', views.allot_pending,name="allot_pending"),
    path('roomallot/delete/<int:d_id>', views.allot_delete,name="allot_delete"),
    path('view_renter_profile/<str:rnt_id>', views.view_renter_profile,name="view_renter_profile"),
    path('owner_room_view/<str:rm_id>', views.owner_room_view,name="owner_room_view"),
    path('owner_room_edit/<int:et_id>', views.owner_room_edit,name="owner_room_edit"),
    path('owner_room_query',views.owner_room_query,name="owner_room_query"),
    path('query_delete/<int:q_id>',views.query_delete,name="query_delete"),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

