import tkinter as tk
import customtkinter
import shared.variables as sv


def initialize_interface():
    global TkApp, config_frame, preview_frame, export_frame
    global hover_color, special_color, dark_gray, medium_gray, light_gray, white, black

    TkApp = customtkinter.CTk()


    hover_color = "#ffffff"
    special_color = "#be5dff"

    dark_gray = "#292929"
    medium_gray = "#6e6e6e"
    light_gray = "#adadad"
    white = "#ffffff"
    almost_black = sv.almost_black
    black = "#000000"



    TkApp.minsize(1280, 720)  # Set minimum size to 800x600
    TkApp.geometry(f"{sv.WIDTH}x{sv.HEIGHT}")
    TkApp.configure(background=black)
    TkApp.title("Animation-to-Particles Converter")

    config_frame_border = tk.Frame(TkApp,background=almost_black)
    config_frame = tk.Frame(config_frame_border,background=almost_black)
    preview_frame = tk.Frame(TkApp, background=dark_gray)
    export_frame_border = tk.Frame(TkApp, background=almost_black)
    export_frame = customtkinter.CTkFrame(export_frame_border, fg_color=dark_gray,border_color=dark_gray,border_width=2)


    TkApp.columnconfigure((0,1), weight=1,uniform="a")
    TkApp.rowconfigure((0), weight=4,uniform="a")
    TkApp.rowconfigure((1), weight=1,uniform="a")
    config_frame_border.rowconfigure((0), weight=1,uniform="a")
    config_frame_border.columnconfigure((0), weight=1,uniform="a")
    export_frame_border.rowconfigure((0), weight=1,uniform="a")
    export_frame_border.columnconfigure((0), weight=1,uniform="a")


    
    config_frame_border.grid(row = 0, column = 0,sticky="nsew",rowspan=2)
    config_frame.grid(row = 0, column = 0,sticky="nsew",pady=10,padx=10)
    preview_frame.grid(row=0, column=1, sticky="nsew")
    export_frame_border.grid(row = 1, column = 1,sticky="nsew")
    export_frame.grid(row = 0, column = 0,sticky="nsew",pady=15,padx=10)



def run_main_loop():
    TkApp.mainloop()