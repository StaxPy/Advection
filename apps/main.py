import pygame
import frontend.preview as preview
import frontend.interface as interface
import shared.variables as sv





def loop():

    # interface.TkApp.columnconfigure(1, minsize=interface.TkApp.winfo_width()/2)

    preview.pygame_loop()

    interface.TkApp.update_idletasks()
    interface.TkApp.after(10, loop)

# def configure_preview_column():
#     interface.TkApp.columnconfigure(1, minsize=interface.TkApp.winfo_width()/2)

if __name__ == "__main__":
    # mp_queue = mp.Queue()
    interface.initialize_interface()
    interface.create_interface()
    preview.initialize(sv.WIDTH, sv.HEIGHT, interface.preview_frame)
    interface.random_cube_refresh_preview()
    loop()
    interface.run_main_loop()

















###

