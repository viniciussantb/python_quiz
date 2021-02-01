from socket import socket, AF_INET, SOCK_DGRAM
import threading
import time


class Player:
    def __init__(self, name, address):
        self.address = address
        self.name = name
        self.message_buffer = []
        self.score = 0


class ServerSocket:
    def __init__(self):
        self.server_sock = socket(AF_INET, SOCK_DGRAM)
        self.server_address = ('localhost', 8080)
        self.players = []
        self.questions = [
            'Which band composed Eleanor Rigby ', 'Who is considered the father of rock ',
            'Which band released the album Dark side of the moon ', 'who is the father of soul in Brazil',
            'Which is considered the singer that composed the best brazilian song to the magazine Rolling Stone ']
        self.answers = ['the beatles', 'chuck berry', 'pink floyd', 'tim maia', 'chico buarque']
        self.server_sock.bind(self.server_address)
        self.next_round = True
        self.finish = False
        self.flag_time = False

        print('waiting for connections...')

        thread_receive = threading.Thread(target=self.receive)
        thread_receive.start()

    def receive(self):
        while not self.finish:
            (data, client_address) = self.server_sock.recvfrom(2048)
            print(f'client address: {client_address}   send the message: {data.decode()}')
            if len(self.players) < 3:
                self.chat(data, client_address)
            else:
                if not self.next_round:
                    for player in self.players:
                        if player.address == client_address:
                            player.message_buffer.append(data.decode())

    def send(self, message, client_address):
        self.server_sock.sendto(message, client_address)

    def send_to_all(self, message, client_address):
        if client_address is not None:
            for player in self.players:
                if player.address != client_address:
                    self.send(message, player.address)
        else:
            for player in self.players:
                self.send(message, player.address)

    def chat(self, data, client_address):
        logged = False
        player_name = ''
        if len(self.players) == 0:
            player_name = data.decode()
            self.players.append(Player(data.decode(), client_address))
            print(f'{player_name} join to the party')
            logged = True
        else:
            for player in self.players:
                if client_address == player.address:
                    player_name = player.name
                    logged = True
        if not logged:
            if len(self.players) == 2:
                self.players.append(Player(data.decode(), client_address))
                self.send_to_all(f'{data.decode()} joined to the party'.encode(), client_address)
                thread_quiz = threading.Thread(target=self.quiz)
                thread_quiz.start()
            else:
                self.players.append(Player(data.decode(), client_address))
                self.send_to_all(f'{data.decode()} joined to the party'.encode(), client_address)
        else:
            message = f'{player_name}: {data.decode()}'.encode()
            self.send_to_all(message, client_address)

    def quiz(self):
        self.send_to_all('the band quiz is about to begin'.encode(), None)
        for secs in range(5, 0, -1):
            time.sleep(1)
            self.send_to_all(f'{secs}...'.encode(), None)
        for r in range(5):
            if r != 0:
                self.send_to_all('next round...'.encode(), None)
                for sec in range(1, 4):
                    self.send_to_all(f'{sec}...'.encode(), None)
                    time.sleep(1)
            self.next_round = False
            self.round(r)
        self.finish = True
        score = []
        scoreboard = '\nSCOREBOARD\n'
        for player in self.players:
            score.append((player.score, player.name))
        self.bubblesort(score, len(score))
        for i in range(len(score)):
            scoreboard += f'{i+1}- {score[i][1]} {score[i][0]} points\n'
        self.send_to_all(scoreboard.encode(), None)
        self.send_to_all('thanks for playing!'.encode(), None)
        self.finish = True

    def round(self, number):

        def round_time():
            self.flag_time = False
            for t in range(15):
                if self.flag_time:
                    break
                time.sleep(1)
            if not self.flag_time:
                self.send_to_all('time is out'.encode(), None)
                self.next_round = True

        message = f'question number {number + 1} - {self.questions[number]}? '.encode()
        self.send_to_all(message, None)
        for player in self.players:
            thread_read_messages = threading.Thread(target=self.read_message_buffer, args=[player, number])
            thread_read_messages.start()
        thread_time = threading.Thread(target=round_time)
        thread_time.start()
        thread_read_messages.join()

    def read_message_buffer(self, player, r):
        while not self.next_round:
            for player_answer in player.message_buffer:
                if player_answer == self.answers[r]:
                    player.score += 10
                    self.send_to_all(f'{player.name} wins the round!'.encode(), player.address)
                    self.send('congrats! correct answer'.encode(), player.address)
                    self.next_round = True
                    self.flag_time = True
                    player.message_buffer = []
                    break
                else:
                    player.score -= 2
                    self.send('wrong answer, try again'.encode(), player.address)
                    player.message_buffer.remove(player_answer)
        player.message_buffer = []

    @staticmethod
    def bubblesort(vector, length):
        for i in range(length-1, 0, -1):
            for j in range(0, i):
                if vector[j][0] < vector[i][0]:
                    bigger = vector[i]
                    vector[i] = vector[j]
                    vector[j] = bigger


server_sock = ServerSocket()
