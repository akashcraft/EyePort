import tkinter as tk
import time
from PIL import Image, ImageTk
from itertools import count, cycle
class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, input):
        if isinstance(input, str):
            self.im = Image.open(input)
        frames = []
        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(self.im.copy()))
                self.im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)
        self.delay = 15
        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()
    def unload(self):
        self.config(image=None)
        self.frames = None
        self.im.close()
    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

def kill():
    lbl.unload()
    root.quit()

if __name__=="__main__": #demo
    root = tk.Tk()
    lbl = ImageLabel(root)
    lbl.pack()
    lbl.load('.\Resources\Loading1.gif')
    lbl.after(10000,kill)
    root.geometry("400x600")
    root.mainloop()
