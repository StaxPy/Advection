import tkinter as tk
import customtkinter
import CTkColorPicker
import os, random
import backend.file_operations as fo
import shared.variables as sv
from PIL import Image

class StylesDefinitions():
    def __init__(self):
        self.hover_color = "#ffffff"
        self.special_color = "#be5dff"
        self.dark_gray = "#292929"
        self.medium_gray = "#6e6e6e"
        self.light_gray = "#adadad"
        self.white = "#ffffff"
        self.almost_black = sv.almost_black
        self.black = "#000000"

        self.path_style = {"state":"disabled","fg_color":self.black,"placeholder_text_color":self.medium_gray,"text_color":self.white,"border_color":self.dark_gray}
        self.disabled_entry_style = {"state":"disabled","fg_color":self.dark_gray,"placeholder_text_color":self.medium_gray,"text_color":self.medium_gray,"border_color":self.medium_gray}
        self.normal_entry_style = {"state":"normal","fg_color":self.black,"placeholder_text_color":self.white,"border_color":self.dark_gray,"text_color":self.white}

        self.checkbox_style = {"checkbox_width":20,"checkbox_height":20,"text_color":self.white,"border_color":self.white,"border_width":1,"hover_color":self.hover_color,"fg_color":self.special_color}

        self.normal_menu_style = {"fg_color":self.black,"button_color":self.medium_gray,"dropdown_fg_color":self.dark_gray,"dropdown_text_color":self.white,"button_hover_color":self.hover_color} 
        
styles = StylesDefinitions()

class UI():

    def __init__(self):
        # global TkApp, UI.config_frame, UI.preview_frame, UI.export_frame
        # global hover_color, special_color, dark_gray, medium_gray, light_gray, white, black

        self.TkApp = customtkinter.CTk()






        self.TkApp.minsize(1280, 720)  # Set minimum size to 800x600
        self.TkApp.geometry(f"{sv.WIDTH}x{sv.HEIGHT}")
        self.TkApp.configure(background=styles.black)
        self.TkApp.title("Animation-to-Particles Converter")

        self.config_frame_border = tk.Frame(self.TkApp,background=styles.almost_black)
        self.config_frame = tk.Frame(self.config_frame_border,background=styles.almost_black)
        self.preview_frame = tk.Frame(self.TkApp, background=styles.almost_black)
        self.export_frame_border = tk.Frame(self.TkApp, background=styles.almost_black)
        self.export_frame = customtkinter.CTkFrame(self.export_frame_border, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)


        self.TkApp.columnconfigure((0,1), weight=1,uniform="a")
        self.TkApp.rowconfigure((0), weight=4,uniform="a")
        self.TkApp.rowconfigure((1), weight=1,uniform="a")
        self.config_frame_border.rowconfigure((0), weight=1,uniform="a")
        self.config_frame_border.columnconfigure((0), weight=1,uniform="a")
        self.export_frame_border.rowconfigure((0), weight=1,uniform="a")
        self.export_frame_border.columnconfigure((0), weight=1,uniform="a")


        
        self.config_frame_border.grid(row = 0, column = 0,sticky="nsew",rowspan=2)
        self.config_frame.grid(row = 0, column = 0,sticky="nsew",pady=10,padx=10)
        self.preview_frame.grid(row=0, column=1, sticky="nsew")
        self.export_frame_border.grid(row = 1, column = 1,sticky="nsew")
        self.export_frame.grid(row = 0, column = 0,sticky="nsew",pady=15,padx=10)

def initialize_interface():
    global UI
    UI = UI()

def run_main_loop():
    UI.TkApp.mainloop()

def create_interface():
    global input_frame, input_path_entry, output_path_entry, choose_file_button, sequence_checkbox, sequence_detected_label, sequence_start_Entry, sequence_end_Entry, preview_framenumber_slider, preview_framenumber_label
    global disabled_entry_style, normal_entry_style, disabled_slider_style, normal_slider_style, preview_framenumber, InterFont

    def focus_on_click(event):
        event.widget.focus_set() # Focus on selected element

    def verify_widget(event):
        print("Verifying",event.widget)
        UI.TkApp.focus_set() # Unfocus
    
    UI.TkApp.bind_all('<Button-1>', focus_on_click)

    InterFont = customtkinter.CTkFont(family="Inter", size=12)

    # Debouncer that wraps the original refresh function
    slider_debouncer = SliderDebouncer(UI.TkApp, refresh_preview)




    """ 1 CONFIG """
    # ELEMENT PARAMETERS
    UI.input_frame = customtkinter.CTkFrame(UI.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
    UI.sequence_frame = customtkinter.CTkFrame(UI.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
    UI.alignment_frame = customtkinter.CTkFrame(UI.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
    UI.model_frame = customtkinter.CTkFrame(UI.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
    UI.image_frame = customtkinter.CTkFrame(UI.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
    UI.particle_frame = customtkinter.CTkFrame(UI.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)

    # GRID PARAMETERS
    UI.config_frame.columnconfigure([0], weight=1,uniform="a")
    UI.config_frame.rowconfigure([0,1,2,3,4,5],weight=1)

    # PLACEMENT PARAMETERS
    UI.input_frame.grid(row = 0, column = 0,sticky="nsew",pady=5,padx=10)
    UI.sequence_frame.grid(row = 1, column = 0,sticky="nsew",pady=5,padx=10)
    UI.alignment_frame.grid(row = 2, column = 0,sticky="nsew",pady=5,padx=10)
    UI.model_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
    UI.image_frame.grid(row = 4, column = 0,sticky="nsew",pady=5,padx=10)
    UI.particle_frame.grid(row = 5, column = 0,sticky="nsew",pady=5,padx=10)


    


    """ 2 INPUT FILE """
    # ELEMENT PARAMETERS
    file_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/file_lines_icon.png")),size=(20,20))
    folder_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/folder_open_document_icon.png")),size=(20,20))
    export_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/hand_point_right_icon.png")),size=(20,20))
    input_label = customtkinter.CTkLabel(UI.input_frame, text = 'Input File',text_color=styles.white,font=InterFont,height=15)
    input_path_entry = customtkinter.CTkEntry(UI.input_frame, **styles.path_style,textvariable=customtkinter.StringVar(value="OBJ file or PNG/JPG image"),font=InterFont)
    choose_file_button = customtkinter.CTkButton(UI.input_frame, image = file_button_image, text=None, width=20,height=20,command = find_input_dialog,fg_color=styles.special_color,hover_color=styles.hover_color,text_color=styles.white,font=InterFont)

    # GRID PARAMETERS
    UI.input_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    UI.input_frame.grid_rowconfigure([0,1], weight=1,uniform="a")
    
    # PLACEMENT PARAMETERS
    input_label.grid(column=0, row=0, padx=15, pady=5,sticky="ws",)
    input_path_entry.grid(column=0, row=1, padx=10, pady=0,sticky="wen",columnspan=3)
    choose_file_button.grid(column=3, row=1, padx=0, pady=0,sticky="nw")

    """ 2 SEQUENCE """
    # ELEMENT PARAMETERS
    sv.sequence_boolean = tk.IntVar(value=0)
    sequence_checkbox = customtkinter.CTkCheckBox(UI.sequence_frame,state="disabled",variable=sv.sequence_boolean,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,**styles.checkbox_style)
    sequence_detected_label = customtkinter.CTkLabel(UI.sequence_frame, text="Frames detected: ~",text_color=styles.medium_gray,font=InterFont)
    sequence_start_Entry = customtkinter.CTkEntry(UI.sequence_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="start"),font=InterFont)
    sequence_end_Entry = customtkinter.CTkEntry(UI.sequence_frame,**styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="end"),font=InterFont)


    # GRID PARAMETERS
    UI.sequence_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    UI.sequence_frame.grid_rowconfigure([0], weight=1,uniform="a")

    # PLACEMENT PARAMETERS
    sequence_detected_label.grid(column=0, row=0, padx=0, pady=0)
    sequence_start_Entry.grid(column=1, row=0, padx=0, pady=0)
    sequence_end_Entry.grid(column=2, row=0, padx=0, pady=0)
    sequence_checkbox.grid(column=3, row=0, padx=0, pady=0,sticky="w")



    """ 2 ALIGNMENT """
    # ELEMENT PARAMETERS
    coordinate_axis_label = customtkinter.CTkLabel(UI.alignment_frame, text="Coordinate Axis",text_color=styles.light_gray,font=InterFont)
    coordinate_axis_menu = customtkinter.CTkOptionMenu(UI.alignment_frame,dropdown_font=InterFont,values=["X-Y","Y-Z","Z-X"],**styles.normal_menu_style)
    rotation_label = customtkinter.CTkLabel(UI.alignment_frame, text="Rotation",text_color=styles.light_gray,font=InterFont)
    rotation_menu = customtkinter.CTkOptionMenu(UI.alignment_frame,dropdown_font=InterFont,values=["0°","90°","180°","270°"],**styles.normal_menu_style)
    horizontal_align_label = customtkinter.CTkLabel(UI.alignment_frame, text="Horizontal Align",text_color=styles.light_gray,font=InterFont)
    horizontal_align_menu = customtkinter.CTkOptionMenu(UI.alignment_frame,dropdown_font=InterFont,values=["Left","Center","Right"],**styles.normal_menu_style)
    vertical_align_label = customtkinter.CTkLabel(UI.alignment_frame, text="Vertical Align",text_color=styles.light_gray,font=InterFont)
    vertical_align_menu = customtkinter.CTkOptionMenu(UI.alignment_frame,dropdown_font=InterFont,values=["Top","Center","Bottom"],**styles.normal_menu_style)

    # GRID PARAMETERS
    UI.alignment_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    UI.alignment_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

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


    model_with_label = customtkinter.CTkLabel(UI.model_frame, text="Width",text_color=styles.light_gray,font=InterFont)
    model_height_label = customtkinter.CTkLabel(UI.model_frame, text="Height",text_color=styles.light_gray,font=InterFont)
    model_depth_label = customtkinter.CTkLabel(UI.model_frame, text="Depth",text_color=styles.light_gray,font=InterFont)
    model_width_entry = customtkinter.CTkEntry(UI.model_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=InterFont,justify="center")
    model_height_entry = customtkinter.CTkEntry(UI.model_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=InterFont,justify="center")
    model_depth_entry = customtkinter.CTkEntry(UI.model_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Depth"),font=InterFont,justify="center")
    model_wh_X_label = customtkinter.CTkLabel(UI.model_frame, text="X",text_color=styles.white,font=("Inter", 20))
    model_hd_X_label = customtkinter.CTkLabel(UI.model_frame, text="X",text_color=styles.white,font=("Inter", 20))
    sv.model_resize_boolean = tk.IntVar(value=sv.model_resize_boolean)
    resize_checkbox = customtkinter.CTkCheckBox(UI.model_frame,variable=sv.model_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**styles.checkbox_style)


    # GRID PARAMETERS
    UI.model_frame.grid_columnconfigure([1,3,5,6], weight=1,uniform="a")
    UI.model_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

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
    image_size_label = customtkinter.CTkLabel(UI.image_frame, text="Size",text_color=styles.light_gray,font=InterFont)
    image_width_label = customtkinter.CTkLabel(UI.image_frame, text="Width",text_color=styles.light_gray,font=InterFont)
    image_height_label = customtkinter.CTkLabel(UI.image_frame, text="Height",text_color=styles.light_gray,font=InterFont)

    image_width_entry = customtkinter.CTkEntry(UI.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=InterFont,justify="center")
    image_height_entry = customtkinter.CTkEntry(UI.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=InterFont,justify="center")
    
    size_X_label = customtkinter.CTkLabel(UI.image_frame, text="X",text_color=styles.white,font=("Inter", 20))

    sv.autosize_boolean = tk.IntVar(value=1)
    autosize_checkbox = customtkinter.CTkCheckBox(UI.image_frame,variable=sv.autosize_boolean,command=None, text="Size From Density", onvalue=True, offvalue=False,**styles.checkbox_style)




    density_label = customtkinter.CTkLabel(UI.image_frame, text="Density",text_color=styles.light_gray,font=InterFont)
    density_entry = customtkinter.CTkEntry(UI.image_frame, **styles.normal_entry_style,textvariable=customtkinter.StringVar(value="8"),font=InterFont)

    image_resolution_label = customtkinter.CTkLabel(UI.image_frame, text="Resolution",text_color=styles.light_gray,font=InterFont)
    image_resolution_width_entry = customtkinter.CTkEntry(UI.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=InterFont,justify="center")
    image_resolution_height_entry = customtkinter.CTkEntry(UI.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=InterFont,justify="center")
    resolution_X_label = customtkinter.CTkLabel(UI.image_frame, text="X",text_color=styles.white,font=("Inter", 20))

    sv.image_resize_boolean = tk.IntVar(value=sv.image_resize_boolean)
    image_resize_checkbox = customtkinter.CTkCheckBox(UI.image_frame,variable=sv.image_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**styles.checkbox_style)



    # GRID PARAMETERS
    UI.image_frame.grid_columnconfigure([0,1,3,4], weight=1,uniform="a")
    UI.image_frame.grid_rowconfigure([0,1,2,3,4], weight=1,uniform="a")

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
    particle_size_label = customtkinter.CTkLabel(UI.particle_frame, text="Particle Size",text_color=styles.light_gray,font=InterFont)
    particle_size_entry = customtkinter.CTkEntry(UI.particle_frame, **styles.normal_entry_style,textvariable=customtkinter.StringVar(value="1.00"),font=InterFont)
    particle_size_entry.bind("<FocusOut>", verify_widget)
    particle_size_entry.bind("<Return>", verify_widget)

    
    sv.particle_type = tk.StringVar(value=sv.particle_type)
    particle_type_menu = customtkinter.CTkOptionMenu(UI.particle_frame, **styles.normal_menu_style,variable=sv.particle_type, values=["dust", "effect"],font=InterFont)
    particle_type_label = customtkinter.CTkLabel(UI.particle_frame, text="Particle Type",text_color=styles.light_gray,font=InterFont)

    sv.particle_mode = tk.StringVar(value=sv.particle_mode)
    particle_mode_menu = customtkinter.CTkOptionMenu(UI.particle_frame, **styles.normal_menu_style,variable=sv.particle_mode, values=["Force", "Normal"],font=InterFont)
    particle_mode_label = customtkinter.CTkLabel(UI.particle_frame, text="Particle Type",text_color=styles.light_gray,font=InterFont)

    particle_viewer_entry = customtkinter.CTkEntry(UI.particle_frame, **styles.normal_entry_style,textvariable=customtkinter.StringVar(value="@a"),font=InterFont)
    particle_viewer_label = customtkinter.CTkLabel(UI.particle_frame, text="Viewer",text_color=styles.light_gray,font=InterFont)

    sv.particle_color_boolean = tk.IntVar(value=sv.particle_color_boolean)
    particle_color_checkbox = customtkinter.CTkCheckBox(UI.particle_frame,variable=sv.particle_color_boolean,command=None, text="ReColor", onvalue=True, offvalue=False,**styles.checkbox_style)
    particle_hexcode_label = customtkinter.CTkLabel(UI.particle_frame, text="Hexcode",text_color=styles.light_gray,font=InterFont)
    particle_hexcode_entry = customtkinter.CTkEntry(UI.particle_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="#ff0000"),font=InterFont)

    def ask_color():
        pick_color = CTkColorPicker.AskColor(bg_color=styles.dark_gray,fg_color=styles.dark_gray,button_color=styles.medium_gray,button_hover_color=styles.hover_color,corner_radius=10) # open the color picker
        color = pick_color.get() # get the color string
        particle_color_button.configure(fg_color=color)
        particle_hexcode_entry.cget("textvariable").set(color)

    particle_color_button = customtkinter.CTkButton(UI.particle_frame, text=None,command = ask_color,fg_color=styles.medium_gray,hover_color=styles.hover_color,text_color=styles.white,font=InterFont)





    # GRID PARAMETERS
    UI.particle_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
    UI.particle_frame.grid_rowconfigure([0,1,2], weight=1,uniform="a")

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




    # sv.sequence_boolean = tk.IntVar(value=0)
    # sequence_checkbox = customtkinter.CTkCheckBox(UI.input_frame,state="disabled",variable=sv.sequence_boolean,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,text_color=styles.white,border_color=styles.white,border_width=1)
    # sequence_checkbox.grid(column=1, row=2, padx=0, pady=0)
    # sequence_start_Entry = customtkinter.CTkEntry(UI.input_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="start"))
    # sequence_start_Entry.grid(column=2, row=2, padx=0, pady=0)
    # sequence_end_Entry = customtkinter.CTkEntry(UI.input_frame,**styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="end"))
    # sequence_end_Entry.grid(column=3, row=2, padx=0, pady=0)



    """ 1 EXPORT """
    # ELEMENTS
    output_path_entry = customtkinter.CTkEntry(UI.export_frame, **styles.path_style,textvariable=customtkinter.StringVar(value="Output folder"),font=InterFont)
    choose_output_button = customtkinter.CTkButton(UI.export_frame, image = folder_button_image, text=None, width=20,height=20,command = find_output_dialog,fg_color=styles.special_color,hover_color=styles.hover_color,text_color=styles.white,font=InterFont)
    export_button = customtkinter.CTkButton(UI.export_frame, image = export_button_image, text="EXPORT", width=30,height=30,command = export,fg_color=styles.special_color,hover_color=styles.hover_color,text_color=styles.white,font=InterFont)


    # GRID
    UI.export_frame.grid_columnconfigure([0,1,2,3,4], weight=1,uniform="a")
    UI.export_frame.grid_rowconfigure([0], weight=1,uniform="a")

    # PLACEMENT
    output_path_entry.grid(column=0, columnspan=3, row=0, padx=10, pady=0,sticky="we")
    choose_output_button.grid(column=3, row=0, padx=0, pady=0,sticky="w")
    export_button.grid(column=4, row=0, padx=0, pady=0,sticky="w")





    launch_frame = customtkinter.CTkFrame(UI.config_frame, width=200, height=200, corner_radius=10, fg_color="transparent")
    # launch_frame.pack(side=tk.TOP, expand=True)
    launch_button = customtkinter.CTkButton(launch_frame, text = 'Convert to .mcfunction file(s)',  command = None,fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
    # launch_button.pack(side=tk.RIGHT, expand=True)

    disabled_slider_style = {"state":"disabled","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
    normal_slider_style = {"state":"normal","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":styles.hover_color,"button_hover_color":styles.hover_color}

    UI.preview_framenumber_label = customtkinter.CTkLabel(UI.preview_frame, text = 'frame',text_color='#525252',bg_color='black',width=100)
    # UI.preview_framenumber_label.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0,)

    UI.preview_framenumber = customtkinter.IntVar(value=0)
    UI.preview_framenumber_slider = customtkinter.CTkSlider(UI.preview_frame,from_=0, to=100,number_of_steps=10,variable=UI.preview_framenumber,**disabled_slider_style,command=slider_debouncer.debounced_refresh)
    # UI.preview_framenumber_slider.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0)



    randomize_button = customtkinter.CTkButton(UI.preview_frame, text = 'randomize',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
    randomize_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
    reset_camera_button = customtkinter.CTkButton(UI.preview_frame, text = 'reset',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
    reset_camera_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
    # preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
    # preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

    sv.preview_boolean = tk.IntVar(value=sv.preview_boolean)
    preview_toggle_checkbox = customtkinter.CTkCheckBox(UI.preview_frame,text="Preview",text_color=styles.white,command=None, variable=sv.preview_boolean,onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color='#7a7a7a',hover_color=styles.hover_color,bg_color='black',border_color=styles.white,border_width=1)
    preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=0, pady=0)


    # progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
    # progressbar.pack(side=tk.BOTTOM, expand=True)
    # progressbar.start() 


def find_input_dialog():
    global preview_framenumber
    initial_directory = fo.get_json_memory("input_path") # Retrive the last path from the JSON file
    dialog_result = tk.filedialog.askopenfilename(initialdir=initial_directory) # Ask for a file
    if dialog_result == "":
        print("User exited file dialog without selecting a file")
        return
    sv.input_path = dialog_result
    fo.update_json_memory("input_path",os.path.dirname(sv.input_path)) # Update the JSON file
    
    input_path_entry.cget("textvariable").set(sv.input_path)

    fo.find_file_sequence(sv.input_path) # Search for frames

    # Update the sequence section
    sequence_start_Entry.cget("textvariable").set(str(sv.first_frame))
    sequence_end_Entry.cget("textvariable").set(str(sv.last_frame))
    sequence_detected_label.configure(text = "Frames detected: " + str(sv.last_frame-sv.first_frame+1))

    if sv.first_frame == sv.last_frame: # If the sequence is 1 frame long
        sequence_detected_label.configure(text_color='#9c9c9c')
        sequence_checkbox.configure(state="disabled") # Disable the checkbox (no more frames to select)
        if sequence_checkbox.get() == 1:
            sequence_checkbox.toggle()
    else: # If the sequence is more than 1 frame long
        sequence_detected_label.configure(text_color=styles.white)
        sequence_checkbox.configure(state="normal") # Allow the checkbox to be selected
        if sequence_checkbox.get() == 0:
            sequence_checkbox.toggle()

    # Change the preview to the first_frame 
    UI.preview_framenumber.set(sv.first_frame)

    UI.preview_framenumber_slider.configure(from_=sv.first_frame,to=sv.last_frame, number_of_steps=sv.last_frame-1)
    UI.preview_framenumber_label.configure(text = str(sv.first_frame))

    refresh_preview()

def export ():
    print("Export")

    
def find_output_dialog():
    initial_directory = fo.get_json_memory("output_path")
    dialog_result = tk.filedialog.askdirectory(initialdir=initial_directory)
    if dialog_result == "":
        print("User exited file dialog without selecting a folder")
        return
    
    sv.output_path = dialog_result
    fo.update_json_memory("output_path",sv.output_path)

    output_path_entry.cget("textvariable").set(sv.output_path)

def update_sequence_section():

    # If the checkbox was checked, 
    if sequence_checkbox.get() == 1:
        sequence_start_Entry.configure(**styles.normal_entry_style,placeholder_text="start")
        sequence_end_Entry.configure(**styles.normal_entry_style,placeholder_text="end")
        # UI.preview_frame_slider.pack(side=tk.BOTTOM, expand=False, padx=50, pady=50)
        UI.preview_framenumber_slider.configure(**normal_slider_style)


    if sequence_checkbox.get() == 0:
        sequence_start_Entry.configure(**styles.disabled_entry_style)
        sequence_end_Entry.configure(**styles.disabled_entry_style)
        # UI.preview_frame_slider.pack_forget()
        UI.preview_framenumber_slider.configure(**disabled_slider_style)





class SliderDebouncer:
    def __init__(self, root, refresh_callback):
        self.root = root
        self.refresh_callback = refresh_callback
        self.delay_time = 500  # 500 milliseconds (0.5 seconds)
        self.after_id = None

    def debounced_refresh(self, value):
        UI.preview_framenumber_label.configure(text = str(int(value)))
        # Cancel any previous refresh if the slider was moved again
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        
        # Schedule the new refresh after a delay
        self.after_id = self.root.after(self.delay_time, lambda: self.refresh_preview(value))

    def refresh_preview(self, value):
        # print(f"Preview refreshed with value: {value}")
        # Call your original refresh function
        UI.preview_framenumber.set(value)
        self.refresh_callback()



def refresh_preview():
    # TODO MODIFIER ANCIEN CODE
    pass