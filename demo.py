# Bàn cờ 5x5 cho ví dụ
size = 3
board = [["." for _ in range(size)] for _ in range(size)]

def play(move):
    try:
        parts = move.split(":")
        player = parts[0].upper()   # X hoặc O
        row = int(parts[1])
        col = int(parts[2])
        # Kiểm tra hợp lệ
        if board[row][col] == ".":
            board[row][col] = player
        else:
            print("Ô này đã có người đánh rồi!")
    except Exception as e:
        print("Lỗi nhập lệnh:", e)

def show():
    for row in board:
        print(" ".join(row))
    print()

# Ví dụ
play("x:0:2")
play("o:1:1")
show()
