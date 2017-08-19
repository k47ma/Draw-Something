from tkinter import *
from ThreadSafeText import *
from config import settings

# module for chatting frame


class ChattingFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.textarea = ThreadSafeText(self, width=30, wrap=WORD)
        self.textarea.pack(side=TOP, fill=BOTH, expand=True, padx=6, pady=3)
        settings["TEXTAREA"] = self.textarea

        entry_frame = Frame(self)
        entry_frame.pack(side=BOTTOM, fill=X)

        self.entry = Entry(entry_frame, width=30)
        self.entry.pack(side=LEFT, padx=(6, 3))
        self.entry.bind("<Return>", self.send_message)

        send_btn = Button(entry_frame, text="send", command=self.send_message)
        send_btn.pack(side=RIGHT, padx=(0, 6))

    def send_message(self, event=None):
        message = self.entry.get()
        if message:
            s = settings["SOCKET"]
            s.send(str({"type": "message", "data": message}))

            self.textarea.insert(END, "Me: " + message + "\n")
            self.entry.delete(0, END)
