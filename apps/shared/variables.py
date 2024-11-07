import math


class sv():

    DEBUG = True
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

class Styles():
    hover_color = "#ffffff"
    special_color = "#be5dff"
    dark_gray = "#292929"
    medium_gray = "#6e6e6e"
    light_gray = "#adadad"
    white = "#ffffff"
    almost_black = sv.almost_black
    black = "#000000"

    InterFont = ""
    InterFont_bold = ""

    # Path
    path_style = {"state":"disabled","fg_color":black,"placeholder_text_color":medium_gray,"text_color":white,"border_color":dark_gray}
    # Entry
    disabled_entry_style = {"state":"disabled","fg_color":dark_gray,"placeholder_text_color":medium_gray,"text_color":medium_gray,"border_color":medium_gray}
    normal_entry_style = {"state":"normal","fg_color":black,"placeholder_text_color":white,"border_color":dark_gray,"text_color":white}
    # Checkbox
    checkbox_style = {"checkbox_width":20,"checkbox_height":20,"text_color":white,"border_color":white,"border_width":1,"hover_color":hover_color,"fg_color":special_color}
    # Menu
    normal_menu_style = {"fg_color":black,"button_color":medium_gray,"dropdown_fg_color":dark_gray,"dropdown_text_color":white,"button_hover_color":hover_color} 
    # Slider
    disabled_slider_style = {"state":"disabled","bg_color":almost_black,"fg_color":medium_gray,'progress_color': medium_gray,"border_color":almost_black,"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
    normal_slider_style = {"state":"normal","bg_color":almost_black,"fg_color":medium_gray,'progress_color': medium_gray,"border_color":almost_black,"button_color":hover_color,"button_hover_color":hover_color}
    # Button
    disabled_special_button_style = {"fg_color":medium_gray,"hover_color":medium_gray,"text_color":dark_gray,"border_color":medium_gray}
    normal_special_button_style = {"fg_color":special_color,"hover_color":hover_color,"text_color":black,"border_color":dark_gray}
    disabled_button_style = {"fg_color":dark_gray,"hover_color":dark_gray,"text_color":black,"border_color":dark_gray}
    normal_button_style = {"fg_color":light_gray,"hover_color":hover_color,"text_color":black,"border_color":light_gray}
    



class PygameData():
    PygameRenderer = None
    frame = 0
    texture = None

class PygameTempData():
    toggle = 1
    update_requested = False



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
    coordinate_axis  = 'X-Y'
    coordinate_axis_y = {"X-Y": 0, "Y-Z": math.pi/2, "Z-X": math.pi}
    coordinate_axis_x = {"X-Y": 0, "Y-Z": 0, "Z-X": math.pi/2}

    rotate = '0°'
    rotate_radians = {'0°': 0, '90°': math.pi/2, '180°': math.pi, '270°': 3*math.pi/2}

    horizontal_align = 'Left'
    vertical_align = 'Top'
    horizontal_align_offset = {'Left': 1, 'Center': 0, 'Right': -1, 'None': 0}
    vertical_align_offset = {'Top': -1, 'Center': 0, 'Bottom': 1, 'None': 0}
    model_horizontal_align_offset = {'Left': 1, 'Center': 0, 'Right': -1, 'None': 0}
    model_vertical_align_offset = {'Top': -1, 'Center': 0, 'Bottom': 1, 'None': 0}
    image_horizontal_align_offset = {'Left': 1, 'Center': 0, 'Right': -1}
    image_vertical_align_offset = {'Top': -1, 'Center': 0, 'Bottom': 1}

class ResizeData():
    toggle = 0
    width, height, depth = "1.00000", "1.00000", "1.00000"
    


class ParticleData():
    size = "1.0"
    viewmode = "force"

class OutputData():
    path = None

class PygameParticles():
    DataParticlesCloud = None
    TexturedParticlesCloud = None


class Modifiers():
    def __init__(self, center, size):

        self.mode = InputData.mode
        self.center = center
        self.size = [*size,1]
        self.center = self.center

        self.coordinate_axis_y = AlignmentData.coordinate_axis_y[AlignmentData.coordinate_axis.get()]
        self.coordinate_axis_x = AlignmentData.coordinate_axis_x[AlignmentData.coordinate_axis.get()]
        self.rotate = AlignmentData.rotate_radians[AlignmentData.rotate.get()]
        self.vertical_align_offset = AlignmentData.vertical_align_offset[AlignmentData.vertical_align.get()]
        self.horizontal_align_offset = AlignmentData.horizontal_align_offset[AlignmentData.horizontal_align.get()]
        self.vertical_align = AlignmentData.vertical_align.get()
        self.horizontal_align = AlignmentData.horizontal_align.get()

        self.resize = ResizeData.toggle.get()
        self.resize_width, self.resize_height, self.resize_depth = float(ResizeData.width.get()), float(ResizeData.height.get()), float(ResizeData.depth.get())
        self.model_resize = [self.resize_width, self.resize_height, self.resize_depth,1]
        self.image_resize = [self.resize_width, self.resize_height, 1]