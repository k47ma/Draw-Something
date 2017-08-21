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
        except socket.error:
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


# thread for listening to messages from server
class ClientReceivingThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)

        self.connection = connection
        self.image = None
        self.last_draw = None
        self.history = []
        self.bitmaps = []

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
                    controller = settings["CONTROLLER"]

                    if data["type"] == "mouse":
                        # update mouse position
                        pos = data["data"]
                        cursor = PhotoImage(file="image\\cursor2.gif")
                        canvas.create_image(pos, image=cursor, anchor=NW)
                    elif data["type"] == "pencil":
                        if not self.last_draw:
                            self.last_draw = []
                        # add pencil line
                        pos, color, width = data["data"]
                        line = canvas.create_line(pos, fill=color, width=width, capstyle=ROUND, joinstyle=ROUND)
                        self.last_draw.append(line)
                        self.history.append(line)
                    elif data["type"] == "brush":
                        if not self.last_draw:
                            self.last_draw = []
                        # add brush line
                        brush_type, pos, color, width = data["data"]
                        if brush_type == "circle":
                            brush = canvas.create_line(pos, fill=color, width=width, capstyle=ROUND, joinstyle=ROUND)
                        else:
                            brush = canvas.create_line(pos, fill=color, width=width, capstyle=PROJECTING, joinstyle=BEVEL)
                        self.last_draw.append(brush)
                        self.history.append(brush)
                    elif data["type"] == "textarea":
                        text_data = data["data"][0]
                        background_data = data["data"][1]
                        action = []
                        if background_data:
                            # add background for text
                            coords, color, fill_color = background_data
                            background = canvas.create_rectangle(coords, outline=color, fill=fill_color)
                            action.append(background)
                        # add text
                        x, y, text, font, width, text_color = text_data
                        text = canvas.create_text(x, y, text=text, anchor=NW, font=font, width=width, fill=text_color)
                        action.append(text)
                        self.history.append(action)
                    elif data["type"] == "line":
                        # clear last line
                        if self.last_draw:
                            canvas.delete(self.last_draw)
                        # add new line
                        coords, color, width = data["data"]
                        line = canvas.create_line(coords, fill=color, width=width, capstyle=ROUND)
                        self.last_draw = line
                    elif data["type"] == "set":
                        if self.last_draw:
                            self.history.append(self.last_draw)
                        self.last_draw = None
                    elif data["type"] == "rect":
                        # clear last rectangle
                        if self.last_draw:
                            canvas.delete(self.last_draw)
                        # add new rectangle
                        coords, width, color, fill_color = data["data"]
                        rect = canvas.create_rectangle(coords, width=width, outline=color, fill=fill_color)
                        self.last_draw = rect
                    elif data["type"] == "circle":
                        # clear last circle
                        if self.last_draw:
                            canvas.delete(self.last_draw)
                        # add new circle
                        coords, width, color, fill_color = data["data"]
                        circle = canvas.create_oval(coords, width=width, outline=color, fill=fill_color)
                        self.last_draw = circle
                    elif data["type"] == "spray":
                        if not self.last_draw:
                            self.last_draw = []
                        # add spray
                        coords, spray_size = data["data"]
                        image = PhotoImage(file="image\\shaped_spray.gif")
                        zoomed_image = image.zoom(spray_size)
                        self.bitmaps.append(zoomed_image)
                        spray = canvas.create_image(coords, image=self.bitmaps[-1])
                        self.last_draw.append(spray)
                    elif data["type"] == "revert":
                        # get the last action
                        try:
                            last_action = self.history.pop()
                        except IndexError:
                            continue
                        # delete last action from canvas
                        if type(last_action) is int:
                            canvas.delete(last_action)
                        else:
                            for action in last_action:
                                canvas.delete(action)
                    elif data["type"] == "message":
                        textarea = settings["TEXTAREA"]
                        message = data["data"]
                        textarea.insert(END, message + "\n")
                        textarea.see(END)
                    elif data["type"] == "drawer":
                        word = data["data"]
                        canvas.update_word(word)
                        canvas.drawer = True
                        controller.set_state(True)
                    elif data["type"] == "guess":
                        guess_word = data["data"].replace("*", u"\u25a1").replace(" ", "_")
                        canvas.update_word(guess_word)
                        canvas.drawer = False
                        controller.set_state(False)
                        controller.deselect_all()
                    elif data["type"] == "finished":
                        self.clear_canvas()
                    elif data["type"] == "clear":
                        self.clear_canvas()
        except socket.error:
            controller = settings["CONTROLLER"]
            controller.status.configure(text="Offline", fg="#FF8C00")

    def clear_canvas(self):
        canvas = settings["CANVAS"]
        if canvas.drawer:
            history = canvas.history
        else:
            history = self.history

        # clear all history
        for action in history:
            if type(action) is int:
                canvas.delete(action)
            else:
                for act in action:
                    canvas.delete(act)
