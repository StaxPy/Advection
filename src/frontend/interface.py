import tkinter as tk
import customtkinter
import CTkColorPicker
import CTkToolTip
from os import path as os_path
import src.backend.file_dialog as fd
import src.backend.file_processor as fp
import src.frontend.exporter_dialog as ed
from src.shared.variables import *
import src.shared.color_operations as co
from PIL import Image
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
    



        TkApp.minsize(720, 480)
        TkApp.geometry(f"{AppConstants.WIDTH}x{AppConstants.HEIGHT}")
        TkApp.configure(background=Styles.black)
        TkApp.title("Advection - Animation to particles")
        TkApp.iconbitmap("src/assets/icon.ico")

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
            PygameTempData.update_requested += 1 # Update the preview

        def round_float_to_int(float):
                return int(float) if float.is_integer() else float

        def request_pygame_update(value=None):
            PygameTempData.update_requested += 1



        def choose_input_dialog():
            print("find_input_dialog")
            initial_directory = fd.get_json_memory("input_path") # Retrive the last path from the JSON file
            dialog_result = tk.filedialog.askopenfilename(initialdir=initial_directory, filetypes=[("OBJ or Image Files","*.obj;*.png;*.jpg;*.jpeg")]) # Ask for a file
            if dialog_result == "":
                print("User exited file dialog without selecting a file")
                return
            fd.update_json_memory("input_path",os_path.dirname(dialog_result)) # Update the JSON file
            if os_path.splitext(os_path.basename(dialog_result))[1] != "": # Check if the file has a name and extension
                UI.try_update_input(dialog_result, reset_image_size=True, use_sequence=False)
            else :
                tk.messagebox.showerror("File name or extension is empty", "Please select another file.",icon="info")


        def try_update_input(input_path, reset_image_size=False,use_sequence=True):
            """
            Tries to update the particles cloud with the given input path.

            If it succeeds, it updates the interface and shared variables to the correct mode (model or image).
            """
            if AppConstants.DEBUG:
                print("try_update_input")

            try:
                UI.update_particles_cloud(input_path, reset_image_size,use_sequence) # Try to generate a new cloud
            except Exception as e:
                print(f"{e}, Updating canceled")
            else :
                InputData.path = input_path # Update the global input path
                InputData.extension = os_path.splitext(input_path)[1] # Update the global input extension

                # Update the global input mode
                if InputData.extension == ".obj":
                    InputData.mode = "model"
                    UI.image_frame.grid_forget()
                    UI.model_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
                    PygameTempData.update_requested += 1
                elif InputData.extension == ".png" or InputData.extension == ".jpg" or InputData.extension == ".jpeg":
                    InputData.mode = "image"
                    UI.model_frame.grid_forget()
                    UI.image_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
                    PygameTempData.update_requested += 1
                else:
                    return # Return if the extension is not supported
                

                UI.input_path_entry.cget("textvariable").set(input_path) # Update the input path display
                fd.find_file_sequence(input_path) # Search for frames

                # UI Update


                UI.update_alignment_section() # Update the alignment section
                UI.update_sequence_section() # Update the sequence section
                UI.update_preview_frame_section() # Update the preview frame section




                
                UI.reset_image_size() # Update the image size
                UI.reset_model_resize() # Update the model resize

            


        def update_particles_cloud(input_path=None, reset_image_data=False,use_sequence=True):
            """
            Attemps to create a new DataParticlesCloud and TexturedParticlesCloud.

            If the sequence toggle is on, the fle is the current frame, otherwise it is the input file.

            If it succeeds, it refreshes the cloud stats and requests a renderer update.
            Parameters:
                input_path: The path to the input file.
            """
            
            if AppConstants.DEBUG:
                print("update_particles_cloud")

            if input_path == None: # If no path is given
                input_path = InputData.path # Use the stored input path

            if use_sequence and SequenceData.toggle.get() == 1: # If the sequence toggle is on
                input_path = InputData.sequence_files[int(PygameData.frame.get())]["path"] # Change the path to the selected frame

            if input_path == None: # If no input path is found
                UI.random_cloud()
                return

            try:
                # modifiers = Modifiers()
                newDataParticlesCloud = fp.create_DataParticlesCloud_from_file(input_path,None,reset_image_data ) # Create the DataParticlesCloud
            except Exception as e:
                # print("Error while creating DataParticlesCloud from file")
                tk.messagebox.showerror("Conversion warning", f"{e} Cancelling.",icon="info")
                raise Exception("Error while creating DataParticlesCloud from file",e)

            else: 
                print("DataParticlesCloud created", "Particle center: ",newDataParticlesCloud.center, "Particles count: ",newDataParticlesCloud.count)
                ParticlesCache.DataParticlesCloud = newDataParticlesCloud
                ParticlesCache.TexturedParticlesCloud = PygameData.PygameRenderer.DataParticlesCloud_to_TexturedParticlesCloud(ParticlesCache.DataParticlesCloud) # Create the TexturedParticlesCloud
                PygameData.PygameRenderer.refresh_cloud_stats()
                PygameTempData.update_requested += 2
            
        def random_cloud():
            print("random_cloud")
            InputData.mode = "model"
            # UI.image_frame.grid_forget()
            UI.model_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
            
            AlignmentData.horizontal_align.set('None')
            AlignmentData.vertical_align.set('None')
            ParticlesCache.DataParticlesCloud = fp.create_random_cube_DataParticlesCloud(100,(2,2,2))
            ParticlesCache.TexturedParticlesCloud = PygameData.PygameRenderer.DataParticlesCloud_to_TexturedParticlesCloud(ParticlesCache.DataParticlesCloud) # Create the TexturedParticlesCloud
            UI.reset_model_resize() # Update the model resize
            PygameData.PygameRenderer.refresh_cloud_stats()
            PygameTempData.update_requested += 2

            print(ParticlesCache.DataParticlesCloud.min_pos,ParticlesCache.DataParticlesCloud.max_pos)


        def reset_model_resize():
            width = round(ParticlesCache.DataParticlesCloud.size[0],4)
            height = round(ParticlesCache.DataParticlesCloud.size[1],4)
            depth = round(ParticlesCache.DataParticlesCloud.size[2],4)
            ModelData.width.set(width)
            ModelData.height.set(height)
            ModelData.depth.set(depth)
            ModelData.old_width = width
            ModelData.old_height = height
            ModelData.old_depth = depth

        def reset_image_size():
            """
            Resets the image size based on the input resolution and image density.
            The new image size is calculated by dividing the input resolution by the image density.
            The image size is then set to the new value.
            """
            # Resets the image size
            def round_float_to_int(float):
                return int(float) if float.is_integer() else float
            
            ImageData.width_resolution.set(InputData.image_resolution_width)
            ImageData.old_width_resolution.set(InputData.image_resolution_width)
            ImageData.height_resolution.set(InputData.image_resolution_height)
            ImageData.old_height_resolution.set(InputData.image_resolution_height)
            
            width_density = float(ImageData.width_density.get())
            height_density = float(ImageData.height_density.get())
            new_width = round_float_to_int(InputData.image_resolution_width/width_density)
            new_height = round_float_to_int(InputData.image_resolution_height/height_density)
            ImageData.width.set(new_width)
            ImageData.height.set(new_height)
            ImageData.old_width.set(new_width)
            ImageData.old_height.set(new_height)




        
            

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
            if AppConstants.DEBUG: print("update_sequence_section")
            
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






        def ask_color():
            pick_color = CTkColorPicker.AskColor(initial_color=ParticleData.force_color,bg_color=Styles.dark_gray,fg_color=Styles.dark_gray,button_color=Styles.medium_gray,button_hover_color=Styles.hover_color,corner_radius=10) # open the color picker
            color = pick_color.get() # get the color string
            if color != None:
                UI.particle_hexcode_entry.cget("textvariable").set(color)
                UI.particle_color_button.configure(fg_color=color)
                # UI.particle_hexcode_entry.cget("textvariable").set(color)
                ParticleData.force_color = color
                ParticlesCache.TexturedParticlesCloud.refresh_colors()

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
            if InputData.path == None: # If no input is selected
                UI.highlight_frame_loop(UI.input_frame) # Launch a highlight animation on the input frame
                return
            
            if OutputData.path == None: # If no output is selected
                UI.highlight_frame_loop(UI.export_frame) # Launch a highlight animation on the export frame
                return
            
            modifiers = Modifiers() # 

            # SINGLE EXPORT
            if SequenceData.toggle.get() == 0:
                ed.Single_Exporter_Progress(UI.TkApp,UI.export_button,modifiers)


            # SEQUENCE EXPORT 
            else:
                if InputData.seq_length <= 1: # If the sequence is just 1 frame, warning
                    tk.messagebox.showerror("Single file", "Only one file was found in the sequence, exporting anyways. \n Make sure your files have the same name + number",icon="info")

                # Launch the multiprocessor
                ed.Sequence_Exporter_Progress(UI.TkApp,UI.export_button,modifiers)


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
            # return customtkinter.CTkImage(Image.open(os_path.join(os_path.dirname(__file__), path)),size=size)
            return customtkinter.CTkImage(Image.open(path),size=size)

        file_button_image = load_ctk_image("src/assets/file_lines_icon.png",size=(20,20))
        link_open_button_image = load_ctk_image("src/assets/link_open_icon.png",size=(20,20))
        link_close_button_image = load_ctk_image("src/assets/link_closed_icon.png",size=(20,20))
        folder_button_image = load_ctk_image("src/assets/folder_open_document_icon.png",size=(20,20))
        export_button_image = load_ctk_image("src/assets/hand_point_right_icon.png",size=(20,20))


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
        config_frame.rowconfigure([0,1,2,3,4],weight=1)

        # PLACEMENT PARAMETERS
        input_frame.grid(row = 0, column = 0,sticky="nsew",pady=5,padx=10)
        sequence_frame.grid(row = 1, column = 0,sticky="nsew",pady=5,padx=10)
        alignment_frame.grid(row = 2, column = 0,sticky="nsew",pady=5,padx=10)
        # model_frame.grid(row = 3, column = 0,sticky="nsew",pady=5,padx=10)
        # image_frame.grid(row = 4, column = 0,sticky="nsew",pady=5,padx=10)
        particle_frame.grid(row = 4, column = 0,sticky="nsew",pady=5,padx=10)




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
            if event.widget.cget("state") == "disabled": return
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
            if event.widget.cget("state") == "disabled": return
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
        model_width_entry = customtkinter.CTkEntry(model_frame, **Styles.normal_entry_style,textvariable=ModelData.width,font=Styles.InterFont,justify="center")
        model_height_entry = customtkinter.CTkEntry(model_frame, **Styles.normal_entry_style,textvariable=ModelData.height,font=Styles.InterFont,justify="center")
        model_depth_entry = customtkinter.CTkEntry(model_frame, **Styles.normal_entry_style,textvariable=ModelData.depth,font=Styles.InterFont,justify="center")
        model_wh_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        model_hd_X_label = customtkinter.CTkLabel(model_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        # ModelData.resize_toggle = tk.IntVar(value=ModelData.resize_toggle)
        # model_resize_checkbox = customtkinter.CTkCheckBox(model_frame,variable=ModelData.resize_toggle,command=toggle_model_resize_section, text="Resize", onvalue=True, offvalue=False,**Styles.checkbox_style)
        def lock_model_size_ratio():
            if ModelData.lock_size_ratio == True:
                ModelData.lock_size_ratio = False
                UI.model_size_ratio_button_1.configure(image = UI.link_open_button_image)
                UI.model_size_ratio_button_2.configure(image = UI.link_open_button_image)
            else:
                ModelData.lock_size_ratio = True
                UI.model_size_ratio_button_1.configure(image = UI.link_close_button_image)
                UI.model_size_ratio_button_2.configure(image = UI.link_close_button_image)
        
        
        model_size_ratio_button_1 = customtkinter.CTkButton(model_frame,command=lock_model_size_ratio, image = link_close_button_image, text=None,width=0, **Styles.ratio_button_style)
        model_size_ratio_button_2 = customtkinter.CTkButton(model_frame,command=lock_model_size_ratio, image = link_close_button_image, text=None,width=0, **Styles.ratio_button_style)

        # GRID PARAMETERS
        model_frame.grid_columnconfigure([1,3,5], weight=1,uniform="a")
        model_frame.grid_rowconfigure([0,1], weight=1,uniform="a")

        # PLACEMENT PARAMETERS

        model_with_label.grid(column=1, row=0, padx=0, pady=0,sticky="s")
        model_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="s")
        model_depth_label.grid(column=5, row=0, padx=0, pady=0,sticky="s")

        model_width_entry.grid(column=1, row=1, padx=15, pady=0,sticky="n")
        # model_wh_X_label.grid(column=2, row=1, padx=0, pady=0,sticky="n")
        model_height_entry.grid(column=3, row=1, padx=15, pady=0,sticky="n")
        # model_hd_X_label.grid(column=4, row=1, padx=0, pady=0,sticky="n")
        model_depth_entry.grid(column=5, row=1, padx=15, pady=0,sticky="n")
        # model_resize_checkbox.grid(column=6, row=1, padx=0, pady=0,sticky="nw")
        model_size_ratio_button_1.grid(column=2, row=1, padx=0, pady=0,sticky="nw")
        model_size_ratio_button_2.grid(column=4, row=1, padx=0, pady=0,sticky="nw")
        
        def verify_image_entries(type: str, dim: str):
            if type == "resolution":
                lock_ratio = ImageData.lock_resolution_ratio
                if dim == "width":
                    tested_var = ImageData.width_resolution
                    tested_old_var = ImageData.old_width_resolution
                    default = InputData.image_resolution_width
                elif dim == "height":
                    tested_var = ImageData.height_resolution
                    tested_old_var = ImageData.old_height_resolution
                    default = InputData.image_resolution_height
            elif type == "size":
                lock_ratio = ImageData.lock_size_ratio
                if dim == "width":
                    tested_var = ImageData.width
                    tested_old_var = ImageData.old_width
                    default = UI.round_float_to_int(InputData.image_resolution_width / float(ImageData.width_density.get()))
                elif dim == "height":
                    tested_var = ImageData.height
                    tested_old_var = ImageData.old_height
                    default = UI.round_float_to_int(InputData.image_resolution_height / float(ImageData.height_density.get()))
            elif type == "density":
                lock_ratio = ImageData.lock_size_ratio
                if dim == "width":
                    tested_var = ImageData.width_density
                    tested_old_var = ImageData.old_width_density
                    default = ImageData.default_width_density
                elif dim == "height":
                    tested_var = ImageData.height_density
                    tested_old_var = ImageData.old_height_density
                    default = ImageData.default_height_density
            else:
                raise Exception("Invalid type")

            
            
            try: # Try to convert the entry to a number
                new_value = UI.round_float_to_int(float(numexpr.evaluate(tested_var.get())))
                if new_value == 0: # If the ratio is locked and the value is 0, raise an exception
                    raise ValueError("Trying to set a value to 0")
                if type == "resolution": # Resolution is necessarily a integer
                    new_value = round(new_value)
            except: # If the entry is invalid, reset to default
                new_value = UI.round_float_to_int(default)
            finally: # Finally, update the variable to the result (rounded and eventually result of the operation)
                old_value = float(tested_old_var.get())
                tested_var.set(old_value) # Reset the tested_value so it is not multiplied twice
                multiplier = new_value / old_value # Calculate the multiplier
 
                if not lock_ratio: # If the ratio is not locked
                    if type == "size":
                        if dim == "width":
                            linked_var = ImageData.width_density
                            linked_var_old = ImageData.old_width_density
                        elif dim == "height":
                            linked_var = ImageData.height_density
                            linked_var_old = ImageData.old_height_density
                    elif type == "density":
                        if dim == "width":
                            linked_var = ImageData.width
                            linked_var_old = ImageData.old_width
                        elif dim == "height":
                            linked_var = ImageData.height
                            linked_var_old = ImageData.old_height
                    
                    new_var_value = UI.round_float_to_int(float(tested_var.get()) * multiplier) # Calculate the tested entry
                    new_linked_var_value = UI.round_float_to_int(float(linked_var.get()) / multiplier) # Calculate the linked entry
                    tested_var.set(new_var_value) # Update the tested entry
                    tested_old_var.set(new_var_value)
                    linked_var.set(new_linked_var_value) # Update the linked entry
                    linked_var_old.set(new_linked_var_value)


                else: # If the ratio is locked
                    # Update the linked entries accordingly
                    if type == "size":
                        # Scale size
                        new_width = UI.round_float_to_int(float(ImageData.width.get()) * multiplier)
                        new_height = UI.round_float_to_int(float(ImageData.height.get()) * multiplier)
                        ImageData.width.set(new_width)
                        ImageData.height.set(new_height)
                        ImageData.old_width.set(new_width)
                        ImageData.old_height.set(new_height)

                        # Scale density
                        new_width_density = UI.round_float_to_int(float(ImageData.width_density.get()) / multiplier)
                        new_height_density = UI.round_float_to_int(float(ImageData.height_density.get()) / multiplier)
                        ImageData.width_density.set(new_width_density)
                        ImageData.height_density.set(new_height_density)
                        ImageData.old_width_density.set(new_width_density)
                        ImageData.old_height_density.set(new_height_density)
                    
                    elif type == "density":
                        # Scale density
                        new_width_density = UI.round_float_to_int(float(ImageData.width_density.get()) * multiplier)
                        new_height_density = UI.round_float_to_int(float(ImageData.height_density.get()) * multiplier)
                        ImageData.width_density.set(new_width_density)
                        ImageData.height_density.set(new_height_density)
                        ImageData.old_width_density.set(new_width_density)
                        ImageData.old_height_density.set(new_height_density)

                        # Scale size
                        new_width = UI.round_float_to_int(float(ImageData.width.get()) / multiplier)
                        new_height = UI.round_float_to_int(float(ImageData.height.get()) / multiplier)
                        ImageData.width.set(new_width)
                        ImageData.height.set(new_height)
                        ImageData.old_width.set(new_width)
                        ImageData.old_height.set(new_height)
                    

                    elif type == "resolution":
                        # Scale resolution
                        new_width_resolution = max(round(float(ImageData.width_resolution.get()) * multiplier),8)
                        new_height_resolution = max(round(float(ImageData.height_resolution.get()) * multiplier),8)
                        ImageData.width_resolution.set(new_width_resolution) 
                        ImageData.height_resolution.set(new_height_resolution)
                        ImageData.old_width_resolution.set(new_width_resolution)
                        ImageData.old_height_resolution.set(new_height_resolution)
                        new_width =new_width_resolution/float(ImageData.width_density.get())
                        new_height =new_height_resolution/float(ImageData.height_density.get())
                        ImageData.width.set(new_width)
                        ImageData.height.set(new_height)
                        ImageData.old_width.set(new_width)
                        ImageData.old_height.set(new_height)
                    
                        # Update the particle cloud
                        UI.update_particles_cloud()


            PygameTempData.update_requested += 1

        def verify_model_entries(dim: str):

            lock_ratio = ModelData.lock_size_ratio
            if dim == "width":
                tested_var = ModelData.width
                old_value = ModelData.old_width
                default = ParticlesCache.DataParticlesCloud.size[0]
            elif dim == "height":
                tested_var = ModelData.height
                old_value = ModelData.old_height
                default = ParticlesCache.DataParticlesCloud.size[1]
            elif dim == "depth":
                tested_var = ModelData.depth
                old_value = ModelData.old_depth
                default = ParticlesCache.DataParticlesCloud.size[2]
            else:
                raise Exception("Invalid type")

            def round_float_to_int(float):
                return int(float) if float.is_integer() else float
            
            
            try: # Try to convert the entry to a number
                new_value = round_float_to_int(float(numexpr.evaluate(tested_var.get())))
                if new_value == 0:
                    raise ValueError("Trying to set a value to 0")
            except: # If the entry is invalid, reset to default
                if AppConstants.DEBUG: print("Invalid entry")
                new_value = round_float_to_int(round(default,4))

            finally: # Finally, update the variable to the result (rounded and eventually result of the operation)
                tested_var.set(new_value)
                # Update the tested entry to the formatted value
                width = float(ModelData.width.get())
                height = float(ModelData.height.get())
                depth = float(ModelData.depth.get())

                # Update the old values
                ModelData.old_width = width
                ModelData.old_height = height
                ModelData.old_depth = depth

                if lock_ratio == True: # If the ratio is locked
                    multiplier = new_value / old_value # Calculate the multiplier

                    # Update the linked entries accordingly
                    if dim == "width":
                        ModelData.height.set(round(height * multiplier,4))
                        ModelData.depth.set(round(depth * multiplier,4))
                    elif dim == "height":
                        ModelData.width.set(round(width * multiplier,4))
                        ModelData.depth.set(round(depth * multiplier,4))
                    elif dim == "depth":
                        ModelData.width.set(round(width * multiplier,4))
                        ModelData.height.set(round(height * multiplier,4))

                PygameTempData.update_requested += 1
        
        def verify_model_width_entry(_):
            UI.verify_model_entries("width")
        
        def verify_model_height_entry(_):
            UI.verify_model_entries("height")
        
        def verify_model_depth_entry(_):
            UI.verify_model_entries("depth")

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

            PygameTempData.update_requested += 1

        model_width_entry.bind("<FocusOut>", verify_model_width_entry)
        model_width_entry.bind("<Return>", verify_model_width_entry)
        model_height_entry.bind("<FocusOut>", verify_model_height_entry)
        model_height_entry.bind("<Return>", verify_model_height_entry)
        model_depth_entry.bind("<FocusOut>", verify_model_depth_entry)
        model_depth_entry.bind("<Return>", verify_model_depth_entry)

        """ 2 IMAGE """
        # ELEMENT PARAMETERS
        image_size_label = customtkinter.CTkLabel(image_frame, text="Size",text_color=Styles.light_gray,font=Styles.InterFont)
        image_width_label = customtkinter.CTkLabel(image_frame, text="Width",text_color=Styles.light_gray,font=Styles.InterFont)
        image_height_label = customtkinter.CTkLabel(image_frame, text="Height",text_color=Styles.light_gray,font=Styles.InterFont)


        def verify_image_width(event=None):
            UI.verify_image_entries(type= "size", dim= "width")

        def verify_image_height(event=None):
            UI.verify_image_entries(type= "size", dim= "height")

        def lock_image_size_ratio():
            if AppConstants.DEBUG == True:
                print("Locking image size ratio")
            if ImageData.lock_size_ratio == True:
                ImageData.lock_size_ratio = False
                UI.lock_image_ratio_toggle_button.configure(image = UI.link_open_button_image)
            else:
                ImageData.lock_size_ratio = True
                UI.lock_image_ratio_toggle_button.configure(image = UI.link_close_button_image)

        ImageData.width = customtkinter.StringVar(value=ImageData.width)
        ImageData.height = customtkinter.StringVar(value=ImageData.height)
        ImageData.old_width = customtkinter.StringVar(value=ImageData.old_width)
        ImageData.old_height = customtkinter.StringVar(value=ImageData.old_height)
        image_width_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.width,font=Styles.InterFont,justify="center")
        image_height_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.height,font=Styles.InterFont,justify="center")
        image_width_entry.bind("<FocusOut>", verify_image_width)
        image_width_entry.bind("<Return>", verify_image_width)
        image_height_entry.bind("<FocusOut>", verify_image_height)
        image_height_entry.bind("<Return>", verify_image_height)

        lock_image_ratio_toggle_button = customtkinter.CTkButton(image_frame,command=lock_image_size_ratio, image = link_close_button_image, text=None,width=0,**Styles.ratio_button_style)
        size_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=Styles.white,font=("Inter", 20))

        def verify_density_x_entry(event):
            UI.verify_image_entries(type="density", dim="width")

        def verify_density_y_entry(event):
            UI.verify_image_entries(type="density", dim="height")

        density_label = customtkinter.CTkLabel(image_frame, text="Density",text_color=Styles.light_gray,font=Styles.InterFont)
        density_tooltip = CTkToolTip.CTkToolTip(density_label, message= "Define the size automatically using density (particles per block)",bg_color= Styles.light_gray, text_color= Styles.black, border_width=10,border_color= Styles.light_gray, alpha= 1, delay= 0, x_offset= -170, y_offset= 30, justify= "center",font= Styles.InterFont)
        
        ImageData.width_density = customtkinter.StringVar(value=ImageData.width_density)
        ImageData.height_density = customtkinter.StringVar(value=ImageData.height_density)
        ImageData.old_width_density = customtkinter.StringVar(value=ImageData.old_width_density)
        ImageData.old_height_density = customtkinter.StringVar(value=ImageData.old_height_density)
        
        width_density_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.width_density,font=Styles.InterFont,justify="center")
        height_density_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.height_density,font=Styles.InterFont,justify="center")
        
        width_density_entry.bind("<FocusOut>", verify_density_x_entry)
        width_density_entry.bind("<Return>", verify_density_x_entry)
        height_density_entry.bind("<FocusOut>", verify_density_y_entry)
        height_density_entry.bind("<Return>", verify_density_y_entry)

        image_resolution_label = customtkinter.CTkLabel(image_frame, text="Resolution",text_color=Styles.light_gray,font=Styles.InterFont)

        def update_image_resampling(value):
            ImageData.resampling = value
            UI.update_particles_cloud(InputData.path)

        image_resampling_label = customtkinter.CTkLabel(image_frame, text="Resampling",text_color=Styles.light_gray,font=Styles.InterFont)
        image_resampling_menu = customtkinter.CTkOptionMenu(image_frame, values=["Nearest","Bilinear","Bicubic"], height=25, command=update_image_resampling,**Styles.normal_menu_style)

        def lock_image_resolution_ratio():
            if AppConstants.DEBUG == True:
                print("Locking image resolution ratio")
            if ImageData.lock_resolution_ratio == True:
                ImageData.lock_resolution_ratio = False
                UI.lock_resolution_ratio_toggle_button.configure(image = UI.link_open_button_image)
            else:
                ImageData.lock_resolution_ratio = True
                UI.lock_resolution_ratio_toggle_button.configure(image = UI.link_close_button_image)

            

        # Image resolution variable that is not directly updating the shared variables (until verified)
        ImageData.width_resolution, ImageData.height_resolution = customtkinter.StringVar(value=ImageData.width_resolution), customtkinter.StringVar(value=ImageData.height_resolution)
        ImageData.old_width_resolution, ImageData.old_height_resolution = customtkinter.StringVar(value=ImageData.old_width_resolution), customtkinter.StringVar(value=ImageData.old_height_resolution)
        image_resolution_width_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.width_resolution,font=Styles.InterFont,justify="center")
        image_resolution_height_entry = customtkinter.CTkEntry(image_frame, **Styles.normal_entry_style,textvariable=ImageData.height_resolution,font=Styles.InterFont,justify="center")
        
        lock_resolution_ratio_toggle_button = customtkinter.CTkButton(image_frame,command=lock_image_resolution_ratio, image = link_close_button_image, text=None,width=0,**Styles.ratio_button_style)
        resolution_X_label = customtkinter.CTkLabel(image_frame, text="X",text_color=Styles.white,font=("Inter", 20))
        # update_image_resolution_button = customtkinter.CTkButton(image_frame,command=update_image_resolution, text="Update",width=0,**Styles.normal_button_style)
        # sv.image_resize_boolean = tk.IntVar(value=sv.image_resize_boolean)
        # image_resize_checkbox = customtkinter.CTkCheckBox(image_frame,variable=sv.image_resize_boolean,command=None, text="Resize", onvalue=True, offvalue=False,**Styles.checkbox_style)

        def slider_update_alpha_threshold(value):
            print("slider_update_alpha_threshold", round(value))
            InputData.alpha_threshold = round(value)
            UI.update_particles_cloud(InputData.path)

        def update_alpha_threshold_tooltip(value):
            UI.alpha_threshold_tooltip.configure(message=round(value)) # Update the tooltip

        alpha_threshold_label = customtkinter.CTkLabel(image_frame, text="Alpha threshold",text_color=Styles.light_gray,font=Styles.InterFont)
        alpha_threshold_slider_debouncer = Debouncer(TkApp, 500, update_alpha_threshold_tooltip, slider_update_alpha_threshold)
        alpha_threshold_slider = customtkinter.CTkSlider(image_frame,from_=0, to=254,number_of_steps=256,**Styles.normal_slider_style,command=alpha_threshold_slider_debouncer.debouncer)
        alpha_threshold_tooltip = CTkToolTip.CTkToolTip(alpha_threshold_slider, message= str(InputData.alpha_threshold), delay= 0, x_offset= -20, y_offset= 20, font= Styles.InterFont)


        # GRID PARAMETERS
        image_frame.grid_columnconfigure([0,1,3,4], weight=1,uniform="a")
        image_frame.grid_rowconfigure([0,1,2,3,4,5,6], weight=1,uniform="a")

        # PLACEMENT PARAMETERS
        image_size_label.grid(column=0, row=1, padx=15, pady=0,sticky="e")
        image_width_label.grid(column=1, row=0, padx=0, pady=0,sticky="")
        image_height_label.grid(column=3, row=0, padx=0, pady=0,sticky="")
        image_width_entry.grid(column=1, row=1, padx=0, pady=0,sticky="")
        image_height_entry.grid(column=3, row=1, padx=0, pady=0,sticky="")
        lock_image_ratio_toggle_button.grid(column=2, row=1, rowspan=2, padx=15, pady=0,sticky="ns")

        density_label.grid(column=0, row=2, padx=0, pady=0,sticky="e")
        width_density_entry.grid(column=1, row=2, padx=0, pady=0)
        height_density_entry.grid(column=3, row=2, padx=0, pady=0)

        def verify_image_resolution_X(event=None):
            UI.verify_image_entries(type="resolution", dim="width")

        def verify_image_resolution_Y(event=None):
            UI.verify_image_entries(type="resolution", dim="height")


        image_resolution_width_entry.bind("<FocusOut>", verify_image_resolution_X)
        image_resolution_width_entry.bind("<Return>", verify_image_resolution_X)
        image_resolution_height_entry.bind("<FocusOut>", verify_image_resolution_Y)
        image_resolution_height_entry.bind("<Return>", verify_image_resolution_Y)


        
        image_resolution_label.grid(column=0, row=4, padx=15, pady=0,sticky="e")
        image_resolution_width_entry.grid(column=1, row=4, padx=0, pady=0,sticky="")
        image_resolution_height_entry.grid(column=3, row=4, padx=0, pady=0,sticky="")
        lock_resolution_ratio_toggle_button.grid(column=2, row=4, padx=15, pady=10,sticky="ns")

        image_resampling_label.grid(column=0, row=5, padx=15, pady=0,sticky="en")
        image_resampling_menu.grid(column=1, columnspan=3, row=5, padx=0, pady=0,sticky="wen")
        # update_image_resolution_button.grid(column=4, row=4, padx=0, pady=0,sticky="nw")
        # image_resize_checkbox.grid(column=4, row=4, padx=0, pady=0,sticky="nw")
        alpha_threshold_label.grid(column=0, row=6, padx=0, pady=0,sticky="e")
        alpha_threshold_slider.grid(column=1, columnspan=3, row=6, padx=15, pady=0,sticky="we")




        
        """ 2 PARTICLE """
        # ELEMENT PARAMETERS
        particle_size_label = customtkinter.CTkLabel(particle_frame, text="Particle Size",text_color=Styles.light_gray,font=Styles.InterFont)
        # preview_frame_slider = customtkinter.CTkSlider(preview_frame,from_=0, to=100,number_of_steps=10,variable=PygameData.frame,**Styles.disabled_slider_style,command=preview_frame_slider_debouncer.debouncer)
        particle_size_slider = customtkinter.CTkSlider(particle_frame,from_=0, to=1,number_of_steps=10,variable= customtkinter.DoubleVar(value=1.0),**Styles.normal_slider_style,command=particle_size_slider_moved)
        particle_size_tooltip = CTkToolTip.CTkToolTip(particle_size_slider, message= str(ParticleData.size), delay= 0, x_offset= -20, y_offset= 20, font= Styles.InterFont)

        # particle_size_entry = customtkinter.CTkEntry(particle_frame, **Styles.normal_entry_style,textvariable=ParticleData.size,font=Styles.InterFont)
        # particle_size_entry.bind("<FocusOut>", particle_size_slider_moved)
        # particle_size_entry.bind("<Return>", particle_size_slider_moved)

        def change_particle_type(value):
            PygameData.PygameRenderer.set_particles_texture(value)
            UI.update_particles_cloud(InputData.path)
            if value == "effect" :
                ParticleData.size = 1
                UI.particle_size_slider.grid_forget()
                UI.particle_size_label.grid_forget()
            if value == "dust" :
                UI.particle_size_slider.set(ParticleData.size)
                UI.particle_size_label.grid(column=0, row=0, padx=0, pady=0)
                UI.particle_size_slider.grid(column=1, row=0, padx=15, pady=0)


            
        
        ParticleData.particle_type = tk.StringVar(value=ParticleData.particle_type)
        particle_type_menu = customtkinter.CTkOptionMenu(particle_frame, command= change_particle_type, **Styles.normal_menu_style,variable=ParticleData.particle_type, values=["dust", "effect"],font=Styles.InterFont)
        particle_type_label = customtkinter.CTkLabel(particle_frame, text="Particle Type",text_color=Styles.light_gray,font=Styles.InterFont)

        ParticleData.viewmode = tk.StringVar(value=ParticleData.viewmode)
        particle_mode_menu = customtkinter.CTkOptionMenu(particle_frame, **Styles.normal_menu_style,variable=ParticleData.viewmode, values=["force", "normal"],font=Styles.InterFont)
        particle_mode_label = customtkinter.CTkLabel(particle_frame, text="View mode",text_color=Styles.light_gray,font=Styles.InterFont)

        ParticleData.viewer = tk.StringVar(value=ParticleData.viewer)
        particle_viewer_entry = customtkinter.CTkEntry(particle_frame, **Styles.normal_entry_style,textvariable=ParticleData.viewer,font=Styles.InterFont)
        particle_viewer_label = customtkinter.CTkLabel(particle_frame, text="Viewer",text_color=Styles.light_gray,font=Styles.InterFont)

        def toggle_force_color():
            ParticleData.force_color_toggle = not ParticleData.force_color_toggle
            if ParticleData.force_color_toggle:
                UI.particle_color_button.configure(fg_color=ParticleData.force_color)
            else:
                UI.particle_color_button.configure(fg_color=Styles.medium_gray)
            ParticlesCache.TexturedParticlesCloud.refresh_colors()

        particle_color_checkbox = customtkinter.CTkCheckBox(particle_frame,variable=tk.IntVar(value=False),command=toggle_force_color, text="ReColor", onvalue=True, offvalue=False,**Styles.checkbox_style)
        particle_hexcode_label = customtkinter.CTkLabel(particle_frame, text="Hexcode",text_color=Styles.light_gray,font=Styles.InterFont)
        



        particle_hexcode_entry = customtkinter.CTkEntry(particle_frame, **Styles.disabled_entry_style,textvariable=tk.StringVar(value=ParticleData.force_color),font=Styles.InterFont)

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


        def reset_camera_button_pressed():
            PygameData.PygameRenderer.reset_camera()
            

        # randomize_button = customtkinter.CTkButton(preview_frame, text = 'randomize',  command = None,bg_color='black',fg_color='#7a7a7a',hover_color=Styles.hover_color,text_color=Styles.white)
        # randomize_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)
        reset_camera_button = customtkinter.CTkButton(preview_frame, text = 'Reset camera',  command = reset_camera_button_pressed,bg_color='black',fg_color=Styles.dark_gray,hover_color=Styles.hover_color,text_color=Styles.light_gray)
        reset_camera_button.pack(side=tk.TOP, expand=False, padx=0, pady=10)
        # preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=Styles.hover_color,text_color=Styles.white)
        # preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

        PygameData.toggle_render = tk.IntVar(value=PygameData.toggle_render)
        def toggle_preview():
            
            PygameTempData.update_requested += 1

        preview_toggle_checkbox = customtkinter.CTkCheckBox(preview_frame,text="Preview",text_color=Styles.white,command=toggle_preview, variable=PygameData.toggle_render,onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color=Styles.light_gray,hover_color=Styles.hover_color,bg_color=Styles.almost_black,border_color=Styles.white,border_width=1)
        preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=0, pady=0)


        # progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
        # progressbar.pack(side=tk.BOTTOM, expand=True)
        # progressbar.start() 



        



   











