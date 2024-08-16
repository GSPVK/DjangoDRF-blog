"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from ckeditor_uploader.views import upload, browse
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import permission_required
from django.urls import path, include
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView

from . import settings

admin.site.site_header = 'Blog project'
admin.site.site_title = 'Blog'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('blog/', include('blog.urls')),
    path('blog/', include('rating.urls')),
    path('blog/', include('subscription.urls')),
    path('', RedirectView.as_view(url='blog/index/')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
]

#CKEditor
upload_view = permission_required('blog.add_post')(upload)
browse_view = never_cache(permission_required('blog.add_post')(browse))
urlpatterns += [
    path('ckeditor/upload/', upload_view, name='ckeditor_upload'),
    path('ckeditor/browse/', browse_view, name='ckeditor_browse'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls')), ]
