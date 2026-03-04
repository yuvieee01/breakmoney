from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Allauth
    path("accounts/", include("allauth.urls")),

    # Your app urls (keep these)
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    path("friends/", include(("friends.urls", "friends"), namespace="friends")),
    path("groups/", include(("groups.urls", "groups"), namespace="groups")),
    path("expenses/", include(("expenses.urls", "expenses"), namespace="expenses")),
    path("settlements/", include(("settlements.urls", "settlements"), namespace="settlements")),
    path("activity/", include(("audit.urls", "audit"), namespace="audit")),
    path("", include(("ledger.urls", "ledger"), namespace="ledger")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)