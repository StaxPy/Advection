import tkinter as tk
import customtkinter
import CTkColorPicker
import os
import backend.file_dialog as fd
import backend.file_processor as fp
import backend.file_multi_processor as fmp
import frontend.preview2 as preview
from shared.variables import *
from PIL import Image
import frontend.color_operations as co






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

        def verify_particle_size_widget(event):
            print("Verifying",event.widget)
            # UI.TkApp.focus_set() # Unfocus


        def request_pygame_update(value):
            PygameTempData.update_requested = True



        def find_input_dialog():
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
            UI.update_particles_cloud() # Generate a new cloud
            UI.update_model_resize() # Update the model resize


        def update_particles_cloud():
            print("refresh_preview")
            path = InputData.path # Charge default path

            if SequenceData.toggle.get() == 1: # If the sequence toggle is on
                path = InputData.sequence_files[int(PygameData.frame.get())]["path"] # Change the path to the selected frame

            if InputData.path: # If the path is not None
                DataParticlesCloud = fp.create_DataParticlesCloud_from_file(path) # Create the DataParticlesCloud
                if DataParticlesCloud is not None: # If the DataParticlesCloud is not None
                    PygameParticles.DataParticlesCloud = fp.create_DataParticlesCloud_from_file(path) # Create the DataParticlesCloud
                    PygameParticles.TexturedParticlesCloud = PygameData.PygameRenderer.DataParticlesCloud_to_TexturedParticlesCloud(PygameParticles.DataParticlesCloud) # Create the TexturedParticlesCloud
                    PygameData.PygameRenderer.refresh_cloud_stats()
                    PygameTempData.update_requested = True


        def update_model_resize():
            ResizeData.width.set(str(round(PygameParticles.DataParticlesCloud.size[0],4)))
            ResizeData.height.set(str(round(PygameParticles.DataParticlesCloud.size[1],4)))
            ResizeData.depth.set(str(round(PygameParticles.DataParticlesCloud.size[2],4)))

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
                UI.preview_frame_slider.configure(**Styles.normal_slider_style)
            else:
                UI.sequence_start_Entry.configure(**Styles.disabled_entry_style)
                UI.sequence_end_Entry.configure(**Styles.disabled_entry_style)
                # preview_frame_slider.pack_forget()
                UI.preview_frame_slider.configure(**Styles.disabled_slider_style)


        def toggle_model_resize_section():

            if ResizeData.width.get() == '1.00000':
                ResizeData.width.set(str(round(PygameParticles.DataParticlesCloud.size[0],4)))
            if ResizeData.height.get() == '1.00000':
                ResizeData.height.set(str(round(PygameParticles.DataParticlesCloud.size[1],4)))
            if ResizeData.depth.get() == '1.00000':
                ResizeData.depth.set(str(round(PygameParticles.DataParticlesCloud.size[2],4)))


            # If ModelResize is checked
            if ResizeData.toggle.get() == 1:
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
            
            
            if InputData.path == None:
                UI.highlight_frame_loop(UI.input_frame)
                # tk.messagebox.showerror("Output folder required", "Please select an output folder",icon="info")
                return
            
            if OutputData.path == None:
                UI.highlight_frame_loop(UI.export_frame)
                return
            if SequenceData.toggle.get() == 0:
                result = fp.write_mcfunction_file(InputData.path,OutputData.path,os.path.splitext(os.path.basename(InputData.path))[0].lower(),Modifiers(PygameParticles.DataParticlesCloud.center,PygameParticles.DataParticlesCloud.size))
                if sv.DEBUG == True:
                    print(result)
            else:
                if InputData.seq_length <= 1:
                    tk.messagebox.showerror("Single file", "Only one file was found in the sequence, exporting anyways. \n Make sure your files have the same name + number",icon="info")
                
                UI.export_button.configure(state="disabled")
                # UI.TkApp.attributes('-disabled', True)
                # UI.TkApp.state = "disabled"


                # UI.TkApp.attributes("-alpha", 0.7)
                multiprocessor = fmp.MultiProcessor_Progress(UI.TkApp,UI.export_button)
                multiprocessor.grab_set()
                multiprocessor.transient(UI.TkApp)
                # multiprocessor.finished_event.bind(toggle_button)
                # fp.write_mcfunction_sequence()
                    

        """ END OF FUNCTION DEFINITIONS """




        TkApp.bind_all('<Button-1>', focus_on_click)





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
        file_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/file_lines_icon.png")),size=(20,20))
        folder_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/folder_open_document_icon.png")),size=(20,20))
        export_button_image = customtkinter.CTkImage(Image.open(os.path.join(os.path.dirname(__file__), "assets/hand_point_right_icon.png")),size=(20,20))
        input_label = customtkinter.CTkLabel(input_frame, text = 'Input File',text_color=Styles.white,font=Styles.InterFont,height=15)
        input_path_entry = customtkinter.CTkEntry(input_frame, **Styles.path_style,textvariable=customtkinter.StringVar(value="OBJ file or PNG/JPG image"),font=Styles.InterFont)
        choose_file_button = customtkinter.CTkButton(input_frame, image = file_button_image, text=None, width=20,height=20,command = find_input_dialog,fg_color=Styles.special_color,hover_color=Styles.hover_color,text_color=Styles.white,font=Styles.InterFont)

        # GRID PARAMETERS
        input_frame.grid_columnconfigure([0,1,2,3], weight=1,uniform="a")
        input_frame.grid_rowconfigure([0,1], weight=1,uniform="a")
        
        # PLACEMENT PARAMETERS
        input_label.grid(column=0, row=0, padx=15, pady=5,sticky="ws",)
        input_path_entry.grid(column=0, row=1, padx=10, pady=0,sticky="wen",columnspan=3)
        choose_file_button.grid(column=3, row=1, padx=0, pady=0,sticky="nw")

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
        ResizeData.width = customtkinter.StringVar(value=ResizeData.width)
        ResizeData.height = customtkinter.StringVar(value=ResizeData.height)
        ResizeData.depth = customtkinter.StringVar(value=ResizeData.depth)
        model_width_entry = customtkinter.CTkEntry(model_frame, **Styles.disabled_entry_style,textvariable=ResizeData.width,font=Styles.InterFont,justify="center")
        model_height_entry = customtkinter.CTkEntry(model_frame, **Styles.disabled_entry_style,textvariable=ResizeData.height,font=Styles.InterFont,justify="center")
        model_depth_entry = customtkinter.CTkEntry(model_frame, **Styles.disabled_entry_style,textvariable=ResizeData.depth,font=Styles.InterFont,justify="center")
        model_wh_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        model_hd_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        ResizeData.toggle = tk.IntVar(value=ResizeData.toggle)
        model_resize_checkbox = customtkinter.CTkCheckBox(model_frame,variable=ResizeData.toggle,command=toggle_model_resize_section, text="Resize", onvalue=True, offvalue=False,**Styles.checkbox_style)


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
        
        def verify_resize(event):
            """
            Verify that the resize values are numbers , and correct it if needed.
            """
            def reset_entry(widget, dim):
                widget.set(str(round(PygameParticles.DataParticlesCloud.size[dim],4)))
            def check_dimension(widget,dim):
                try :
                    float(widget.get())
                except:
                    reset_entry(widget,dim)

            check_dimension(ResizeData.width,0)
            check_dimension(ResizeData.height,1)
            check_dimension(ResizeData.depth,2)

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

        image_width_entry = customtkinter.CTkEntry(image_frame, **Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=Styles.InterFont,justify="center")
        image_height_entry = customtkinter.CTkEntry(image_frame, **Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=Styles.InterFont,justify="center")
        
        size_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=Styles.white,font=("Inter", 20))

        sv.autosize_boolean = tk.IntVar(value=1)
        autosize_checkbox = customtkinter.CTkCheckBox(image_frame,variable=sv.autosize_boolean,command=None, text="Size From Density", onvalue=True, offvalue=False,**Styles.checkbox_style)




        density_label = customtkinter.CTkLabel(image_frame, text="Density",text_color=Styles.light_gray,font=Styles.InterFont)
        density_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=customtkinter.StringVar(value="8"),font=Styles.InterFont)

        image_resolution_label = customtkinter.CTkLabel(image_frame, text="Resolution",text_color=Styles.light_gray,font=Styles.InterFont)
        image_resolution_width_entry = customtkinter.CTkEntry(image_frame, **Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Width"),font=Styles.InterFont,justify="center")
        image_resolution_height_entry = customtkinter.CTkEntry(image_frame, **Styles.disabled_entry_style,textvariable=customtkinter.StringVar(value="Height"),font=Styles.InterFont,justify="center")
        resolution_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=Styles.white,font=("Inter", 20))

        sv.image_resize_boolean = tk.IntVar(value=sv.image_resize_boolean)
        image_resize_checkbox = customtkinter.CTkCheckBox(image_frame,variable=sv.image_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**Styles.checkbox_style)



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
        particle_size_label = customtkinter.CTkLabel(particle_frame, text="Particle Size",text_color=Styles.light_gray,font=Styles.InterFont)
        ParticleData.size = customtkinter.StringVar(value=ParticleData.size)
        particle_size_entry = customtkinter.CTkEntry(particle_frame, **Styles.normal_entry_style,textvariable=ParticleData.size,font=Styles.InterFont)
        particle_size_entry.bind("<FocusOut>", verify_particle_size_widget)
        particle_size_entry.bind("<Return>", verify_particle_size_widget)

        
        sv.particle_type = tk.StringVar(value=sv.particle_type)
        particle_type_menu = customtkinter.CTkOptionMenu(particle_frame, **Styles.normal_menu_style,variable=sv.particle_type, values=["dust", "effect"],font=Styles.InterFont)
        particle_type_label = customtkinter.CTkLabel(particle_frame, text="Particle Type",text_color=Styles.light_gray,font=Styles.InterFont)

        sv.particle_mode = tk.StringVar(value=sv.particle_mode)
        particle_mode_menu = customtkinter.CTkOptionMenu(particle_frame, **Styles.normal_menu_style,variable=sv.particle_mode, values=["Force", "Normal"],font=Styles.InterFont)
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
        preview_frame_slider = customtkinter.CTkSlider(preview_frame,from_=0, to=100,number_of_steps=10,variable=PygameData.frame,**Styles.disabled_slider_style,command=preview_frame_slider_debouncer.debouncer)
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



        



   











