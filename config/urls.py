"""
URL configuration for config project.

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
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from infoMFSS import views
from users.urls import urlpatterns as users_patterns
from users.views import LoginView

# Mount account routes under /users/ and login under /login/ in one namespace.
users_namespace = (
    [
        *[path(f"users/{pattern.pattern}", pattern.callback, name=pattern.name) for pattern in users_patterns],
        path("login/", LoginView.as_view(), name="login"),
    ],
    "users",
)

urlpatterns = [
    path("", include(users_namespace, namespace="users")),
    path("admin/", admin.site.urls),
    path("sass_page", views.sass_page_handler),
    # path(r'^chaining/', include('smart_selects.urls')),
    path("chaining/", include("smart_selects.urls")),
    path("", include("infoMFSS.urls", namespace="mfss")),
    path("captcha/", include("captcha.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
