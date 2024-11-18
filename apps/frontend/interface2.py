import tkinter as tk
import customtkinter
import CTkColorPicker
import CTkToolTip
import os
import backend.file_dialog as fd
import backend.file_processor as fp
import backend.file_multi_processor as fmp
from shared.variables import *
from PIL import Image
import frontend.color_operations as co
import numexpr






class Input():
    path = ""

class Debouncer:
    def __init__(self, root, delay, normal_function, debounced_function):
        self.root = root
        self.normal_function = normal_function
        self.debounced_function = debounced_function
        self.delay_time = delay  # 500 milliseconds = 0.5 seconds
        self.after_id = None

    def debouncer(self, value):
        self.normal_function(value)
        
        # Cancel any previous refresh if the slider was moved again
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        
        # Schedule the new refresh after a delay
        self.after_id = self.root.after(self.delay_time, lambda: self.debounced_function(value))



class UI():

        TkApp = customtkinter.CTk()

        Styles.InterFont = customtkinter.CTkFont(family="Inter", size=12)
        Styles.InterFont_bold = customtkinter.CTkFont(family="Inter", size=12, weight="bold")
    



        TkApp.minsize(1280, 720)  # Set minimum size to 800x600
        TkApp.geometry(f"{sv.WIDTH}x{sv.HEIGHT}")
        TkApp.configure(background=Styles.black)
        TkApp.title("Animation-to-Particles Converter")

        config_frame_border = tk.Frame(TkApp,background=Styles.almost_black)
        config_frame = tk.Frame(config_frame_border,background=Styles.almost_black)
        preview_frame = tk.Frame(TkApp, background=Styles.almost_black)
        export_frame_border = tk.Frame(TkApp, background=Styles.almost_black)
        export_frame = customtkinter.CTkFrame(export_frame_border, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)


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

        highlight_progress = 0

        """ FUNCTIONS """


        def focus_on_click(event):
            if isinstance(event.widget, tk.Widget):
                event.widget.focus_set()  # Focus on selected element

        def particle_size_slider_moved(value):
            if value <= 0.01: # Minimum value
                value = 0.01
            ParticleData.size = round(value,2) # Update the shared variable
            UI.particle_size_tooltip.configure(message=ParticleData.size) # Update the tooltip
            PygameTempData.update_requested = True # Update the preview



        def request_pygame_update(value=None):
            PygameTempData.update_requested = True



        def choose_input_dialog():
            print("find_input_dialog")
            initial_directory = fd.get_json_memory("input_path") # Retrive the last path from the JSON file
            dialog_result = tk.filedialog.askopenfilename(initialdir=initial_directory, filetypes=[("OBJ or Image Files","*.obj;*.png;*.jpg;*.jpeg")]) # Ask for a file
            if dialog_result == "":
                print("User exited file dialog without selecting a file")
                return
            fd.update_json_memory("input_path",os.path.dirname(dialog_result)) # Update the JSON file

            UI.update_input(dialog_result)

        def update_input(input_path):
            InputData.extension = os.path.splitext(input_path)[1] # Update the global input extension

            # Update the global input mode
            if InputData.extension == ".obj":
                InputData.mode = "model"
            elif InputData.extension == ".png" or InputData.extension == ".jpg" or InputData.extension == ".jpeg":
                InputData.mode = "image"
            else:
                return # Return if the extension is not supported
            
            
            InputData.path = input_path # Update the global input path
            UI.input_path_entry.cget("textvariable").set(input_path) # Update the input path display
            fd.find_file_sequence(input_path) # Search for frames

            # UI Update


            UI.update_alignment_section() # Update the alignment section
            UI.update_sequence_section() # Update the sequence section
            UI.update_preview_frame_section() # Update the preview frame section

            # Cloud Update
            ImageData.reset_to_input = True # Ask to reset image data on next cloud generation

            UI.update_particles_cloud() # Generate a new cloud
            
            UI.reset_image_size() # Update the image size
            UI.reset_model_resize() # Update the model resize
            


        def update_particles_cloud():
            print("refresh_preview")
            path = InputData.path # Charge default path

            if SequenceData.toggle.get() == 1: # If the sequence toggle is on
                path = InputData.sequence_files[int(PygameData.frame.get())]["path"] # Change the path to the selected frame

            if InputData.path: # If the path is not None
                try:
                    ParticlesCache.DataParticlesCloud = fp.create_DataParticlesCloud_from_file(path) # Create the DataParticlesCloud
                except:
                    raise Exception("Error while creating DataParticlesCloud from file")
                else: 
                    ParticlesCache.TexturedParticlesCloud = PygameData.PygameRenderer.DataParticlesCloud_to_TexturedParticlesCloud(ParticlesCache.DataParticlesCloud) # Create the TexturedParticlesCloud
                    PygameData.PygameRenderer.refresh_cloud_stats()
                    PygameTempData.update_requested = True


        def reset_model_resize():
            ModelData.width.set(str(round(ParticlesCache.DataParticlesCloud.size[0],4)))
            ModelData.height.set(str(round(ParticlesCache.DataParticlesCloud.size[1],4)))
            ModelData.depth.set(str(round(ParticlesCache.DataParticlesCloud.size[2],4)))

        def reset_image_size():
            # Resets the image size
            def round_float_to_int(float):
                return int(float) if float.is_integer() else float
            
            density = float(ImageData.width_density.get())
            ImageData.resolution_x.set(InputData.image_resolution_x)
            ImageData.resolution_y.set(InputData.image_resolution_y)
            ImageData.width.set(round_float_to_int(InputData.image_resolution_x/density)) # Init the image size
            ImageData.height.set(round_float_to_int(InputData.image_resolution_y/density))

        
            

        def find_output_dialog():
            initial_directory = fd.get_json_memory("output_path")
            dialog_result = tk.filedialog.askdirectory(initialdir=initial_directory)
            if dialog_result == "":
                print("User exited file dialog without selecting a folder")
                return
            
            OutputData.path = dialog_result
            fd.update_json_memory("output_path",OutputData.path)

            UI.output_path_entry.cget("textvariable").set(OutputData.path)
        
        def update_sequence_section():
            """
            Updates the UI components related to the sequence section based on the detected sequence of frames.

            - Sets the start and end entries to the first and last frame numbers.
            - Configures the detected label to show the number of frames detected.
            - Disables the sequence checkbox if only one frame is found and adjusts the UI accordingly.
            - Enables the sequence checkbox if more than one frame is found and ensures it is checked.
            """
            if sv.DEBUG: print("update_sequence_section")
            
            # Update the sequence section
            UI.sequence_start_Entry.cget("textvariable").set(str(InputData.first_frame))
            UI.sequence_end_Entry.cget("textvariable").set(str(InputData.last_frame))
            UI.sequence_detected_label.configure(text = "Frames detected: " + str(InputData.last_frame-InputData.first_frame+1))
            if InputData.first_frame == InputData.last_frame: # If the sequence is 1 frame long
                InputData.last_frame += 1 # To prevent slider error
                UI.sequence_detected_label.configure(text_color=Styles.light_gray)
                # PygameSettings.toggle.set(False)
                if UI.sequence_checkbox.get() == True:
                    UI.sequence_checkbox.toggle() # Unckeck sequence and update the UI
                UI.sequence_checkbox.configure(state="disabled") # Make sequence uncheckable
            else: # If the sequence is more than 1 frame long
                UI.sequence_detected_label.configure(text_color=Styles.white)
                UI.sequence_checkbox.configure(state="normal") # Make sequence uncheckable
                if UI.sequence_checkbox.get() == False:
                    UI.sequence_checkbox.toggle() # Check the sequence and update the UI
            
            UI.toggle_sequence_section() # Toggle the sequence section

        def update_alignment_section():
            if InputData.mode == "model": # If the input mode is model
                # Reset alignement to none
                AlignmentData.horizontal_align.set('None')
                AlignmentData.vertical_align.set('None')
                
                UI.horizontal_align_menu.configure(values=list(AlignmentData.model_horizontal_align_offset.keys()))
                UI.vertical_align_menu.configure(values=list(AlignmentData.model_vertical_align_offset.keys()))
            elif InputData.mode == "image": # If the input mode is image
                # Reset alignement to none
                AlignmentData.horizontal_align.set('Left')
                AlignmentData.vertical_align.set('Bottom')
                
                UI.horizontal_align_menu.configure(values=list(AlignmentData.image_horizontal_align_offset.keys()))
                UI.vertical_align_menu.configure(values=list(AlignmentData.image_vertical_align_offset.keys()))

        def update_preview_frame_section():
            print("update_preview_frame_section")
            # Change the preview to the first_frame 
            PygameData.frame.set(InputData.first_frame)
            UI.preview_frame_slider.configure(from_=InputData.first_frame,to=InputData.last_frame, number_of_steps=InputData.last_frame-1)
            
            UI.slider_update_preview_frame_label(InputData.first_frame)

        

        def toggle_sequence_section():

            
            """
            If the sequence checkbox is checked, this function will enable the start and end sequence entry fields and the sequence slider.
            If the sequence checkbox is unchecked, this function will disable the start and end sequence entry fields and the sequence slider.
            """
            # If sequence is checked
            if UI.sequence_checkbox.get() == 1:
                UI.sequence_start_Entry.configure(**Styles.normal_entry_style,placeholder_text="start")
                UI.sequence_end_Entry.configure(**Styles.normal_entry_style,placeholder_text="end")
                # preview_frame_slider.pack(side=tk.BOTTOM, expand=False, padx=50, pady=50)
                UI.preview_frame_slider.configure(**Styles.normal_preview_slider_style)
            else:
                UI.sequence_start_Entry.configure(**Styles.disabled_entry_style)
                UI.sequence_end_Entry.configure(**Styles.disabled_entry_style)
                # preview_frame_slider.pack_forget()
                UI.preview_frame_slider.configure(**Styles.disabled_preview_slider_style)


        def toggle_model_resize_section():

            if ModelData.width.get() == '1.00000':
                ModelData.width.set(str(round(ParticlesCache.DataParticlesCloud.size[0],4)))
            if ModelData.height.get() == '1.00000':
                ModelData.height.set(str(round(ParticlesCache.DataParticlesCloud.size[1],4)))
            if ModelData.depth.get() == '1.00000':
                ModelData.depth.set(str(round(ParticlesCache.DataParticlesCloud.size[2],4)))


            # If ModelResize is checked
            if ModelData.resize_toggle.get() == 1:
                UI.model_width_entry.configure(**Styles.normal_entry_style)
                UI.model_height_entry.configure(**Styles.normal_entry_style)
                UI.model_depth_entry.configure(**Styles.normal_entry_style)
            else:
                UI.model_width_entry.configure(**Styles.disabled_entry_style)
                UI.model_height_entry.configure(**Styles.disabled_entry_style)
                UI.model_depth_entry.configure(**Styles.disabled_entry_style)

            PygameTempData.update_requested = True



        def ask_color():
            pick_color = CTkColorPicker.AskColor(bg_color=Styles.dark_gray,fg_color=Styles.dark_gray,button_color=Styles.medium_gray,button_hover_color=Styles.hover_color,corner_radius=10) # open the color picker
            color = pick_color.get() # get the color string
            UI.particle_color_button.configure(fg_color=color)
            UI.particle_hexcode_entry.cget("textvariable").set(color)

        def slider_update_preview_frame(frame):
            PygameData.frame.set(frame)
            UI.update_particles_cloud()

        def slider_update_preview_frame_label(frame):
            UI.preview_frame_label.configure(text = str(int(frame)))

        def highlight_frame_loop(frame):
            color = co.interpolate_colors(Styles.special_color,Styles.dark_gray,UI.highlight_progress/100)
            frame.configure(fg_color=color,border_color=color)


            if UI.highlight_progress <= 100:
                UI.highlight_progress += 5

                UI.TkApp.after(16,UI.highlight_frame_loop,frame)
            else:
                UI.highlight_progress = 0
            
        def export ():
            print("Export")


            if InputData.path == None: # If no input is selected
                UI.highlight_frame_loop(UI.input_frame) # Launch a highlight animation on the input frame
                # tk.messagebox.showerror("Output folder required", "Please select an output folder",icon="info")
                return
            
            if OutputData.path == None: # If no output is selected
                UI.highlight_frame_loop(UI.export_frame) # Launch a highlight animation on the export frame
                return
            
            modifiers = Modifiers() # 

            if SequenceData.toggle.get() == 0:
                result = fp.write_mcfunction_file(ParticlesCache.DataParticlesCloud,OutputData.path,os.path.splitext(os.path.basename(InputData.path))[0].lower(),modifiers)
                if sv.DEBUG == True:
                    print(result)
            else:
                if InputData.seq_length <= 1:
                    tk.messagebox.showerror("Single file", "Only one file was found in the sequence, exporting anyways. \n Make sure your files have the same name + number",icon="info")
                
                UI.export_button.configure(state="disabled")
                multiprocessor = fmp.MultiProcessor_Progress(UI.TkApp,UI.export_button,modifiers)
                multiprocessor.grab_set()
                multiprocessor.transient(UI.TkApp)

        def bind_unbind_unfocus_widget(widgets:list[tk.Widget],bind:bool,callback=None):
            for widget in widgets:
                if bind:
                    widget.bind("<Return>",callback)
                    widget.bind("<FocusOut>",callback)
                else:
                    widget.unbind("<Return>")
                    widget.unbind("<FocusOut>")          

        """ END OF FUNCTION DEFINITIONS """




        TkApp.bind_all('<Button-1>', focus_on_click)


        """ 0 ICONS """
        def load_ctk_image(path,size):
            return customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), path)),size=size)

        file_button_image = load_ctk_image("assets/file_lines_icon.png",size=(20,20))
        link_open_button_image = load_ctk_image("assets/link_open_icon.png",size=(20,20))
        link_close_button_image = load_ctk_image("assets/link_closed_icon.png",size=(20,20))
        folder_button_image = load_ctk_image("assets/folder_open_document_icon.png",size=(20,20))
        export_button_image = load_ctk_image("assets/hand_point_right_icon.png",size=(20,20))


        """ 1 MAIN FRAMES """
        # ELEMENT PARAMETERS
        input_frame = customtkinter.CTkFrame(config_frame, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)
        sequence_frame = customtkinter.CTkFrame(config_frame, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)
        alignment_frame = customtkinter.CTkFrame(config_frame, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)
        model_frame = customtkinter.CTkFrame(config_frame, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)
        image_frame = customtkinter.CTkFrame(config_frame, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)
        particle_frame = customtkinter.CTkFrame(config_frame, fg_color=Styles.dark_gray,border_color=Styles.dark_gray,border_width=2)

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
        input_label = customtkinter.CTkLabel(input_frame, text = 'Input File',text_color=Styles.white,font=Styles.InterFont,height=15)
        input_path_entry = customtkinter.CTkEntry(input_frame, **Styles.path_style,textvariable=customtkinter.StringVar(value="OBJ file or PNG/JPG image"),font=Styles.InterFont)
        choose_input_button = customtkinter.CTkButton(input_frame, image = file_button_image, text=None, width=20,height=20,command = choose_input_dialog,fg_color=Styles.special_color,hover_color=Styles.hover_color,text_color=Styles.white,font=Styles.InterFont)

        # GRID PARAMETERS
        input_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        input_frame.grid_rowconfigure([0,1], weight=1,uniform="a")
        
        # PLACEMENT PARAMETERS
        input_label.grid(column=0, row=0, padx=15, pady=5,sticky="ws",)
        input_path_entry.grid(column=0, row=1, padx=10, pady=0,sticky="wen",columnspan=3)
        choose_input_button.grid(column=3, row=1, padx=0, pady=0,sticky="nw")

        """ 2 SEQUENCE """
        # ELEMENT PARAMETERS
        SequenceData.toggle = tk.IntVar(value=SequenceData.toggle)
        sequence_checkbox = customtkinter.CTkCheckBox(sequence_frame,state="disabled",variable=SequenceData.toggle,command=toggle_sequence_section, text="Sequence", onvalue=True, offvalue=False,**Styles.checkbox_style)
        sequence_detected_label = customtkinter.CTkLabel(sequence_frame, text="Frames detected: ~",text_color=Styles.medium_gray,font=Styles.InterFont)
        SequenceData.start = customtkinter.StringVar(value="start")
        SequenceData.end = customtkinter.StringVar(value="end")
        sequence_start_Entry = customtkinter.CTkEntry(sequence_frame, **Styles.disabled_entry_style,textvariable=SequenceData.start,font=Styles.InterFont)
        sequence_end_Entry = customtkinter.CTkEntry(sequence_frame,**Styles.disabled_entry_style,textvariable=SequenceData.end,font=Styles.InterFont)
        def verify_sequence_start_entry(event):
            """
            Verify that the start sequence value is valid (i.e. within the range of the detected sequence and less than the end value), and correct it.
            """
            try :
                value = int(SequenceData.start.get())
                if value >= int(SequenceData.end.get()):
                    SequenceData.start.set(int(SequenceData.end.get())-1)
                elif value < InputData.first_frame :
                    SequenceData.start.set(InputData.first_frame)

            except:
                SequenceData.start.set(InputData.first_frame)
                
                
        
        def verify_sequence_end_entry(event):
            """
            Verify that the end sequence value is valid (i.e. within the range of the detected sequence and more than the start value), and correct it.
            """
            try :
                value = int(SequenceData.end.get())
                if value <= int(SequenceData.start.get()):
                    SequenceData.end.set(int(SequenceData.start.get())+1)
                elif value > InputData.last_frame :
                    SequenceData.end.set(InputData.last_frame)
            except:
                SequenceData.end.set(InputData.last_frame)

        sequence_start_Entry.bind("<FocusOut>", verify_sequence_start_entry)
        sequence_start_Entry.bind("<Return>", verify_sequence_start_entry)
        sequence_end_Entry.bind("<FocusOut>", verify_sequence_end_entry)
        sequence_end_Entry.bind("<Return>", verify_sequence_end_entry)

        



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
        AlignmentData.coordinate_axis = customtkinter.StringVar(value=AlignmentData.coordinate_axis)
        AlignmentData.rotate = customtkinter.StringVar(value=AlignmentData.rotate)
        AlignmentData.horizontal_align = customtkinter.StringVar(value=AlignmentData.horizontal_align)
        AlignmentData.vertical_align = customtkinter.StringVar(value=AlignmentData.vertical_align)

        coordinate_axis_label = customtkinter.CTkLabel(alignment_frame, text="Coordinate Axis",text_color=Styles.light_gray,font=Styles.InterFont)
        coordinate_axis_menu = customtkinter.CTkOptionMenu(alignment_frame,command=request_pygame_update,dropdown_font=Styles.InterFont,values=list(AlignmentData.coordinate_axis_x.keys()),variable=AlignmentData.coordinate_axis,**Styles.normal_menu_style)
        rotation_label = customtkinter.CTkLabel(alignment_frame, text="Rotation",text_color=Styles.light_gray,font=Styles.InterFont)
        rotation_menu = customtkinter.CTkOptionMenu(alignment_frame,command=request_pygame_update,dropdown_font=Styles.InterFont,values=list(AlignmentData.rotate_radians.keys()),variable=AlignmentData.rotate,**Styles.normal_menu_style)
        horizontal_align_label = customtkinter.CTkLabel(alignment_frame, text="Horizontal Align",text_color=Styles.light_gray,font=Styles.InterFont)
        horizontal_align_menu = customtkinter.CTkOptionMenu(alignment_frame,command=request_pygame_update,dropdown_font=Styles.InterFont,values=list(AlignmentData.horizontal_align_offset.keys()),variable=AlignmentData.horizontal_align,**Styles.normal_menu_style)
        vertical_align_label = customtkinter.CTkLabel(alignment_frame, text="Vertical Align",text_color=Styles.light_gray,font=Styles.InterFont)
        vertical_align_menu = customtkinter.CTkOptionMenu(alignment_frame,command=request_pygame_update,dropdown_font=Styles.InterFont,values=list(AlignmentData.vertical_align_offset.keys()),variable=AlignmentData.vertical_align,**Styles.normal_menu_style)

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


        model_with_label = customtkinter.CTkLabel(model_frame, text="Width",text_color=Styles.light_gray,font=Styles.InterFont)
        model_height_label = customtkinter.CTkLabel(model_frame, text="Height",text_color=Styles.light_gray,font=Styles.InterFont)
        model_depth_label = customtkinter.CTkLabel(model_frame, text="Depth",text_color=Styles.light_gray,font=Styles.InterFont)
        ModelData.width = customtkinter.StringVar(value=ModelData.width)
        ModelData.height = customtkinter.StringVar(value=ModelData.height)
        ModelData.depth = customtkinter.StringVar(value=ModelData.depth)
        model_width_entry = customtkinter.CTkEntry(model_frame, **Styles.disabled_entry_style,textvariable=ModelData.width,font=Styles.InterFont,justify="center")
        model_height_entry = customtkinter.CTkEntry(model_frame, **Styles.disabled_entry_style,textvariable=ModelData.height,font=Styles.InterFont,justify="center")
        model_depth_entry = customtkinter.CTkEntry(model_frame, **Styles.disabled_entry_style,textvariable=ModelData.depth,font=Styles.InterFont,justify="center")
        model_wh_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        model_hd_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        ModelData.resize_toggle = tk.IntVar(value=ModelData.resize_toggle)
        model_resize_checkbox = customtkinter.CTkCheckBox(model_frame,variable=ModelData.resize_toggle,command=toggle_model_resize_section, text="Resize", onvalue=True, offvalue=False,**Styles.checkbox_style)


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
        model_resize_checkbox.grid(column=6, row=1, padx=0, pady=0,sticky="nw")
        
        def verify_resize(_):
            """
            Verify that the resize values are numbers , and correct it if needed.
            """
            def reset_entry(var, dim):
                var.set(str(round(ParticlesCache.DataParticlesCloud.size[dim],4)))
            def check_dimension(var,dim):
                try :
                    float(numexpr.evaluate(var.get()))
                except:
                    reset_entry(var,dim)

            check_dimension(ModelData.width,0)
            check_dimension(ModelData.height,1)
            check_dimension(ModelData.depth,2)

            PygameTempData.update_requested = True

        model_width_entry.bind("<FocusOut>", verify_resize)
        model_width_entry.bind("<Return>", verify_resize)
        model_height_entry.bind("<FocusOut>", verify_resize)
        model_height_entry.bind("<Return>", verify_resize)
        model_depth_entry.bind("<FocusOut>", verify_resize)
        model_depth_entry.bind("<Return>", verify_resize)

        """ 2 IMAGE """
        # ELEMENT PARAMETERS
        image_size_label = customtkinter.CTkLabel(image_frame, text="Size",text_color=Styles.light_gray,font=Styles.InterFont)
        image_width_label = customtkinter.CTkLabel(image_frame, text="Width",text_color=Styles.light_gray,font=Styles.InterFont)
        image_height_label = customtkinter.CTkLabel(image_frame, text="Height",text_color=Styles.light_gray,font=Styles.InterFont)


        def verify_image_width(event=None):
            UI.verify_image_entries(type= "image_size", dim= "X",widget=event.widget)

        def verify_image_height(event=None):
            UI.verify_image_entries(type= "image_size", dim= "Y",widget=event.widget)

        def lock_image_size_ratio():
            if sv.DEBUG == True:
                print("Locking image size ratio")
            if ImageData.lock_size_ratio == True:
                ImageData.lock_size_ratio = False
                UI.lock_image_ratio_toggle_button.configure(image = UI.link_open_button_image)
            else:
                ImageData.lock_size_ratio = True
                UI.lock_image_ratio_toggle_button.configure(image = UI.link_close_button_image)

        ImageData.width = customtkinter.StringVar(value=ImageData.width)
        ImageData.height = customtkinter.StringVar(value=ImageData.height)
        image_width_entry = customtkinter.CTkEntry(image_frame, **Styles.disabled_entry_style,textvariable=ImageData.width,font=Styles.InterFont,justify="center")
        image_height_entry = customtkinter.CTkEntry(image_frame, **Styles.disabled_entry_style,textvariable=ImageData.height,font=Styles.InterFont,justify="center")
        image_width_entry.bind("<FocusOut>", verify_image_width)
        image_width_entry.bind("<Return>", verify_image_width)
        image_height_entry.bind("<FocusOut>", verify_image_height)
        image_height_entry.bind("<Return>", verify_image_height)

        lock_image_ratio_toggle_button = customtkinter.CTkButton(image_frame,command=lock_image_size_ratio, image = link_close_button_image, text=None,width=0,**Styles.icon_button_style)
        size_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=Styles.white,font=("Inter", 20))

        def density_toggle():
            
            if UI.density_checkbox.get():
                ImageData.autosize = True
                UI.width_density_entry.configure(**Styles.normal_entry_style)
                UI.height_density_entry.configure(**Styles.normal_entry_style)
                UI.image_height_entry.configure(**Styles.disabled_entry_style)
                UI.image_width_entry.configure(**Styles.disabled_entry_style)
            else:
                ImageData.autosize = False
                UI.width_density_entry.configure(**Styles.disabled_entry_style)
                UI.height_density_entry.configure(**Styles.disabled_entry_style)
                UI.image_height_entry.configure(**Styles.normal_entry_style)
                UI.image_width_entry.configure(**Styles.normal_entry_style)

        density_checkbox = customtkinter.CTkCheckBox(image_frame,command=density_toggle, text=None, width=20, variable=customtkinter.IntVar(value=1), onvalue=True, offvalue=False,**Styles.checkbox_style)
        density_tooltip = CTkToolTip.CTkToolTip(density_checkbox, message= "Define the size automatically using density (particles per block)",bg_color= Styles.light_gray, text_color= Styles.black, border_width=10,border_color= Styles.light_gray, alpha= 1, delay= 0, x_offset= -170, y_offset= 30, justify= "center",font= Styles.InterFont)

        def verify_density_x_entry(event):
            """
            Verify that the density is a float and trigger a preview update
            """
            UI.verify_image_entries(type="image_density", dim="X",widget=event.widget)

            return
            try :
                new_width_density = float(numexpr.evaluate(ImageData.width_density.get()))
                new_height_density = float(numexpr.evaluate(ImageData.height_density.get()))
                if new_width_density.is_integer(): # Remove the .0 when the number is round
                    new_width_density = int(new_width_density)
                if new_height_density.is_integer(): # Remove the .0 when the number is round
                    new_height_density = int(new_height_density)
            except:
                new_width_density, new_height_density = ImageData.default_density
            else: # Update the image
                ImageData.width.set(float(InputData.image_resolution_x / new_width_density))
                ImageData.height.set(float(InputData.image_resolution_y / new_height_density))
            finally:
                ImageData.width_density.set(new_width_density)
                ImageData.height_density.set(new_height_density)
            PygameTempData.update_requested = True

        def verify_density_y_entry(event):
            UI.verify_image_entries(type="image_density", dim="Y",widget=event.widget)

        density_label = customtkinter.CTkLabel(image_frame, text="Density",text_color=Styles.light_gray,font=Styles.InterFont)
        ImageData.width_density = customtkinter.StringVar(value=ImageData.width_density)
        width_density_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.width_density,font=Styles.InterFont,justify="center")
        width_density_entry.bind("<FocusOut>", verify_density_x_entry)
        width_density_entry.bind("<Return>", verify_density_x_entry)
        ImageData.height_density = customtkinter.StringVar(value=ImageData.height_density)
        height_density_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.height_density,font=Styles.InterFont,justify="center")
        height_density_entry.bind("<FocusOut>", verify_density_y_entry)
        height_density_entry.bind("<Return>", verify_density_y_entry)

        image_resolution_label = customtkinter.CTkLabel(image_frame, text="Resolution",text_color=Styles.light_gray,font=Styles.InterFont)

        # ImageData.resolution = customtkinter.StringVar(value=ImageData.resolution[0]),customtkinter.StringVar(value=ImageData.resolution[1])
        def update_image_resolution():
            print("Updating image resolution")
            UI.verify_image_resolution_X()
            UI.verify_image_resolution_Y()
            UI.update_particles_cloud()

        def lock_image_resolution_ratio():
            if sv.DEBUG == True:
                print("Locking image resolution ratio")
            if ImageData.lock_resolution_ratio == True:
                ImageData.lock_resolution_ratio = False
                UI.lock_resolution_ratio_toggle_button.configure(image = UI.link_open_button_image)
            else:
                ImageData.lock_resolution_ratio = True
                UI.lock_resolution_ratio_toggle_button.configure(image = UI.link_close_button_image)

            

        # Image resolution variable that is not directly updating the shared variables (until verified)
        ImageData.resolution_x, ImageData.resolution_y = customtkinter.StringVar(value=ImageData.resolution_x), customtkinter.StringVar(value=ImageData.resolution_y)
        image_resolution_width_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.resolution_x,font=Styles.InterFont,justify="center")
        image_resolution_height_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.resolution_y,font=Styles.InterFont,justify="center")
        
        lock_resolution_ratio_toggle_button = customtkinter.CTkButton(image_frame,command=lock_image_resolution_ratio, image = link_close_button_image, text=None,width=0,**Styles.icon_button_style)
        resolution_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        image_resolution_update_button = customtkinter.CTkButton(image_frame,command=update_image_resolution, text="Update",width=0,**Styles.normal_button_style)
        # sv.image_resize_boolean = tk.IntVar(value=sv.image_resize_boolean)
        # image_resize_checkbox = customtkinter.CTkCheckBox(image_frame,variable=sv.image_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**Styles.checkbox_style)



        # GRID PARAMETERS
        image_frame.grid_columnconfigure([0,1,3,4], weight=1,uniform="a")
        image_frame.grid_rowconfigure([0,1,2,3,4], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        image_size_label.grid(column=0, row=1, padx=0, pady=0,sticky="e")
        image_width_label.grid(column=1, row=0, padx=0, pady=0,sticky="s")
        image_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="s")
        image_width_entry.grid(column=1, row=1, padx=15, pady=0,sticky="n")
        image_height_entry.grid(column=3, row=1, padx=15, pady=0,sticky="n")
        lock_image_ratio_toggle_button.grid(column=2, row=1, rowspan=2, padx=0, pady=0,sticky="ns")
        density_checkbox.grid(column=4, row=2, padx=0, pady=0,sticky="w")

        density_label.grid(column=0, row=2, padx=0, pady=0,sticky="e")
        width_density_entry.grid(column=1, row=2, padx=15, pady=0)
        height_density_entry.grid(column=3, row=2, padx=15, pady=0)

        def verify_image_resolution_X(event=None):
            UI.verify_image_entries(type="image_resolution", dim="X",widget=event.widget)

        def verify_image_resolution_Y(event=None):
            UI.verify_image_entries(type="image_resolution", dim="Y",widget=event.widget)


        def verify_image_entries(type: str, dim: str, widget: tk.Widget = None):
            if sv.DEBUG:
                print("Verifying :" + type + " " + dim)

            if widget.cget("state") == "disabled": # Skip if the widget is disabled
                return
            
            if type == "image_resolution":
                lock_ratio = ImageData.lock_resolution_ratio
                ratio = ImageData.resolution_ratio
                if dim == "X":
                    tested_var = ImageData.resolution_x
                    linked_var = ImageData.resolution_y
                    default = InputData.image_resolution_x
                elif dim == "Y":
                    tested_var = ImageData.resolution_y
                    linked_var = ImageData.resolution_x
                    default = InputData.image_resolution_y
            elif type == "image_size":
                lock_ratio = ImageData.lock_size_ratio
                ratio = ImageData.size_ratio
                if dim == "X":
                    tested_var = ImageData.width
                    linked_var = ImageData.height
                    default = InputData.image_resolution_x / float(ImageData.width_density.get())
                elif dim == "Y":
                    tested_var = ImageData.height
                    linked_var = ImageData.width
                    default = InputData.image_resolution_y / float(ImageData.height_density.get())
            elif type == "image_density":
                lock_ratio = ImageData.lock_size_ratio
                ratio = ImageData.size_ratio
                if dim == "X":
                    tested_var = ImageData.width_density
                    linked_var = ImageData.height_density
                    default = ImageData.default_density[0]
                elif dim == "Y":
                    tested_var = ImageData.height_density
                    linked_var = ImageData.width_density
                    default = ImageData.default_density[1]
            else:
                raise Exception("Invalid type")

            def round_float_to_int(float):
                return int(float) if float.is_integer() else float
            
            try: # Try to convert the entry to a number
                new_value = round_float_to_int(float(numexpr.evaluate(tested_var.get())))
                if type == "image_resolution":
                    new_value = round(new_value)
            except: # If the entry is invalid, reset to default
                if sv.DEBUG: print("Invalid entry")
                new_value = round_float_to_int(default)

            finally: # Finally, update the variable to the result (rounded and eventually result of the operation)

                tested_var.set(new_value) # Update the tested entry to the formatted value
                if lock_ratio: # If the ratio is locked
                    if dim == "X": # Update the Y dimension
                        if sv.DEBUG: print("locked, updating linked_var to ",new_value,"/",ratio)
                        new_linked_value = round_float_to_int(new_value/ratio)
                        if new_value.is_integer(): # Remove the .0 when the number is round
                            new_value = int(new_value)
                        if type == "image_resolution": new_linked_value = round(new_linked_value)
                        linked_var.set(new_linked_value)
                    elif dim == "Y": # Update the X dimension
                        if sv.DEBUG: print("locked, updating linked_var to ",new_value,"*",ratio)
                        new_linked_value = round_float_to_int(new_value*ratio)
                        if type == "image_resolution": new_linked_value = round(new_linked_value)
                        linked_var.set(new_linked_value)
                else: # If the ratio is not locked, update the ratio
                    if type == "image_resolution":
                        ImageData.resolution_ratio = int(ImageData.resolution_x.get()) / int(ImageData.resolution_y.get()) 
                    elif type == "image_size":
                        ImageData.size_ratio = float(ImageData.width.get()) / float(ImageData.height.get())
                    elif type == "image_density":
                        ImageData.size_ratio = float(ImageData.width_density.get()) / float(ImageData.height_density.get())

                if type == "image_density":
                    ImageData.width.set(round_float_to_int(float(InputData.image_resolution_x / float(ImageData.width_density.get()))))
                    ImageData.height.set(round_float_to_int(float(InputData.image_resolution_y / float(ImageData.height_density.get()))))
                elif type == "image_size":
                    ImageData.width_density.set(round_float_to_int(float(InputData.image_resolution_x / float(ImageData.width.get()))))
                    ImageData.height_density.set(round_float_to_int(float(InputData.image_resolution_y / float(ImageData.height.get()))))

            PygameTempData.update_requested = True



        image_resolution_width_entry.bind("<FocusOut>", verify_image_resolution_X)
        image_resolution_width_entry.bind("<Return>", verify_image_resolution_X)
        image_resolution_height_entry.bind("<FocusOut>", verify_image_resolution_Y)
        image_resolution_height_entry.bind("<Return>", verify_image_resolution_Y)

        
        
        image_resolution_label.grid(column=0, row=4, padx=0, pady=0,sticky="e")
        image_resolution_width_entry.grid(column=1, row=4, padx=15, pady=0,sticky="n")
        image_resolution_height_entry.grid(column=3, row=4, padx=15, pady=0,sticky="n")
        lock_resolution_ratio_toggle_button.grid(column=2, row=4, padx=0, pady=0,sticky="n")
        image_resolution_update_button.grid(column=4, row=4, padx=0, pady=0,sticky="nw")
        # image_resize_checkbox.grid(column=4, row=4, padx=0, pady=0,sticky="nw")


        
        """ 2 PARTICLE """
        # ELEMENT PARAMETERS
        particle_size_label = customtkinter.CTkLabel(particle_frame, text="Particle Size",text_color=Styles.light_gray,font=Styles.InterFont)
        # preview_frame_slider = customtkinter.CTkSlider(preview_frame,from_=0, to=100,number_of_steps=10,variable=PygameData.frame,**Styles.disabled_slider_style,command=preview_frame_slider_debouncer.debouncer)
        particle_size_slider = customtkinter.CTkSlider(particle_frame,from_=0, to=1,number_of_steps=10,variable= customtkinter.DoubleVar(value=1.0),**Styles.normal_slider_style,command=particle_size_slider_moved)
        particle_size_tooltip = CTkToolTip.CTkToolTip(particle_size_slider, message= str(ParticleData.size), delay= 0, x_offset= -20, y_offset= 20, font= Styles.InterFont)

        # particle_size_entry = customtkinter.CTkEntry(particle_frame, **Styles.normal_entry_style,textvariable=ParticleData.size,font=Styles.InterFont)
        # particle_size_entry.bind("<FocusOut>", particle_size_slider_moved)
        # particle_size_entry.bind("<Return>", particle_size_slider_moved)

        
        sv.particle_type = tk.StringVar(value=sv.particle_type)
        particle_type_menu = customtkinter.CTkOptionMenu(particle_frame, **Styles.normal_menu_style,variable=sv.particle_type, values=["dust", "effect"],font=Styles.InterFont)
        particle_type_label = customtkinter.CTkLabel(particle_frame, text="Particle Type",text_color=Styles.light_gray,font=Styles.InterFont)

        ParticleData.viewmode = tk.StringVar(value=ParticleData.viewmode)
        particle_mode_menu = customtkinter.CTkOptionMenu(particle_frame, **Styles.normal_menu_style,variable=ParticleData.viewmode, values=["Force", "Normal"],font=Styles.InterFont)
        particle_mode_label = customtkinter.CTkLabel(particle_frame, text="Particle Type",text_color=Styles.light_gray,font=Styles.InterFont)

        particle_viewer_entry = customtkinter.CTkEntry(particle_frame, **Styles.normal_entry_style,textvariable=customtkinter.StringVar(value="@a"),font=Styles.InterFont)
        particle_viewer_label = customtkinter.CTkLabel(particle_frame, text="Viewer",text_color=Styles.light_gray,font=Styles.InterFont)

        sv.particle_color_boolean = tk.IntVar(value=sv.particle_color_boolean)
        particle_color_checkbox = customtkinter.CTkCheckBox(particle_frame,variable=sv.particle_color_boolean,command=None, text="ReColor", onvalue=True, offvalue=False,**Styles.checkbox_style)
        particle_hexcode_label = customtkinter.CTkLabel(particle_frame, text="Hexcode",text_color=Styles.light_gray,font=Styles.InterFont)
        particle_hexcode_entry = customtkinter.CTkEntry(particle_frame, **Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="#ff0000"),font=Styles.InterFont)

        particle_color_button = customtkinter.CTkButton(particle_frame, text=None,command = ask_color,fg_color=Styles.medium_gray,hover_color=Styles.hover_color,text_color=Styles.white,font=Styles.InterFont)
        







        # GRID PARAMETERS
        particle_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        particle_frame.grid_rowconfigure([0,1,2], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        particle_size_label.grid(column=0, row=0, padx=0, pady=0,sticky="e")
        particle_size_slider.grid(column=1, row=0, padx=15, pady=0)
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
        # sequence_checkbox = customtkinter.CTkCheckBox(input_frame,state="disabled",variable=SequenceData.toggle,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,text_color=Styles.white,border_color=Styles.white,border_width=1)
        # sequence_checkbox.grid(column=1, row=2, padx=0, pady=0)
        # UI.sequence_start_Entry = customtkinter.CTkEntry(input_frame, **Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="start"))
        # UI.sequence_start_Entry.grid(column=2, row=2, padx=0, pady=0)
        # UI.sequence_end_Entry = customtkinter.CTkEntry(input_frame,**Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="end"))
        # UI.sequence_end_Entry.grid(column=3, row=2, padx=0, pady=0)



        """ 1 EXPORT """
        # ELEMENTS
        output_path_entry = customtkinter.CTkEntry(export_frame, **Styles.path_style,textvariable=customtkinter.StringVar(value="Output folder"),font=Styles.InterFont)
        choose_output_button = customtkinter.CTkButton(export_frame, image = folder_button_image, text=None, width=20,height=20,command = find_output_dialog,fg_color=Styles.special_color,hover_color=Styles.hover_color,text_color=Styles.white,font=Styles.InterFont)
        export_button = customtkinter.CTkButton(export_frame, image = export_button_image, text="EXPORT", width=30,height=30,command = export,**Styles.normal_special_button_style,font=Styles.InterFont_bold)


        # GRID
        export_frame.grid_columnconfigure([0,1,2,3,4], weight=1,uniform="a")
        export_frame.grid_rowconfigure([0], weight=1,uniform="a")

        # PLACEMENT
        output_path_entry.grid(column=0, columnspan=3, row=0, padx=10, pady=0,sticky="we")
        choose_output_button.grid(column=3, row=0, padx=0, pady=0,sticky="w")
        export_button.grid(column=4, row=0, padx=0, pady=0,sticky="w")



        preview_frame_label = customtkinter.CTkLabel(preview_frame, text = 'frame',text_color=Styles.medium_gray,bg_color=Styles.almost_black,width=100)
        preview_frame_label.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0,)

        PygameData.frame = customtkinter.IntVar(value=0)
        preview_frame_slider_debouncer = Debouncer(TkApp, 500, slider_update_preview_frame_label, slider_update_preview_frame)
        preview_frame_slider = customtkinter.CTkSlider(preview_frame,from_=0, to=100,number_of_steps=10,variable=PygameData.frame,**Styles.disabled_preview_slider_style,command=preview_frame_slider_debouncer.debouncer)
        preview_frame_slider.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0)



        randomize_button = customtkinter.CTkButton(preview_frame, text = 'randomize',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=Styles.hover_color,text_color=Styles.white)
        randomize_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
        reset_camera_button = customtkinter.CTkButton(preview_frame, text = 'reset',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=Styles.hover_color,text_color=Styles.white)
        reset_camera_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
        # preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=Styles.hover_color,text_color=Styles.white)
        # preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

        PygameData.toggle = tk.IntVar(value=sv.preview_boolean)
        def toggle_preview():
            PygameTempData.update_requested = True

        preview_toggle_checkbox = customtkinter.CTkCheckBox(preview_frame,text="Preview",text_color=Styles.white,command=toggle_preview, variable=PygameData.toggle,onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color=Styles.light_gray,hover_color=Styles.hover_color,bg_color=Styles.almost_black,border_color=Styles.white,border_width=1)
        preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=0, pady=0)


        # progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
        # progressbar.pack(side=tk.BOTTOM, expand=True)
        # progressbar.start() 



        



   











