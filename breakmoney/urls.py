from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("friends/", include("friends.urls", namespace="friends")),
    path("groups/", include("groups.urls", namespace="groups")),
    path("expenses/", include("expenses.urls", namespace="expenses")),
    path("settlements/", include("settlements.urls", namespace="settlements")),
    path("activity/", include("audit.urls", namespace="audit")),
    path("", include("ledger.urls", namespace="ledger")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)