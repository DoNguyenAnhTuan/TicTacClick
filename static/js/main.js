document.addEventListener("DOMContentLoaded", () => {
  // nếu có socket.io từ server
  const ioObj = window.io || (window.parent && window.parent.io);
  if (!ioObj) return;

  const socket = ioObj(); // auto connect same origin

  const table = document.querySelector(".board table") || document.querySelector("table");
  const msgBox = document.querySelector(".msg");

  function renderBoard(board) {
    if (!table || !board) return;
    let html = "";
    for (const row of board) {
      html += "<tr>";
      for (const cell of row) {
        const cls = cell === "X" ? "x" : cell === "O" ? "o" : "e";
        html += `<td class="cell ${cls}"><span class="mark">${cell}</span></td>`;
      }
      html += "</tr>";
    }
    table.innerHTML = html;
  }

  socket.on("board_update", (data) => {
    renderBoard(data.board);
    if (msgBox && data.message) {
      msgBox.textContent = data.message;
      msgBox.className = "msg ok";
    }
  });

  socket.on("toast", (data) => {
    if (msgBox) {
      msgBox.textContent = data.message || "";
      msgBox.className = "msg " + (data.error ? "error" : "ok");
    }
  });
});
