
# CONSTANTS PARAMETERS
WIDTH, HEIGHT = 1280, 720
MEMORY_PATH = '../shared/Memory.json'
PARTICLE_SIZE = 0.5
DEBUG_PARTICLE_COLOR = True
PARTICLE_TEXTURE_PATH = "assets/texture.png"


# LOGIC RELATED VARIABLES
sequence_boolean = 0
model_resize_boolean = 0
image_resize_boolean = 0
particle_type = "dust"
particle_mode = "Force"
particle_color_boolean = 0
autosize_boolean = 1
sequence_files = {}
data_particles = []
textured_particles = []
input_path = ""
input_folder = ""
input_name = ""
input_extension = ""
output_path = ""
first_frame = 0
last_frame = 0
seq_length = 0
global_size = (0,0,0)

# PREVIEW RELATED VARIABLES
pygame_width, pygame_height = WIDTH/2, HEIGHT
preview_boolean = 1
loading_done = False

