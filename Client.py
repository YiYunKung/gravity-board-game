import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

def send_move(server_socket, move):     # 傳送移動位置
    server_socket.send(move.encode())

def receive_move(server_socket):        # 接收移動資訊
    data = server_socket.recv(1024).decode()
    return data

class GameUI:
    def __init__(self, root, network_thread):
        self.root = root
        self.network_thread = network_thread
        self.root.resizable(width=False, height=False)    # 長寬不可調整

        self.canvas = tk.Canvas(self.root, width=700, height=600, bg="#0072E3")
        '''
        # 创建TextBox
        self.text_box = tk.Text( width=30, height=5, wrap=tk.WORD)
        self.text_box.insert(tk.END, "遊戲狀態\n等待对手加入...")
        self.text_box.pack(side=tk.RIGHT, fill=tk.Y)
        '''
        # 右側文字介面
        frame = tk.Frame(self.root)
        frame.pack(side=tk.RIGHT, fill=tk.Y)     # 靠右，填滿Y軸

        scrollbar = tk.Scrollbar(frame)          # 滾動軸
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_box = scrolledtext.ScrolledText(frame, width=20, height=5, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.text_box.insert(tk.END, "遊戲狀態\n")
        self.text_box.pack(side=tk.LEFT, fill=tk.Y)

        scrollbar.config(command=self.text_box.yview)

        # 設定框中的字體和大小
        self.text_box.configure(font=("微軟正黑體", 20))

        self.board = [["white"] * 7 for _ in range(6)]
        self.canvas.pack()

        # 綁定滑鼠左鍵點擊事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.can_click = False      # 預設為不可點擊

        self.draw_board()
        
    def update_text(self, text):
        self.text_box.insert(tk.END, text + "\n")
        self.text_box.see(tk.END)

    def draw_board(self):
        self.canvas.delete("all")

        for row in range(6):
            for col in range(7):
                x1 = col * 100
                y1 = row * 100
                x2 = x1 + 100
                y2 = y1 + 100

                fill_color = self.board[row][col]       # 獲取對應位置的顏色
                # 在該位置繪製棋子顏色
                self.canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill=fill_color)

    def update_board(self, row, col, color):
        self.board[row][col] = color
        self.draw_board()
        
    def show_winner_message(self, winner):      # 勝負結果文字方塊
        # 繪製矩形色塊 (左上x, 左上y, 右下x, 右下y, 顏色)
        self.canvas.create_rectangle(200, 250, 500, 350, fill="black")
        # 文字位置, 內容, 字體及大小, 顏色
        self.canvas.create_text(350, 300, text= winner, font=("微軟正黑體", 30), fill="white")

    def on_click(self, event):
        
        if not self.network_thread.game_running or not self.can_click:
            return

        col = event.x // 100     # 透過點擊位置計算col值
        color = network_thread.player    # 取得當前player顏色

        # 由該行尚未落棋的最下層開始填棋子
        for row in range(5, -1, -1):
            if self.board[row][col] == "white":     # 白色 尚未有棋子
                self.board[row][col] = color        # 該位置填上顏色
                self.draw_board()       # 更新到畫面上

                move = f"{row},{col}"
                #print(move)
                send_move(self.network_thread.server_socket, move)

                self.can_click = False    # 點擊一次後，當前為不可點擊
                break        

class NetworkThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(("127.0.0.1", 8888))

        self.game_running = False
        winning_color = None
        
    def run(self):
        while True:
            data = receive_move(self.server_socket)

            if data == "1":
                print("加入遊戲成功。")
                game_ui.update_text("加入遊戲成功。\n等待對手加入\n")
                continue

            # 收到遊戲開始訊息
            elif data == "start,red":
                print("遊戲開始！")
                self.game_running = True
                self.player = "red"     # 初始化玩家顏色
                game_ui.update_text("遊戲開始！\n你是紅色")
                game_ui.can_click = True    # 剛開始紅方先進行下棋動作
                continue
            elif data == "start,yellow":
                print("遊戲開始！")
                self.game_running = True
                self.player = "yellow"      # 初始化玩家顏色
                game_ui.update_text("遊戲開始！\n你是黃色")
                continue

            # 收到遊戲結果
            elif "draw" in data:
                game_ui.update_text("遊戲結束！\n你們平手")
                game_ui.show_winner_message(data)
                game_ui.canvas.unbind("<Button-1>")     # 取消綁定點擊事件
                #game_ui.draw_board.stop()
                break
            
            elif "wins" in data:
                winning_color = data.split()[0]
                game_ui.update_text("遊戲結束！\n" + winning_color + " win!")
                game_ui.show_winner_message(winning_color)
                game_ui.show_winner_message(data)
                game_ui.canvas.unbind("<Button-1>")     # 取消綁定點擊事件
                #game_ui.draw_board.stop()
                break

            # 接收對手操作的位置跟顏色
            row, col, player = map(str, data.split(","))
            row, col = int(row), int(col)
            
            game_ui.board[row][col] = player

            # 新的移動訊息
            updated_move = f"{row},{col},{player}"
            print("Updated move:", updated_move)

            #print(f"對手的操作：{data}")
            #row, col, full_color = map(int, data.split(","))
            game_ui.update_board(row, col, player)
            game_ui.update_text("對手下棋位置為:"+f"{col+1},{row+1}")

            # 交換玩家點擊權限
            if game_ui.can_click:
                game_ui.can_click = False
            else:
                game_ui.can_click = True

        self.server_socket.close()

root = tk.Tk()
network_thread = NetworkThread()
game_ui = GameUI(root, network_thread)

network_thread.start()

root.mainloop()
