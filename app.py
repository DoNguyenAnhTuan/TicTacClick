from flask import Flask, request, render_template

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
        lines.append(b[i])  # hàng
        lines.append([b[0][i], b[1][i], b[2][i]])  # cột
    lines.append([b[0][0], b[1][1], b[2][2]])      # chéo chính
    lines.append([b[0][2], b[1][1], b[2][0]])      # chéo phụ

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

# ===== RENDER HELPERS =====
def render_select():
    return render_template("select.html", maps=MAPS, course=COURSE)

def render_play(message=None, error=False, last_player="X"):
    return render_template(
        "play.html",
        board=board, message=message, error=error, last_player=last_player,
        course=COURSE
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
