from moderngl_window.conf import settings
import moderngl_window

settings.WINDOW['class'] = 'moderngl_window.context.tk.Window'


window = moderngl_window.create_window_from_settings()

while not window.is_closing:
    window.clear()
    # Render your OpenGL content here
    window.swap_buffers()

print(window.__dict__)