from django.urls import path,include
from . import views
from events.views import login_view, signup_view, forgotpassword_view, dashboard_view, markets_view
# Event_App/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


app_name = 'events'

# Public URLs for attendees
urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/register/', views.register_attendee, name='register_attendee'),
    path('confirmation/<str:confirmation_code>/', views.registration_confirmation, name='registration_confirmation'),
    path('check-registration/', views.check_registration_status, name='check_registration'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('<int:event_id>/status/', views.check_registration_api, name='check_registration_status'),


# Management URLs for event staff

    path('', views.manage_attendees, name='attendee_list'),
    path('events/<int:event_id>/attendees/', views.manage_attendees, name='manage_attendees'),
    path('events/<int:event_id>/check-in/', views.check_in_attendee, name='check_in_attendee'),
    path('attendees/<int:attendee_id>/update-status/', views.update_attendance_status, name='update_attendance_status'),
    path('events/<int:event_id>/report/', views.attendance_report, name='attendance_report'),

# Login Urls

path('', login_view, name='login'),
    path('signup', signup_view, name='signup'),
    path('forgotpassword', forgotpassword_view, name='forgotpassword'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('markets', markets_view, name='markets'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])


