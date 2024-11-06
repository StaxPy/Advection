import math


class sv():
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

    data_particles = []
    textured_particles = []

    output_path = ""


    global_size = (0,0,0)

    # PREVIEW RELATED VARIABLES
    pygame_width, pygame_height = WIDTH/2, HEIGHT
    preview_boolean = 1
    loading_done = False
    almost_black = "#181818"


class PygameData():
    PygameRenderer = None
    frame = 0
    texture = None

class PygameTempData():
    toggle = 1
    toggle_changed = False
    input_detected = True
    next_frame_freeze = False



class InputData():
    path = None
    folder = None
    name = None
    extension = None
    first_frame = 0
    last_frame = 0
    seq_length = 0
    sequence_files = {}

class SequenceData():
    toggle = 0
    start = 0
    end = 0

class AlignmentData():
    coordinate_axis  = None
    coordinate_axis_y = {"X-Y": 0, "Y-Z": math.pi/2, "Z-X": math.pi}
    coordinate_axis_x = {"X-Y": 0, "Y-Z": 0, "Z-X": math.pi/2}

class ParticleData():
    size = 1
    viewmode = "force"

class OutputData():
    path = None

class PygameParticles():
    DataParticlesCloud = None
    TexturedParticlesCloud = None
