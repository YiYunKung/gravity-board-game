import socket
import threading

class GameState: #遊戲狀態
    WAITING = 0
    PLAYING = 1
    GAME_OVER = 2

class ClientThread(threading.Thread):
    def __init__(self, client_socket, game):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.game = game

    def run(self):
        try:
            while True:
                data = self.client_socket.recv(1024).decode()   # 接收clien端訊息
                #print(f"Received data: {data}")
                
                if not data:    # 沒有接收到訊息
                    #break  這邊若使用break會結束整個run()函式
                    continue
                
                if data == "start":      # 收到開始的訊息
                    self.game.start_game()
                else:      # 收到對手下棋位置
                    row, col = map(int, data.split(","))
                    self.game.process_opponent_move(row, col)
        finally:
            self.client_socket.close()

class FourInARowGame():
    def __init__(self):
        self.clients = [] #存客戶端連接
        self.game_state = GameState.WAITING
        self.board = [[None] * 7 for _ in range(6)]
        self.current_player = "red"

    def add_client(self, client_socket):
        if self.game_state != GameState.WAITING or len(self.clients) >= 2:
            client_socket.send("0".encode())  # 遊戲已經開始or滿人
            client_socket.close()
            return
        else:
            client_socket.send("1".encode())  # 加入遊戲
            self.clients.append(client_socket)

        if len(self.clients) == 2:
            self.start_game()
    '''
    def start_game(self):
        self.game_state = GameState.PLAYING

        for client_socket in self.clients:
            client_socket.send("start".encode())
    '''
    def start_game(self):
        self.game_state = GameState.PLAYING
        self.current_player = "red"
        self.clients[0].send("start,red".encode())
        self.clients[1].send("start,yellow".encode())
        
    def process_opponent_move(self, row, col):      # 更新並傳送棋子的動作
        if self.game_state != GameState.PLAYING:
            print("OK self.game_state != GameState.PLAYING")
            return
        #print(f"對手的操作：{row},{col}")

        self.board[row][col] = self.current_player      # 棋盤位置設定player的顏色
        move = f"{row},{col},{self.current_player}"     # 格式化
        print(move)

        '''
        for client in self.clients:
            print("OK for client in self.clients:")
            client.send(move.encode())
        '''

        for i, client in enumerate(self.clients):
            if self.current_player == "red" and i == 1:     
                client.send(move.encode())      # 將紅棋位置傳給黃方(client[1])
            elif self.current_player == "yellow" and i == 0:
                client.send(move.encode())      # 將黃棋位置傳給紅方(client[0])

        self.check_game_over()    # 檢查遊戲是否結束
        self.switch_player()      # 交換玩家

    def switch_player(self):     
        if self.current_player == "red":
            self.current_player = "yellow"
        else:
            self.current_player = "red"
  
    def check_game_over(self):
        # win?
        for row in range(6):
            for col in range(4):     # 檢查橫向
                if self.board[row][col] is not None and self.board[row][col] == self.board[row][col+1] == self.board[row][col+2] == self.board[row][col+3]:
                    self.game_state = GameState.GAME_OVER
                    self.send_game_over_message(f"{self.board[row][col]} wins!")
                    return

        for row in range(3):         # 檢查直行
            for col in range(7):
                if self.board[row][col] is not None and self.board[row][col] == self.board[row+1][col] == self.board[row+2][col] == self.board[row+3][col]:
                    self.game_state = GameState.GAME_OVER
                    self.send_game_over_message(f"{self.board[row][col]} wins!")
                    return

        for row in range(3):         # 檢查斜線
            for col in range(4):
                if self.board[row][col] is not None and self.board[row][col] == self.board[row+1][col+1] == self.board[row+2][col+2] == self.board[row+3][col+3]:
                    self.game_state = GameState.GAME_OVER
                    self.send_game_over_message(f"{self.board[row][col]} wins!")
                    return

        for row in range(3, 6):      # 檢查斜線
            for col in range(4):
                if self.board[row][col] is not None and self.board[row][col] == self.board[row-1][col+1] == self.board[row-2][col+2] == self.board[row-3][col+3]:
                    self.game_state = GameState.GAME_OVER
                    self.send_game_over_message(f"{self.board[row][col]} wins!")
                    return

        # 平手?
        is_full = all(all(cell is not None for cell in row) for row in self.board)
        if is_full:
            self.game_state = GameState.GAME_OVER
            self.send_game_over_message("平手")

    def send_game_over_message(self, message):
        for client_socket in self.clients:
            print(message)
            client_socket.send(message.encode())

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("127.0.0.1", 8888))
        self.server_socket.listen(2)

        self.game = FourInARowGame()

    def start(self):
        print("等待客戶端連接...")

        while True:
            client_socket, address = self.server_socket.accept()
            print("客戶端連接成功")

            self.game.add_client(client_socket)
            # 啟動ClientThread
            client_thread = ClientThread(client_socket, self.game)
            client_thread.start()

server = Server()
server.start()
