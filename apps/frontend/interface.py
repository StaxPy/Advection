import tkinter as tk
import customtkinter
import CTkColorPicker
from PIL import Image
import os, random
import threading
import backend.file_dialog as fd
import backend.converter as converter
import frontend.preview as preview
from shared.variables import *
import multiprocessing as mp



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

    # config_frame.pack(side=tk.LEFT,fill=tk.NONE,expand=False)
    # TkApp.grid_columnconfigure(0, weight=1)
    # TkApp.grid_columnconfigure(1, weight=1)
    # TkApp.grid_rowconfigure(0, weight=1)
    # config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # pygame_frame = tk.Frame(TkApp, width=1200, height=500, background="#181818")
    # pygame_frame.pack(fill=tk.NONE, expand=True, side=tk.RIGHT)

    # canvas = tk.Canvas(TkApp, width=1200, height=600, bg="#ff0000")
    # canvas.grid(row=0, column=1, sticky="nsew")

    TkApp.columnconfigure((0,1), weight=1,uniform="a")
    TkApp.rowconfigure((0), weight=4,uniform="a")
    TkApp.rowconfigure((1), weight=1,uniform="a")
    config_frame_border.rowconfigure((0), weight=1,uniform="a")
    config_frame_border.columnconfigure((0), weight=1,uniform="a")
    export_frame_border.rowconfigure((0), weight=1,uniform="a")
    export_frame_border.columnconfigure((0), weight=1,uniform="a")

    # # canvas.pack(side=tk.RIGHT,fill=tk.NONE,expand=False)

    # pygame_frame = tk.Frame(canvas, background="#ff0000")
    # pygame_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    
    config_frame_border.grid(row = 0, column = 0,sticky="nsew",rowspan=2)
    config_frame.grid(row = 0, column = 0,sticky="nsew",pady=10,padx=10)
    preview_frame.grid(row=0, column=1, sticky="nsew")
    export_frame_border.grid(row = 1, column = 1,sticky="nsew")
    export_frame.grid(row = 0, column = 0,sticky="nsew",pady=15,padx=10)

    # preview_frame.bind("<Button-2>", pan_cursor)
    # preview_frame.bind("<ButtonRelease-2>", reset_cursor)
    # preview_frame.bind("<Button-3>", rotate_cursor)
    # preview_frame.bind("<ButtonRelease-3>", reset_cursor)


    



    

    # pygame_frame.grid(row = 0, column = 1,sticky="nsew")
    # pygame_frame.config(width=800, height=300)  # Adjust these values as needed
    # pygame_frame.grid_propagate(False)
    # TkApp.bind('<Configure>', on_resize)
    # TkApp.grid_columnconfigure(1, weight=1,minsize=sv.WIDTH/2)

def on_pan():
    print("Pan")

def pan_cursor(event):
    preview_frame.config(cursor="fleur")

def rotate_cursor(event):
    preview_frame.config(cursor="exchange")

def reset_cursor(event):
    preview_frame.config(cursor="arrow")





def on_resize(event):
    print("Resizing")
    sv.pygame_width, sv.pygame_height = preview.display.get_size()
    TkApp.columnconfigure(1, minsize=TkApp.winfo_width()/2)


    # pygame_frame.pack(side = tk.RIGHT,fill=tk.BOTH, expand=True,minsize=(0,0))

def run_main_loop():
    # tk.mainloop()
    TkApp.mainloop()

def create_interface():
    global input_frame, input_path_entry, output_path_entry, choose_file_button, sequence_checkbox, sequence_detected_label, sequence_start_Entry, sequence_end_Entry, preview_framenumber_slider, preview_framenumber_label
    global disabled_entry_style, normal_entry_style, disabled_slider_style, normal_slider_style, preview_framenumber, InterFont

    def focus_on_click(event):
        event.widget.focus_set() # Focus on selected element

    def verify_widget(event):
        print("Verifying",event.widget)
        TkApp.focus_set() # Unfocus
    
    TkApp.bind_all('<Button-1>', focus_on_click)

    InterFont = customtkinter.CTkFont(family="Inter", size=12)

    # Debouncer that wraps the original refresh function
    slider_debouncer = SliderDebouncer(TkApp, refresh_preview)

    path_style = {"state":"disabled","fg_color":black,"placeholder_text_color":medium_gray,"text_color":white,"border_color":dark_gray}
    disabled_entry_style = {"state":"disabled","fg_color":dark_gray,"placeholder_text_color":medium_gray,"text_color":medium_gray,"border_color":medium_gray}
    normal_entry_style = {"state":"normal","fg_color":black,"placeholder_text_color":white,"border_color":dark_gray,"text_color":white}

    checkbox_style = {"checkbox_width":20,"checkbox_height":20,"text_color":white,"border_color":white,"border_width":1,"hover_color":hover_color,"fg_color":special_color}

    normal_menu_style = {"fg_color":black,"button_color":medium_gray,"dropdown_fg_color":dark_gray,"dropdown_text_color":white,"button_hover_color":hover_color} 


    """ 1 CONFIG """
    # ELEMENT PARAMETERS
    input_frame = customtkinter.CTkFrame(config_frame, fg_color=dark_gray,border_color=dark_gray,border_width=2)
    sequence_frame = customtkinter.CTkFrame(config_frame, fg_color=dark_gray,border_color=dark_gray,border_width=2)
    alignment_frame = customtkinter.CTkFrame(config_frame, fg_color=dark_gray,border_color=dark_gray,border_width=2)
    model_frame = customtkinter.CTkFrame(config_frame, fg_color=dark_gray,border_color=dark_gray,border_width=2)
    image_frame = customtkinter.CTkFrame(config_frame, fg_color=dark_gray,border_color=dark_gray,border_width=2)
    particle_frame = customtkinter.CTkFrame(config_frame, fg_color=dark_gray,border_color=dark_gray,border_width=2)

    # GRID PARAMETERS
    config_frame.columnconfigure([0], weight=1,uniform="a")
    config_frame.rowconfigure([0,1,2,3,4,5],weight=1)

    # PLACEMENT PARAMETERS
    input_frame.grid(row = 0, column = 0,sticky="nsew",pady=5,padx=10)
    sequence_frame.grid(row = 1, column = 0,sticky="nsew",pady=5,padx=10)
    alignment_frame.grid(row = 2, column = 0,sticky="nsew",pady=5,padx=10)
    model_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
    image_frame.grid(row = 4, column = 0,sticky="nsew",pady=5,padx=10)
    particle_frame.grid(row = 5, column = 0,sticky="nsew",pady=5,padx=10)


    


    """ 2 INPUT FILE """
    # ELEMENT PARAMETERS
    file_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/file_lines_icon.png")),size=(20,20))
    folder_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/folder_open_document_icon.png")),size=(20,20))
    export_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/hand_point_right_icon.png")),size=(20,20))
    input_label = customtkinter.CTkLabel(input_frame, text = 'Input File',text_color=white,font=InterFont,height=15)
    input_path_entry = customtkinter.CTkEntry(input_frame, **path_style,textvariable=customtkinter.StringVar(value="OBJ file or PNG/JPG image"),font=InterFont)
    choose_file_button = customtkinter.CTkButton(input_frame, image = file_button_image, text=None, width=20,height=20,command = find_input_dialog,fg_color=special_color,hover_color=hover_color,text_color=white,font=InterFont)

    # GRID PARAMETERS
    input_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    input_frame.grid_rowconfigure([0,1], weight=1,uniform="a")
    
    # PLACEMENT PARAMETERS
    input_label.grid(column=0, row=0, padx=15, pady=5,sticky="ws",)
    input_path_entry.grid(column=0, row=1, padx=10, pady=0,sticky="wen",columnspan=3)
    choose_file_button.grid(column=3, row=1, padx=0, pady=0,sticky="nw")

    """ 2 SEQUENCE """
    # ELEMENT PARAMETERS
    SequenceData.toggle = tk.IntVar(value=0)
    sequence_checkbox = customtkinter.CTkCheckBox(sequence_frame,state="disabled",variable=SequenceData.toggle,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,**checkbox_style)
    sequence_detected_label = customtkinter.CTkLabel(sequence_frame, text="Frames detected: ~",text_color=medium_gray,font=InterFont)
    sequence_start_Entry = customtkinter.CTkEntry(sequence_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="start"),font=InterFont)
    sequence_end_Entry = customtkinter.CTkEntry(sequence_frame,**disabled_entry_style,textvariable=customtkinter.StringVar(value="end"),font=InterFont)


    # GRID PARAMETERS
    sequence_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    sequence_frame.grid_rowconfigure([0], weight=1,uniform="a")

    # PLACEMENT PARAMETERS
    sequence_detected_label.grid(column=0, row=0, padx=0, pady=0)
    sequence_start_Entry.grid(column=1, row=0, padx=0, pady=0)
    sequence_end_Entry.grid(column=2, row=0, padx=0, pady=0)
    sequence_checkbox.grid(column=3, row=0, padx=0, pady=0,sticky="w")



    """ 2 ALIGNMENT """
    # ELEMENT PARAMETERS
    coordinate_axis_label = customtkinter.CTkLabel(alignment_frame, text="Coordinate Axis",text_color=light_gray,font=InterFont)
    coordinate_axis_menu = customtkinter.CTkOptionMenu(alignment_frame,dropdown_font=InterFont,values=["X-Y","Y-Z","Z-X"],**normal_menu_style)
    rotation_label = customtkinter.CTkLabel(alignment_frame, text="Rotation",text_color=light_gray,font=InterFont)
    rotation_menu = customtkinter.CTkOptionMenu(alignment_frame,dropdown_font=InterFont,values=["0°","90°","180°","270°"],**normal_menu_style)
    horizontal_align_label = customtkinter.CTkLabel(alignment_frame, text="Horizontal Align",text_color=light_gray,font=InterFont)
    horizontal_align_menu = customtkinter.CTkOptionMenu(alignment_frame,dropdown_font=InterFont,values=["Left","Center","Right"],**normal_menu_style)
    vertical_align_label = customtkinter.CTkLabel(alignment_frame, text="Vertical Align",text_color=light_gray,font=InterFont)
    vertical_align_menu = customtkinter.CTkOptionMenu(alignment_frame,dropdown_font=InterFont,values=["Top","Center","Bottom"],**normal_menu_style)

    # GRID PARAMETERS
    alignment_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    alignment_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

    # PLACEMENT PARAMETERS
    coordinate_axis_label.grid(column=0, row=0, padx=0, pady=0,sticky="e")
    coordinate_axis_menu.grid(column=1, row=0, padx=0, pady=0)
    rotation_label.grid(column=3, row=0, padx=0, pady=0,sticky="w")
    rotation_menu.grid(column=2, row=0, padx=0, pady=0)
    horizontal_align_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")
    horizontal_align_menu.grid(column=1, row=1, padx=0, pady=0)
    vertical_align_label.grid(column=3, row=1, padx=0, pady=0,sticky="w")
    vertical_align_menu.grid(column=2, row=1, padx=0, pady=0)


    """ 2 3D_MODEL """
    # ELEMENT PARAMETERS


    model_with_label = customtkinter.CTkLabel(model_frame, text="Width",text_color=light_gray,font=InterFont)
    model_height_label = customtkinter.CTkLabel(model_frame, text="Height",text_color=light_gray,font=InterFont)
    model_depth_label = customtkinter.CTkLabel(model_frame, text="Depth",text_color=light_gray,font=InterFont)
    model_width_entry = customtkinter.CTkEntry(model_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=InterFont,justify="center")
    model_height_entry = customtkinter.CTkEntry(model_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=InterFont,justify="center")
    model_depth_entry = customtkinter.CTkEntry(model_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Depth"),font=InterFont,justify="center")
    model_wh_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=white,font=("Inter", 20))
    model_hd_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=white,font=("Inter", 20))
    sv.model_resize_boolean = tk.IntVar(value=sv.model_resize_boolean)
    resize_checkbox = customtkinter.CTkCheckBox(model_frame,variable=sv.model_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**checkbox_style)


    # GRID PARAMETERS
    model_frame.grid_columnconfigure([1,3,5,6], weight=1,uniform="a")
    model_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

    # PLACEMENT PARAMETERS

    model_with_label.grid(column=1, row=0, padx=0, pady=0,sticky="s")
    model_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="s")
    model_depth_label.grid(column=5, row=0, padx=0, pady=0,sticky="s")

    model_width_entry.grid(column=1, row=1, padx=15, pady=0,sticky="n")
    model_wh_X_label.grid(column=2, row=1, padx=0, pady=0,sticky="n")
    model_height_entry.grid(column=3, row=1, padx=15, pady=0,sticky="n")
    model_hd_X_label.grid(column=4, row=1, padx=0, pady=0,sticky="n")
    model_depth_entry.grid(column=5, row=1, padx=15, pady=0,sticky="n")
    resize_checkbox.grid(column=6, row=1, padx=0, pady=0,sticky="nw")
    


    """ 2 IMAGE """
    # ELEMENT PARAMETERS
    image_size_label = customtkinter.CTkLabel(image_frame, text="Size",text_color=light_gray,font=InterFont)
    image_width_label = customtkinter.CTkLabel(image_frame, text="Width",text_color=light_gray,font=InterFont)
    image_height_label = customtkinter.CTkLabel(image_frame, text="Height",text_color=light_gray,font=InterFont)

    image_width_entry = customtkinter.CTkEntry(image_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=InterFont,justify="center")
    image_height_entry = customtkinter.CTkEntry(image_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=InterFont,justify="center")
    
    size_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=white,font=("Inter", 20))

    sv.autosize_boolean = tk.IntVar(value=1)
    autosize_checkbox = customtkinter.CTkCheckBox(image_frame,variable=sv.autosize_boolean,command=None, text="Size From Density", onvalue=True, offvalue=False,**checkbox_style)




    density_label = customtkinter.CTkLabel(image_frame, text="Density",text_color=light_gray,font=InterFont)
    density_entry = customtkinter.CTkEntry(image_frame, **normal_entry_style,textvariable=customtkinter.StringVar(value="8"),font=InterFont)

    image_resolution_label = customtkinter.CTkLabel(image_frame, text="Resolution",text_color=light_gray,font=InterFont)
    image_resolution_width_entry = customtkinter.CTkEntry(image_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=InterFont,justify="center")
    image_resolution_height_entry = customtkinter.CTkEntry(image_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=InterFont,justify="center")
    resolution_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=white,font=("Inter", 20))

    sv.image_resize_boolean = tk.IntVar(value=sv.image_resize_boolean)
    image_resize_checkbox = customtkinter.CTkCheckBox(image_frame,variable=sv.image_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**checkbox_style)



    # GRID PARAMETERS
    image_frame.grid_columnconfigure([0,1,3,4], weight=1,uniform="a")
    image_frame.grid_rowconfigure([0,1,2,3,4], weight=1,uniform="a")

    # PLACEMENT PARAMETERS
    image_size_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")
    image_width_label.grid(column=1, row=0, padx=0, pady=0,sticky="s")
    image_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="s")
    image_width_entry.grid(column=1, row=1, padx=15, pady=0,sticky="n")
    image_height_entry.grid(column=3, row=1, padx=15, pady=0,sticky="n")
    size_X_label.grid(column=2, row=1, padx=0, pady=0,sticky="n")
    autosize_checkbox.grid(column=4, row=1, padx=0, pady=0,sticky="nw")

    density_label.grid(column=4, row=2, padx=0, pady=0,sticky="wn")
    density_entry.grid(column=3, row=2, padx=15, pady=0)

    image_resolution_label.grid(column=0, row=4, padx=0, pady=0,sticky="e")
    image_resolution_width_entry.grid(column=1, row=4, padx=15, pady=0,sticky="n")
    image_resolution_height_entry.grid(column=3, row=4, padx=15, pady=0,sticky="n")
    resolution_X_label.grid(column=2, row=4, padx=0, pady=0,sticky="n")
    image_resize_checkbox.grid(column=4, row=4, padx=0, pady=0,sticky="nw")


    
    """ 2 PARTICLE """
    # ELEMENT PARAMETERS
    particle_size_label = customtkinter.CTkLabel(particle_frame, text="Particle Size",text_color=light_gray,font=InterFont)
    particle_size_entry = customtkinter.CTkEntry(particle_frame, **normal_entry_style,textvariable=customtkinter.StringVar(value="1.00"),font=InterFont)
    particle_size_entry.bind("<FocusOut>", verify_widget)
    particle_size_entry.bind("<Return>", verify_widget)

    
    sv.particle_type = tk.StringVar(value=sv.particle_type)
    particle_type_menu = customtkinter.CTkOptionMenu(particle_frame, **normal_menu_style,variable=sv.particle_type, values=["dust", "effect"],font=InterFont)
    particle_type_label = customtkinter.CTkLabel(particle_frame, text="Particle Type",text_color=light_gray,font=InterFont)

    sv.particle_mode = tk.StringVar(value=sv.particle_mode)
    particle_mode_menu = customtkinter.CTkOptionMenu(particle_frame, **normal_menu_style,variable=sv.particle_mode, values=["Force", "Normal"],font=InterFont)
    particle_mode_label = customtkinter.CTkLabel(particle_frame, text="Particle Type",text_color=light_gray,font=InterFont)

    particle_viewer_entry = customtkinter.CTkEntry(particle_frame, **normal_entry_style,textvariable=customtkinter.StringVar(value="@a"),font=InterFont)
    particle_viewer_label = customtkinter.CTkLabel(particle_frame, text="Viewer",text_color=light_gray,font=InterFont)

    sv.particle_color_boolean = tk.IntVar(value=sv.particle_color_boolean)
    particle_color_checkbox = customtkinter.CTkCheckBox(particle_frame,variable=sv.particle_color_boolean,command=None, text="ReColor", onvalue=True, offvalue=False,**checkbox_style)
    particle_hexcode_label = customtkinter.CTkLabel(particle_frame, text="Hexcode",text_color=light_gray,font=InterFont)
    particle_hexcode_entry = customtkinter.CTkEntry(particle_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="#ff0000"),font=InterFont)

    def ask_color():
        pick_color = CTkColorPicker.AskColor(bg_color=dark_gray,fg_color=dark_gray,button_color=medium_gray,button_hover_color=hover_color,corner_radius=10) # open the color picker
        color = pick_color.get() # get the color string
        particle_color_button.configure(fg_color=color)
        particle_hexcode_entry.cget("textvariable").set(color)

    particle_color_button = customtkinter.CTkButton(particle_frame, text=None,command = ask_color,fg_color=medium_gray,hover_color=hover_color,text_color=white,font=InterFont)





    # GRID PARAMETERS
    particle_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    particle_frame.grid_rowconfigure([0,1,2], weight=1,uniform="a")

    # PLACEMENT PARAMETERS
    particle_size_label.grid(column=0, row=0, padx=0, pady=0,sticky="e")
    particle_size_entry.grid(column=1, row=0, padx=15, pady=0)
    particle_type_menu.grid(column=2, row=0, padx=0, pady=0)
    particle_type_label.grid(column=3, row=0, padx=0, pady=0,sticky="w")

    particle_mode_menu.grid(column=2, row=1, padx=0, pady=0)
    particle_mode_label.grid(column=3, row=1, padx=0, pady=0,sticky="w")
    particle_viewer_entry.grid(column=1, row=1, padx=15, pady=0)
    particle_viewer_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")


    particle_color_checkbox.grid(column=3, row=2, padx=0, pady=0,sticky="w")
    particle_hexcode_label.grid(column=2, row=2, padx=0, pady=0)
    particle_hexcode_entry.grid(column=2, row=2, padx=0, pady=0)
    particle_color_button.grid(column=1, row=2, padx=15, pady=0,sticky="we")




    # SequenceData.toggle = tk.IntVar(value=0)
    # sequence_checkbox = customtkinter.CTkCheckBox(input_frame,state="disabled",variable=SequenceData.toggle,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,text_color=white,border_color=white,border_width=1)
    # sequence_checkbox.grid(column=1, row=2, padx=0, pady=0)
    # sequence_start_Entry = customtkinter.CTkEntry(input_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="start"))
    # sequence_start_Entry.grid(column=2, row=2, padx=0, pady=0)
    # sequence_end_Entry = customtkinter.CTkEntry(input_frame,**disabled_entry_style,textvariable=customtkinter.StringVar(value="end"))
    # sequence_end_Entry.grid(column=3, row=2, padx=0, pady=0)



    """ 1 EXPORT """
    # ELEMENTS
    output_path_entry = customtkinter.CTkEntry(export_frame, **path_style,textvariable=customtkinter.StringVar(value="Output folder"),font=InterFont)
    choose_output_button = customtkinter.CTkButton(export_frame, image = folder_button_image, text=None, width=20,height=20,command = find_output_dialog,fg_color=special_color,hover_color=hover_color,text_color=white,font=InterFont)
    export_button = customtkinter.CTkButton(export_frame, image = export_button_image, text="EXPORT", width=30,height=30,command = export,fg_color=special_color,hover_color=hover_color,text_color=white,font=InterFont)


    # GRID
    export_frame.grid_columnconfigure([0,1,2,3,4], weight=1,uniform="a")
    export_frame.grid_rowconfigure([0], weight=1,uniform="a")

    # PLACEMENT
    output_path_entry.grid(column=0, columnspan=3, row=0, padx=10, pady=0,sticky="we")
    choose_output_button.grid(column=3, row=0, padx=0, pady=0,sticky="w")
    export_button.grid(column=4, row=0, padx=0, pady=0,sticky="w")





    launch_frame = customtkinter.CTkFrame(config_frame, width=200, height=200, corner_radius=10, fg_color="transparent")
    # launch_frame.pack(side=tk.TOP, expand=True)
    launch_button = customtkinter.CTkButton(launch_frame, text = 'Convert to .mcfunction file(s)',  command = launch_converter,fg_color='#7a7a7a',hover_color=hover_color,text_color=white)
    # launch_button.pack(side=tk.RIGHT, expand=True)

    disabled_slider_style = {"state":"disabled","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
    normal_slider_style = {"state":"normal","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":hover_color,"button_hover_color":hover_color}

    preview_framenumber_label = customtkinter.CTkLabel(preview_frame, text = 'frame',text_color='#525252',bg_color='black',width=100)
    # preview_framenumber_label.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0,)

    preview_framenumber = customtkinter.IntVar(value=0)
    preview_framenumber_slider = customtkinter.CTkSlider(preview_frame,from_=0, to=100,number_of_steps=10,variable=preview_framenumber,**disabled_slider_style,command=slider_debouncer.debounced_refresh)
    # preview_framenumber_slider.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0)



    randomize_button = customtkinter.CTkButton(preview_frame, text = 'randomize',  command = random_cube_refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color=white)
    randomize_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
    reset_camera_button = customtkinter.CTkButton(preview_frame, text = 'reset',  command = preview.reset_camera,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color=white)
    reset_camera_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
    # preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color=white)
    # preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

    sv.preview_boolean = tk.IntVar(value=sv.preview_boolean)
    preview_toggle_checkbox = customtkinter.CTkCheckBox(preview_frame,text="Preview",text_color=white,command=None, variable=sv.preview_boolean,onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color='#7a7a7a',hover_color=hover_color,bg_color='black',border_color=white,border_width=1)
    preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=0, pady=0)


    # progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
    # progressbar.pack(side=tk.BOTTOM, expand=True)
    # progressbar.start() 

def find_input_dialog():
    global preview_framenumber
    initial_directory = fd.get_json_memory("input_path") # Retrive the last path from the JSON file
    dialog_result = tk.filedialog.askopenfilename(initialdir=initial_directory) # Ask for a file
    if dialog_result == "":
        print("User exited file dialog without selecting a file")
        return
    InputData.path = dialog_result
    fd.update_json_memory("input_path",os.path.dirname(InputData.path)) # Update the JSON file
    
    input_path_entry.cget("textvariable").set(InputData.path)

    fd.find_file_sequence(InputData.path) # Search for frames

    # Update the sequence section
    sequence_start_Entry.cget("textvariable").set(str(InputData.first_frame))
    sequence_end_Entry.cget("textvariable").set(str(InputData.last_frame))
    sequence_detected_label.configure(text = "Frames detected: " + str(InputData.last_frame-InputData.first_frame+1))

    if InputData.first_frame == InputData.last_frame: # If the sequence is 1 frame long
        sequence_detected_label.configure(text_color='#9c9c9c')
        sequence_checkbox.configure(state="disabled") # Disable the checkbox (no more frames to select)
        if sequence_checkbox.get() == 1:
            sequence_checkbox.toggle()
    else: # If the sequence is more than 1 frame long
        sequence_detected_label.configure(text_color=white)
        sequence_checkbox.configure(state="normal") # Allow the checkbox to be selected
        if sequence_checkbox.get() == 0:
            sequence_checkbox.toggle()

    # Change the preview to the first_frame 
    preview_framenumber.set(InputData.first_frame)

    preview_framenumber_slider.configure(from_=InputData.first_frame,to=InputData.last_frame, number_of_steps=InputData.last_frame-1)
    preview_framenumber_label.configure(text = str(InputData.first_frame))

    refresh_preview()

def export ():
    print("Export")

    
def find_output_dialog():
    initial_directory = fd.get_json_memory("output_path")
    dialog_result = tk.filedialog.askdirectory(initialdir=initial_directory)
    if dialog_result == "":
        print("User exited file dialog without selecting a folder")
        return
    
    sv.output_path = dialog_result
    fd.update_json_memory("output_path",sv.output_path)

    output_path_entry.cget("textvariable").set(sv.output_path)

def update_sequence_section():

    # If the checkbox was checked, 
    if sequence_checkbox.get() == 1:
        sequence_start_Entry.configure(**normal_entry_style,placeholder_text="start")
        sequence_end_Entry.configure(**normal_entry_style,placeholder_text="end")
        # preview_frame_slider.pack(side=tk.BOTTOM, expand=False, padx=50, pady=50)
        preview_framenumber_slider.configure(**normal_slider_style)


    if sequence_checkbox.get() == 0:
        sequence_start_Entry.configure(**disabled_entry_style)
        sequence_end_Entry.configure(**disabled_entry_style)
        # preview_frame_slider.pack_forget()
        preview_framenumber_slider.configure(**disabled_slider_style)


def random_cube_mp():
    random_cube_process = mp.Process(target=random_cube_refresh_preview)
    random_cube_process.start()

    square_size = 50
    squares = []
    # Create positions for the squares in a 2x2 grid
    for row in range(2):
        for col in range(2):
            x = sv.pygame_width // 2 - square_size + col * square_size
            y = sv.pygame_height // 2 - square_size + row * square_size
            squares.append((x, y))

    current_square = 0  # Initial square index

    # while random_cube_process.is_alive():
    #     animation(current_square, squares, square_size)


# Function to generate random particle inside a cube
def random_cube_refresh_preview():



    print("random cube")



    sv.data_particles = []
    sv.textured_particles = []
    sv.loading_done = False

    #     # Start the loading animation in a separate thread
    # loading_thread = threading.Thread(target=loading_animation,daemon=True)
    # loading_thread.start()

    # Generate particle positions and create particles
    amount = 8 # Number of particles

    # Generate random particle positions
    random_positions = []
    for _ in range(amount):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        z = random.uniform(0, 1)
        random_positions.append((x, y, z))

    # Create a list of randomly tinted particles
    for i, position in enumerate(random_positions):
        color = (int((position[0]) * 255),
                int((position[1]) * 255),
                int((position[2]) * 255))
        
        
        sv.data_particles.append(converter.ParticleData(position, color))
        # surface = Preview.create_particle_surface(PARTICLE_TEXTURE, color)
        sv.textured_particles.append(preview.TexturedParticle(position, color))
        # surface = Preview.create_particle_surface(PARTICLE_TEXTURE, color)
    sv.global_size = round(max(x for x, _, _ in random_positions)-min(x for x, _, _ in random_positions),1), round(max(y for _, y, _ in random_positions)-min(y for y, y, _ in random_positions),1), round(max(z for _, _, z in random_positions)-min(z for _, _, z in random_positions),1)

        
    

    # Set loading_done to True to stop the loading animation
    sv.loading_done = True

def refresh_preview():
    print("refresh_preview")
    if len(InputData.sequence_files) == 0: # Stops if no sequence is found.
        return
    sv.loading_done = False

    
    # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=preview.loading_animation,daemon=True)
    loading_thread.start()



    path = InputData.path

    if sequence_checkbox.get() == 1:
        path = InputData.sequence_files[int(preview_framenumber.get())]["path"] # Change the file path to the selected frame
        
    
    # Read particle positions from file
    if InputData.path:
        sv.data_particles =converter.create_ParticleData_list_from_file(path) # Read the ParticleData from the file
        sv.textured_particles = [] # Empty the particles list
        for particle in sv.data_particles[0]: # Transform the data into a list of textures particles
            sv.textured_particles.append(preview.TexturedParticle(particle.position, particle.color))
        sv.global_size = sv.data_particles[1]
        
    
    else:
        # Set loading_done to True to stop the loading animation
        sv.loading_done = True
        return
    

    
    # Set loading_done to True to stop the loading animation
    sv.loading_done = True

def cube_corners_refresh_preview():
    print("cube corners")
    sv.data_particles = []
    sv.textured_particles = []
    sv.loading_done = False

    # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=preview.loading_animation,daemon=True)
    loading_thread.start()

    # Define the cube corners
    cube_corners = [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)
    ]

    # Create a list of particles at each corner
    for position in cube_corners:
        color = (255, 0 , 0)  # White color for all particles
        sv.data_particles.append(converter.ParticleData(position, color))
        sv.textured_particles.append(preview.TexturedParticle(position, color))

    sv.global_size = (1.0,1.0,1.0)
    # Set loading_done to True to stop the loading animation

    sv.loading_done = True

def Warning_OutputFolderRequired():
    tk.messagebox.showerror("Output folder required", "Please select an output folder",icon="info")


class SliderDebouncer:
    def __init__(self, root, refresh_callback):
        self.root = root
        self.refresh_callback = refresh_callback
        self.delay_time = 500  # 500 milliseconds (0.5 seconds)
        self.after_id = None

    def debounced_refresh(self, value):
        preview_framenumber_label.configure(text = str(int(value)))
        # Cancel any previous refresh if the slider was moved again
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        
        # Schedule the new refresh after a delay
        self.after_id = self.root.after(self.delay_time, lambda: self.refresh_preview(value))

    def refresh_preview(self, value):
        # print(f"Preview refreshed with value: {value}")
        # Call your original refresh function
        preview_framenumber.set(value)
        self.refresh_callback()

def launch_converter():
    if sv.output_path == "":
        tk.messagebox.showerror("Output folder required", "Please select an output folder",icon="info")
        return
    
    if SequenceData.toggle.get() == 0: # If we are not in sequence mode
        if InputData.path != "": # If an input was selected
            sv.data_particles, sv.global_size = converter.create_ParticleData_list_from_file(InputData.path)
        else : # If no input was selected
            InputData.path = "particles" 
        converter.write_mc_function(False,0,sv.output_path,os.path.splitext(os.path.basename(InputData.path))[0],sv.data_particles)

    if sequence_checkbox.get() == 1: # If we are in sequence mode
        if InputData.path == "":
            tk.messagebox.showerror("Input required", "Please select an input for a sequence export",icon="info")
        if InputData.seq_length == 1:
            tk.messagebox.showerror("Single file", "Only one file was found in the sequence, exporting anyways. \n Make sure your files have the same name + number",icon="info")
        
        for i in range(int(sequence_start_Entry.get()), int(sequence_end_Entry.get())+1):
            path = InputData.sequence_files[i]["path"]
            sv.data_particles, sv.global_size = converter.create_ParticleData_list_from_file(InputData.sequence_files[i]["path"]) 
            converter.write_mc_function(True,i,sv.output_path,os.path.splitext(os.path.basename(path))[0],sv.data_particles)

    
    # Converter.main(input_path, output_path)
    