from django.urls import path

from . import views

app_name = "subgroups"

urlpatterns = [
    path("", views.subgroups, name="list"),
    path("<int:subgroup_id>/", views.subgroup_detail, name="detail"),
]
