import socket
import threading
import time
import random
import re
from ast import literal_eval

# module for game server


class GameServer(object):
    def __init__(self):
        object.__init__(self)

        self.clients = []
        self.drawer = ""
        self.word = ""

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
                print "New player connected from: " + addr[0] + " - " + str(addr[1])

                # register player
                data = client.recv(1024)
                data = literal_eval(data)
                client_name = data["data"]
                print "registering player..."
                if self.check_name(client_name):
                    # send successful result to the player
                    result = {"type": "register", "data": True}
                    client.send(str(result))
                    print client_name + " registered!"
                else:
                    # send failed result to the player
                    result = {"type": "register", "data": False}
                    client.send(str(result))
                    print "Registration failed! Name(" + client_name + ") has been used."
                    continue

                client_info = {"name": client_name, "socket": client, "ready": False, "win": False}
                self.clients.append(client_info)

                # assign each client a thread
                client_thread = ClientDataHandlingThread(self, client, client_name)
                client_thread.daemon = True
                client_thread.start()

                ind += 1

    def check_name(self, name):
        for client_info in self.clients:
            if client_info["name"] == name:
                return False
        return True

    def send_message(self, message, name=None):
        if name:
            # check if message is correct
            save_message = self.check_guess(message, name)
            msg = name + ": " + save_message
        else:
            msg = message

        for client_info in self.clients:
            # pack up and send the message
            if client_info["name"] != name:
                data = {"type": "message", "data": msg}
                client_info["socket"].send(str(data))

    def broadcast_data(self, data, name=None):
        for client_info in self.clients:
            if client_info["name"] != name:
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

    def check_guess(self, message, name):
        guess = message.lower().strip()
        if guess == self.word:
            # update the player status
            for client_info in self.clients:
                if client_info["name"] == name and name != self.drawer:
                    client_info["win"] = True
                    self.send_message(name + " won!")
                    break
        return re.sub(self.word, "*" * len(self.word), message, flags=re.IGNORECASE)


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
                datas = self.client.recv(1024)
                for data in re.findall("{.*?}", datas):
                    try:
                        data = literal_eval(data)
                    except ValueError:
                        continue
                    except TypeError:
                        continue
                    except SyntaxError:
                        continue

                    if data["type"] == "message":
                        self.server.send_message(data["data"], self.client_name)
                    elif data["type"] == "ready":
                        self.server.player_ready(self.client_name)
                    else:
                        self.server.broadcast_data(data, self.client_name)
            except socket.error:
                print self.client_name + " disconnected."
                self.server.remove_player(self.client_name)
                self.server.send_message(self.client_name + " left game.", self.client_name)
                break


# thread for game status management
class GameStatusManageThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)

        self.server = server

    def run(self):
        while True:
            while True:
                if self.check_ready_status():
                    print "Game start!"
                    break
                time.sleep(0.1)

            # start new round
            clients = self.server.clients
            ind = 0
            while True:
                self.server.send_message("Game started!")

                # reset the player status
                for client_info in clients:
                    client_info["win"] = False

                # generate a random word
                try:
                    word = self.get_word()
                except IndexError:
                    word = self.get_word()
                self.server.word = word

                # send drawer information to all players
                try:
                    drawer = clients[ind]["name"]
                except IndexError:
                    break
                self.assign_drawer(drawer, word)

                # check the game status
                while not self.check_game_status():
                    time.sleep(0.2)

                # send new round command to all players
                data = {"type": "finished", "data": None}
                self.server.broadcast_data(str(data))

                self.server.send_message("-------------------------\nNew Round!")

                ind += 1
                if ind == len(clients):
                    ind = 0

    def check_ready_status(self):
        clients = self.server.clients
        # check the number of players
        if len(clients) < 2:
            return False

        # check the status of each players
        for client_info in clients:
            if not client_info["ready"]:
                return False
        return True

    def check_game_status(self):
        for client_info in self.server.clients:
            if not client_info["win"]:
                return False
        return True

    @staticmethod
    def get_word():
        file = open('medium.txt', 'r')
        words = file.readlines()
        ind = random.randint(0, len(words))
        return words[ind].strip()

    def assign_drawer(self, drawer_name, word):
        clients = self.server.clients
        self.server.drawer = drawer_name
        for client_info in clients:
            if client_info["name"] == drawer_name:
                client_info["win"] = True
                data = {"type": "drawer", "data": word}
                client_info["socket"].send(str(data))
            else:
                guess_string = re.sub("\S", "*", word)
                data = {"type": "guess", "data": guess_string}
                client_info["socket"].send(str(data))


server = GameServer()
server.start()
