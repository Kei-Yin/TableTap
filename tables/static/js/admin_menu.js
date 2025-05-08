document.addEventListener("DOMContentLoaded", () => {
  const deleteButtons = document.querySelectorAll(".btn-delete");
  const deleteForm = document.getElementById("deleteForm");
  const deleteItemName = document.getElementById("deleteItemName");
  const deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));

  deleteButtons.forEach(button => {
    button.addEventListener("click", () => {
      const itemId = button.getAttribute("data-id");
      const itemName = button.getAttribute("data-name");
      deleteForm.action = `/management/menu/${itemId}/delete/`;
      deleteItemName.textContent = itemName;
      deleteModal.show();
    });
  });
});
