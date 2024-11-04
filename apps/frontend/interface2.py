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

        # Path
        self.path_style = {"state":"disabled","fg_color":self.black,"placeholder_text_color":self.medium_gray,"text_color":self.white,"border_color":self.dark_gray}
        # Entry
        self.disabled_entry_style = {"state":"disabled","fg_color":self.dark_gray,"placeholder_text_color":self.medium_gray,"text_color":self.medium_gray,"border_color":self.medium_gray}
        self.normal_entry_style = {"state":"normal","fg_color":self.black,"placeholder_text_color":self.white,"border_color":self.dark_gray,"text_color":self.white}
        # Checkbox
        self.checkbox_style = {"checkbox_width":20,"checkbox_height":20,"text_color":self.white,"border_color":self.white,"border_width":1,"hover_color":self.hover_color,"fg_color":self.special_color}
        # Menu
        self.normal_menu_style = {"fg_color":self.black,"button_color":self.medium_gray,"dropdown_fg_color":self.dark_gray,"dropdown_text_color":self.white,"button_hover_color":self.hover_color} 
        # Slider
        self.disabled_slider_style = {"state":"disabled","bg_color":'black',"fg_color":self.medium_gray,'progress_color': self.medium_gray,"border_color":'black',"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
        self.normal_slider_style = {"state":"normal","bg_color":'black',"fg_color":self.medium_gray,'progress_color': self.medium_gray,"border_color":'black',"button_color":self.hover_color,"button_hover_color":self.hover_color}

        self.InterFont = ""

styles = StylesDefinitions()

class UI():

    def __init__(self):

        self.TkApp = customtkinter.CTk()

        styles.InterFont = customtkinter.CTkFont(family="Inter", size=12)
    



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


        def focus_on_click(event):
            event.widget.focus_set() # Focus on selected element

        def verify_widget(self, event):
            print("Verifying",event.widget)
            self.TkApp.focus_set() # Unfocus
        
        self.TkApp.bind_all('<Button-1>', focus_on_click)


        # Debouncer that wraps the original refresh function
        slider_debouncer = SliderDebouncer(self.TkApp, self.refresh_preview)




        """ 1 CONFIG """
        # ELEMENT PARAMETERS
        self.input_frame = customtkinter.CTkFrame(self.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
        self.sequence_frame = customtkinter.CTkFrame(self.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
        self.alignment_frame = customtkinter.CTkFrame(self.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
        self.model_frame = customtkinter.CTkFrame(self.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
        self.image_frame = customtkinter.CTkFrame(self.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)
        self.particle_frame = customtkinter.CTkFrame(self.config_frame, fg_color=styles.dark_gray,border_color=styles.dark_gray,border_width=2)

        # GRID PARAMETERS
        self.config_frame.columnconfigure([0], weight=1,uniform="a")
        self.config_frame.rowconfigure([0,1,2,3,4,5],weight=1)

        # PLACEMENT PARAMETERS
        self.input_frame.grid(row = 0, column = 0,sticky="nsew",pady=5,padx=10)
        self.sequence_frame.grid(row = 1, column = 0,sticky="nsew",pady=5,padx=10)
        self.alignment_frame.grid(row = 2, column = 0,sticky="nsew",pady=5,padx=10)
        self.model_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
        self.image_frame.grid(row = 4, column = 0,sticky="nsew",pady=5,padx=10)
        self.particle_frame.grid(row = 5, column = 0,sticky="nsew",pady=5,padx=10)


        


        """ 2 INPUT FILE """
        # ELEMENT PARAMETERS
        self.file_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/file_lines_icon.png")),size=(20,20))
        self.folder_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/folder_open_document_icon.png")),size=(20,20))
        self.export_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/hand_point_right_icon.png")),size=(20,20))
        self.input_label = customtkinter.CTkLabel(self.input_frame, text = 'Input File',text_color=styles.white,font=styles.InterFont,height=15)
        self.input_path_entry = customtkinter.CTkEntry(self.input_frame, **styles.path_style,textvariable=customtkinter.StringVar(value="OBJ file or PNG/JPG image"),font=styles.InterFont)
        self.choose_file_button = customtkinter.CTkButton(self.input_frame, image = self.file_button_image, text=None, width=20,height=20,command = self.find_input_dialog,fg_color=styles.special_color,hover_color=styles.hover_color,text_color=styles.white,font=styles.InterFont)

        # GRID PARAMETERS
        self.input_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        self.input_frame.grid_rowconfigure([0,1], weight=1,uniform="a")
        
        # PLACEMENT PARAMETERS
        self.input_label.grid(column=0, row=0, padx=15, pady=5,sticky="ws",)
        self.input_path_entry.grid(column=0, row=1, padx=10, pady=0,sticky="wen",columnspan=3)
        self.choose_file_button.grid(column=3, row=1, padx=0, pady=0,sticky="nw")

        """ 2 SEQUENCE """
        # ELEMENT PARAMETERS
        sv.sequence_boolean = tk.IntVar(value=0)
        self.sequence_checkbox = customtkinter.CTkCheckBox(self.sequence_frame,state="disabled",variable=sv.sequence_boolean,command=self.update_sequence_section, text="Sequence", onvalue=True, offvalue=False,**styles.checkbox_style)
        self.sequence_detected_label = customtkinter.CTkLabel(self.sequence_frame, text="Frames detected: ~",text_color=styles.medium_gray,font=styles.InterFont)
        self.sequence_start_Entry = customtkinter.CTkEntry(self.sequence_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="start"),font=styles.InterFont)
        self.sequence_end_Entry = customtkinter.CTkEntry(self.sequence_frame,**styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="end"),font=styles.InterFont)


        # GRID PARAMETERS
        self.sequence_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        self.sequence_frame.grid_rowconfigure([0], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        self.sequence_detected_label.grid(column=0, row=0, padx=0, pady=0)
        self.sequence_start_Entry.grid(column=1, row=0, padx=0, pady=0)
        self.sequence_end_Entry.grid(column=2, row=0, padx=0, pady=0)
        self.sequence_checkbox.grid(column=3, row=0, padx=0, pady=0,sticky="w")



        """ 2 ALIGNMENT """
        # ELEMENT PARAMETERS
        coordinate_axis_label = customtkinter.CTkLabel(self.alignment_frame, text="Coordinate Axis",text_color=styles.light_gray,font=styles.InterFont)
        self.coordinate_axis_menu = customtkinter.CTkOptionMenu(self.alignment_frame,dropdown_font=styles.InterFont,values=["X-Y","Y-Z","Z-X"],**styles.normal_menu_style)
        self.rotation_label = customtkinter.CTkLabel(self.alignment_frame, text="Rotation",text_color=styles.light_gray,font=styles.InterFont)
        self.rotation_menu = customtkinter.CTkOptionMenu(self.alignment_frame,dropdown_font=styles.InterFont,values=["0°","90°","180°","270°"],**styles.normal_menu_style)
        self.horizontal_align_label = customtkinter.CTkLabel(self.alignment_frame, text="Horizontal Align",text_color=styles.light_gray,font=styles.InterFont)
        self.horizontal_align_menu = customtkinter.CTkOptionMenu(self.alignment_frame,dropdown_font=styles.InterFont,values=["Left","Center","Right"],**styles.normal_menu_style)
        self.vertical_align_label = customtkinter.CTkLabel(self.alignment_frame, text="Vertical Align",text_color=styles.light_gray,font=styles.InterFont)
        self.vertical_align_menu = customtkinter.CTkOptionMenu(self.alignment_frame,dropdown_font=styles.InterFont,values=["Top","Center","Bottom"],**styles.normal_menu_style)

        # GRID PARAMETERS
        self.alignment_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        self.alignment_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        coordinate_axis_label.grid(column=0, row=0, padx=0, pady=0,sticky="e")
        self.coordinate_axis_menu.grid(column=1, row=0, padx=0, pady=0)
        self.rotation_label.grid(column=3, row=0, padx=0, pady=0,sticky="w")
        self.rotation_menu.grid(column=2, row=0, padx=0, pady=0)
        self.horizontal_align_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")
        self.horizontal_align_menu.grid(column=1, row=1, padx=0, pady=0)
        self.vertical_align_label.grid(column=3, row=1, padx=0, pady=0,sticky="w")
        self.vertical_align_menu.grid(column=2, row=1, padx=0, pady=0)


        """ 2 3D_MODEL """
        # ELEMENT PARAMETERS


        self.model_with_label = customtkinter.CTkLabel(self.model_frame, text="Width",text_color=styles.light_gray,font=styles.InterFont)
        self.model_height_label = customtkinter.CTkLabel(self.model_frame, text="Height",text_color=styles.light_gray,font=styles.InterFont)
        self.model_depth_label = customtkinter.CTkLabel(self.model_frame, text="Depth",text_color=styles.light_gray,font=styles.InterFont)
        self.model_width_entry = customtkinter.CTkEntry(self.model_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=styles.InterFont,justify="center")
        self.model_height_entry = customtkinter.CTkEntry(self.model_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=styles.InterFont,justify="center")
        self.model_depth_entry = customtkinter.CTkEntry(self.model_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Depth"),font=styles.InterFont,justify="center")
        self.model_wh_X_label = customtkinter.CTkLabel(self.model_frame, text="X",text_color=styles.white,font=("Inter", 20))
        self.model_hd_X_label = customtkinter.CTkLabel(self.model_frame, text="X",text_color=styles.white,font=("Inter", 20))
        sv.model_resize_boolean = tk.IntVar(value=sv.model_resize_boolean)
        self.resize_checkbox = customtkinter.CTkCheckBox(self.model_frame,variable=sv.model_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**styles.checkbox_style)


        # GRID PARAMETERS
        self.model_frame.grid_columnconfigure([1,3,5,6], weight=1,uniform="a")
        self.model_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

        # PLACEMENT PARAMETERS

        self.model_with_label.grid(column=1, row=0, padx=0, pady=0,sticky="s")
        self.model_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="s")
        self.model_depth_label.grid(column=5, row=0, padx=0, pady=0,sticky="s")

        self.model_width_entry.grid(column=1, row=1, padx=15, pady=0,sticky="n")
        self.model_wh_X_label.grid(column=2, row=1, padx=0, pady=0,sticky="n")
        self.model_height_entry.grid(column=3, row=1, padx=15, pady=0,sticky="n")
        self.model_hd_X_label.grid(column=4, row=1, padx=0, pady=0,sticky="n")
        self.model_depth_entry.grid(column=5, row=1, padx=15, pady=0,sticky="n")
        self.resize_checkbox.grid(column=6, row=1, padx=0, pady=0,sticky="nw")
        


        """ 2 IMAGE """
        # ELEMENT PARAMETERS
        self.image_size_label = customtkinter.CTkLabel(self.image_frame, text="Size",text_color=styles.light_gray,font=styles.InterFont)
        self.image_width_label = customtkinter.CTkLabel(self.image_frame, text="Width",text_color=styles.light_gray,font=styles.InterFont)
        self.image_height_label = customtkinter.CTkLabel(self.image_frame, text="Height",text_color=styles.light_gray,font=styles.InterFont)

        self.image_width_entry = customtkinter.CTkEntry(self.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=styles.InterFont,justify="center")
        self.image_height_entry = customtkinter.CTkEntry(self.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=styles.InterFont,justify="center")
        
        self.size_X_label = customtkinter.CTkLabel(self.image_frame, text="X",text_color=styles.white,font=("Inter", 20))

        sv.autosize_boolean = tk.IntVar(value=1)
        self.autosize_checkbox = customtkinter.CTkCheckBox(self.image_frame,variable=sv.autosize_boolean,command=None, text="Size From Density", onvalue=True, offvalue=False,**styles.checkbox_style)




        self.density_label = customtkinter.CTkLabel(self.image_frame, text="Density",text_color=styles.light_gray,font=styles.InterFont)
        self.density_entry = customtkinter.CTkEntry(self.image_frame, **styles.normal_entry_style,textvariable=customtkinter.StringVar(value="8"),font=styles.InterFont)

        self.image_resolution_label = customtkinter.CTkLabel(self.image_frame, text="Resolution",text_color=styles.light_gray,font=styles.InterFont)
        self.image_resolution_width_entry = customtkinter.CTkEntry(self.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=styles.InterFont,justify="center")
        self.image_resolution_height_entry = customtkinter.CTkEntry(self.image_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=styles.InterFont,justify="center")
        self.resolution_X_label = customtkinter.CTkLabel(self.image_frame, text="X",text_color=styles.white,font=("Inter", 20))

        sv.image_resize_boolean = tk.IntVar(value=sv.image_resize_boolean)
        self.image_resize_checkbox = customtkinter.CTkCheckBox(self.image_frame,variable=sv.image_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**styles.checkbox_style)



        # GRID PARAMETERS
        self.image_frame.grid_columnconfigure([0,1,3,4], weight=1,uniform="a")
        self.image_frame.grid_rowconfigure([0,1,2,3,4], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        self.image_size_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")
        self.image_width_label.grid(column=1, row=0, padx=0, pady=0,sticky="s")
        self.image_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="s")
        self.image_width_entry.grid(column=1, row=1, padx=15, pady=0,sticky="n")
        self.image_height_entry.grid(column=3, row=1, padx=15, pady=0,sticky="n")
        self.size_X_label.grid(column=2, row=1, padx=0, pady=0,sticky="n")
        self.autosize_checkbox.grid(column=4, row=1, padx=0, pady=0,sticky="nw")

        self.density_label.grid(column=4, row=2, padx=0, pady=0,sticky="wn")
        self.density_entry.grid(column=3, row=2, padx=15, pady=0)

        self.image_resolution_label.grid(column=0, row=4, padx=0, pady=0,sticky="e")
        self.image_resolution_width_entry.grid(column=1, row=4, padx=15, pady=0,sticky="n")
        self.image_resolution_height_entry.grid(column=3, row=4, padx=15, pady=0,sticky="n")
        self.resolution_X_label.grid(column=2, row=4, padx=0, pady=0,sticky="n")
        self.image_resize_checkbox.grid(column=4, row=4, padx=0, pady=0,sticky="nw")


        
        """ 2 PARTICLE """
        # ELEMENT PARAMETERS
        self.particle_size_label = customtkinter.CTkLabel(self.particle_frame, text="Particle Size",text_color=styles.light_gray,font=styles.InterFont)
        self.particle_size_entry = customtkinter.CTkEntry(self.particle_frame, **styles.normal_entry_style,textvariable=customtkinter.StringVar(value="1.00"),font=styles.InterFont)
        self.particle_size_entry.bind("<FocusOut>", verify_widget)
        self.particle_size_entry.bind("<Return>", verify_widget)

        
        sv.particle_type = tk.StringVar(value=sv.particle_type)
        self.particle_type_menu = customtkinter.CTkOptionMenu(self.particle_frame, **styles.normal_menu_style,variable=sv.particle_type, values=["dust", "effect"],font=styles.InterFont)
        self.particle_type_label = customtkinter.CTkLabel(self.particle_frame, text="Particle Type",text_color=styles.light_gray,font=styles.InterFont)

        sv.particle_mode = tk.StringVar(value=sv.particle_mode)
        self.particle_mode_menu = customtkinter.CTkOptionMenu(self.particle_frame, **styles.normal_menu_style,variable=sv.particle_mode, values=["Force", "Normal"],font=styles.InterFont)
        self.particle_mode_label = customtkinter.CTkLabel(self.particle_frame, text="Particle Type",text_color=styles.light_gray,font=styles.InterFont)

        self.particle_viewer_entry = customtkinter.CTkEntry(self.particle_frame, **styles.normal_entry_style,textvariable=customtkinter.StringVar(value="@a"),font=styles.InterFont)
        self.particle_viewer_label = customtkinter.CTkLabel(self.particle_frame, text="Viewer",text_color=styles.light_gray,font=styles.InterFont)

        sv.particle_color_boolean = tk.IntVar(value=sv.particle_color_boolean)
        self.particle_color_checkbox = customtkinter.CTkCheckBox(self.particle_frame,variable=sv.particle_color_boolean,command=None, text="ReColor", onvalue=True, offvalue=False,**styles.checkbox_style)
        self.particle_hexcode_label = customtkinter.CTkLabel(self.particle_frame, text="Hexcode",text_color=styles.light_gray,font=styles.InterFont)
        self.particle_hexcode_entry = customtkinter.CTkEntry(self.particle_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="#ff0000"),font=styles.InterFont)

        def ask_color():
            pick_color = CTkColorPicker.AskColor(bg_color=styles.dark_gray,fg_color=styles.dark_gray,button_color=styles.medium_gray,button_hover_color=styles.hover_color,corner_radius=10) # open the color picker
            color = pick_color.get() # get the color string
            self.particle_color_button.configure(fg_color=color)
            self.particle_hexcode_entry.cget("textvariable").set(color)

        self.particle_color_button = customtkinter.CTkButton(self.particle_frame, text=None,command = ask_color,fg_color=styles.medium_gray,hover_color=styles.hover_color,text_color=styles.white,font=styles.InterFont)





        # GRID PARAMETERS
        self.particle_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        self.particle_frame.grid_rowconfigure([0,1,2], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        self.particle_size_label.grid(column=0, row=0, padx=0, pady=0,sticky="e")
        self.particle_size_entry.grid(column=1, row=0, padx=15, pady=0)
        self.particle_type_menu.grid(column=2, row=0, padx=0, pady=0)
        self.particle_type_label.grid(column=3, row=0, padx=0, pady=0,sticky="w")

        self.particle_mode_menu.grid(column=2, row=1, padx=0, pady=0)
        self.particle_mode_label.grid(column=3, row=1, padx=0, pady=0,sticky="w")
        self.particle_viewer_entry.grid(column=1, row=1, padx=15, pady=0)
        self.particle_viewer_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")


        self.particle_color_checkbox.grid(column=3, row=2, padx=0, pady=0,sticky="w")
        self.particle_hexcode_label.grid(column=2, row=2, padx=0, pady=0)
        self.particle_hexcode_entry.grid(column=2, row=2, padx=0, pady=0)
        self.particle_color_button.grid(column=1, row=2, padx=15, pady=0,sticky="we")




        # sv.sequence_boolean = tk.IntVar(value=0)
        # sequence_checkbox = customtkinter.CTkCheckBox(self.input_frame,state="disabled",variable=sv.sequence_boolean,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,text_color=styles.white,border_color=styles.white,border_width=1)
        # sequence_checkbox.grid(column=1, row=2, padx=0, pady=0)
        # sequence_start_Entry = customtkinter.CTkEntry(self.input_frame, **styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="start"))
        # sequence_start_Entry.grid(column=2, row=2, padx=0, pady=0)
        # sequence_end_Entry = customtkinter.CTkEntry(self.input_frame,**styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="end"))
        # sequence_end_Entry.grid(column=3, row=2, padx=0, pady=0)



        """ 1 EXPORT """
        # ELEMENTS
        self.output_path_entry = customtkinter.CTkEntry(self.export_frame, **styles.path_style,textvariable=customtkinter.StringVar(value="Output folder"),font=styles.InterFont)
        self.choose_output_button = customtkinter.CTkButton(self.export_frame, image = self.folder_button_image, text=None, width=20,height=20,command = self.find_output_dialog,fg_color=styles.special_color,hover_color=styles.hover_color,text_color=styles.white,font=styles.InterFont)
        self.export_button = customtkinter.CTkButton(self.export_frame, image = self.export_button_image, text="EXPORT", width=30,height=30,command = self.export,fg_color=styles.special_color,hover_color=styles.hover_color,text_color=styles.white,font=styles.InterFont)


        # GRID
        self.export_frame.grid_columnconfigure([0,1,2,3,4], weight=1,uniform="a")
        self.export_frame.grid_rowconfigure([0], weight=1,uniform="a")

        # PLACEMENT
        self.output_path_entry.grid(column=0, columnspan=3, row=0, padx=10, pady=0,sticky="we")
        self.choose_output_button.grid(column=3, row=0, padx=0, pady=0,sticky="w")
        self.export_button.grid(column=4, row=0, padx=0, pady=0,sticky="w")





        self.launch_frame = customtkinter.CTkFrame(self.config_frame, width=200, height=200, corner_radius=10, fg_color="transparent")
        # launch_frame.pack(side=tk.TOP, expand=True)
        self.launch_button = customtkinter.CTkButton(self.launch_frame, text = 'Convert to .mcfunction file(s)',  command = None,fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
        # launch_button.pack(side=tk.RIGHT, expand=True)


        self.preview_framenumber_label = customtkinter.CTkLabel(self.preview_frame, text = 'frame',text_color=styles.medium_gray,bg_color='black',width=100)
        # self.preview_framenumber_label.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0,)

        self.preview_framenumber = customtkinter.IntVar(value=0)
        self.preview_framenumber_slider = customtkinter.CTkSlider(self.preview_frame,from_=0, to=100,number_of_steps=10,variable=self.preview_framenumber,**styles.disabled_slider_style,command=slider_debouncer.debounced_refresh)
        # self.preview_framenumber_slider.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0)



        self.randomize_button = customtkinter.CTkButton(self.preview_frame, text = 'randomize',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
        self.randomize_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
        self.reset_camera_button = customtkinter.CTkButton(self.preview_frame, text = 'reset',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
        self.reset_camera_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
        # preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=styles.hover_color,text_color=styles.white)
        # preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

        sv.preview_boolean = tk.IntVar(value=sv.preview_boolean)
        self.preview_toggle_checkbox = customtkinter.CTkCheckBox(self.preview_frame,text="Preview",text_color=styles.white,command=None, variable=sv.preview_boolean,onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color='#7a7a7a',hover_color=styles.hover_color,bg_color='black',border_color=styles.white,border_width=1)
        self.preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=0, pady=0)


        # progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
        # progressbar.pack(side=tk.BOTTOM, expand=True)
        # progressbar.start() 

    def find_input_dialog(self):
        initial_directory = fo.get_json_memory("input_path") # Retrive the last path from the JSON file
        dialog_result = tk.filedialog.askopenfilename(initialdir=initial_directory) # Ask for a file
        if dialog_result == "":
            print("User exited file dialog without selecting a file")
            return
        sv.input_path = dialog_result
        fo.update_json_memory("input_path",os.path.dirname(sv.input_path)) # Update the JSON file
        
        self.input_path_entry.cget("textvariable").set(sv.input_path)

        fo.find_file_sequence(sv.input_path) # Search for frames

        # Update the sequence section
        self.sequence_start_Entry.cget("textvariable").set(str(sv.first_frame))
        self.sequence_end_Entry.cget("textvariable").set(str(sv.last_frame))
        self.sequence_detected_label.configure(text = "Frames detected: " + str(sv.last_frame-sv.first_frame+1))

        if sv.first_frame == sv.last_frame: # If the sequence is 1 frame long
            self.sequence_detected_label.configure(text_color='#9c9c9c')
            self.sequence_checkbox.configure(state="disabled") # Disable the checkbox (no more frames to select)
            if self.sequence_checkbox.get() == 1:
                self.sequence_checkbox.toggle()
        else: # If the sequence is more than 1 frame long
            self.sequence_detected_label.configure(text_color=styles.white)
            self.sequence_checkbox.configure(state="normal") # Allow the checkbox to be selected
            if self.sequence_checkbox.get() == 0:
                self.sequence_checkbox.toggle()

        # Change the preview to the first_frame 
        self.preview_framenumber.set(sv.first_frame)

        self.preview_framenumber_slider.configure(from_=sv.first_frame,to=sv.last_frame, number_of_steps=sv.last_frame-1)
        self.preview_framenumber_label.configure(text = str(sv.first_frame))

        self.refresh_preview()

    def export (self):
        print("Export")

        
    def find_output_dialog(self):
        initial_directory = fo.get_json_memory("output_path")
        dialog_result = tk.filedialog.askdirectory(initialdir=initial_directory)
        if dialog_result == "":
            print("User exited file dialog without selecting a folder")
            return
        
        sv.output_path = dialog_result
        fo.update_json_memory("output_path",sv.output_path)

        self.output_path_entry.cget("textvariable").set(sv.output_path)

    def update_sequence_section(self):

        # If the checkbox was checked, 
        if self.sequence_checkbox.get() == 1:
            self.sequence_start_Entry.configure(**styles.normal_entry_style,placeholder_text="start")
            self.sequence_end_Entry.configure(**styles.normal_entry_style,placeholder_text="end")
            # self.preview_frame_slider.pack(side=tk.BOTTOM, expand=False, padx=50, pady=50)
            self.preview_framenumber_slider.configure(**normal_slider_style)


        if self.sequence_checkbox.get() == 0:
            self.sequence_start_Entry.configure(**styles.disabled_entry_style)
            self.sequence_end_Entry.configure(**styles.disabled_entry_style)
            # self.preview_frame_slider.pack_forget()
            self.preview_framenumber_slider.configure(**styles.disabled_slider_style)

    def refresh_preview(self):
        print("refresh_preview")
        if len(sv.sequence_files) == 0: # Stops if no sequence is found.
            return
        sv.loading_done = False


def initialize_interface():
    global UI
    UI = UI()




   








class SliderDebouncer:
    def __init__(self, root, refresh_callback):
        self.root = root
        self.refresh_callback = refresh_callback
        self.delay_time = 500  # 500 milliseconds (0.5 seconds)
        self.after_id = None

    def debounced_refresh(self, value):
        self.preview_framenumber_label.configure(text = str(int(value)))
        # Cancel any previous refresh if the slider was moved again
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        
        # Schedule the new refresh after a delay
        self.after_id = self.root.after(self.delay_time, lambda: self.refresh_preview(value))

    def refresh_preview(self, value):
        # print(f"Preview refreshed with value: {value}")
        # Call your original refresh function
        self.preview_framenumber.set(value)
        self.refresh_callback()



