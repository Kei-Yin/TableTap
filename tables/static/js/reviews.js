
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".like-button").forEach(btn => {
    btn.addEventListener("click", () => {
      const reviewId = btn.dataset.reviewId;
      fetch(`/tabletap/reviews/${reviewId}/like/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const countSpan = btn.querySelector(".like-count");
          countSpan.textContent = data.likes;
        }
      });
    });
  });

  document.querySelectorAll(".reply-form").forEach(form => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const reviewId = form.dataset.reviewId;
      const input = form.querySelector("input[name='reply']");
      fetch(`/tabletap/reviews/${reviewId}/reply/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `reply=${encodeURIComponent(input.value)}`
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          location.reload();
        }
      });
    });
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
