import math


class sv():

    DEBUG = True
    WIDTH, HEIGHT = 1280, 720
    MEMORY_PATH = './src/shared/Memory.json'


class Styles():
    hover_color = "#ffffff"
    special_color = "#be5dff"
    dark_gray = "#292929"
    medium_gray = "#6e6e6e"
    light_gray = "#adadad"
    white = "#ffffff"
    almost_black = "#181818"
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
    # Preview Slider (on black)
    disabled_preview_slider_style = {"state":"disabled","bg_color":almost_black,"fg_color":medium_gray,'progress_color': medium_gray,"border_color":almost_black,"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
    normal_preview_slider_style = {"state":"normal","bg_color":almost_black,"fg_color":medium_gray,'progress_color': medium_gray,"border_color":almost_black,"button_color":hover_color,"button_hover_color":hover_color}
    # Slider
    disabled_slider_style = {"state":"disabled","bg_color":dark_gray,"fg_color":medium_gray,'progress_color': medium_gray,"border_color":dark_gray,"button_color":'#3a3a3a',"button_hover_color":'#3a3a3a'}
    normal_slider_style = {"state":"normal","bg_color":dark_gray,"fg_color":medium_gray,'progress_color': medium_gray,"border_color":dark_gray,"button_color":hover_color,"button_hover_color":hover_color}
    # Button
    disabled_special_button_style = {"fg_color":medium_gray,"hover_color":medium_gray,"text_color":dark_gray,"border_color":medium_gray}
    normal_special_button_style = {"fg_color":special_color,"hover_color":hover_color,"text_color":black,"border_color":dark_gray}
    disabled_button_style = {"fg_color":dark_gray,"hover_color":dark_gray,"text_color":black,"border_color":dark_gray}
    normal_button_style = {"fg_color":light_gray,"hover_color":hover_color,"text_color":black,"border_color":light_gray}
    ratio_button_style = {"fg_color":almost_black,"hover_color":light_gray,"text_color":black,"border_color":almost_black}



class PygameData():
    PygameRenderer = None
    frame = 0
    texture = None
    textures = []
    toggle_render = 1

class PygameTempData():
    toggle = 1
    update_requested = 0



class InputData():
    path = None
    folder = None
    name = None
    mode = None
    extension = None
    first_frame = 0
    last_frame = 0
    seq_length = 0
    sequence_files = {}
    image_resolution_width, image_resolution_height = 0, 0
    alpha_threshold = 127

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

class ModelData():
    lock_size_ratio = True
    width, height, depth = "0", "0", "0"
    old_width, old_height, old_depth = "0", "0", "0"
    
class ImageData():
    original_width, original_height = 0, 0
    default_width_density, default_height_density = 8, 8
    width_density, height_density = 8, 8
    old_width_density, old_height_density = 8, 8
    autosize = True
    width, height = 0, 0
    old_width, old_height = 0, 0
    size_ratio = 0
    lock_size_ratio = True
    width_resolution, height_resolution = 0, 0
    old_width_resolution, old_height_resolution = 0, 0
    resolution_ratio = 0
    lock_resolution_ratio = True
    resampling = "Nearest"

class ParticleData():
    size = 1.0
    particle_type = "dust"
    type_scaling = {"dust": 20, "effect": 15}
    type_pos_variation = {"dust": 0.01, "effect": 0.02}
    viewmode = "force"
    viewer="@a"
    force_color = "#fcfcfc"
    force_color_toggle = False

class OutputData():
    path = None

class ParticlesCache():
    DataParticlesCloud = None
    TexturedParticlesCloud = None


class Modifiers():
    def __init__(self):
        self.mode = InputData.mode
        self.center = ParticlesCache.DataParticlesCloud.center
        self.size = [*ParticlesCache.DataParticlesCloud.size,1]
        
        self.particle_size = ParticleData.size
        self.particle_type = ParticleData.particle_type.get()
        self.viewmode = ParticleData.viewmode.get()
        self.viewers = ParticleData.viewer.get()
        # self.particle_size = float(particle_size)
        # self.viewmode = viewmode
        self.force_color = ParticleData.force_color
        self.force_color_toggle = ParticleData.force_color_toggle


        self.coordinate_axis_y = AlignmentData.coordinate_axis_y[AlignmentData.coordinate_axis.get()]
        self.coordinate_axis_x = AlignmentData.coordinate_axis_x[AlignmentData.coordinate_axis.get()]
        self.rotate = AlignmentData.rotate_radians[AlignmentData.rotate.get()]
        self.vertical_align_offset = AlignmentData.vertical_align_offset[AlignmentData.vertical_align.get()]
        self.horizontal_align_offset = AlignmentData.horizontal_align_offset[AlignmentData.horizontal_align.get()]
        self.vertical_align = AlignmentData.vertical_align.get()
        self.horizontal_align = AlignmentData.horizontal_align.get()

        # self.resize_toggle = ModelData.resize_toggle.get()
        self.resize_width, self.resize_height, self.resize_depth = float(ModelData.width.get()), float(ModelData.height.get()), float(ModelData.depth.get())
        self.model_resize = [self.resize_width, self.resize_height, self.resize_depth,1]
        
        self.image_size_width, self.image_size_height = float(ImageData.width.get()), float(ImageData.height.get())
        self.image_size = [self.image_size_width, self.image_size_height,1,1]
        self.image_resolution = [int(ImageData.width_resolution.get()), int(ImageData.height_resolution.get())]
        self.resampling = ImageData.resampling