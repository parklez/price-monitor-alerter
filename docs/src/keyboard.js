document.addEventListener("keydown", (ev) => {
  if (ev.key !== "Shift") {
    return;
  }
  const element = document.querySelector('[data-keyboard-key="SHIFT"]');
  element.classList.add("active");
});

document.addEventListener("keyup", (ev) => {
  if (ev.key !== "Shift") {
    return;
  }
  const element = document.querySelector('[data-keyboard-key="SHIFT"]');
  element.classList.remove("active");
});
