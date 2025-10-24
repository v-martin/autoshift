'''
URL configuration for 123 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
'''
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


api_urlpatterns = [
    path('auth/', include('user.urls')),
    path('shifts/', include('shifts.urls')),
    path('warehouses/', include('warehouses.urls')),
    path('cargo/', include('cargo.urls')),
]

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='shifts_dashboard'), name='home'),
    path('', include('shifts.urls')),
    path('admin/', admin.site.urls),
    path('api/', include((api_urlpatterns, 'api'))),
]

if settings.DEBUG or settings.ENVIRONMENT == 'development':
    urlpatterns += [
        path('api-docs/schema/', SpectacularAPIView.as_view(), name='schema'),
        path(
            'api-docs/',
            SpectacularSwaggerView.as_view(url_name='schema'),
            name='swagger-ui',
        ),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
