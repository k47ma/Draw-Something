import tkFont
import tkMessageBox
import tkFileDialog
from tkinter import *
from tooltip import *
from config import *
from ttk import Combobox
from PIL import ImageGrab
import tkColorChooser


# frame for control buttons
class ControlFrame(Frame):
    def __init__(self, parent, canvas):
        Frame.__init__(self, parent, width=130)

        self.parent = parent
        self.canvas = canvas
        self.canvas.controller = self
        self.types = {}
        self.cursors = {}
        self.pack_propagate(False)
        self.shift_image = PhotoImage(file="image\\up.gif")
        settings["CONTROLLER"] = self

        # frame for showing the connection status
        self.status = Label(self, text="Offline", font=("", 8, "bold"), fg="#FF8C00")
        self.status.pack(side=TOP, pady=(3, 0))
        self.create_tooltip(self.status, "connection status")

        # tools setting
        tools_frame = LabelFrame(self, text="Tools")
        tools_frame.pack(side=TOP, fill=BOTH, ipady=5)

        tools_btn_frame = Frame(tools_frame)
        tools_btn_frame.pack(side=TOP)

        self.pencil_img = PhotoImage(file="image\\pencil.gif")
        pencil_btn = Button(tools_btn_frame, image=self.pencil_img, command=lambda: self.select("pencil"))
        pencil_btn.grid(row=0, column=0)
        self.create_tooltip(pencil_btn, "pencil", "left")
        self.types["pencil"] = pencil_btn
        self.cursors["pencil"] = "@pencil.cur"

        self.brush_img = PhotoImage(file="image\\brush.gif")
        brush_btn = Button(tools_btn_frame, image=self.brush_img, command=lambda: self.select("brush"))
        brush_btn.grid(row=1, column=0)
        self.create_tooltip(brush_btn, "brush", "left")
        self.types["brush"] = brush_btn
        self.cursors["brush"] = "@brush.cur"

        self.eraser_img = PhotoImage(file="image\\eraser.gif")
        eraser_btn = Button(tools_btn_frame, image=self.eraser_img, command=lambda: self.select("eraser"))
        eraser_btn.grid(row=2, column=0)
        self.create_tooltip(eraser_btn, "eraser", "left")
        self.types["eraser"] = eraser_btn
        self.cursors["eraser"] = "@eraser.cur"

        self.text_img = PhotoImage(file="image\\text.gif")
        text_btn = Button(tools_btn_frame, image=self.text_img, command=lambda: self.select("text"))
        text_btn.grid(row=3, column=0)
        self.create_tooltip(text_btn, "textfield", "left")
        self.types["text"] = text_btn
        self.cursors["text"] = "tcross"

        self.line_img = PhotoImage(file="image\\line.gif")
        line_btn = Button(tools_btn_frame, image=self.line_img, command=lambda: self.select("line"))
        line_btn.grid(row=0, column=1)
        self.create_tooltip(line_btn, "line")
        self.types["line"] = line_btn
        self.cursors["line"] = "plus"

        self.rect_img = PhotoImage(file="image\\rect.gif")
        rect_btn = Button(tools_btn_frame, image=self.rect_img, command=lambda: self.select("rect"))
        rect_btn.grid(row=1, column=1)
        self.create_tooltip(rect_btn, "rectangle")
        self.types["rect"] = rect_btn
        self.cursors["rect"] = "tcross"

        self.oval_img = PhotoImage(file="image\\oval.gif")
        circle_btn = Button(tools_btn_frame, image=self.oval_img, command=lambda: self.select("circle"))
        circle_btn.grid(row=2, column=1)
        self.create_tooltip(circle_btn, "oval")
        self.types["circle"] = circle_btn
        self.cursors["circle"] = "tcross"

        self.spray_img = PhotoImage(file="image\\spray.gif")
        spray_btn = Button(tools_btn_frame, image=self.spray_img, command=lambda: self.select("spray"))
        spray_btn.grid(row=3, column=1)
        self.create_tooltip(spray_btn, "spray")
        self.types["spray"] = spray_btn
        self.cursors["spray"] = "@spray.cur"

        self.revert_img = PhotoImage(file="image\\revert.gif")
        self.revert_btn = Button(tools_btn_frame, image=self.revert_img, command=self.canvas.revert)
        self.revert_btn.grid(row=4, column=0, pady=6)
        self.create_tooltip(self.revert_btn, "revert")

        # colors setting
        color_frame = LabelFrame(self, text="Colors")
        color_frame.pack(side=TOP, fill=BOTH, pady=(6, 0), ipady=5)
        color_frame.columnconfigure(0, weight=1)
        color_frame.columnconfigure(1, weight=2)
        color_frame.columnconfigure(2, weight=2)

        color_label = Label(color_frame, text="Outline", anchor=CENTER)
        color_label.grid(row=0, column=0)

        color_btn_frame = Frame(color_frame, width=25, height=25)
        color_btn_frame.pack_propagate(False)
        color_btn_frame.grid(row=1, column=0)

        self.color_btn = Button(color_btn_frame, bg=settings["COLOR"], bd=2, relief=GROOVE,
                                activebackground=settings["COLOR"], command=self.select_color)
        self.color_btn.pack(side=TOP, fill=BOTH, expand=True)

        fill_color_label = Label(color_frame, text="Fill", anchor=CENTER)
        fill_color_label.grid(row=0, column=1)

        fill_color_btn_frame = Frame(color_frame, width=25, height=25)
        fill_color_btn_frame.pack_propagate(False)
        fill_color_btn_frame.grid(row=1, column=1)

        self.fill_color_btn = Button(fill_color_btn_frame, bg=settings["FILL_COLOR"], bd=2, relief=GROOVE,
                                     activebackground=settings["FILL_COLOR"], command=self.select_fill_color)
        self.fill_color_btn.pack(side=TOP, fill=BOTH, expand=True)

        font_color_lbl = Label(color_frame, text="Text")
        font_color_lbl.grid(row=0, column=2)

        font_color_frame = Frame(color_frame, width=25, height=25)
        font_color_frame.pack_propagate(False)
        font_color_frame.grid(row=1, column=2)

        self.text_color_btn = Button(font_color_frame, bg=settings["TEXT_COLOR"], bd=2, relief=GROOVE,
                                     activebackground=settings["TEXT_COLOR"], command=self.select_text_color)
        self.text_color_btn.pack(side=TOP, fill=BOTH, expand=True)

        self.transparency_var = IntVar()
        self.transparency_var.set(1)
        self.transparency = Checkbutton(color_frame, text="Transparent Fill", variable=self.transparency_var,
                                        command=self.set_transparency)
        self.transparency.grid(row=2, column=0, columnspan=3, pady=(5, 0))

        self.clear_img = PhotoImage(file="image\\cross.gif")
        self.clear_btn = Button(self, image=self.clear_img, cursor="hand2", command=self.ask_clear)
        self.clear_btn.pack(side=BOTTOM, pady=10)
        self.create_tooltip(self.clear_btn, "clear all")

        self.position = Label(self, text="(0, 0)", font=("Arial", 8), compound=RIGHT)
        self.position.pack(side=BOTTOM)

        # settings for specific tool
        self.setting_frame = SettingFrame(self)
        self.setting_frame.pack(side=TOP, fill=BOTH, expand=True, ipady=6, pady=6)

    def printMousePosition(self, event):
        self.position["text"] = "(%d, %d)" % (event.x, event.y)
        if event.state == SHIFT or event.state == 9:
            self.position["image"] = self.shift_image
        else:
            self.position["image"] = ""

        # send current mouse position to client or server
        socket = settings["SOCKET"]
        if socket and self.canvas.drawer:
            try:
                message = {"type": "mouse", "data": (event.x, event.y)}
                socket.send(str(message))
            except Exception:
                pass

    def select(self, name):
        # deselect all the buttons and select target button
        for key in self.types:
            self.types[key]["relief"] = RAISED

        self.canvas.type = name
        self.types[name]["relief"] = SUNKEN
        self.setting_frame.show(name)
        self.canvas["cursor"] = self.cursors[name]

    def deselect_all(self):
        for key in self.types:
            self.types[key]["relief"] = RAISED

        self.canvas.type = ""
        self.canvas["cursor"] = "@main.cur"

    def select_color(self):
        selected_color = tkColorChooser.askcolor(settings["COLOR"], parent=self, title="Select Outline Color")
        if selected_color[1]:
            settings["COLOR"] = selected_color[1]
            self.color_btn["bg"] = settings["COLOR"]

    def select_fill_color(self):
        selected_color = tkColorChooser.askcolor(settings["FILL_COLOR"], parent=self, title="Select Fill Color")
        if selected_color[1]:
            settings["FILL_COLOR"] = selected_color[1]
            self.fill_color_btn["bg"] = settings["FILL_COLOR"]

    def select_text_color(self):
        selected_color = tkColorChooser.askcolor(settings["TEXT_COLOR"], parent=self.parent,
                                                 title="Select Outline Color")
        if selected_color[1]:
            settings["TEXT_COLOR"] = selected_color[1]
            self.text_color_btn["bg"] = settings["TEXT_COLOR"]

    def set_transparency(self):
        settings["TRANSPARENT"] = bool(self.transparency_var.get())

    def create_tooltip(self, widget, text, direction="right"):
        Tooltip(widget, text, direction)

    def ask_clear(self):
        clear = tkMessageBox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?", default="no")
        if clear:
            # clear the canvas
            self.canvas.clear()

            # send clear command to the server
            socket = settings["SOCKET"]
            if socket and self.canvas.drawer:
                try:
                    message = {"type": "clear", "data": None}
                    socket.send(str(message))
                except socket.error:
                    pass

    def save(self):
        directory = tkFileDialog.asksaveasfilename(
            filetypes=[("JPG", "*.jpg"), ("Bitmap", "*.bmp"), ("PNG", "*.png"), ("GIF", "*.gif")],
            defaultextension=".jpg")
        if directory:
            x1 = self.parent.winfo_rootx() + self.canvas.winfo_x()
            y1 = self.parent.winfo_rooty() + self.canvas.winfo_y()
            x2 = x1 + self.canvas.winfo_width()
            y2 = y1 + self.canvas.winfo_height()
            ImageGrab.grab().crop((x1, y1, x2, y2)).save(directory)

    def set_state(self, status):
        if status:
            for key in self.types:
                self.types[key]["state"] = NORMAL
            self.clear_btn["state"] = NORMAL
            self.revert_btn["state"] = NORMAL
        else:
            for key in self.types:
                self.types[key]["state"] = DISABLED
            self.clear_btn["state"] = DISABLED
            self.revert_btn["state"] = DISABLED


# frame for containing tool settings
class SettingFrame(LabelFrame):
    def __init__(self, parent):
        LabelFrame.__init__(self, parent, text="Settings")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.frames = {}

        pencil_frame = self.PencilFrame(self)
        pencil_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["pencil"] = pencil_frame

        brush_frame = self.BrushFrame(self)
        brush_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["brush"] = brush_frame

        eraser_frame = self.EraserFrame(self)
        eraser_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["eraser"] = eraser_frame

        line_frame = self.LineFrame(self)
        line_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["line"] = line_frame

        rect_frame = self.RectFrame(self)
        rect_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["rect"] = rect_frame

        circle_frame = self.CircleFrame(self)
        circle_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["circle"] = circle_frame

        text_frame = self.TextFrame(self)
        text_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["text"] = text_frame

        spray_frame = self.SprayFrame(self)
        spray_frame.grid(row=0, column=0, sticky=NSEW)
        self.frames["spray"] = spray_frame

    def show(self, name):
        self.frames[name].lift()

    class PencilFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Width")
            label1.pack(side=TOP, pady=(6, 0))

            self.pencil_width = Scale(self, from_=1.0, to=5.0, resolution=0.1, sliderlength=25, orient=HORIZONTAL,
                                      command=self.set_pencil_width)
            self.pencil_width.set(settings["PENCIL_WIDTH"])
            self.pencil_width.pack(side=TOP)

        def set_pencil_width(self, event):
            settings["PENCIL_WIDTH"] = self.pencil_width.get()

    class BrushFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Width")
            label1.pack(side=TOP, pady=(6, 0))

            self.brush_width = Scale(self, from_=3.0, to=50.0, resolution=0.1, sliderlength=25, orient=HORIZONTAL,
                                     command=self.set_brush_width)
            self.brush_width.set(settings["BRUSH_WIDTH"])
            self.brush_width.pack(side=TOP)

            label2 = Label(self, text="Shape")
            label2.pack(side=TOP, pady=(6, 0))

            shape_frame = Frame(self)
            shape_frame.pack(side=TOP)

            shape_circle = Label(shape_frame, text=u"\u26ab", font=("times", 10), anchor=W)
            shape_circle.grid(row=0, column=1)

            shape_rect = Label(shape_frame, text=u"\u25a0", font=("times", 15), anchor=W)
            shape_rect.grid(row=1, column=1)

            self.mode = StringVar()
            self.mode.set("circle")

            mode1 = Radiobutton(shape_frame, variable=self.mode, value="circle", command=self.set_brush_mode)
            mode2 = Radiobutton(shape_frame, variable=self.mode, value="square", command=self.set_brush_mode)
            mode1.grid(row=0, column=0)
            mode2.grid(row=1, column=0)

        def set_brush_width(self, event):
            settings["BRUSH_WIDTH"] = self.brush_width.get()

        def set_brush_mode(self):
            settings["BRUSH_MODE"] = self.mode.get()

    class EraserFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Width")
            label1.pack(side=TOP, pady=(6, 0))

            self.eraser_width = Scale(self, from_=3.0, to=50.0, resolution=0.1, sliderlength=25, orient=HORIZONTAL,
                                      command=self.set_eraser_width)
            self.eraser_width.set(settings["ERASER_WIDTH"])
            self.eraser_width.pack(side=TOP)

            label2 = Label(self, text="Shape")
            label2.pack(side=TOP, pady=(6, 0))

            shape_frame = Frame(self)
            shape_frame.pack(side=TOP)

            shape_circle = Label(shape_frame, text=u"\u26ab", font=("times", 10), anchor=W)
            shape_circle.grid(row=0, column=1)

            shape_rect = Label(shape_frame, text=u"\u25a0", font=("times", 15), anchor=W)
            shape_rect.grid(row=1, column=1)

            self.mode = StringVar()
            self.mode.set("circle")

            mode1 = Radiobutton(shape_frame, variable=self.mode, value="circle", command=self.set_eraser_mode)
            mode2 = Radiobutton(shape_frame, variable=self.mode, value="square", command=self.set_eraser_mode)
            mode1.grid(row=0, column=0)
            mode2.grid(row=1, column=0)

        def set_eraser_width(self, event):
            settings["ERASER_WIDTH"] = self.eraser_width.get()

        def set_eraser_mode(self):
            settings["ERASER_MODE"] = self.mode.get()

    class LineFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Width")
            label1.pack(side=TOP, pady=(6, 0))

            self.line_width = Scale(self, from_=1.0, to=10.0, resolution=0.1, sliderlength=25, orient=HORIZONTAL,
                                    command=self.set_line_width)
            self.line_width.set(settings["LINE_WIDTH"])
            self.line_width.pack(side=TOP)

            label2 = Label(self, text="Dash Width")
            label2.pack(side=TOP, pady=(6, 0))

            self.dash_width = Scale(self, from_=1, to=5, resolution=1, sliderlength=25, orient=HORIZONTAL,
                                    command=self.set_dash_width)
            self.dash_width.set(settings["DASH_WIDTH"])
            self.dash_width.pack(side=TOP)

            self.dash_var = IntVar()
            self.dash_var.set(settings["DASH"])
            dash_box = Checkbutton(self, text="Dash Line", variable=self.dash_var, command=self.set_dash)
            dash_box.pack(side=TOP, pady=3)

        def set_line_width(self, event):
            settings["LINE_WIDTH"] = self.line_width.get()

        def set_dash(self, event=None):
            dash = self.dash_var.get()
            if dash:
                settings["DASH"] = True
            else:
                settings["DASH"] = False

        def set_dash_width(self, event=None):
            settings["DASH_WIDTH"] = self.dash_width.get()

    class RectFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Width")
            label1.pack(side=TOP, pady=(6, 0))

            self.rect_width = Scale(self, from_=1.0, to=5.0, resolution=0.1, sliderlength=25, orient=HORIZONTAL,
                                    command=self.set_rect_width)
            self.rect_width.set(settings["RECT_WIDTH"])
            self.rect_width.pack(side=TOP)

        def set_rect_width(self, event):
            settings["RECT_WIDTH"] = self.rect_width.get()

    class CircleFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Width")
            label1.pack(side=TOP, pady=(6, 0))

            self.circle_width = Scale(self, from_=1.0, to=5.0, resolution=0.1, sliderlength=25, orient=HORIZONTAL,
                                      command=self.set_circle_width)
            self.circle_width.set(settings["CIRCLE_WIDTH"])
            self.circle_width.pack(side=TOP)

        def set_circle_width(self, event):
            settings["CIRCLE_WIDTH"] = self.circle_width.get()

    class TextFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)
            self.parent = parent

            # font family setting
            font_family_frame = Frame(self)
            font_family_frame.pack(side=TOP, pady=(3, 0), padx=5)

            self.font_families = sorted(tkFont.families())

            font_family_label = Label(font_family_frame, text="Font Family")
            font_family_label.pack(side=TOP)

            self.font_family = Combobox(font_family_frame, height=10, values=self.font_families, state="readonly")
            self.font_family.set("Times New Roman")
            self.font_family.pack(side=TOP)
            self.font_family.bind("<<ComboboxSelected>>", self.set_font_family)
            self.font_family.bind("<FocusOut>", self.set_font_family)
            self.font_family.bind("<Key>", self.validate_font)

            # font size setting
            font_size_frame = Frame(self)
            font_size_frame.pack(side=TOP, pady=(6, 0), padx=5)

            font_size_label = Label(font_size_frame, text="Font Size")
            font_size_label.pack(side=TOP)

            self.font_size_var = IntVar()
            self.font_size_var.set(10)
            self.font_size = Spinbox(font_size_frame, textvariable=self.font_size_var, font=("arial", 10), from_=0,
                                     to=100, command=self.set_font_size)
            self.font_size.pack(side=TOP)
            self.font_size.bind("<FocusOut>", self.set_font_size)

            # font decoration setting
            decoration_frame = Frame(self)
            decoration_frame.pack(side=TOP, pady=(10, 0))

            self.weight_btn = Button(decoration_frame, text="T", font=("times", 10, "bold"),
                                     command=lambda: self.set_decoration("weight"))
            self.weight_btn.grid(row=0, column=0)

            self.slant_btn = Button(decoration_frame, text="T", font=("times", 10, "italic"),
                                    command=lambda: self.set_decoration("slant"))
            self.slant_btn.grid(row=0, column=1)

            self.underline_btn = Button(decoration_frame, text="T", font=("times", 10, "underline"),
                                        command=lambda: self.set_decoration("underline"))
            self.underline_btn.grid(row=0, column=2)

            self.overstrike_btn = Button(decoration_frame, text="T", font=("times", 10, "overstrike"),
                                         command=lambda: self.set_decoration("overstrike"))
            self.overstrike_btn.grid(row=0, column=3)

        def set_font_family(self, event):
            settings["FONT_FAMILY"] = self.font_family.get()

        def validate_font(self, event):
            if event.char:
                ind = 0
                for font in self.font_families:
                    if font.lower().startswith(event.char):
                        self.font_family.current(ind)
                    else:
                        ind += 1

        def set_font_size(self, event=None):
            try:
                font_size = int(self.font_size.get())
            except ValueError:
                return
            if 0 < font_size < 100:
                settings["FONT_SIZE"] = font_size

        def set_decoration(self, decoration_type):
            if decoration_type == "weight":
                if settings["BOLD"]:
                    settings["BOLD"] = False
                    self.weight_btn["relief"] = RAISED
                else:
                    settings["BOLD"] = True
                    self.weight_btn["relief"] = SUNKEN
            elif decoration_type == "slant":
                if settings["SLANT"]:
                    settings["SLANT"] = False
                    self.slant_btn["relief"] = RAISED
                else:
                    settings["SLANT"] = True
                    self.slant_btn["relief"] = SUNKEN
            elif decoration_type == "underline":
                if settings["UNDERLINE"]:
                    settings["UNDERLINE"] = False
                    self.underline_btn["relief"] = RAISED
                else:
                    settings["UNDERLINE"] = True
                    self.underline_btn["relief"] = SUNKEN
            elif decoration_type == "overstrike":
                if settings["OVERSTRIKE"]:
                    settings["OVERSTRIKE"] = False
                    self.overstrike_btn["relief"] = RAISED
                else:
                    settings["OVERSTRIKE"] = True
                    self.overstrike_btn["relief"] = SUNKEN

    class SprayFrame(Frame):
        def __init__(self, parent):
            Frame.__init__(self, parent)

            label1 = Label(self, text="Size")
            label1.pack(side=TOP, pady=(6, 0))

            self.spray_size = Scale(self, from_=1, to=10, resolution=1, sliderlength=25, orient=HORIZONTAL,
                                    command=self.set_spray_size)
            self.spray_size.set(settings["SPRAY_SIZE"])
            self.spray_size.pack(side=TOP)

        def set_spray_size(self, event):
            settings["SPRAY_SIZE"] = self.spray_size.get()
