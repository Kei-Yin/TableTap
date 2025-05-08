from django.shortcuts import render,redirect


menu_items = [
    {"id": 1, "name": "Hamburger", "price": 26, "image": "burger.png", "description": "juicy burger"},
    {"id": 2, "name": "Coke(medium)", "price": 8, "image": "coke.png", "description": "cool coke"},
]

# 首页
# 用户端视图
def index(request):
    return render(request, "index.html")

# 登录
def login_view(request):
    return render(request, "login.html")

# 注册
def register(request):
    return render(request, "register.html")

# 菜单页面
def menu(request):
    return render(request, "menu.html", {"menu_items": menu_items})


# 餐桌页面
def tables(request):
    return render(request, "tables.html")

# 订单页面
def orders(request):
    return render(request, "orders.html")

def order_detail(request, order_id):
    return render(request, "order_detail.html", {"order_id": order_id})

# 评论页面
def reviews(request):
    return render(request, "reviews.html")

# 管理者端视图
def admin_menu(request):

    return render(request, "admin_menu.html",{"menu_items": menu_items})

def edit_menu_item(request, item_id):
    item = next((i for i in menu_items if i["id"] == item_id), None)
    if not item:
        return redirect("admin_menu")

    if request.method == "POST":
        item["name"] = request.POST["name"]
        item["description"] = request.POST["description"]
        item["price"] = float(request.POST["price"])
        item["image_url"] = request.POST["image_url"]
        return redirect("admin_menu")

    return render(request, "edit_menu_item.html", {"item": item})

def delete_menu_item(request, item_id):
    global menu_items
    if request.method == "POST":
        menu_items = [item for item in menu_items if item["id"] != item_id]
        return redirect("admin_menu")
    return redirect("admin_menu")

def add_menu_item(request):
    global menu_items
    if request.method == "POST":
        new_id = max([item["id"] for item in menu_items], default=0) + 1
        new_item = {
            "id": new_id,
            "name": request.POST["name"],
            "description": request.POST["description"],
            "price": float(request.POST["price"]),
            "image_url": request.POST["image_url"],
        }
        menu_items.append(new_item)
        return redirect("admin_menu")
    return render(request, "add_menu_item.html")

def admin_orders(request):
    return render(request, "admin_orders.html")