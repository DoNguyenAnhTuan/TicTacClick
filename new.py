from flask import Flask, request, render_template_string, url_for

app = Flask(__name__)

SIZE = 3
board = [["." for _ in range(SIZE)] for _ in range(SIZE)]
game_over = False
winner = None  # 'X', 'O', 'draw', or None

COL_MAP = {"h": 0, "y": 1, "t": 2}  # trái -> phải
ROW_MAP = {"6": 0, "5": 1, "3": 2}  # trên -> dưới

def check_winner(b):
    """Trả về 'X' / 'O' nếu có 3 liên tiếp; 'draw' nếu bàn đầy mà chưa ai thắng; None nếu chưa kết thúc."""
    lines = []

    # Hàng & Cột
    for i in range(3):
        lines.append(b[i])                         # hàng i
        lines.append([b[0][i], b[1][i], b[2][i]]) # cột i

    # Chéo
    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])

    for line in lines:
        if line[0] != "." and line.count(line[0]) == 3:
            return line[0]  # 'X' hoặc 'O'

    # Bàn đầy?
    full = all(cell != "." for row in b for cell in row)
    if full:
        # Đếm quân để phân thắng nếu chưa ai 3 liên tiếp
        x_cnt = sum(cell == "X" for row in b for cell in row)
        o_cnt = sum(cell == "O" for row in b for cell in row)
        if x_cnt > o_cnt:
            return "X"
        elif o_cnt > x_cnt:
            return "O"
        else:
            return "draw"

    return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Cáp quang và laser</title>
  <style>
    :root{
      --bg:#f7f7fb; --card:#ffffff; --ink:#0f172a; --muted:#6b7280;
      --line:#e5e7eb; --error:#ef4444; --ok:#065f46; --radius:12px;
    }
    *{box-sizing:border-box}
    body{margin:0; font-family:Inter,system-ui,Arial,sans-serif; color:var(--ink); background:var(--bg)}
    h1{margin:24px 0 12px; text-align:center; font-size:28px; letter-spacing:.3px}
    .container{
      max-width:1040px; margin:0 auto; padding:0 16px 28px;
      display:grid; gap:18px; grid-template-columns:300px minmax(260px, 1fr) 320px;
      align-items:start; justify-items:center;
    }
    .card{background:var(--card); border:1px solid var(--line); border-radius:var(--radius); padding:14px}
    .caption{font-size:12px; color:var(--muted); text-align:center; margin-top:6px}
    img{max-width:100%; height:auto; display:block; border-radius:10px}

    /* Board */
    .board-wrap{display:flex; justify-content:center}
    table{border-collapse:collapse; margin:0 auto}
    td{width:70px; height:70px; text-align:center; vertical-align:middle;
       border:2px solid #000; font-size:30px}
    .legend{margin-top:8px; font-size:13px; color:var(--muted); text-align:center}

    /* Rules */
    .rules h3{margin:4px 0 8px}
    .rules ul{margin:8px 0 0 18px; line-height:1.55}

    /* Controls */
    .controls{max-width:820px; margin:10px auto 20px; display:flex; flex-direction:column; gap:10px}
    form{display:flex; flex-direction:column; align-items:center; gap:10px}
    .row-inline{display:flex; gap:16px; flex-wrap:wrap; align-items:center; justify-content:center}
    label{font-weight:600}
    select, input[type="text"]{
      padding:8px 10px; font-size:16px; border-radius:10px; border:1px solid var(--line); outline:none;
      background:#fff; min-width:64px; text-align:center;
    }
    input::placeholder{color:#9ca3af}
    .btns{display:flex; gap:10px; justify-content:center}
    button{
      padding:10px 18px; font-size:16px; border-radius:12px; border:1px solid #111;
      background:#fff; cursor:pointer;
    }
    .msg{font-size:15px; margin-top:6px}
    .msg.error{color:var(--error); font-weight:700}
    .msg.ok{color:var(--ok); font-weight:700}
  </style>
</head>
<body>
  <h1>Cáp quang và laser</h1>

  <div class="container">
    <!-- Trái: Ảnh morse -->
    <div class="card">
      <img src="{{ url_for('static', filename='morse.png') }}" alt="Mã Morse">
      <div class="caption">Bảng mã Morse (tham khảo)</div>
    </div>

    <!-- Giữa: Bàn Caro 3x3 -->
    <div class="card board-wrap">
      <div>
        <table>
          {% for row in board %}
          <tr>
            {% for cell in row %}
            <td>{{ cell }}</td>
            {% endfor %}
          </tr>
          {% endfor %}
        </table>
      
      </div>
    </div>

    <!-- Phải: Luật chơi -->
    <div class="card rules">
      <h3>Luật chơi</h3>
      <ul>
        <li>Hai người chơi lần lượt đánh dấu <b>X</b> hoặc <b>O</b> vào một ô trống.</li>
        <li>Nhập toạ độ theo <b>cột chữ</b> (h, y, t) và <b>hàng số</b> (6, 5, 3).</li>
        <li>Nếu đầy bàn mà chưa ai 3 liên tiếp: bên có <b>số quân nhiều hơn</b> thắng; bằng nhau thì hoà.</li>
        <li>Bấm <b>Reset</b> để chơi ván mới.</li>
      </ul>
    </div>
  </div>

  <!-- Điều khiển dưới cùng -->
  <div class="controls">
    <form method="post" action="/move">
      <div class="row-inline">
        <label>Người chơi:</label>
        <select name="player">
          <option value="X" {% if last_player=='X' %}selected{% endif %}>X</option>
          <option value="O" {% if last_player=='O' %}selected{% endif %}>O</option>
        </select>

        <label>Hàng:</label>
        <input type="text" name="row_label" placeholder="Nhập tọa độ hàng" autocomplete="off">

        <label>Cột:</label>
        <input type="text" name="col_label" placeholder="Nhập tọa độ cột" autocomplete="off">
      </div>

      <div class="btns">
        <button type="submit">Enter</button>
      </div>

      {% if message %}
        <div class="msg {{ 'error' if error else 'ok' }}">{{ message }}</div>
      {% endif %}
    </form>

    <form method="post" action="/reset" style="display:flex; justify-content:center">
      <button type="submit">Reset</button>
    </form>
  </div>
</body>
</html>
"""

def render(message=None, error=False, last_player="X"):
    return render_template_string(
        HTML_TEMPLATE,
        board=board, message=message, error=error, last_player=last_player,
        url_for=url_for  # for static
    )

@app.route("/", methods=["GET"])
def home():
    return render(message=None, error=False, last_player="X")

@app.route("/move", methods=["POST"])
def move():
    global game_over, winner

    player = (request.form.get("player") or "").upper().strip()
    row_label = (request.form.get("row_label") or "").strip()
    col_label = (request.form.get("col_label") or "").strip().lower()

    if game_over:
        return render(message="Ván đã kết thúc. Bấm Reset để chơi lại.", error=True, last_player=player)

    if player not in ("X", "O"):
        return render(message="Người chơi không hợp lệ (chỉ X hoặc O).", error=True, last_player=player)

    if row_label not in ROW_MAP or col_label not in COL_MAP:
        return render(message="Toạ độ không hợp lệ.", error=True, last_player=player)

    r = ROW_MAP[row_label]
    c = COL_MAP[col_label]

    if board[r][c] != ".":
        return render(message=f"Ô {row_label}{col_label} đã có giá trị, hãy chọn ô khác.", error=True, last_player=player)

    # Đánh
    board[r][c] = player

    # Kiểm tra kết quả
    result = check_winner(board)
    if result == "X" or result == "O":
        game_over, winner = True, result
        return render(message=f"{result} thắng! 🎉", error=False, last_player=player)
    elif result == "draw":
        game_over, winner = True, "draw"
        return render(message="Hoà (số quân bằng nhau).", error=False, last_player=player)

    # Chưa kết thúc
    return render(message=f"Đánh vào ô {row_label}{col_label} thành công.", error=False, last_player=player)

@app.route("/reset", methods=["POST"])
def reset():
    global board, game_over, winner
    board = [["." for _ in range(SIZE)] for _ in range(SIZE)]
    game_over, winner = False, None
    return render(message="Đã reset bàn cờ.", error=False, last_player="X")

if __name__ == "__main__":
    # Đặt 'morse.png' trong thư mục ./static/
    app.run(host="0.0.0.0", port=5000, debug=True)
