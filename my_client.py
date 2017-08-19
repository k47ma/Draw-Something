import threading
import socket
import tkMessageBox
import random
from tkinter import *
from config import settings
from ast import literal_eval


# module for client side program


class ClientSettingFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        container = Frame(self)
        container.pack(side=TOP, padx=6, pady=(6, 0), fill=BOTH, expand=True)

        lbl1 = Label(container, text="Host: ")
        lbl1.grid(row=0, column=0, padx=10, pady=5, sticky=E)

        lbl2 = Label(container, text="Port Number: ")
        lbl2.grid(row=1, column=0, padx=10, pady=5, sticky=E)

        self.host_name = Entry(container)
        self.host_name.grid(row=0, column=1, sticky=E + W)
        self.host_name.bind("<Return>", self.create_connection)

        self.port_number = Entry(container)
        self.port_number.grid(row=1, column=1, sticky=E + W)
        self.port_number.bind("<Return>", self.create_connection)

        self.status = Label(self, font=("", 9), fg="red")
        self.status.pack(side=TOP)

        self.connect_btn = Button(self, text="Connect", command=self.create_connection)
        self.connect_btn.pack(side=BOTTOM, ipadx=3, ipady=1, pady=(3, 6))

    def create_connection(self, event=None):
        host = self.host_name.get()
        if not host:
            self.status["text"] = "Please enter a valid hostname! ^^"
            return

        port = self.port_number.get()
        if not port:
            self.status["text"] = "Please enter a valid port number! ^^"
            return

        try:
            port_number = int(port)
        except ValueError:
            self.status["text"] = "Please enter a valid port number! ^^"
            return

        settings["HOST"] = host
        settings["PORT"] = port_number

        self.status.configure(text="Connecting...", fg="#228B22")

        try:
            self.setup_client()
        except Exception:
            self.status.configure(
                text="Can't connect to the given host at given port.\nPlease check your input!", fg="red")

    def setup_client(self):
        host = settings["HOST"]
        port = settings["PORT"]

        s = socket.socket()
        s.connect((host, port))
        settings["SOCKET"] = s

        controller = settings["CONTROLLER"]
        controller.status.configure(text="Connected to:\n" + host + " - " + str(port), fg="#228B22")
        self.status.configure(text="Connected to:\n" + host + " - " + str(port), fg="#228B22")
        self.connect_btn["state"] = DISABLED

        thread = ClientReceivingThread(s)
        thread.daemon = True
        thread.start()

        self.parent.game_frame.lift()
        self.parent.wm_geometry("900x680")
        self.parent.controller.set_state(False)


# thread for new client connection
class ClientThread(threading.Thread):
    def __init__(self, parent, host, port):
        threading.Thread.__init__(self)

        self.parent = parent
        self.host = host
        self.port = port

    def run(self):
        self.parent.status.configure(text="Connecting...", fg="#228B22")

        try:
            self.setup_client()
        except Exception:
            self.parent.status.configure(
                text="Can't connect to the given host at given port.\nPlease check your input!", fg="red")

    def setup_client(self):
        s = socket.socket()
        s.connect((self.host, self.port))
        settings["SOCKET"] = s

        controller = settings["CONTROLLER"]
        controller.status.configure(text="Connected to:\n" + self.host + " - " + str(self.port), fg="#228B22")
        self.parent.status.configure(text="Connected to:\n" + self.host + " - " + str(self.port), fg="#228B22")
        self.parent.connect_btn["state"] = DISABLED

        thread = ClientReceivingThread(s)
        thread.daemon = True
        thread.start()


# thread for listening to messages from server
class ClientReceivingThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)

        self.connection = connection
        self.image = None
        self.last_draw = None

    def run(self):
        # listen to the server
        try:
            while True:
                datas = self.connection.recv(1024)
                for data in re.findall("{.*?}", datas):
                    try:
                        data = literal_eval(data)
                    except ValueError:
                        continue
                    except TypeError:
                        continue
                    except SyntaxError:
                        continue

                    canvas = settings["CANVAS"]

                    if data["type"] == "mouse":
                        # update mouse position
                        pos = data["data"]
                        cursor = PhotoImage(file="image\\cursor2.gif")
                        canvas.create_image(pos, image=cursor, anchor=NW)
                    elif data["type"] == "pencil":
                        # add pencil line
                        pos, color, width = data["data"]
                        canvas.create_line(pos, fill=color, width=width, capstyle=ROUND, joinstyle=ROUND)
                    elif data["type"] == "brush":
                        # add brush line
                        type, pos, color, width = data["data"]
                        if type == "circle":
                            canvas.create_line(pos, fill=color, width=width, capstyle=ROUND, joinstyle=ROUND)
                        else:
                            canvas.create_line(pos, fill=color, width=width, capstyle=PROJECTING, joinstyle=BEVEL)
                    elif data["type"] == "text":
                        # add text
                        x, y, text, font, width, text_color = data["data"]
                        canvas.create_text(x, y, text=text, anchor=NW, font=font, width=width, fill=text_color)
                    elif data["type"] == "background":
                        # add background for text
                        pos, color, fill_color = data["data"]
                        canvas.create_rectangle(pos, outline=color, fill=fill_color)
                    elif data["type"] == "line":
                        # clear last line
                        if self.last_draw:
                            canvas.delete(self.last_draw)

                        # add new line
                        coords, color, width = data["data"]
                        line = canvas.create_line(coords, fill=color, width=width, capstyle=ROUND)
                        self.last_draw = line
                    elif data["type"] == "set":
                        self.last_draw = None
        except Exception:
            controller = settings["CONTROLLER"]
            controller.status.configure(text="Offline", fg="#FF8C00")
