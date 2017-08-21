from tkinter import *
from config import *
from math import *


# frame for canvas
class PaintCanvas(Canvas):
    def __init__(self, parent):
        Canvas.__init__(self, parent, bg="white")

        settings["CANVAS"] = self
        self.parent = parent
        self.type = ""
        self.lastX = 0
        self.lastY = 0
        self.firstClick = True
        self.history = []
        self.action = []
        self.points = []
        self.entry = None
        self.controller = None
        self.bitmaps = []
        self.drawer = False

        word_frame = Frame(self, bg="white")
        self.word_lbl = Label(word_frame, text="Word: ", font=("Arial", 12, "bold"))
        self.word_lbl.pack(side=LEFT)
        self.create_window(0, 0, anchor=NW, window=word_frame)

        # add ready button to canvas
        ready_frame = Frame(self, width=700, height=650, bg="white")
        ready_btn = Button(ready_frame, text="READY!", font=("Arial", 12, "bold"), command=self.ready)
        ready_btn.pack(padx=6, pady=3)
        ready_btn.place(x=200, y=300)
        self.ready_window = self.create_window(0, 0, anchor=NW, window=ready_frame)

        self.bind("<Button-1>", self.startDraw)
        self.bind("<Motion>", self.printMousePosition)
        self.bind("<B1-Motion>", self.draw)
        self.bind("<ButtonRelease-1>", self.setDraw)

    def printMousePosition(self, event):
        if self.controller:
            self.controller.printMousePosition(event)

    def startDraw(self, event):
        if self.firstClick:
            self.lastX, self.lastY = event.x, event.y
            self.points = [event.x, event.y]
            self.firstClick = False
        if self.type == "text" and self.entry:
            self.entry.draw_text()
        self.draw(event)

    def draw(self, event):
        self.printMousePosition(event)

        type = self.type
        if type == "pencil":
            self.addPencilLine(event)
        elif type == "brush":
            self.addBrushLine(event)
        elif type == "eraser":
            self.addEraserLine(event)
        elif type == "line":
            self.addLine(event)
        elif type == "rect":
            self.addRect(event)
        elif type == "circle":
            self.addCircle(event)
        elif type == "text":
            self.addDashRect(event)
        elif type == "spray":
            self.addSpray(event)

    def addPencilLine(self, event):
        line = self.create_line((self.lastX, self.lastY, event.x, event.y), fill=settings["COLOR"],
                                width=settings["PENCIL_WIDTH"], capstyle=ROUND, joinstyle=ROUND)

        # send line information
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "pencil",
                           "data": ((self.lastX, self.lastY, event.x, event.y),
                                    settings["COLOR"], settings["PENCIL_WIDTH"])}
                socket.send(str(message))
            except socket.error:
                pass

        self.points.extend([event.x, event.y])
        self.action.append(line)
        self.lastX = event.x
        self.lastY = event.y

    def addBrushLine(self, event, eraser_mode=False):
        type = settings["BRUSH_MODE"]
        r = settings["BRUSH_WIDTH"]
        color = settings["COLOR"]

        if eraser_mode:
            type = settings["ERASER_MODE"]
            r = settings["ERASER_WIDTH"]
            color = "white"

        if type == "circle":
            line = self.create_line((self.lastX, self.lastY, event.x, event.y), fill=color,
                                    width=r, capstyle=ROUND, joinstyle=ROUND)
        else:
            line = self.create_line((self.lastX, self.lastY, event.x, event.y), fill=color,
                                    width=r, capstyle=PROJECTING, joinstyle=BEVEL)

        # send line information
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "brush",
                           "data": (type, (self.lastX, self.lastY, event.x, event.y), color, r)}
                socket.send(str(message))
            except socket.error:
                pass

        self.points.extend([event.x, event.y])
        self.action.append(line)
        self.lastX = event.x
        self.lastY = event.y

    def addEraserLine(self, event):
        self.addBrushLine(event, True)

    def addLine(self, event):
        if self.action:
            self.delete(self.action[0])

        if event.state == SHIFT:
            # avoid "divided by 0" error
            if event.x == self.lastX:
                line = self.create_line((self.lastX, self.lastY, self.lastX, event.y),
                                        fill=settings["COLOR"], width=settings["LINE_WIDTH"],
                                        capstyle=ROUND)
                self.sendLine((self.lastX, self.lastY, self.lastX, event.y))
                self.action = [line]
                return

            slope = float((event.y - self.lastY) / (event.x - self.lastX))

            # calculate the endpoint of line
            if slope >= tan(radians(67.5)) or slope < tan(radians(112.5)):
                line = self.create_line((self.lastX, self.lastY, self.lastX, event.y),
                                        fill=settings["COLOR"], width=settings["LINE_WIDTH"],
                                        capstyle=ROUND)
                self.sendLine((self.lastX, self.lastY, self.lastX, event.y))
            elif tan(radians(-22.5)) <= slope < tan(radians(22.5)):
                line = self.create_line((self.lastX, self.lastY, event.x, self.lastY),
                                        fill=settings["COLOR"], width=settings["LINE_WIDTH"],
                                        capstyle=ROUND)
                self.sendLine((self.lastX, self.lastY, event.x, self.lastY))
            elif tan(radians(22.5)) <= slope < tan(radians(67.5)):
                end_x = int(round((self.lastX + event.x - self.lastY + event.y) / 2))
                end_y = int(round((event.x - self.lastX + event.y + self.lastY) / 2))
                line = self.create_line((self.lastX, self.lastY, end_x, end_y), fill=settings["COLOR"],
                                        width=settings["LINE_WIDTH"], capstyle=ROUND)
                self.sendLine((self.lastX, self.lastY, end_x, end_y))
            else:
                end_x = int(round((self.lastX + event.x + self.lastY - event.y) / 2))
                end_y = int(round((self.lastX - event.x + self.lastY + event.y) / 2))
                line = self.create_line((self.lastX, self.lastY, end_x, end_y), fill=settings["COLOR"],
                                        width=settings["LINE_WIDTH"], capstyle=ROUND)
                self.sendLine((self.lastX, self.lastY, end_x, end_y))
        else:
            line = self.create_line((self.lastX, self.lastY, event.x, event.y), fill=settings["COLOR"],
                                    width=settings["LINE_WIDTH"], capstyle=ROUND)
            self.sendLine((self.lastX, self.lastY, event.x, event.y))
        self.action = [line]

    def addRect(self, event):
        if self.action:
            self.delete(self.action[0])

        width = settings["RECT_WIDTH"]
        color = settings["COLOR"]

        if settings["TRANSPARENT"]:
            fill_color = ""
        else:
            fill_color = settings["FILL_COLOR"]

        if event.state == SHIFT:
            side = min(abs(self.lastX - event.x), abs(self.lastY - event.y))

            # determine the direction of endpoint
            if event.x - self.lastX >= 0:
                dir_x = 1
            else:
                dir_x = -1

            if event.y - self.lastY >= 0:
                dir_y = 1
            else:
                dir_y = -1

            # draw square
            end_x = self.lastX + dir_x * side
            end_y = self.lastY + dir_y * side
            rect = self.create_rectangle(self.lastX, self.lastY, end_x, end_y, width=width, outline=color,
                                         fill=fill_color)
        else:
            # draw rectangle
            end_x = event.x
            end_y = event.y
            rect = self.create_rectangle(self.lastX, self.lastY, end_x, end_y, width=width, outline=color,
                                         fill=fill_color)

        # send rectangle information
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "rect",
                           "data": ((self.lastX, self.lastY, end_x, end_y), width, color, fill_color)}
                socket.send(str(message))
            except socket.error:
                pass

        self.action = [rect]

    def addCircle(self, event):
        if self.action:
            self.delete(self.action[0])

        if settings["TRANSPARENT"]:
            fill_color = ""
        else:
            fill_color = settings["FILL_COLOR"]
        width = settings["CIRCLE_WIDTH"]
        color = settings["COLOR"]

        if event.state == SHIFT:
            diameter = min(abs(self.lastX - event.x), abs(self.lastY - event.y))

            # determine the direction of endpoint
            if event.x - self.lastX >= 0:
                dir_x = 1
            else:
                dir_x = -1

            if event.y - self.lastY >= 0:
                dir_y = 1
            else:
                dir_y = -1

            # draw circle
            end_x = self.lastX + dir_x * diameter
            end_y = self.lastY + dir_y * diameter
            oval = self.create_oval((self.lastX, self.lastY, end_x, end_y), width=width, outline=color, fill=fill_color)
        else:
            end_x = event.x
            end_y = event.y
            oval = self.create_oval((self.lastX, self.lastY, end_x, end_y), width=width, outline=color, fill=fill_color)

        # send circle information
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "circle",
                           "data": ((self.lastX, self.lastY, end_x, end_y), width, color, fill_color)}
                socket.send(str(message))
            except socket.error:
                pass

        self.action = [oval]

    def addDashRect(self, event):
        if self.action:
            self.delete(self.action[0])

        if event.state == SHIFT:
            side = min(abs(self.lastX - event.x), abs(self.lastY - event.y))

            # determine the direction of endpoint
            if event.x - self.lastX >= 0:
                dir_x = 1
            else:
                dir_x = -1

            if event.y - self.lastY >= 0:
                dir_y = 1
            else:
                dir_y = -1

            # draw square
            end_x = self.lastX + dir_x * side
            end_y = self.lastY + dir_y * side
            rect = self.create_rectangle(self.lastX, self.lastY, end_x, end_y, outline="black", fill="white",
                                         dash=[3, 3])
        else:
            # draw rectangle
            rect = self.create_rectangle(self.lastX, self.lastY, event.x, event.y, outline="black", fill="white",
                                         dash=[3, 3])
        self.action = [rect]

    def addSpray(self, event):
        spray_size = settings["SPRAY_SIZE"]
        image = PhotoImage(file="image\\shaped_spray.gif")
        zoomed_image = image.zoom(spray_size)
        self.bitmaps.append(zoomed_image)

        spray = self.create_image((event.x, event.y), image=self.bitmaps[-1])

        # send spray information
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "spray",
                           "data": ((event.x, event.y), spray_size)}
                socket.send(str(message))
            except socket.error:
                pass

        self.action.append(spray)

    def revert(self, event=None):
        try:
            last_action = self.history.pop()
        except IndexError:
            return

        for action in last_action:
            self.delete(action)

        # send revert command
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "revert",
                           "data": None}
                socket.send(str(message))
            except socket.error:
                pass

    def setDraw(self, event=None):
        type = self.type
        if type == "text":
            try:
                (x1, y1, x2, y2) = self.coords(self.action[0])
            except IndexError:
                return

            width = abs(x1 - x2)
            height = abs(y1 - y2)

            char_width = int(width // 7)
            char_height = int(height // 15)

            if char_width < 10:
                char_width = 10

            self.delete(self.action[0])

            paint_text = self.PaintText(self, x1, y1, char_width, char_height)
            paint_text.place(x=x1, y=y1, anchor=NW)
        elif type == "pencil":
            # clear pencil lines
            for action in self.action:
                self.delete(action)

            # draw a single smooth pencil line
            line = self.create_line(tuple(self.points), fill=settings["COLOR"], width=settings["PENCIL_WIDTH"],
                                    capstyle=ROUND, joinstyle=ROUND, smooth=True)

            self.points = []
            self.history.append([line])
        elif type == "brush":
            # clear brush lines
            for action in self.action:
                self.delete(action)

            # draw a single smooth brush line
            type = settings["BRUSH_MODE"]
            color = settings["COLOR"]
            width = settings["BRUSH_WIDTH"]
            if type == "circle":
                line = self.create_line(tuple(self.points), fill=color, width=width, capstyle=ROUND, joinstyle=ROUND,
                                        smooth=True)
            else:
                line = self.create_line(tuple(self.points), fill=color, width=width, capstyle=PROJECTING,
                                        joinstyle=BEVEL, smooth=True)

            self.points = []
            self.history.append([line])
        else:
            self.history.append(self.action)

        # send setDraw command
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "set", "data": None}
                socket.send(str(message))
            except socket.error:
                pass

        self.firstClick = True
        self.action = []

    def clear(self):
        # clear all history
        for action in self.history:
            if type(action) is int:
                self.delete(action)
            else:
                for act in action:
                    self.delete(act)

    def sendLine(self, coords):
        # send line information
        socket = settings["SOCKET"]
        if socket and self.drawer:
            try:
                message = {"type": "line",
                           "data": (coords, settings["COLOR"], settings["LINE_WIDTH"])}
                socket.send(str(message))
            except socket.error:
                pass

    def ready(self):
        # send server ready command
        socket = settings["SOCKET"]
        if socket:
            try:
                data = {"type": "ready",
                        "data": None}
                socket.send(str(data))
            except socket.error:
                return
        textarea = settings["TEXTAREA"]
        textarea.insert(END, "READY!\n")
        self.delete(self.ready_window)

    def update_word(self, word):
        self.word_lbl["text"] = "Word: " + word

    class PaintText(Text):
        def __init__(self, canvas, x, y, width, height):
            Text.__init__(self, canvas, relief=SOLID, width=width, height=height, wrap=WORD, bd=1,
                          fg=settings["TEXT_COLOR"])
            self.width = width
            self.height = height
            self.canvas = canvas
            self.x = x
            self.y = y
            self["font"] = self.get_font()

            if not settings["TRANSPARENT"]:
                self["bg"] = settings["FILL_COLOR"]

            self.focus()
            self.bind("<FocusOut>", self.draw_text)
            self.bind("<Key-Return>", self.draw_text)
            self.bind("<Control-Return>", lambda x: self.insert(INSERT, ""))

        def draw_text(self, *args):
            background = None
            background_info = None

            # draw the background of text
            if not settings["TRANSPARENT"]:
                x1 = self.x
                y1 = self.y
                x2 = x1 + self.width * 7
                y2 = y1 + self.height * 15
                background_coords = (x1, y1, x2, y2)
                color = settings["COLOR"]
                fill_color = settings["FILL_COLOR"]

                background = self.canvas.create_rectangle(background_coords, outline=color, fill=fill_color)
                background_info = (background_coords, color, fill_color)

            text = self.get(1.0, END)
            width = self.width * 7
            text_color = settings["TEXT_COLOR"]
            font = self.get_font()
            draw = self.canvas.create_text(self.x + 3, self.y - 2, text=text, anchor=NW, font=font, width=width,
                                           fill=text_color)

            # send text information
            socket = settings["SOCKET"]
            if socket and self.drawer:
                try:
                    message = {"type": "textarea",
                               "data": ((self.x + 3, self.y - 2, text, font, width, text_color), background_info)}
                    socket.send(str(message))
                except socket.error:
                    pass

            if not settings["TRANSPARENT"]:
                self.canvas.history.append([draw, background])
            else:
                self.canvas.history.append([draw])

            self.canvas.entry = None
            self.destroy()

        def get_font(self):
            font_family = settings["FONT_FAMILY"]
            font_size = settings["FONT_SIZE"]
            font_decoration_list = []

            if settings["BOLD"]:
                font_decoration_list.append("bold")
            if settings["SLANT"]:
                font_decoration_list.append("italic")
            if settings["UNDERLINE"]:
                font_decoration_list.append("underline")
            if settings["OVERSTRIKE"]:
                font_decoration_list.append("overstrike")

            font_decoration = " ".join(font_decoration_list)

            return (font_family, font_size, font_decoration)
