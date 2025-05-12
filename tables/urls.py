from django.urls import path
from . import views

urlpatterns = [
    # === 公共页面 ===
    path("", views.index, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/<int:user_id>/", views.dashboard_redirect, name="dashboard_redirect"),

    # === 顾客使用页面（扫码访问 menu 不带 user_id） ===
    path("menu/<int:table_id>/", views.menu, name="menu"),
    path("orders/create/", views.create_order, name="create_order"),

    # === 顾客个人页面 ===
    path("customer/<int:user_id>/home/", views.customer_home, name="customer_home"),
    path("customer/<int:user_id>/orders/", views.orders, name="orders"),
    path("customer/<int:user_id>/order/<int:order_id>/", views.order_detail, name="order_detail"),
    path("customer/<int:user_id>/reviews/", views.reviews, name="reviews"),
    path("customer/<int:user_id>/user/", views.user_center, name="user_center"),
    path("customer/<int:user_id>/order/<int:order_id>/review/", views.add_review, name="add_review"),

    # === 后台管理：控制台 / 订单 / 密码 ===
    path("management/<int:user_id>/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("management/<int:user_id>/orders/", views.admin_orders, name="admin_orders"),
    path("management/<int:user_id>/orders/<int:order_id>/status/", views.update_order_status, name="update_order_status"),
    path("management/<int:user_id>/change_password/", views.admin_change_password, name="admin_change_password"),

    # === 后台：菜单管理 ===
    path("management/<int:user_id>/menu/", views.admin_menu, name="admin_menu"),
    path("management/<int:user_id>/menu/add/", views.add_menu_item, name="add_menu_item"),
    path("management/<int:user_id>/menu/<int:item_id>/edit/", views.edit_menu_item, name="edit_menu_item"),
    path("management/<int:user_id>/menu/<int:item_id>/delete/", views.delete_menu_item, name="delete_menu_item"),

    # === 后台：桌号管理 ===
    path("management/<int:user_id>/tables/", views.table_list, name="table_list"),
    path("management/<int:user_id>/tables/add/", views.add_table, name="add_table"),
    path("management/<int:user_id>/tables/<int:table_id>/delete/", views.delete_table, name="delete_table"),

    # === 后台：菜品分类管理 ===
    path("management/<int:user_id>/categories/", views.admin_categories, name="admin_categories"),
    path("management/<int:user_id>/categories/add/", views.add_category, name="add_category"),
    path("management/<int:user_id>/categories/<int:category_id>/edit/", views.edit_category, name="edit_category"),

    # === 后台：商家管理 ===
    path("management/<int:user_id>/businesses/", views.business_list, name="business_list"),
    path("management/<int:user_id>/businesses/add/", views.add_business, name="add_business"),
    path("management/<int:user_id>/businesses/<int:business_id>/edit/", views.edit_business, name="edit_business"),
    path("management/<int:user_id>/businesses/<int:business_id>/use/", views.use_business, name="use_business"),
]
