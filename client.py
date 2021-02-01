from socket import socket, AF_INET, SOCK_DGRAM
import threading


class Client:
    def __init__(self):
        self.client_sock = socket(AF_INET, SOCK_DGRAM)
        self.server_address = ('localhost', 8080)
        self.name = str(input('name: '))
        self.client_sock.sendto(self.name.encode(), self.server_address)
        self.quit = False
        print('chat server, have fun!')
        thread_receive = threading.Thread(target=self.receive)
        thread_receive.start()
        thread_send = threading.Thread(target=self.send)
        thread_send.start()

    def receive(self):
        while True:
            (data, address) = self.client_sock.recvfrom(2048)
            if data.decode() == '700':
                self.quit = True
                break
            else:
                print(f'{data.decode()}')

    def send(self):
        while True:
            if self.quit:
                break
            message = str(input('')).lower().encode()
            self.client_sock.sendto(message, self.server_address)


client_sock = Client()
