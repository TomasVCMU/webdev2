# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include  # add this
from apps.home import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),      # Django admin route
    path("accounts/", include('allauth.urls')),
    path("", include("apps.authentication.urls")), # Auth routes - login / register
    path("", include("apps.home.urls")),           # UI Kits Html files
    path('budget/', views.pages, name='budget'),
    path('transactions/', views.pages, name='transactions'),
    path('monthly_expense_breakdown/', views.monthly_expense_breakdown, name='monthly_expense_breakdown'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)