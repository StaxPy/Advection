import tkinter as tk
from pyopengltk import OpenGLFrame
import moderngl
import numpy as np  # For properly formatted vertex data


class ModernGLTkinterApp(OpenGLFrame):
    def initgl(self):
        """Initialize ModernGL context and resources."""
        self.ctx = moderngl.create_context()

        # Vertex and fragment shaders
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
                }
            """,
        )

        # Properly define the triangle vertices as a NumPy array
        vertices = np.array(
            [
                -0.5, -0.5,  # Bottom-left
                0.5, -0.5,   # Bottom-right
                0.0,  0.5    # Top-center
            ],
            dtype='f4'  # Float32 data
        )

        # Create buffer and vertex array object
        self.vbo = self.ctx.buffer(vertices.tobytes())  # Upload vertex data
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, "2f", "in_vert")],
        )
    def tkResize(self, evt):
        self.width, self.height = evt.width, evt.height
        print(self.width, self.height)


    def redraw(self):
        """Render the scene."""
        self.ctx.clear(0.2, 0.5, 0.3)  # Clear screen with a teal color
        self.vao.render(moderngl.TRIANGLES)  # Render the triangle


# Create the tkinter application
root = tk.Tk()
root.title("ModernGL with pyopengltk")

# Create the OpenGL frame
frame = ModernGLTkinterApp(root, width=800, height=600)
root.columnconfigure((0, 1), weight=1, uniform='a')
root.rowconfigure((0), weight=1, uniform='a')
frame.grid(row=0, column=0, sticky="nsew")
frame2 = tk.Frame(root)
frame2.grid(row=0, column=1, sticky="nsew")

# Start the tkinter main loop
frame.mainloop()
