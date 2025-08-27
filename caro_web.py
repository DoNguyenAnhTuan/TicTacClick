from flask import Flask, request, render_template_string

app = Flask(__name__)

SIZE = 10
board = [["." for _ in range(SIZE)] for _ in range(SIZE)]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Caro 3x3</title>
    <style>
        table { border-collapse: collapse; margin: 20px auto; }
        td { width: 60px; height: 60px; text-align: center; 
             font-size: 28px; border: 2px solid black; }
        .form { text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <h2 style="text-align:center;">Game Caro 3x3</h2>
    <table>
        {% for row in board %}
        <tr>
            {% for cell in row %}
            <td>{{cell}}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>

    <div class="form">
        <form method="post" action="/move">
            <label>Người chơi:</label>
            <select name="player">
                <option value="X">X</option>
                <option value="O">O</option>
            </select><br><br>

            <label>Hàng (0-2):</label>
            <input type="number" name="row" min="0" max="2" required><br><br>
            <label>Cột (0-2):</label>
            <input type="number" name="col" min="0" max="2" required><br><br>

            <button type="submit">Đánh</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, board=board)

@app.route("/move", methods=["POST"])
def move():
    player = request.form.get("player", "").upper()
    row = int(request.form.get("row"))
    col = int(request.form.get("col"))

    if player in ["X", "O"]:
        if 0 <= row < SIZE and 0 <= col < SIZE:
            if board[row][col] == ".":
                board[row][col] = player
    return render_template_string(HTML_TEMPLATE, board=board)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
