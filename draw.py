from tkinter import *
from canvas import *
from controller import *
from my_client import *
from chatting import *
import tkMessageBox

# module for draw something game interface


class Game(Tk):
    def __init__(self):
        Tk.__init__(self)

        self.iconbitmap(r'image\paint.ico')
        self.wm_title("Draw Something")
        self.geometry("300x150+0+0")
        self.minsize(300, 150)
        #self.protocol("WM_DELETE_WINDOW", self.ask_quit)
        self["cursor"] = "@main.cur"

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.start_frame = Frame(self)
        self.start_frame.grid(row=0, column=0, sticky=NSEW)

        self.setting_frame = ClientSettingFrame(self)
        self.setting_frame.grid(row=0, column=0, sticky=NSEW)

        self.game_frame = Frame(self)
        self.game_frame.grid(row=0, column=0, sticky=NSEW)

        self.chatting = ChattingFrame(self.game_frame)
        self.chatting.pack(side=RIGHT, fill=Y)

        self.canvas = PaintCanvas(self.game_frame)
        self.canvas.pack(side=RIGHT, fill=BOTH, expand=True)

        self.controller = ControlFrame(self.game_frame, self.canvas)
        self.controller.pack(side=LEFT, fill=Y)

        start_btn = Button(self.start_frame, text="Start", command=self.connect)
        start_btn.pack()

        quit_btn = Button(self.start_frame, text="Quit", command=self.ask_quit)
        start_btn.pack()

        start_btn.place(relx=0.35, rely=0.4, width=50, height=30)
        quit_btn.place(relx=0.55, rely=0.4, width=50, height=30)

        self.start_frame.lift()

    def ask_quit(self):
        if tkMessageBox.askyesnocancel("Quit", "Are you sure you want to quit?", parent=self):
            self.quit()

    def connect(self):
        self.setting_frame.lift()


game = Game()
game.mainloop()
