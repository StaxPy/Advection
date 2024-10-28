import tkinter as tk
import customtkinter
import os, random
import threading
import backend.file_operations as fo
import backend.converter as converter
import frontend.preview as preview
import shared.variables as sv
import multiprocessing as mp



def initialize_interface():
    global TkApp, config_frame, preview_frame
    TkApp = customtkinter.CTk()

    TkApp.minsize(800, 600)  # Set minimum size to 800x600
    TkApp.geometry(f"{sv.WIDTH}x{sv.HEIGHT}")
    TkApp.configure(bg="#2b2b2b")
    TkApp.title("Advanced Particle Converter")

    config_frame = tk.Frame(TkApp,background="#181818")
    preview_frame = tk.Frame(TkApp, background="#181818")
    export_frame = tk.Frame(TkApp, background="#dd0c0c")

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
    TkApp.rowconfigure((0), weight=3,uniform="a")
    TkApp.rowconfigure((1), weight=1,uniform="a")

    # # canvas.pack(side=tk.RIGHT,fill=tk.NONE,expand=False)

    # pygame_frame = tk.Frame(canvas, background="#ff0000")
    # pygame_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    
    config_frame.grid(row = 0, column = 0,sticky="nsew",rowspan=2)
    preview_frame.grid(row=0, column=1, sticky="nsew")
    export_frame.grid(row = 1, column = 1,sticky="nsew")

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
    global input_frame, output_frame, input_path_label, output_path_label, choose_file_button, sequence_checkbox, sequence_start_Entry, sequence_end_Entry, preview_framenumber_slider, preview_framenumber_label
    global disabled_entry_style, normal_entry_style, hover_color, disabled_slider_style, normal_slider_style, preview_framenumber, InterFont
    hover_color = "#52c9af"
    InterFont = customtkinter.CTkFont(family="Inter", size=10)

    # Debouncer that wraps the original refresh function
    slider_debouncer = SliderDebouncer(TkApp, refresh_preview)

    disabled_entry_style = {"state":"disabled","fg_color":'#3d3d3d',"placeholder_text_color":'#585858',"text_color":'#131313',"border_color":'#3d3d3d'}
    normal_entry_style = {"state":"normal","fg_color":'#202020',"placeholder_text_color":'#ffffff',"border_color":'#3d3d3d',"text_color":'white'}

    input_frame = customtkinter.CTkFrame(config_frame, corner_radius=10, fg_color='#313131')
    input_frame.pack(side=tk.TOP, expand=True,fill='x',padx=50)
    input_frame.grid_columnconfigure([0,1,2,3], weight=1)

    input_frame.grid_rowconfigure(0, weight=1)
    input_frame.grid_rowconfigure(1, weight=1)
    input_frame_label = customtkinter.CTkLabel(input_frame, text = 'INPUT',text_color='white',font=InterFont)
    input_frame_label.grid(column=2, row=0, padx=0, pady=0,sticky="wens")
    input_path_label = customtkinter.CTkLabel(input_frame, text = '/',text_color='white',font=InterFont)
    input_path_label.grid(column=0, row=1, padx=0, pady=0)
    choose_file_button = customtkinter.CTkButton(input_frame, text = 'Choose 3D .obj file',  command = find_input_dialog,width=200,fg_color='#7a7a7a',hover_color=hover_color,text_color='white',font=InterFont)
    choose_file_button.grid(column=1, row=1, padx=0, pady=0)

    sv.sequence_boolean = tk.IntVar(value=0)
    sequence_checkbox = customtkinter.CTkCheckBox(input_frame,state="disabled",variable=sv.sequence_boolean,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,text_color='white',border_color='#ffffff',border_width=1)
    sequence_checkbox.grid(column=1, row=2, padx=0, pady=0)
    sequence_start_Entry = customtkinter.CTkEntry(input_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="start"))
    sequence_start_Entry.grid(column=2, row=2, padx=0, pady=0)
    sequence_end_Entry = customtkinter.CTkEntry(input_frame,**disabled_entry_style,textvariable=customtkinter.StringVar(value="end"))
    sequence_end_Entry.grid(column=3, row=2, padx=0, pady=0)





    output_frame = customtkinter.CTkFrame(config_frame, width=200, height=200, corner_radius=10, fg_color='#313131')
    output_frame.pack(side=tk.TOP, expand=True,fill='x',padx=0)
    output_path_label = customtkinter.CTkLabel(output_frame, text = '/',text_color='white')
    output_path_label.grid(column=0, row=1, padx=0, pady=0)
    choose_file_button = customtkinter.CTkButton(output_frame, text = 'Choose output folder',  command = find_output_dialog,fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
    choose_file_button.grid(column=1, row=1, padx=0, pady=0)

    launch_frame = customtkinter.CTkFrame(config_frame, width=200, height=200, corner_radius=10, fg_color="transparent")
    launch_frame.pack(side=tk.TOP, expand=True)
    launch_button = customtkinter.CTkButton(launch_frame, text = 'Convert to .mcfunction file(s)',  command = launch_converter,fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
    launch_button.pack(side=tk.RIGHT, expand=True)

    disabled_slider_style = {"state":"disabled","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
    normal_slider_style = {"state":"normal","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":hover_color,"button_hover_color":hover_color}

    preview_framenumber_label = customtkinter.CTkLabel(preview_frame, text = 'frame',text_color='#525252',bg_color='black',width=100)
    preview_framenumber_label.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0,)

    preview_framenumber = customtkinter.IntVar(value=0)
    preview_framenumber_slider = customtkinter.CTkSlider(preview_frame,from_=0, to=100,number_of_steps=10,variable=preview_framenumber,**disabled_slider_style,command=slider_debouncer.debounced_refresh)
    preview_framenumber_slider.pack(side=tk.BOTTOM, expand=False, padx=0, pady=0)



    randomize_button = customtkinter.CTkButton(preview_frame, text = 'randomize',  command = random_cube_refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
    randomize_button.pack(side=tk.TOP, expand=False, padx=0, pady=0)

    # preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
    # preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

    sv.preview_boolean = tk.IntVar(value=sv.preview_boolean)
    preview_toggle_checkbox = customtkinter.CTkCheckBox(preview_frame,text="Preview",text_color='white',command=None, variable=sv.preview_boolean,onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color='#7a7a7a',hover_color=hover_color,bg_color='black',border_color='#ffffff',border_width=1)
    preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=0, pady=0)


    # progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
    # progressbar.pack(side=tk.BOTTOM, expand=True)
    # progressbar.start()

def find_input_dialog():
    global preview_framenumber
    initial_directory = fo.get_json_memory("input_path")
    dialog_result = tk.filedialog.askopenfilename(initialdir=initial_directory) # ask for a file
    if dialog_result == "":
        print("User exited file dialog without selecting a file")
        return
    sv.input_path = dialog_result
    fo.update_json_memory("input_path",os.path.dirname(sv.input_path))
    
    sv.input_name = os.path.basename(sv.input_path)
    # if len(output_path) > 70:
    #     inut_display = '...' + input_path[-70:]
    input_path_label.configure(text = sv.input_name)

    fo.find_file_sequence(sv.input_path)

    sequence_start_Entry.cget("textvariable").set(str(sv.first_frame))
    sequence_end_Entry.cget("textvariable").set(str(sv.last_frame))
    if sv.first_frame == sv.last_frame:
        sequence_checkbox.deselect()
        sequence_checkbox.configure(state="disabled")
        update_sequence_section()
    else:
        sequence_checkbox.configure(state="normal")
        update_sequence_section()
    preview_framenumber.set(sv.first_frame)
    print("sv.first_frame: " + str(sv.first_frame) + " sv.last_frame: " + str(sv.last_frame))
    preview_framenumber_slider.configure(from_=sv.first_frame,to=sv.last_frame, number_of_steps=sv.last_frame-1)
    preview_framenumber_label.configure(text = str(sv.first_frame))

    refresh_preview()

def find_output_dialog():
    initial_directory = fo.get_json_memory("output_path")
    dialog_result = tk.filedialog.askdirectory(initialdir=initial_directory)
    if dialog_result == "":
        print("User exited file dialog without selecting a folder")
        return
    
    sv.output_path = dialog_result
    fo.update_json_memory("output_path",sv.output_path)

    output_path_display = sv.output_path
    if len(sv.output_path) > 30:
        output_path_display = '...' + sv.output_path[-30:]
    output_path_label.configure(text = output_path_display)

def update_sequence_section():
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
    if len(sv.sequence_files) == 0: # Stops if no sequence is found.
        return
    sv.loading_done = False

    
    # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=preview.loading_animation,daemon=True)
    loading_thread.start()



    path = sv.input_path

    if sequence_checkbox.get() == 1:
        path = sv.sequence_files[int(preview_framenumber.get())]["path"] # Change the file path to the selected frame
        
    
    # Read particle positions from file
    if sv.input_path:
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
    
    if sv.sequence_boolean.get() == 0: # If we are not in sequence mode
        if sv.input_path != "": # If an input was selected
            sv.data_particles, sv.global_size = converter.create_ParticleData_list_from_file(sv.input_path)
        else : # If no input was selected
            sv.input_path = "particles" 
        converter.write_mc_function(False,0,sv.output_path,os.path.splitext(os.path.basename(sv.input_path))[0],sv.data_particles)

    if sequence_checkbox.get() == 1: # If we are in sequence mode
        if sv.input_path == "":
            tk.messagebox.showerror("Input required", "Please select an input for a sequence export",icon="info")
        if sv.seq_length == 1:
            tk.messagebox.showerror("Single file", "Only one file was found in the sequence, exporting anyways. \n Make sure your files have the same name + number",icon="info")
        
        for i in range(int(sequence_start_Entry.get()), int(sequence_end_Entry.get())+1):
            path = sv.sequence_files[i]["path"]
            sv.data_particles, sv.global_size = converter.create_ParticleData_list_from_file(sv.sequence_files[i]["path"]) 
            converter.write_mc_function(True,i,sv.output_path,os.path.splitext(os.path.basename(path))[0],sv.data_particles)

    
    # Converter.main(input_path, output_path)
    