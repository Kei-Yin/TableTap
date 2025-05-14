from django.contrib import admin
from .models import User, Menu, MenuItem, Table, Order, OrderItem, Review, Business, Category
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.sites.models import Site

admin.site.register(User)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Table)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Business)
admin.site.register(Category)