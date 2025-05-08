from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("menu/", views.menu, name="menu"),
    path("tables/", views.tables, name="tables"),
    path("orders/", views.orders, name="orders"),
    path("reviews/", views.reviews, name="reviews"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),

# 管理者端
    path("management/menu/", views.admin_menu, name="admin_menu"),
    path("management/menu/add/", views.add_menu_item, name="add_menu_item"),
    path("management/menu/<int:item_id>/edit/", views.edit_menu_item, name="edit_menu_item"),
    path("management/menu/<int:item_id>/delete/", views.delete_menu_item, name="delete_menu_item"),
    path("management/orders/", views.admin_orders, name="admin_orders"),
]