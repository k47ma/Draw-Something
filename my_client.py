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

        lbl3 = Label(container, text="Name: ")
        lbl3.grid(row=2, column=0, padx=10, pady=(5, 0), sticky=E)

        self.host_name = Entry(container)
        self.host_name.grid(row=0, column=1, sticky=E+W)
        self.host_name.bind("<Return>", self.create_connection)

        self.port_number = Entry(container)
        self.port_number.grid(row=1, column=1, sticky=E+W)
        self.port_number.bind("<Return>", self.create_connection)

        self.name_entry = Entry(container)
        self.name_entry.grid(row=2, column=1, sticky=E+W)
        self.name_entry.bind("<Return>", self.create_connection)

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

        name = self.name_entry.get()
        if not name:
            self.status["text"] = "Please enter a name! ^^"
            return

        self.connect_btn["state"] = DISABLED

        try:
            port_number = int(port)
        except ValueError:
            self.status["text"] = "Please enter a valid port number! ^^"
            self.connect_btn["state"] = NORMAL
            return

        settings["HOST"] = host
        settings["PORT"] = port_number

        self.status.configure(text="Connecting...", fg="#228B22")

        try:
            if not self.setup_client(name):
                self.status.configure(text="This name has been used. Please choose another name!", fg="red")
                self.connect_btn["state"] = NORMAL
        except socket.error:
            self.status.configure(
                text="Can't connect to the given host at given port.\nPlease check your input!", fg="red")
            self.connect_btn["state"] = NORMAL

    def setup_client(self, name):
        host = settings["HOST"]
        port = settings["PORT"]

        s = socket.socket()
        s.connect((host, port))
        settings["SOCKET"] = s

        # register player at server
        data = {"type": "register", "data": name}
        self.status.configure(text="Registering player at server...", fg="blue")
        s.send(str(data))
        result = s.recv(1024)
        result = literal_eval(result)
        if not result["data"]:
            return False

        controller = settings["CONTROLLER"]
        controller.status.configure(text="Connected to:\n" + host + " - " + str(port), fg="#228B22")
        self.status.configure(text="Connected to:\n" + host + " - " + str(port), fg="#228B22")

        thread = ClientReceivingThread(s)
        thread.daemon = True
        thread.start()

        self.parent.game_frame.lift()
        self.parent.wm_geometry("900x680")
        self.parent.controller.set_state(False)

        return True


# thread for listening to messages from server
class ClientReceivingThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)

        self.connection = connection
        self.image = None
        self.last_draw = None
        self.history = []
        self.bitmaps = []
        self.points = []
        self.draw_info = None
        self.mouse = 0

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

                    try:
                        if data["type"] == "mouse":
                            # update mouse position
                            pos = data["data"]
                            cursor = PhotoImage(file="image\\cursor2.gif")
                            self.mouse = canvas.create_image(pos, image=cursor, anchor=NW)
                        elif data["type"] == "pencil":
                            if not self.last_draw:
                                self.last_draw = []

                            # read line info
                            pos, color, width = data["data"]

                            # record line info
                            self.draw_info = ("pencil", color, width)
                            self.points.extend([pos[2], pos[3]])

                            # add the pencil line
                            line = canvas.create_line(pos, fill=color, width=width, capstyle=ROUND, joinstyle=ROUND)

                            # record it in history
                            self.last_draw.append(line)
                        elif data["type"] == "brush":
                            if not self.last_draw:
                                self.last_draw = []

                            # read brush info
                            brush_type, pos, color, width = data["data"]

                            # record brush info
                            self.draw_info = ("brush", brush_type, color, width)
                            self.points.extend([pos[2], pos[3]])

                            # add brush line
                            if brush_type == "circle":
                                brush = canvas.create_line(pos, fill=color, width=width, capstyle=ROUND, joinstyle=ROUND)
                            else:
                                brush = canvas.create_line(pos, fill=color, width=width, capstyle=PROJECTING, joinstyle=BEVEL)

                            # record it in history
                            self.last_draw.append(brush)
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
                            coords, color, width, dash, dash_width = data["data"]
                            if dash:
                                line = canvas.create_line(coords, fill=color, width=width, capstyle=ROUND,
                                                          dash=(dash_width,))
                            else:
                                line = canvas.create_line(coords, fill=color, width=width, capstyle=ROUND)
                            self.last_draw = line
                        elif data["type"] == "set":
                            if self.draw_info:
                                if self.draw_info[0] == "pencil":
                                    color = self.draw_info[1]
                                    width = self.draw_info[2]

                                    # draw a new optimized line
                                    new_line = canvas.create_line(tuple(self.points), fill=color, width=width, capstyle=ROUND,
                                                                  joinstyle=ROUND, smooth=True)

                                    # reset the history
                                    self.clear_action(self.last_draw)
                                    self.last_draw = new_line
                                elif self.draw_info[0] == "brush":
                                    brush_type = self.draw_info[1]
                                    color = self.draw_info[2]
                                    width = self.draw_info[3]

                                    # draw a new optimized brush line
                                    if brush_type == "circle":
                                        new_brush = canvas.create_line(tuple(self.points), fill=color, width=width,
                                                                       capstyle=ROUND, joinstyle=ROUND, smooth=True)
                                    else:
                                        new_brush = canvas.create_line(tuple(self.points), fill=color, width=width,
                                                                       capstyle=PROJECTING, joinstyle=BEVEL, smooth=True)

                                    # reset the history
                                    self.clear_action(self.last_draw)
                                    self.last_draw = new_brush

                            if self.last_draw:
                                self.history.append(self.last_draw)

                            self.points = []
                            self.last_draw = None
                            self.draw_info = None
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
                            self.clear_action(last_action)
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
                            canvas.delete(self.mouse)
                        elif data["type"] == "clear":
                            self.clear_canvas()
                    except Exception:
                        continue
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

    def clear_action(self, action):
        canvas = settings["CANVAS"]

        # clear all action
        if type(action) is int:
            canvas.delete(action)
        else:
            for act in action:
                canvas.delete(act)
