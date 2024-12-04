import tkinter as tk

import moderngl
import numpy as np

from tkinter_framebuffer import FramebufferImage
from renderer_example import HelloWorld2D, PanTool

ctx = moderngl.create_standalone_context()

canvas = HelloWorld2D(ctx)
pan_tool = PanTool()


def vertices():
    x = np.linspace(-1.0, 1.0, 50)
    y = np.random.rand(50) - 0.5
    r = np.ones(50)
    g = np.zeros(50)
    b = np.zeros(50)
    a = np.ones(50)
    return np.dstack([x, y, r, g, b, a])


verts = vertices()


def update(evt):
    if evt.type == tk.EventType.ButtonPress:
        pan_tool.start_drag(evt.x / size[0], evt.y / size[1])
    if evt.type == tk.EventType.Motion:
        pan_tool.dragging(evt.x / size[0], evt.y / size[1])
    if evt.type == tk.EventType.ButtonRelease:
        pan_tool.stop_drag(evt.x / size[0], evt.y / size[1])
    canvas.pan(pan_tool.value)

    with tkfbo:
        ctx.clear()
        canvas.plot(verts)

def middle_click(evt):
    print("MIDDLE CLICK")

size = (512, 512)

root = tk.Tk()
tkfbo = FramebufferImage(root, ctx, size)

# Create a frame
root.columnconfigure((0,1), weight=1,uniform="a")

frame = tk.Frame(root, bg="gray", highlightbackground="black", highlightthickness=1)
frame.grid(row = 0, column = 1,sticky="nsew",pady=10,padx=10)
frameleft = tk.Frame(root, bg="gray", highlightbackground="black", highlightthickness=1)
frameleft.grid(row = 0, column = 0,sticky="nsew",pady=10,padx=10)


lbl = tk.Label(frame, image=tkfbo)
lbl.bind("<ButtonPress-1>", update)
lbl.bind("<ButtonRelease-1>", update)
lbl.bind('<Motion>', update)
lbl.bind("<ButtonPress-2>", middle_click)
lbl.pack()

# btn = tk.Button(root, text='Hello', command=update)
# btn.pack()

root.mainloop()