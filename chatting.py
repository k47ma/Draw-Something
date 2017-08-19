from tkinter import *
from ThreadSafeText import *

# module for chatting frame


class ChattingFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.textarea = ThreadSafeText(self, width=30)
        self.textarea.pack(side=TOP, fill=Y, expand=True)

        self.entry = Entry(self, width=30)
        self.entry.pack(side=BOTTOM)
