from django.urls import path

from dashboard.customer import views

urlpatterns = [
    path(
        "address-list/",
        views.addresses.CustomerAddressListView.as_view(),
        name="address_list",
    ),
    # path("address-create/" , views.addresses.CustomerAddressCreateView.as_view() , name = "create_address"),
    # path("address-edit/<int:pk>/" , views.addresses.CustomerAddressEditView.as_view() , name = "edit_address"),
    # path("address-delete/<int:pk>/" , views.addresses.CustomerAddressDeleteView.as_view() , name = "delete_address"),
]
