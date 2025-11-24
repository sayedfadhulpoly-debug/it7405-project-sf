from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<str:id>/', views.car_detail, name='car_detail'),
    path('cars/<str:id>/buy/', views.buy_car, name='buy_car'),
    path('cars/<str:id>/offer/', views.make_offer, name='make_offer'),

    # New pages:
    path('reviews/', views.reviews_page, name='reviews'),
    path('appointments/', views.appointment_page, name='appointments'),
    path('my-activity/', views.my_activity, name='my_activity'),

    path('my-activity/order/<str:order_id>/delete/', views.delete_order, name='delete_order'),
    path('my-activity/offer/<str:offer_id>/delete/', views.delete_offer, name='delete_offer'),
    path('my-activity/appointment/<str:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('my-activity/review/<str:review_id>/edit/', views.edit_review, name='edit_review'),
    path('my-activity/review/<str:review_id>/delete/', views.delete_review, name='delete_review'),
    path("account/", views.account_settings, name="account_settings"),


]
