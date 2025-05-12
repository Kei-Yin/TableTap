document.addEventListener("DOMContentLoaded", function () {
  const cart = {};
  const cartBar = document.getElementById("cartBar");
  const cartSummary = document.getElementById("cartSummary");

  document.querySelectorAll(".quantity-control").forEach(control => {
    const plusBtn = control.querySelector(".btn-plus");
    const minusBtn = control.querySelector(".btn-minus");
    const qtySpan = control.querySelector(".quantity");
    const itemId = control.dataset.id;
    const price = parseFloat(control.dataset.price);

    plusBtn.addEventListener("click", () => {
      cart[itemId] = (cart[itemId] || 0) + 1;
      updateCart();
    });

    minusBtn.addEventListener("click", () => {
      if (cart[itemId]) {
        cart[itemId]--;
        if (cart[itemId] <= 0) delete cart[itemId];
      }
      updateCart();
    });

    function updateCart() {
      const count = cart[itemId] || 0;
      qtySpan.textContent = count;
      qtySpan.classList.toggle("d-none", count === 0);
      minusBtn.classList.toggle("d-none", count === 0);

      let totalQty = 0;
      let totalPrice = 0;
      for (const [id, qty] of Object.entries(cart)) {
        const el = document.querySelector(`.quantity-control[data-id='${id}']`);
        if (!el) continue;
        const price = parseFloat(el.dataset.price);
        totalQty += qty;
        totalPrice += price * qty;
      }

      if (totalQty > 0) {
        cartBar.style.display = "flex";
        cartSummary.textContent = ` ${totalQty} selected, total$ ${totalPrice.toFixed(2)}`;
      } else {
        cartBar.style.display = "none";
        cartSummary.textContent = "Unpicked items";
      }
    }
  });

  // 分类锚点平滑滚动
  document.querySelectorAll(".category-link").forEach(link => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  // checkout
  document.getElementById("checkoutBtn").onclick = function () {
    const tableId = document.body.dataset.tableId;
    const userId = document.body.dataset.userId;
    const items = Object.entries(cart).map(([id, qty]) => ({ id, qty }));

    fetch("/tabletap/orders/create/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ table_id: tableId, items: items })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("The order has been submitted with the order number:" + data.order_id);
        window.location.href = `/tabletap/customer/${userId}/order/${data.order_id}/`;
      } else {
        alert("Failed to submit:" + data.error);
      }
    });
  };
});
