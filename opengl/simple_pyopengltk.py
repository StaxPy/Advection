
import time
import tkinter
from OpenGL import GL
from pyopengltk import OpenGLFrame
import os
import pygame

class OpenGLFrameTk(OpenGLFrame):

    def initgl(self):
        """Initalize gl states when the frame is created"""
        GL.glViewport(0, 0, self.width, self.height)
        GL.glClearColor(0.0, 1.0, 0.0, 0.0)    
        self.start = time.time()
        self.nframes = 0

    def redraw(self):
        """Render a single frame"""
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        tm = time.time() - self.start
        self.nframes += 1
        print("fps",self.nframes / tm, end="\r" )

if __name__ == '__main__':

    pygame.init() # Initialize pygame first (solves the delay after the tkinter opening ?)
    # Create a tkinter window
    root = tkinter.Tk()
    app_width, app_height = 1280, 720

    # Create an OpenGL frame
    renderer_frame = OpenGLFrameTk(root, width=1280, height=720)
    renderer_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # Set up Pygame to use the frame
    os.environ['SDL_WINDOWID'] = str(renderer_frame.winfo_id()) # Refers the same window
    # os.environ['SDL_VIDEODRIVER'] = 'windib' #? Necessary ?
    screen = pygame.display.set_mode((app_width, app_height))


    renderer_frame.animate = 1

    pygame.display.flip()

    def loop():


        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                print(pygame.mouse.get_pos())
        
        root.update_idletasks()
        root.after(15, loop)
    
    loop()
    renderer_frame.after(100, renderer_frame.printContext)
    renderer_frame.mainloop()


    # # Main loop
    # while True:
        
    #     pygame.display.flip()
    #     pygame.time.delay(1000 // 60)