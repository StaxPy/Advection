
import time
import tkinter
from OpenGL.GL import *
from pyopengltk import OpenGLFrame
import os
import pygame

class OpenGLFrameTk(OpenGLFrame):
    def __init__(self, master,hwnd, **kwargs):
        super().__init__(master, **kwargs)
        self.hwnd = hwnd

    def initgl(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.0, 1.0, 0.0, 0.0)
        glEnable(GL_BLEND) # Enable alpha blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # Set the blend function
        glEnable(GL_DEPTH_TEST)

        self.start = time.time()
        self.nframes = 0

    def redraw(self):
        glClear(GL_COLOR_BUFFER_BIT)
        pass
        # Your OpenGL drawing code here

if __name__ == '__main__':

    pygame.init() # Initialize pygame first (solves the delay after the tkinter opening ?)



    # Set OpenGL version to 3.3 core
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

    pygame.display.set_mode((512, 512), pygame.OPENGL | pygame.DOUBLEBUF)

    # Get the window handle for OpenGL
    hwnd = pygame.display.get_wm_info()["window"]

    # Create a tkinter window
    root = tkinter.Tk()
    app_width, app_height = 1280, 720

    # Create an OpenGL frame
    demo_frame = tkinter.Frame(root, width=1280, height=720)
    demo_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES,side=tkinter.LEFT)
    renderer_frame = OpenGLFrameTk(root, width=1280, height=720, hwnd=hwnd)
    renderer_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES,side=tkinter.RIGHT)

    # Set up Pygame to use the frame
    os.environ['SDL_WINDOWID'] = str(renderer_frame.winfo_id()) # Refers the same window
    screen = pygame.display.set_mode((app_width, app_height))


    renderer_frame.animate = 1

    pygame.display.flip()

    def loop():


        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                print(pygame.mouse.get_pos())
                # screen.fill(color=pygame.Color('red'))
        
        root.update_idletasks()
        root.after(15, loop)
    
    loop()
    renderer_frame.after(100, renderer_frame.printContext)
    renderer_frame.mainloop()

