document.addEventListener("DOMContentLoaded", function () {
    const toggles = document.querySelectorAll(".accordion-toggle");
    toggles.forEach(toggle => {
      toggle.style.cursor = "pointer";
      toggle.addEventListener("click", function () {
        const targetId = this.getAttribute("data-bs-target");
        const content = document.querySelector(targetId);
        if (content.classList.contains("show")) {
          content.classList.remove("show");
        } else {
          document.querySelectorAll(".collapse.show").forEach(el => el.classList.remove("show"));
          content.classList.add("show");
        }
      });
    });
  });
  