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
      update();
    });

    minusBtn.addEventListener("click", () => {
      if (cart[itemId]) {
        cart[itemId]--;
        if (cart[itemId] <= 0) delete cart[itemId];
      }
      update();
    });

function update() {
  const count = cart[itemId] || 0;
  qtySpan.textContent = count;
  qtySpan.classList.toggle("d-none", count === 0);
  minusBtn.classList.toggle("d-none", count === 0);

  // 👇 计算总数 & 总价
  let totalItems = 0;
  let totalPrice = 0;

  for (const [id, qty] of Object.entries(cart)) {
    const el = document.querySelector(`.quantity-control[data-id="${id}"]`);
    if (!el) continue;

    const price = parseFloat(el.dataset.price || 0);
    totalItems += qty;
    totalPrice += price * qty;
  }

  if (totalItems > 0) {
    cartBar.style.display = "flex";
    cartSummary.textContent = `已选 ${totalItems} 件，总计 ¥${totalPrice.toFixed(2)}`;
  } else {
    cartBar.style.display = "none";
    cartSummary.textContent = "未选购商品";
  }
}

  });
});
