import socket
import threading
from ast import literal_eval

# module for game server


class GameServer(object):
    def __init__(self):
        object.__init__(self)

        self.clients = []

    def start(self):
        host = socket.gethostbyname(socket.gethostname())
        ind = 1
        while True:
            # ask user for port number
            port = raw_input("Please enter a port number: ")
            try:
                port = int(port)
            except ValueError:
                print "Please enter a valid port number!"

            print "Setting up server..."
            s = socket.socket()
            s.bind((host, port))
            s.listen(10)
            print "Server is ready!"
            print "Host: " + host
            print "Port Number: " + str(port)
            print "Waiting for connection..."

            while True:
                client, addr = s.accept()
                client_name = "Client" + str(ind)
                print client_name + " connected from: " + addr[0] + " - " + str(addr[1])

                self.clients.append((client_name, client))
                client_thread = ClientHandlingThread(self, client, client_name)
                client_thread.daemon = True
                client_thread.start()

                ind += 1

    def send_message(self, message, name):
        for client_name, client in self.clients:
            if client_name != name:
                data = {"type": "message", "data": name + ": " + message}
                client.send(str(data))


# thread for handling requests from each client
class ClientHandlingThread(threading.Thread):
    def __init__(self, server, client, client_name):
        threading.Thread.__init__(self)

        self.server = server
        self.client = client
        self.client_name = client_name

    def run(self):
        while True:
            try:
                data = self.client.recv(1024)
                data = literal_eval(data)
                if data["type"] == "message":
                    self.server.send_message(data["data"], self.client_name)
            except socket.error:
                print self.client_name + " disconnected."
                break


server = GameServer()
server.start()
