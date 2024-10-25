import tkinter as tk
from tkinter import filedialog
import pygame
import os, random
import time
import threading
import customtkinter
import Converter
import Preview
import re
import json

# Constants
WIDTH, HEIGHT = 1280, 720
DEFAULT_CAMERA_DISTANCE = 3
PARTICLE_SIZE = 0.5
DEBUG_PARTICLE_COLOR = True
pygame_width, pygame_height = WIDTH/2, HEIGHT

data_particles = []
textured_particles = []
files = {}

root = tk.Tk()
root.minsize(800, 600)  # Set minimum size to 800x600

my_font = customtkinter.CTkFont(family="Inter", size=10)



root.geometry(f"{WIDTH}x{HEIGHT}")
root.configure(bg="#2b2b2b")
root.title("Advanced Particle Converter")

""" canvas = tk.Canvas(
    root,
    bg = "#000000",
    width = WIDTH,
    height = HEIGHT,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x=0, y=0) """



config_frame = tk.Frame(root,background="#181818")
config_frame.grid(row = 0, column = 0,sticky="nsew")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
# config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
pygame_frame = tk.Frame(root)
pygame_frame.grid(row = 0, column = 1,sticky="nsew")
root.grid_columnconfigure(1, weight=1,minsize=WIDTH/2)
# pygame_frame.pack(side = tk.RIGHT,fill=tk.BOTH, expand=True,minsize=(0,0))


os.environ['SDL_WINDOWID'] = str(pygame_frame.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'
pygame.display.init()
pygame_display = pygame.display.set_mode((WIDTH/2, HEIGHT))


# screen.fill((0,0,0))
# pygame.display.update()



PARTICLE_TEXTURE = pygame.image.load(os.path.join(os.path.dirname(__file__), 'texture.png')).convert_alpha()  # Load texture with alpha
# PARTICLE_TEXTURE = pygame.transform.scale(PARTICLE_TEXTURE, (PARTICLE_SIZE,PARTICLE_SIZE))  # Scale texture to desired size


""" ----------------------------------INTERFACE CONFIG------------------------------------------"""


def loading_animation():
    # Define square properties
    square_size = 50
    squares = []
    # Create positions for the squares in a 2x2 grid
    for row in range(2):
        for col in range(2):
            x = pygame_width // 2 - square_size + col * square_size
            y = pygame_height // 2 - square_size + row * square_size
            squares.append((x, y))

    rotation_angle = 0  # Initial rotation angle
    while not loading_done:
        pygame_display.fill((0, 0, 0))

        # Rotate the squares
        for i, (x, y) in enumerate(squares):
            # Rotate square and draw it
            rotated_square = pygame.Surface((square_size, square_size))
            rotated_square.fill((255, 255, 255))  # Fill square with white color
            rotated_square = pygame.transform.rotate(rotated_square, rotation_angle)
            rect = rotated_square.get_rect(center=(x + square_size // 2, y + square_size // 2))
            pygame_display.blit(rotated_square, rect.topleft)

        pygame.display.flip()
        # pygame.display.update()

        # Update rotation angle (90 degrees every 0.5 seconds)
        rotation_angle = (rotation_angle + 90 * 0.1) % 360  # 90 degrees * (1/10) seconds = 9 degrees per frame
        time.sleep(0.05)  # Control the speed of the animation







# Function to generate random particle inside a cube
def random_cube_refresh_preview():

    print("random cube")
    global loading_done, data_particles, textured_particles, global_size
    data_particles = []
    textured_particles = []
    loading_done = False

        # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=loading_animation)
    loading_thread.start()

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
        
        
        data_particles.append(Converter.ParticleData(position, color))
        # surface = Preview.create_particle_surface(PARTICLE_TEXTURE, color)
        textured_particles.append(Preview.TexturedParticle(position, PARTICLE_TEXTURE, color))
        # surface = Preview.create_particle_surface(PARTICLE_TEXTURE, color)
    global_size = round(max(x for x, _, _ in random_positions)-min(x for x, _, _ in random_positions),1), round(max(y for _, y, _ in random_positions)-min(y for y, y, _ in random_positions),1), round(max(z for _, _, z in random_positions)-min(z for _, _, z in random_positions),1)

        
    

    # Set loading_done to True to stop the loading animation
    loading_done = True

def cube_corners_refresh_preview():
    print("cube corners")
    global loading_done, data_particles, textured_particles, global_size
    data_particles = []
    textured_particles = []
    loading_done = False

    # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=loading_animation)
    loading_thread.start()

    # Define the cube corners
    cube_corners = [
        (0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
        (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)
    ]

    # Create a list of particles at each corner
    for position in cube_corners:
        color = (255, 0 , 0)  # White color for all particles
        data_particles.append(Converter.ParticleData(position, color))
        textured_particles.append(Preview.TexturedParticle(position, PARTICLE_TEXTURE, color))

    global_size = (1.0,1.0,1.0)
    # Set loading_done to True to stop the loading animation
    loading_done = True


def refresh_preview():
    print("refresh")
    global  files, input_folder, input_path, input_name, loading_done, textured_particles, preview_framenumber, pan_offset_y, pygame_height, global_size

    if len(files) == 0:
        return

    loading_done = False

    
    # Start the loading animation in a separate thread
    loading_thread = threading.Thread(target=loading_animation)
    loading_thread.start()




    if sequence_checkbox.get() == 1:
        # Find file path for that frame
        input_path = files[int(preview_framenumber.get())]["path"] # Change the file path to the selected frame
        print(input_path)
        
    
    # Read particle positions from file
    if input_path:
        particles_data =Converter.create_ParticleData_list_from_file(input_path) # Read the ParticleData from the file
        textured_particles = [] # Empty the particles list
        for particle in particles_data[0]: # Transform the data into a list of textures particles
            textured_particles.append(Preview.TexturedParticle(particle.position, PARTICLE_TEXTURE, particle.color))
        global_size = particles_data[1]
        
    else:
        # Set loading_done to True to stop the loading animation
        loading_done = True
        return
    

    
    # Set loading_done to True to stop the loading animation
    loading_done = True
    

input_path = ""
output_path = ""

def update_json_memory(parameter,value):
    # Read the JSON file
    with open(os.path.join(os.path.dirname(__file__), 'Memory.json'), 'r') as f:
        data = json.load(f)

    # Modify the desired value
    data[parameter] = value

    # Write the modified data back to the JSON file
    with open(os.path.join(os.path.dirname(__file__), 'Memory.json'), "w") as f:
        json.dump(data, f)

def get_json_memory(parameter):
    # Read the JSON file
    with open(os.path.join(os.path.dirname(__file__), 'Memory.json'), 'r') as f:
        data = json.load(f)
    return data[parameter]

def find_input_dialog():
    global input_folder,input_path, input_name, files, length, preview_framenumber
    initial_directory = get_json_memory("input_path")
    input_path = filedialog.askopenfilename(initialdir=initial_directory) # ask for a file
    if input_path == "":
        print("User exited file dialog without selecting a file")
        return
    
    update_json_memory("input_path",os.path.dirname(input_path))
    
    file_name = os.path.basename(input_path)
    # if len(output_path) > 70:
    #     inut_display = '...' + input_path[-70:]
    input_path_label.configure(text = file_name)

    find_file_sequence(input_path)

    sequence_start_Entry.cget("textvariable").set(str(first))
    sequence_end_Entry.cget("textvariable").set(str(last))
    if first == last:
        sequence_checkbox.deselect()
        sequence_checkbox.configure(state="disabled")
        update_sequence_section()
    else:
        sequence_checkbox.configure(state="normal")
        update_sequence_section()
    preview_framenumber.set(first)
    print("first: " + str(first) + " last: " + str(last))
    preview_framenumber_slider.configure(from_=first,to=last, number_of_steps=last-1)

    refresh_preview()


def find_file_sequence(input_path):
    global input_folder,input_name,files,length,first,last
    length = 0
    first = 1
    last = 1
    input_extension = os.path.splitext(input_path)[1] # Get the extension of the input file
    input_folder = os.path.dirname(input_path) # Get the parent directory of this file
    input_name = re.sub(r'\d+$', '', os.path.splitext(os.path.basename(input_path))[0]) # Get the name of the input file without the number at the end
    
    files["selected"] = {"path": input_path, "filename": input_name} # Store the selected name and path the files dictionary
    for file in os.listdir(input_folder):  # Find all files with the same extension and name as the input file
        if file.endswith(input_extension) and re.sub(r'\d+$', '', os.path.splitext(file)[0]) == input_name and re.search(r'(\d+)$', os.path.splitext(file)[0]):
            match = re.search(r'(\d+)$', os.path.splitext(file)[0]) 
            if match:
                length += 1
                number_part = int(match.group(1))
                first = min(first, number_part)
                last = max(last, number_part)
            files[number_part] = {"path": input_folder+"/"+file, "filename": os.path.splitext(file)[0]} # Store this frame's name and path the files dictionary


        

def find_output_dialog():
    global output_path
    initial_directory = get_json_memory("output_path")
    output_path = filedialog.askdirectory(initialdir=initial_directory)
    if output_path == "":
        print("User exited file dialog without selecting a folder")
        return
    
    update_json_memory("output_path",output_path)

    output_path_display = output_path
    if len(output_path) > 30:
        output_path_display = '...' + output_path[-30:]
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

# Debouncer that wraps the original refresh function
slider_debouncer = SliderDebouncer(root, refresh_preview)


def launch():
    global input_path, output_path, files, data_particles, length
    print(input_path, output_path)
    if output_path == "":
        tk.messagebox.showerror("Output folder required", "Please select an output folder",icon="info")
        return
    
    if sequence_checkbox.get() == 0: # If we are not in sequence mode
        if input_path != "": # If an input was selected
            data_particles, global_size = Converter.create_ParticleData_list_from_file(input_path)
        else : # If no input was selected
            input_path = "particles" 
        Converter.write_mc_function(False,0,output_path,os.path.splitext(os.path.basename(input_path))[0],data_particles)

    print(input_path)
    if sequence_checkbox.get() == 1: # If we are in sequence mode
        if input_path == "":
            tk.messagebox.showerror("Input required", "Please select an input for a sequence export",icon="info")
        if length == 1:
            tk.messagebox.showerror("Single file", "Only one file was found in the sequence, exporting anyways. \n Make sure your files have the same name + number",icon="info")
        
        for i in range(int(sequence_start_Entry.get()), int(sequence_end_Entry.get())+1):
            input_path = files[i]["path"]
            data_particles, global_size = Converter.create_ParticleData_list_from_file(files[i]["path"]) 
            Converter.write_mc_function(True,i,output_path,os.path.splitext(os.path.basename(input_path))[0],data_particles)

    
    # Converter.main(input_path, output_path)


# INITIAL DISPLAY
cube_corners_refresh_preview()


def test():
    print("test")

""" ----------------------------------INTERFACE CONFIG------------------------------------------"""
hover_color = "#52c9af"

disabled_entry_style = {"state":"disabled","fg_color":'#3d3d3d',"placeholder_text_color":'#585858',"text_color":'#131313',"border_color":'#3d3d3d'}
normal_entry_style = {"state":"normal","fg_color":'#202020',"placeholder_text_color":'#ffffff',"border_color":'#3d3d3d',"text_color":'white'}

input_frame = customtkinter.CTkFrame(config_frame, corner_radius=10, fg_color='#313131')
input_frame.pack(side=tk.TOP, expand=True,fill='x',padx=50)
input_frame.grid_columnconfigure([0,1,2,3], weight=1)

input_frame.grid_rowconfigure(0, weight=1)
input_frame.grid_rowconfigure(1, weight=1)
input_frame_label = customtkinter.CTkLabel(input_frame, text = 'INPUT',text_color='white',font=my_font)
input_frame_label.grid(column=2, row=0, padx=50, pady=10,sticky="wens")
input_path_label = customtkinter.CTkLabel(input_frame, text = '/',text_color='white',font=my_font)
input_path_label.grid(column=0, row=1, padx=50, pady=10)
choose_file_button = customtkinter.CTkButton(input_frame, text = 'Choose 3D .obj file',  command = find_input_dialog,width=200,fg_color='#7a7a7a',hover_color=hover_color,text_color='white',font=my_font)
choose_file_button.grid(column=1, row=1, padx=50, pady=10)

sequence_checkbox = customtkinter.CTkCheckBox(input_frame,command=update_sequence_section, text="Sequence", onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,text_color='white',border_color='#ffffff',border_width=1)
sequence_checkbox.grid(column=1, row=2, padx=50, pady=10)
sequence_start_Entry = customtkinter.CTkEntry(input_frame, **disabled_entry_style,textvariable=customtkinter.StringVar(value="start"))
sequence_start_Entry.grid(column=2, row=2, padx=50, pady=10)
sequence_end_Entry = customtkinter.CTkEntry(input_frame,**disabled_entry_style,textvariable=customtkinter.StringVar(value="end"))
sequence_end_Entry.grid(column=3, row=2, padx=50, pady=10)





output_frame = customtkinter.CTkFrame(config_frame, width=200, height=200, corner_radius=10, fg_color='#313131')
output_frame.pack(side=tk.TOP, expand=True,fill='x',padx=50)
output_path_label = customtkinter.CTkLabel(output_frame, text = '/',text_color='white')
output_path_label.grid(column=0, row=1, padx=50, pady=10)
choose_file_button = customtkinter.CTkButton(output_frame, text = 'Choose output folder',  command = find_output_dialog,fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
choose_file_button.grid(column=1, row=1, padx=50, pady=10)

launch_frame = customtkinter.CTkFrame(config_frame, width=200, height=200, corner_radius=10, fg_color="transparent")
launch_frame.pack(side=tk.TOP, expand=True)
launch_button = customtkinter.CTkButton(launch_frame, text = 'Convert to .mcfunction file(s)',  command = launch,fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
launch_button.pack(side=tk.RIGHT, expand=True)

disabled_slider_style = {"state":"disabled","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
normal_slider_style = {"state":"normal","bg_color":'black',"fg_color":'#525252','progress_color': '#525252',"border_color":'black',"button_color":hover_color,"button_hover_color":hover_color}

preview_framenumber_label = customtkinter.CTkLabel(pygame_frame, text = 'frame',text_color='#525252',bg_color='black',width=100)
preview_framenumber_label.pack(side=tk.BOTTOM, expand=False, padx=50, pady=10,)

preview_framenumber = customtkinter.IntVar(value=0)
preview_framenumber_slider = customtkinter.CTkSlider(pygame_frame,from_=0, to=100,number_of_steps=10,variable=preview_framenumber,**disabled_slider_style,command=slider_debouncer.debounced_refresh)
preview_framenumber_slider.pack(side=tk.BOTTOM, expand=False, padx=50, pady=0)



randomize_button = customtkinter.CTkButton(pygame_frame, text = 'randomize',  command = random_cube_refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
randomize_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

# preview_button = customtkinter.CTkButton(pygame_frame, text = 'preview',  command = refresh_preview,bg_color='black',fg_color='#7a7a7a',hover_color=hover_color,text_color='white')
# preview_button.pack(side=tk.TOP, expand=False, padx=50, pady=10)

preview_toggle_checkbox = customtkinter.CTkCheckBox(pygame_frame,text="Preview",text_color='white',command=None, variable=tk.IntVar(value=True),onvalue=True, offvalue=False,checkbox_width=20,checkbox_height=20,fg_color='#7a7a7a',hover_color=hover_color,bg_color='black',border_color='#ffffff',border_width=1)
preview_toggle_checkbox.pack(side=tk.RIGHT, expand=False, padx=50, pady=10)


# progressbar = customtkinter.CTkProgressBar(button_win,  width=200, orientation="horizontal",mode="indeterminate",indeterminate_speed=1)
# progressbar.pack(side=tk.BOTTOM, expand=True)
# progressbar.start()




def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))



# Initialize camera variables
camera_angle_x = -0.5
camera_angle_y = 180
camera_distance = DEFAULT_CAMERA_DISTANCE
last_mouse_pos = None
pan_offset_x = 0
pan_offset_y = 0
panning_active = False
pan_last_mouse_pos = None

pygame.font.init()



###
def pygame_loop():
    global last_mouse_pos, camera_angle_x, camera_angle_y, camera_distance, pygame_display  # Make last_mouse_pos accessible to this function
    global pan_offset_x, pan_offset_y, panning_active, pan_last_mouse_pos  # Access pan variables
    global pygame_width, pygame_height

    pygame_width, pygame_height = pygame_display.get_size()

    root.columnconfigure(1, minsize=root.winfo_width()/2)
    
    pygame_display.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                last_mouse_pos = event.pos
            elif event.button == 2:  # Middle mouse button for pan
                panning_active = True
                pan_last_mouse_pos = event.pos

        if event.type == pygame.MOUSEMOTION:
            if last_mouse_pos:  # Rotate camera with left mouse
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_angle_y += dx * 0.01  # Sensitivity for Y-axis rotation
                camera_angle_x -= dy * 0.01  # Sensitivity for X-axis rotation
                last_mouse_pos = event.pos
            elif panning_active:  # Pan camera with middle mouse
                dx = event.pos[0] - pan_last_mouse_pos[0]
                dy = event.pos[1] - pan_last_mouse_pos[1]
                pan_offset_x += dx  # Adjust pan offset for X direction
                pan_offset_y += dy  # Adjust pan offset for Y direction
                
                pan_last_mouse_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:   # Right mouse button released
                last_mouse_pos = None
            elif event.button == 2:  # Middle mouse button released
                panning_active = False
                pan_last_mouse_pos = None

        if event.type == pygame.MOUSEWHEEL:
            camera_distance -= event.y * 1  # Zoom control with mouse wheel
            camera_distance = max(1, min(camera_distance, 10))

        if event.type == pygame.VIDEORESIZE:
            # screen = pygame.display.set_mode((event.w, event.h))
            root.columnconfigure(1, minsize=root.winfo_width()/2)
    """ OBSOLETE BECAUSE I CALL IT EVERY LOOP ANYWAYS
        if event.type == pygame.VIDEORESIZE:
            # screen = pygame.display.set_mode((event.w, event.h))
            pygame_width, pygame_height = screen.get_size()
            print(pygame_width, pygame_height)
    """


    
    #pygame.draw.circle(screen, circle_color, (250, 250), 125)
    if textured_particles and preview_toggle_checkbox.get() == 1:
        Preview.draw_particles(pygame_display,pygame_width, pygame_height,camera_angle_x,camera_angle_y,camera_distance,pan_offset_x,pan_offset_y,PARTICLE_SIZE,textured_particles)

    

    particles_global_amount_display = pygame.font.SysFont('Inter', 15).render(f'Particles: {len(textured_particles)}', True, (255, 255, 255))
    pygame_display.blit(particles_global_amount_display, (10, 10))
    particles_global_size_display = pygame.font.SysFont('Inter', 15).render(f'Size: {global_size}', True, (255, 255, 255))
    pygame_display.blit(particles_global_size_display, (10, 30))
    pygame.display.flip()
    # root.update()  
    root.update_idletasks()
    root.after(10, pygame_loop)


pygame_loop()
tk.mainloop()