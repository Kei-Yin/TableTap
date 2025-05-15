from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.sessions.models import Session
from .models import User, Menu, MenuItem, Table, Order, OrderItem, Review, Business, Category, StaffAssignment
from .forms import TableForm, BusinessForm, CategoryForm, MenuItemForm, AddStaffForm, ReviewForm
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, HttpResponse
from django.db import models
import qrcode
from io import BytesIO


# ======================= 公共视图 =======================

def index(request):
    return render(request, "index.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        role = request.POST["role"]

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        user = User.objects.create(username=username, email=email, password=password, role=role)
        request.session["username"] = username
        request.session["user_id"] = user.id
        request.session["role"] = role
        return redirect("dashboard_redirect", user_id=user.id)
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = User.objects.filter(email=email, password=password).first()

        if user:
            if not request.session.session_key:
                request.session.create()

            current_session_key = request.session.session_key

            if user.session_key and user.session_key != current_session_key:
                try:
                    old_session = Session.objects.get(session_key=user.session_key)
                    old_session.delete()
                except Session.DoesNotExist:
                    pass

            request.session["user_id"] = user.id
            request.session["username"] = user.username
            request.session["role"] = user.role

            user.session_key = current_session_key
            user.save()

            return redirect("dashboard_redirect", user_id=user.id)

        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")

def logout_view(request):
    request.session.flush()
    return redirect("home")

def dashboard_redirect(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    role = request.session.get("role")
    if role == "owner" or role == "staff":
        return redirect("admin_dashboard", user_id=user_id)
    elif role == "customer":
        return redirect("customer_home", user_id=user_id)
    else:
        return redirect("login")

@login_required
def role_redirect(request):
    user = request.user
    if not hasattr(user, "role") or not user.role:
        return redirect('select_role')

    if user.role == "customer":
        return redirect("customer_home", user_id=user.id)
    elif user.role == "owner":
        return redirect("admin_dashboard", user_id=user.id)
    else:
        return redirect("login")

@login_required
def select_role(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role in ['customer', 'owner', 'staff']:
            request.user.role = role
            request.user.save()
            request.session['role'] = role  # ✅ 保持兼容你原有 session 管理
            return redirect('role_redirect')
    return render(request, "select_role.html")


# ======================= 顾客端视图 =======================

def menu(request, table_id):
    table = get_object_or_404(Table, pk=table_id)
    menu = Menu.objects.filter(business=table.business).first()
    if not menu:
        return render(request, "menu.html", {"error": "No menu"})

    categories = Category.objects.filter(business=table.business).order_by("created_at")

    grouped_items = [
        {
            "category": category,
            "items": menu.items.filter(category=category, available=True)
        }
        for category in categories
    ]

    return render(request, "menu.html", {
        "grouped_items": grouped_items,
        "categories": categories,
        "table": table,
        "active_page": "home",
        "user_id": request.session.get("user_id")
    })



def customer_home(request, user_id):
    if request.session.get("user_id") != user_id or request.session.get("role") != "customer":
        return redirect("login")
    return render(request, "customer_home.html", {"active_page": "home", "user_id": user_id})

def user_center(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.session.get("user_id") != user_id:
        return redirect("login")

    return render(request, "user_center.html", {
        "user": user,
        "active_page": "user",
        "user_id": user_id,
    })


def orders(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    order_list = Order.objects.filter(user_id=user_id).select_related("business", "table").order_by("-ordered_at")
    paginator = Paginator(order_list, 5)
    page = request.GET.get("page")
    orders = paginator.get_page(page)

    # 改为：查询用户已经评论过的订单 ID
    reviewed_order_ids = set(
        Review.objects.filter(customer_id=user_id).values_list("order_id", flat=True)
    )

    return render(request, "user_orders.html", {
        "orders": orders,
        "user_id": user_id,
        "reviewed_order_ids": reviewed_order_ids,
        "active_page": "orders"
    })



def order_detail(request, user_id, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "order_detail.html", {
        "order": order,
        "user_id": user_id
    })


def reviews(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    review_list = Review.objects.filter(customer_id=user_id).select_related("business").order_by("-created_at")
    paginator = Paginator(review_list, 5)
    page = request.GET.get("page")
    reviews = paginator.get_page(page)

    return render(request, "user_reviews.html", {
        "reviews": reviews,
        "user_id": user_id,
        "active_page": "reviews"
    })

@csrf_exempt
def add_review(request, user_id, order_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    order = get_object_or_404(Order, id=order_id, user_id=user_id, status="completed")

    if Review.objects.filter(customer_id=user_id, order=order).exists():
        messages.info(request, "You have already reviewed this order.")
        return redirect("reviews", user_id=user_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer_id = user_id
            review.business = order.business
            review.order = order
            review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect("reviews", user_id=user_id)
    else:
        form = ReviewForm()

    return render(request, "add_review.html", {
        "form": form,
        "order": order,
        "user_id": user_id
    })

def all_reviews(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    businesses = Business.objects.all().annotate(review_count=models.Count("reviews"))
    return render(request, "all_reviews.html", {
        "user_id": user_id,
        "businesses": businesses,
        "active_page": "reviews"
    })

def business_reviews(request, user_id, business_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_object_or_404(Business, pk=business_id)
    reviews = Review.objects.filter(business=business).select_related("customer").order_by("-created_at")
    return render(request, "business_reviews.html", {
        "business": business,
        "reviews": reviews,
        "user_id": user_id
    })


@require_POST
def like_review(request, review_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Login required"}, status=403)

    review = get_object_or_404(Review, pk=review_id)
    _, created = ReviewLike.objects.get_or_create(review=review, user_id=user_id)
    return JsonResponse({"success": created, "likes": review.likes.count()})

@require_POST
def reply_review(request, review_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({"error": "Login required"}, status=403)

    reply_text = request.POST.get("reply")
    if reply_text:
        ReviewReply.objects.create(
            review_id=review_id,
            user_id=user_id,
            reply=reply_text
        )
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Empty reply"}, status=400)

@require_POST
def delete_review(request, user_id, review_id):
    review = get_object_or_404(Review, id=review_id, customer_id=user_id)
    review.delete()
    messages.success(request, "Review deleted.")
    return redirect("reviews", user_id=user_id)


# ======================= 工具函数 =======================

def get_current_business(request):
    business_id = request.session.get("business_id")
    if business_id:
        return Business.objects.filter(id=business_id).first()

    role = request.session.get("role")
    user_id = request.session.get("user_id")

    if role == "owner":
        return Business.objects.filter(owner_id=user_id).first()
    elif role == "staff":
        assignment = StaffAssignment.objects.filter(user_id=user_id).first()
        if assignment:
            return assignment.business
    return None


def generate_qr_code_image(table_id):
    domain = "https://infs3202-4582d0a5.uqcloud.net"  # 或从 settings 或 request 里动态获取
    url = f"{domain}/tabletap/menu/{table_id}/"
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    filename = f"table_{table_id}.png"
    return filename, ContentFile(buffer.getvalue())


# ======================= 管理端视图 =======================

def admin_dashboard(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    return render(request, "admin_dashboard.html", {"user_id": user_id})

def admin_orders(request, user_id):
    business = get_current_business(request)
    all_orders = Order.objects.filter(business=business).order_by("-id").prefetch_related("items__menu_item")
    paginator = Paginator(all_orders, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin_orders.html", {
        "orders": all_orders,  # 可选
        "page_obj": page_obj,
        "user_id": user_id,
        "active_page": "orders",
    })

def admin_menu(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    menu = Menu.objects.filter(business=business).first()
    items = menu.items.all() if menu else []
    categories = Category.objects.filter(business=business).order_by("name")
    return render(request, "admin_menu.html", {
        "menu_items": items,
        "categories": categories,
        "active_page": "menu",
        "user_id": user_id
    })

def add_menu_item(request, user_id):
    # 登录用户身份验证
    if request.session.get("user_id") != user_id:
        return redirect("login")

    business = get_current_business(request)
    if not business:
        messages.error(request, "未找到当前商家，请先选择或创建商家")
        return redirect("business_list", user_id=user_id)

    # 自动创建 menu（避免 None）
    menu, _ = Menu.objects.get_or_create(business=business)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.menu = menu  # 关联 menu -> business -> owner
            item.save()
            return redirect("admin_menu", user_id=user_id)
    else:
        form = MenuItemForm()

    return render(request, "add_menu_item.html", {
        "form": form,
        "user_id": user_id
    })


def edit_menu_item(request, user_id, item_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    business = get_current_business(request)
    item = get_object_or_404(MenuItem, pk=item_id, menu__business=business)

    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect("admin_menu", user_id=user_id)
    else:
        form = MenuItemForm(instance=item)

    return render(request, "edit_menu_item.html", {
        "form": form,
        "item": item,
        "user_id": user_id
    })


def delete_menu_item(request, user_id, item_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    business = get_current_business(request)
    if request.method == "POST":
        item = get_object_or_404(MenuItem, pk=item_id, menu__business=business)
        item.delete()
    return redirect("admin_menu", user_id=user_id)


def table_list(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    tables = Table.objects.filter(business=business).order_by("-created_at")
    form = TableForm()
    return render(request, "admin_table_list.html", {"tables": tables, "form": form, "user_id": user_id, "active_page": "tables",})

def add_table(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    if request.method == "POST":
        form = TableForm(request.POST)
        if form.is_valid():
            table = Table.objects.create(business=business, table_number=form.cleaned_data["table_number"])
            filename, qr_content = generate_qr_code_image(table.id)
            table.qr_code.save(filename, qr_content)
            table.save()
    return redirect("table_list", user_id=user_id)

def delete_table(request, user_id, table_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    if request.method == "POST":
        table = get_object_or_404(Table, pk=table_id, business=business)
        table.delete()
    return redirect("table_list", user_id=user_id)

def admin_categories(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    categories = Category.objects.filter(business=business).order_by("-created_at")
    return render(request, "admin_categories.html", {
        "categories": categories,
        "active_page": "categories",
        "user_id": user_id
    })

def add_category(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.business = business
            category.save()
            return redirect("admin_categories", user_id=user_id)
    else:
        form = CategoryForm()
    return render(request, "admin_add_category.html", {"form": form, "user_id": user_id})

def edit_category(request, user_id, category_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    business = get_current_business(request)
    category = get_object_or_404(Category, pk=category_id, business=business)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("admin_categories", user_id=user_id)
    else:
        form = CategoryForm(instance=category)
    return render(request, "admin_edit_category.html", {"form": form, "category": category, "user_id": user_id})

def admin_change_password(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")
    return render(request, "admin_change_password.html", {"user_id": user_id})

def business_list(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    role = request.session.get("role")

    if role == "owner":
        businesses = Business.objects.filter(owner_id=user_id)
    elif role == "staff":
        businesses = Business.objects.filter(staff__user_id=user_id).distinct()
    else:
        return HttpResponseForbidden("You do not have permission.")

    return render(request, "admin_business_list.html", {
        "businesses": businesses,
        "user_id": user_id,
        "active_page": "business"
    })

def add_business(request, user_id):
    if request.session.get("user_id") != user_id or request.session.get("role") != "owner":
        return HttpResponseForbidden("You do not have permission.")
    if request.method == "POST":
        form = BusinessForm(request.POST)
        if form.is_valid():
            new_business = form.save(commit=False)
            new_business.owner_id = user_id
            new_business.total_tables = 0
            new_business.save()
            return redirect("business_list", user_id=user_id)
    else:
        form = BusinessForm()
    return render(request, "admin_add_business.html", {"form": form, "user_id": user_id})

def edit_business(request, user_id, business_id):
    if request.session.get("user_id") != user_id or request.session.get("role") != "owner":
        return HttpResponseForbidden("You do not have permission.")
    business = get_object_or_404(Business, pk=business_id, owner_id=user_id)
    if request.method == "POST":
        form = BusinessForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            return redirect("business_list", user_id=user_id)
    else:
        form = BusinessForm(instance=business)
    return render(request, "admin_edit_business.html", {"form": form, "user_id": user_id})

def use_business(request, user_id, business_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    role = request.session.get("role")

    if role == "owner":
        business = get_object_or_404(Business, pk=business_id, owner_id=user_id)
    elif role == "staff":
        business = get_object_or_404(Business, pk=business_id, staff__user_id=user_id)
    else:
        return HttpResponseForbidden("You do not have permission.")

    request.session["business_id"] = business.id
    messages.success(request, f"Switched to business: {business.name}")
    return redirect("business_list", user_id=user_id)


def manage_staff(request, user_id):
    if request.session.get("user_id") != user_id:
        return redirect("login")

    business = Business.objects.filter(owner_id=user_id).first()
    if not business:
        return HttpResponse("No Business matches the given query.", status=404)

    form = AddStaffForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"] or "123456"

        user, created = User.objects.get_or_create(email=email, defaults={
            "username": email.split("@")[0],
            "role": "staff",
            "password": make_password(password),
        })

        StaffAssignment.objects.get_or_create(user=user, business=business)

        return redirect("manage_staff", user_id=user_id)

    assigned_staff = business.staff.select_related("user")

    return render(request, "admin_manage_staff.html", {
        "form": form,
        "staff_list": assigned_staff,
        "active_page": "staff"
    })


def remove_staff(request, user_id, staff_id):
    business = request.session.get("business_id")
    assignment = get_object_or_404(StaffAssignment, business_id=business, user_id=staff_id)
    assignment.delete()
    messages.success(request, "Staff removed successfully.")
    return redirect("manage_staff", user_id=user_id)


@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            table_id = data.get("table_id")
            items = data.get("items", [])

            # 获取桌号与商家
            try:
                table = Table.objects.get(id=table_id)
                business = table.business
            except Table.DoesNotExist:
                return JsonResponse({"success": False, "error": "Table not found."})

            # ✅ 获取当前登录用户
            user_id = request.session.get("user_id")
            user = User.objects.get(id=user_id) if user_id else None

            # 创建订单
            order = Order.objects.create(
                table=table,
                business=business,
                user=user  # ✅ 绑定用户（可以为 None）
            )

            total_price = 0
            for item_data in items:
                try:
                    menu_item = MenuItem.objects.get(id=item_data["id"])
                    qty = int(item_data["qty"])
                    if qty <= 0:
                        continue
                    item_price = menu_item.price
                    total_price += item_price * qty

                    OrderItem.objects.create(
                        order=order,
                        menu_item=menu_item,
                        quantity=qty,
                        item_price=item_price
                    )
                except (MenuItem.DoesNotExist, ValueError):
                    continue  # 如果有异常则跳过该菜品

            order.total_price = total_price
            order.save()

            return JsonResponse({
                "success": True,
                "order_id": order.id
            })

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"})

    return JsonResponse({"success": False, "error": "Invalid request method"})



@require_POST
def update_order_status(request, user_id, order_id):
    order = get_object_or_404(Order, id=order_id)
    next_status = request.POST.get("next_status")
    if next_status in dict(Order.STATUS_CHOICES):
        order.status = next_status
        order.save()
        return redirect("admin_orders", user_id=user_id)
    return JsonResponse({"error": "Invalid status"}, status=400)
