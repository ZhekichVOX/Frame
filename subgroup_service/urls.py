"""Маршрутизация верхнего уровня: адреса распределяются по приложениям."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("groups/", include("groups.urls")),
    path("students/", include("students.urls")),
    path("subgroups/", include("subgroups.urls")),
]

# Читается только отсюда и действует для всех приложений сразу.
handler404 = "homepage.views.page_not_found"
