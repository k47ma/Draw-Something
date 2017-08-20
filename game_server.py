import socket
import threading
import time
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
            # listen to the given port
            s = socket.socket()
            s.bind((host, port))
            s.listen(10)

            # set up game management thread
            game_status_thread = GameStatusManageThread(self)
            game_status_thread.daemon = True
            game_status_thread.start()
            print "Server is ready!"
            print "Host: " + host
            print "Port Number: " + str(port)
            print "Waiting for connection..."

            while True:
                client, addr = s.accept()
                client_name = "Player" + str(ind)
                print client_name + " connected from: " + addr[0] + " - " + str(addr[1])

                client_info = {"name": client_name, "socket": client, "ready": False}
                self.clients.append(client_info)

                # assign each client a thread
                client_thread = ClientDataHandlingThread(self, client, client_name)
                client_thread.daemon = True
                client_thread.start()

                ind += 1

    def send_message(self, message, name=None):
        for client_info in self.clients:
            if client_info["name"] != name:
                data = {"type": "message", "data": name + ": " + message}
                client_info["socket"].send(str(data))

    def remove_player(self, client_name):
        for client_info in self.clients:
            if client_info["name"] == client_name:
                self.clients.remove(client_info)
                break

    def player_ready(self, client_name):
        # set ready status and broadcast message
        for client_info in self.clients:
            if client_info["name"] == client_name:
                client_info["ready"] = True
            else:
                data = {"type": "message", "data": client_name + " is ready!"}
                client_info["socket"].send(str(data))


# thread for handling requests from each client
class ClientDataHandlingThread(threading.Thread):
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
                elif data["type"] == "ready":
                    self.server.player_ready(self.client_name)
            except socket.error:
                print self.client_name + " disconnected."
                self.server.remove_player(self.client_name)
                self.server.send_message(self.client_name + " left game.")
                break


# thread for game status management
class GameStatusManageThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)

        self.server = server

    def run(self):
        while True:
            while True:
                if self.check_status():
                    print "Game start!"
                    break
                time.sleep(0.1)

            # start the game
            return

    def check_status(self):
        clients = self.server.clients
        # check the number of players
        if len(clients) < 2:
            return False

        # check the status of each players
        for client_info in clients:
            if not client_info["ready"]:
                return False
        return True


server = GameServer()
server.start()
