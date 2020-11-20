from django.contrib import admin
from django.urls import path,include
from datawork import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="homepage"),
    path('room_request/<int:rq_id>', views.room_request, name="room_request"),
    path('state_search',views.state_search,name="state_search"),
    path('city_search',views.city_search,name="city_search"),
    path('search_room',views.search_room,name="search_room"),
    path('house_view/<str:h_id>', views.house_view,name="house_view"),
    path('room_view/<slug:r_id>', views.room_view,name="room_view"),
    path('logins/',views.logins,name="logins"),
    path('logouts/',views.logouts,name="logouts"),
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'), # AJAX
    #password reset----------------------------
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    #room renter--------------------------------
    path('user_register_renter/',views.user_register_renter,name="user_register_renter"),
    path('register_renter/',views.register_renter,name="register_renter"),
    path('renter_profile/',views.renter_profile,name="renter_profile"),
    path('renter_update_profile/',views.renter_update_profile,name="renter_update_profile"),
    path('renter_update_image/', views.renter_update_image, name="renter_update_image"),
    path('renter_update_id_proof/', views.renter_update_id_proof, name="renter_update_id_proof"),
    path('renter_rooms/',views.renter_rooms,name="renter_rooms"),
    path('renter_payment/',views.renter_payment,name="renter_payment"),
    path('request_delete/<int:r_id>', views.request_delete,name="request_delete"),
    path('password_change_renter/',views.password_change_renter,name="password_change_renter"),
    # room owner------------------------------
    path('user_register_owner/',views.user_register_owner,name="user_register_owner"),
    path('register_owner/',views.register_owner,name="register_owner"),
    path('owner_profile/',views.owner_profile,name="owner_profile"),
    path('owner_update_profile/',views.owner_update_profile,name="owner_update_profile"),
    path('owner_update_image/',views.owner_update_image,name="owner_update_image"),
    path('owner_update_id_proof/',views.owner_update_id_proof,name="owner_update_id_proof"),
    path('owner_rooms/',views.owner_rooms,name="owner_rooms"),
    path('add_room/',views.add_room,name="add_room"),
    path('room_active/<int:a_id>',views.room_active,name="room_active"),
    path('room_pending/<int:p_id>',views.room_pending,name="room_pending"),
    path('room_allot/',views.room_allot,name="room_allot"),
    path('owner_payment/',views.owner_payment,name="owner_payment"),
    path('owner_payment_paid/',views.owner_payment_paid,name="owner_payment_paid"),
    path('owner_payment_gen/',views.owner_payment_gen,name="owner_payment_gen"),
    path('owner_payment_due/',views.owner_payment_due,name="owner_payment_due"),
    path('owner_payment_advance/',views.owner_payment_advance,name="owner_payment_advance"),
    path('password_change_owner/',views.password_change_owner,name="password_change_owner"),
    path('my_renter/',views.my_renter,name="my_renter"),
    path('room_allot_request/',views.room_allot_request,name="room_allot_request"),
    path('room_request_active/',views.room_request_active,name="room_request_active"),
    path('room_allot_pending/',views.room_allot_pending,name="room_allot_pending"),
    path('roomallot/active/<int:a_id>', views.allot_active,name="allot_active"),
    path('roomallot/pending/<int:p_id>', views.allot_pending,name="allot_pending"),
    path('roomallot/delete/<int:d_id>', views.allot_delete,name="allot_delete"),
    path('view_renter_profile/<str:rnt_id>', views.view_renter_profile,name="view_renter_profile"),
    path('owner_room_view/<slug:rm_id>', views.owner_room_view,name="owner_room_view"),
    path('owner_room_edit/<slug:et_id>', views.owner_room_edit,name="owner_room_edit"),
    path('owner_room_query',views.owner_room_query,name="owner_room_query"),
    path('query_delete/<int:q_id>',views.query_delete,name="query_delete"),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

