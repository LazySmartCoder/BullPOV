"""
URL configuration for BullPOVPortal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from BullPOVPortal import settings
from django.conf.urls import handler400, handler403, handler404, handler500

urlpatterns = [
    path('BullPOV-Admin-AB-HG', admin.site.urls),
    path('', include("BullPOVApp.urls")),
    path('admin-panel', include("BullPOVAdmin.urls")),
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root' : settings.MEDIA_ROOT}),
]

handler404 = "BullPOVApp.views.ErrorPage"
handler500 = "BullPOVApp.views.ErrorOccured"
handler403 = "BullPOVApp.views.ErrorPage"
handler400 = "BullPOVApp.views.ErrorPage"
admin.site.site_title = "BullPOV"
admin.site.site_header = "BullPOV"
admin.site.index_title = "Welcome to the Control Center..."