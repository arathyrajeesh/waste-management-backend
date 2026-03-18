from django.urls import path
from .views import register, login, forgot_password, reset_password, all_users, admin_dashboard, my_profile, create_hks_worker, admin_dashboard_live_map, admin_dashboard_ward_monitoring, admin_dashboard_complaints, admin_dashboard_fees, admin_dashboard_waste_reports, create_admin_workaround
from .views import admin_dashboard


urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('users/', all_users),
    path('dashboard/', admin_dashboard),
    path('dashboard/live-map/', admin_dashboard_live_map),
    path('dashboard/ward-monitoring/', admin_dashboard_ward_monitoring),
    path('dashboard/complaints/', admin_dashboard_complaints),
    path('dashboard/fees/', admin_dashboard_fees),
    path('dashboard/waste-reports/', admin_dashboard_waste_reports),
    path('forgot-password/', forgot_password),
    path('reset-password/<int:uid>/<str:token>/', reset_password),
    path('profile/', my_profile),
    path('create-hks-worker/', create_hks_worker),
    path('temporary-create-admin-workaround/', create_admin_workaround),
]
