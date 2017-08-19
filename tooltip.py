from tkinter import Toplevel, Label


class Tooltip(object):
    def __init__(self, widget, text, direction="right"):
        self.widget = widget
        self.text = text
        self.direction = direction
        self.root = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event):
        if self.direction == "right":
            x, y, cx, cy = self.widget.bbox()
            x += self.widget.winfo_rootx() + self.widget.winfo_width()
            y += self.widget.winfo_rooty() + int((self.widget.winfo_height() - 20) / 2)
        else:
            length = len(self.text)
            x, y, cx, cy = self.widget.bbox()
            x += self.widget.winfo_rootx() - 7 * length - 8
            y += self.widget.winfo_rooty() + int((self.widget.winfo_height() - 20) / 2)

        # if the tooltip cannot be displayed (partly outside screen),
        #   then temporarily change the direction to be left
        if x < 0 and self.direction == "left":
            self.direction = "right"
            self.enter(event)
            self.direction = "left"
            return

        self.root = Toplevel(self.widget)
        self.root.wm_overrideredirect(True)
        self.root.wm_geometry("+%d+%d" % (x, y))

        label = Label(self.root, text=self.text, justify="left", bg="white", relief="solid", bd=1, font=("Courier", 8))
        label.pack(ipadx=2)

    def leave(self, event):
        if self.root:
            self.root.destroy()
