document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".snack-list li").forEach((li, i) => {
      li.style.animationDelay = `${i * 80}ms`;
    });
  });
  