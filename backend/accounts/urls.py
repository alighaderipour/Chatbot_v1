from django.urls import path

from .views import (
    AppSettingsView,
    MeView,
    UserBulkImportView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    path("users/", UserListCreateView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/import/", UserBulkImportView.as_view(), name="user-import"),
    path("me/", MeView.as_view(), name="me"),
    path("settings/", AppSettingsView.as_view(), name="app-settings"),
]
