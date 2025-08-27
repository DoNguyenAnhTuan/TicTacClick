from flask import Flask, request, render_template_string, url_for

app = Flask(__name__)

# ===== STATE =====
SIZE = 3
board = [["." for _ in range(SIZE)] for _ in range(SIZE)]
game_over = False
winner = None
current_map = None              # 'map1' | 'map2' | 'map3'
COURSE = "Cáp quang và laser"

# Cột: trái→phải ; Hàng: trên→dưới (KHÔNG hiển thị ra UI)
MAPS = {
    "map1": {"name": "Map 1", "rows": ["6", "5", "3"], "cols": ["h", "y", "t"]},
    "map2": {"name": "Map 2", "rows": ["4", "7", "9"], "cols": ["a", "d", "e"]},
    "map3": {"name": "Map 3", "rows": ["2", "8", "1"], "cols": ["p", "q", "b"]},
}

def make_maps(cols, rows):
    col_map = {str(cols[i]).lower(): i for i in range(3)}
    row_map = {str(rows[i]).lower(): i for i in range(3)}
    return col_map, row_map

def reset_board():
    global board, game_over, winner
    board = [["." for _ in range(SIZE)] for _ in range(SIZE)]
    game_over = False
    winner = None

def check_winner(b):
    lines = []
    for i in range(3):
        lines.append(b[i])
        lines.append([b[0][i], b[1][i], b[2][i]])
    lines.append([b[0][0], b[1][1], b[2][2]])
    lines.append([b[0][2], b[1][1], b[2][0]])

    for ln in lines:
        if ln[0] != "." and ln.count(ln[0]) == 3:
            return ln[0]

    full = all(c != "." for r in b for c in r)
    if full:
        x_cnt = sum(c == "X" for r in b for c in r)
        o_cnt = sum(c == "O" for r in b for c in r)
        if x_cnt > o_cnt: return "X"
        if o_cnt > x_cnt: return "O"
        return "draw"
    return None

# ===== TEMPLATES =====

SELECT_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ course }} — Chọn map</title>
  <style>
    :root{--bg:#f4f7f6;--panel:#fff;--ink:#0f1b14;--muted:#6b7280;--line:#e6ebe9;
          --radius:16px;--shadow:0 12px 30px rgba(16,24,40,.08)}
    *{box-sizing:border-box}
    body{margin:0;font-family:Inter,system-ui,Arial,sans-serif;
         background:linear-gradient(180deg,#eef8f3,#f7faf9 30%,#f4f7f6)}
    /* HERO (logos 2 bên) */
    /* === Hero balance & wrap fix === */
    .hero{
    display:flex; align-items:center; justify-content:space-between;
    max-width:1080px; margin:20px auto 12px; padding:0 16px; gap:16px;
    }

    /* Hộp logo 2 bên có bề rộng cố định để luôn cân */
    .hero-side{
    flex:0 0 140px;              /* cùng một bề rộng */
    display:flex; align-items:center; justify-content:center;
    }
    .hero-side img{
    max-height:60px;             /* cùng chiều cao “nhìn” */
    max-width:120px;             /* không vượt hộp */
    width:auto; height:auto; object-fit:contain; display:block;
    }

    /* Khối giữa cho phép co và wrap chữ */
    .hero-center{
    flex:1 1 auto; min-width:0;  /* quan trọng để không bị clip chữ */
    text-align:center; padding:0 8px;
    }

    /* Tiêu đề: size clamp nhẹ hơn + cho wrap an toàn */
    .hero-title{
    margin:0;
    font-size:clamp(28px, 5.2vw, 46px);  /* hạ chút so với trước */
    line-height:1.12;
    background:linear-gradient(90deg,#0a3f2a 0%, #1d9c6b 60%, #2ebd85 100%);
    -webkit-background-clip:text; background-clip:text; color:transparent;
    text-shadow:0 6px 24px rgba(46,189,133,.25);
    overflow-wrap:anywhere;       /* tránh tràn */
    }

    /* Mobile: thu nhỏ hộp logo để không lấn chữ */
    @media (max-width: 640px){
    .hero{flex-direction:column; gap:8px}
    .hero-side{flex:0 0 auto}
    .hero-side img{max-height:52px; max-width:120px}
    }


    .wrap{max-width:1080px;margin:0 auto;padding:0 16px 28px}
    .grid{display:grid;gap:16px;margin-top:18px;grid-template-columns:repeat(3,1fr)}
    @media (max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}}
    @media (max-width:560px){.grid{grid-template-columns:1fr}}
    .card{background:var(--panel);border:1px solid var(--line);border-radius:16px;
          box-shadow:var(--shadow);padding:16px;text-align:center}
    .maptitle{font-weight:800;color:#0a3f2a}
    .muted{color:var(--muted);font-size:14px;margin-top:6px}
    form{margin-top:10px}
    button{padding:12px 16px;border:1px solid #104d35;border-radius:12px;background:#fff;font-weight:600}
  </style>
</head>
<body>

<section class="hero">
  <div class="hero-side">
    <img src="{{ url_for('static', filename='logo-15nam.png') }}" alt="Logo 15 năm">
  </div>
  <div class="hero-center">
    <div class="hero-pill">Khóa học trải nghiệm</div>
    <h1 class="hero-title">Cáp quang &amp; Laser</h1>
    <br>
    <p class="hero-sub">Chọn map để bắt đầu</p>
  </div>
  <div class="hero-side">
    <img src="{{ url_for('static', filename='logo-fablab.png') }}" alt="Logo FabLab">
  </div>
</section>

<div class="wrap">
  <div class="grid">
    {% for mid, m in maps.items() %}
    <div class="card">
      <div class="maptitle">{{ m.name }}</div>
      <div class="muted">Bắt đầu thi đấu với cấu hình ẩn tọa độ.</div>
      <form method="post" action="/select_map">
        <input type="hidden" name="map_id" value="{{ mid }}">
        <button type="submit">Chọn {{ m.name }}</button>
      </form>
    </div>
    {% endfor %}
  </div>
</div>
</body>
</html>
"""

PLAY_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ course }}</title>
  <style>
    :root{
      --bg:#f4f7f6; --panel:#ffffff; --ink:#0f1b14; --muted:#6b7280;
      --line:#e6ebe9; --accent:#2ebd85; --accent-2:#1d9c6b;
      --radius:16px; --shadow:0 12px 30px rgba(16,24,40,.08);
      --cell:80px;
    }
    *{box-sizing:border-box}
    html,body{margin:0;font-family:Inter,system-ui,Arial,sans-serif;
      background:linear-gradient(180deg,#eef8f3,#f7faf9 30%,#f4f7f6)}

    /* HERO (logos 2 bên) */
    /* === Hero balance & wrap fix === */
    .hero{
    display:flex; align-items:center; justify-content:space-between;
    max-width:1080px; margin:20px auto 12px; padding:0 16px; gap:16px;
    }

    /* Hộp logo 2 bên có bề rộng cố định để luôn cân */
    .hero-side{
    flex:0 0 140px;              /* cùng một bề rộng */
    display:flex; align-items:center; justify-content:center;
    }
    .hero-side img{
    max-height:60px;             /* cùng chiều cao “nhìn” */
    max-width:120px;             /* không vượt hộp */
    width:auto; height:auto; object-fit:contain; display:block;
    }

    /* Khối giữa cho phép co và wrap chữ */
    .hero-center{
    flex:1 1 auto; min-width:0;  /* quan trọng để không bị clip chữ */
    text-align:center; padding:0 8px;
    }

    /* Tiêu đề: size clamp nhẹ hơn + cho wrap an toàn */
    .hero-title{
    margin:0;
    font-size:clamp(28px, 5.2vw, 46px);  /* hạ chút so với trước */
    line-height:1.12;
    background:linear-gradient(90deg,#0a3f2a 0%, #1d9c6b 60%, #2ebd85 100%);
    -webkit-background-clip:text; background-clip:text; color:transparent;
    text-shadow:0 6px 24px rgba(46,189,133,.25);
    overflow-wrap:anywhere;       /* tránh tràn */
    }

    /* Mobile: thu nhỏ hộp logo để không lấn chữ */
    @media (max-width: 640px){
    .hero{flex-direction:column; gap:8px}
    .hero-side{flex:0 0 auto}
    .hero-side img{max-height:52px; max-width:120px}
    }


    .topbar{display:flex;justify-content:center;gap:10px;margin:8px 0;flex-wrap:wrap}
    .topbar button{min-width:120px}

    /* Layout 3 cột → 2 → 1 */
    .container{
      display:grid; gap:18px; align-items:start; justify-items:center;
      max-width:1080px; margin:0 auto; padding:0 16px 20px;
      grid-template-columns:300px minmax(260px,1fr) 320px;
    }
    @media (max-width: 992px){ .container{grid-template-columns:1fr 1fr} }
    @media (max-width: 640px){ .container{grid-template-columns:1fr} }

    .card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
      box-shadow:var(--shadow);padding:16px;width:100%}
    img{max-width:100%;height:auto;border-radius:12px;display:block}
    .caption{font-size:12px;color:var(--muted);text-align:center;margin-top:6px}

    /* Board đẹp + màu X/O */
    table{border-collapse:separate;border-spacing:0;margin:0 auto}
    td{width:var(--cell);height:var(--cell);text-align:center;vertical-align:middle;
       border:3px solid #0a3324;font-size:calc(var(--cell) * .44);font-weight:900}
    @media (max-width:640px){ :root{--cell:64px} }
    @media (max-width:380px){ :root{--cell:56px} }
    .cell .mark{display:inline-block;transform:translateY(-2px)}
    .cell.x .mark{color:#2a63ff;text-shadow:0 0 10px rgba(42,99,255,.2)}
    .cell.o .mark{color:#ff2a7a;text-shadow:0 0 10px rgba(255,42,122,.25)}
    .cell.e .mark{color:#9aa7a1}
    @media (hover:hover){ .cell.e:hover{background:#f3fffa} }

    .rules h3{margin:4px 0 8px;color:#0a3f2a}
    .rules ul{margin:8px 0 0 18px;line-height:1.55}

    .controls{max-width:820px;margin:10px auto 24px;display:flex;flex-direction:column;gap:10px;padding:0 12px}
    form{display:flex;flex-direction:column;align-items:center;gap:12px}
    .row-inline{display:flex;gap:12px;flex-wrap:wrap;align-items:center;justify-content:center;width:100%}
    label{font-weight:700;color:#0a3f2a}
    select,input[type="text"]{
      padding:12px 14px;border-radius:12px;border:1px solid var(--line);
      background:#fff;min-width:90px;text-align:center;box-shadow:inset 0 1px 0 rgba(16,24,40,.04)
    }
    @media (max-width:640px){
      .row-inline > *{flex:1 1 32%}
      select,input[type="text"]{width:100%}
    }

    .btns{display:flex;gap:10px;justify-content:center;width:100%}
    button{padding:12px 16px;border-radius:12px;border:1px solid #104d35;background:#fff;cursor:pointer;font-weight:600}
    button:active{transform:translateY(1px)}
    .msg{font-size:15px;margin-top:6px}
    .ok{color:#0a7a55;font-weight:800}
    .error{color:#c62828;font-weight:800}
  </style>
</head>
<body>

<section class="hero">
  <div class="hero-side">
    <img src="{{ url_for('static', filename='logo-15nam.png') }}" alt="Logo 15 năm">
  </div>
  <div class="hero-center">
    <div class="hero-pill">Khóa học trải nghiệm</div>
    <h1 class="hero-title">Cáp quang &amp; Laser</h1>
    <p class="hero-sub">Trò chơi Tic-Tac-Toe</p>
  </div>
  <div class="hero-side">
    <img src="{{ url_for('static', filename='logo-fablab.png') }}" alt="Logo FabLab">
  </div>
</section>

<div class="topbar">
  <form method="post" action="/change_map"><button type="submit">Đổi map</button></form>
  <form method="post" action="/reset"><button type="submit">Reset</button></form>
</div>

<div class="container">
  <div class="card">
    <img src="{{ url_for('static', filename='morse.png') }}" alt="Mã Morse">
    <div class="caption">Bảng mã Morse (tham khảo)</div>
  </div>

  <div class="card">
    <table>
      {% for row in board %}
      <tr>
        {% for cell in row %}
        <td class="cell {% if cell=='X' %}x{% elif cell=='O' %}o{% else %}e{% endif %}">
          <span class="mark">{{ cell }}</span>
        </td>
        {% endfor %}
      </tr>
      {% endfor %}
    </table>
  </div>

  <div class="card rules">
    <h3>Luật chơi</h3>
    <ul>
      <li>Hai người chơi lần lượt đánh dấu <b>X</b> hoặc <b>O</b> vào ô trống.</li>
      <li>Ô đã có X/O thì không được đánh.</li>
      <li>3 liên tiếp (ngang/dọc/chéo) → thắng. Hết bàn: bên có <b>số quân nhiều hơn</b> thắng; bằng nhau thì hoà.</li>
    </ul>
  </div>
</div>

<div class="controls">
  <form method="post" action="/move">
    <div class="row-inline">
      <label>Người chơi:</label>
      <select name="player">
        <option value="X" {% if last_player=='X' %}selected{% endif %}>X</option>
        <option value="O" {% if last_player=='O' %}selected{% endif %}>O</option>
      </select>

      <label>Hàng:</label>
      <input type="text" name="row_label" placeholder="nhập hàng" autocomplete="off">

      <label>Cột:</label>
      <input type="text" name="col_label" placeholder="nhập cột" autocomplete="off">
    </div>

    <div class="btns">
      <button type="submit">Enter</button>
    </div>

    {% if message %}
      <div class="msg {% if error %}error{% else %}ok{% endif %}">{{ message }}</div>
    {% endif %}
  </form>
</div>
</body>
</html>
"""

# ===== RENDER HELPERS =====
def render_select():
    return render_template_string(SELECT_TEMPLATE, maps=MAPS, course=COURSE)

def render_play(message=None, error=False, last_player="X"):
    return render_template_string(
        PLAY_TEMPLATE,
        board=board, message=message, error=error, last_player=last_player,
        course=COURSE, url_for=url_for
    )

# ===== ROUTES =====
@app.route("/", methods=["GET"])
def index():
    return render_select() if not current_map else render_play()

@app.route("/select_map", methods=["POST"])
def select_map():
    global current_map
    mid = request.form.get("map_id")
    if mid not in MAPS:
        return render_select()
    current_map = mid
    reset_board()
    return render_play(message=f"Đã chọn {MAPS[mid]['name']}.", error=False)

@app.route("/change_map", methods=["POST"])
def change_map():
    return render_select()

@app.route("/move", methods=["POST"])
def move():
    global game_over, winner
    if not current_map:
        return render_select()

    m = MAPS[current_map]
    col_map, row_map = make_maps(m["cols"], m["rows"])

    player = (request.form.get("player") or "").upper().strip()
    row_label = (request.form.get("row_label") or "").strip().lower()
    col_label = (request.form.get("col_label") or "").strip().lower()

    if game_over:
        return render_play(message="Ván đã kết thúc. Bấm Reset để chơi lại.", error=True, last_player=player)
    if player not in ("X", "O"):
        return render_play(message="Người chơi không hợp lệ.", error=True, last_player=player)

    # Tự hoán đổi nếu nhập ngược (ví dụ Hàng=h, Cột=6 ở Map 1)
    if (row_label not in row_map or col_label not in col_map):
        if (row_label in col_map) and (col_label in row_map):
            row_label, col_label = col_label, row_label
        else:
            return render_play(message="Toạ độ không hợp lệ.", error=True, last_player=player)

    r = row_map[row_label]
    c = col_map[col_label]
    if board[r][c] != ".":
        return render_play(message="Ô này đã có giá trị.", error=True, last_player=player)

    board[r][c] = player

    result = check_winner(board)
    if result in ("X", "O"):
        game_over, winner = True, result
        return render_play(message=f"{result} thắng! 🎉", error=False, last_player=player)
    elif result == "draw":
        game_over, winner = True, "draw"
        return render_play(message="Hoà (số quân bằng nhau).", error=False, last_player=player)

    return render_play(message="Đã đánh.", error=False, last_player=player)

@app.route("/reset", methods=["POST"])
def reset():
    if not current_map:
        return render_select()
    reset_board()
    return render_play(message="Đã reset bàn cờ.", error=False, last_player="X")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
