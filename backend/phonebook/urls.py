from django.urls import path

from .views import (
    DepartmentDetailView,
    DepartmentListCreateView,
    PhoneTypeDetailView,
    PhoneTypeListCreateView,
    SearchView,
    SectionDetailView,
    SectionListCreateView,
    SectionPhoneDetailView,
    SectionPhoneListCreateView,
)

urlpatterns = [
    path("departments/", DepartmentListCreateView.as_view(), name="department-list"),
    path("departments/<uuid:pk>/", DepartmentDetailView.as_view(), name="department-detail"),
    path("sections/", SectionListCreateView.as_view(), name="section-list"),
    path("sections/<uuid:pk>/", SectionDetailView.as_view(), name="section-detail"),
    path("phone-types/", PhoneTypeListCreateView.as_view(), name="phonetype-list"),
    path("phone-types/<uuid:pk>/", PhoneTypeDetailView.as_view(), name="phonetype-detail"),
    path("section-phones/", SectionPhoneListCreateView.as_view(), name="sectionphone-list"),
    path("section-phones/<uuid:pk>/", SectionPhoneDetailView.as_view(), name="sectionphone-detail"),
    path("search/", SearchView.as_view(), name="phonebook-search"),
]
