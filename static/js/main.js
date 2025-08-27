// Nhấn Enter trong input sẽ submit form "move"
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("move-form");
  if (!form) return;
  form.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      form.submit();
    }
  });
});
