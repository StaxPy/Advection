from src.frontend.rendering.object_3d import *
from src.frontend.rendering.camera import *
from src.frontend.rendering.projection import *
import src.frontend.rendering.texture_data as td
from src.shared.variables import *
from src.frontend.textured_particle import *
import pygame as pg
from os import environ as os_environ

class PygameRender:
    def __init__(self,WIDTH, HEIGHT, frame):
        self.frame = frame
        self.RES = self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.aspect_ratio = self.WIDTH / self.HEIGHT
        self.FPS = 60

        os_environ['SDL_WINDOWID'] = str(frame.winfo_id())
        os_environ['SDL_VIDEODRIVER'] = 'windib'
        pg.display.init()
        self.screen = pg.display.set_mode(self.RES, pg.RESIZABLE)
        self.clock = pg.time.Clock()
        pg.font.init()

        self.InterFont = pg.font.SysFont('Inter', 13)

        td.load_textures()
        td.load_atlas_animations()

        self.set_particles_texture(ParticleData.particle_type.get()) # Define the texture used of render
        # self.test_surface = td.spritesheet_textures['dust'] #test
        # self.test_index = 0

        self.create_object()

        self.last_mouse_pos = None
        self.panning_active = False
        self.pan_last_mouse_pos = None

    

    def set_particles_texture(self, texture_name):
        PygameData.texture = td.solo_textures[f"{texture_name}"]
        PygameData.textures = td.atlas_frames[f"{texture_name}"]


    def create_object(self):
        self.camera = Camera(self, [0, 1, -5]) # Initialize the camera
        self.projection = Projection(self,self.aspect_ratio) # Instanciate the projection

        self.world_axes = Axes(self)
        self.world_axes.movement_flag = False

        # self.grid = Grid(self, 10, 1.0) #Unused

    def reset_camera(self):
        self.camera = Camera(self, [0, 1, -5])
        PygameTempData.update_requested += 1

    def draw_frame(self):
        # self.model.example_rotation()

        # self.model.rotate_y(pg.time.get_ticks() % 0.05)
        # self.model.translate([0.002, 0.002, 0.002])
        # self.model.draw()
        self.world_axes.draw()
        # self.test_texturedcloud.draw()
        if ParticlesCache.TexturedParticlesCloud:
            ParticlesCache.TexturedParticlesCloud.draw(self)
        # self.grid.draw()
        # self.axes.example_rotation()
        # self.axes.translate([0.002, 0.002, 0.002])
        # self.axes.draw()
        # self.axes.draw()
        # self.object.draw()
        

    # def run(self):
    #     while True:
    #         self.draw()
    #         self.camera.control()
    #         [exit() for i in pg.event.get() if i.type == pg.QUIT]
    #         pg.display.set_caption(str(self.clock.get_fps()))
    #         pg.display.flip()
    #         self.clock.tick(self.FPS)

    def refresh_cloud_stats(self):
        # self.cloud_size = tuple(float(x) for x in np.round(ParticlesCache.TexturedParticlesCloud.size, 2))
        # self.cloud_size_display = self.InterFont.render(f'Size: {self.cloud_size}', True, (255, 255, 255))
        
        self.cloud_count = ParticlesCache.TexturedParticlesCloud.count
        if self.cloud_count > 10000:
            color = (255,0,0)
        else:
            color = (255,255,255)
        self.cloud_count_display = self.InterFont.render(f'Count: {self.cloud_count}', True, color)

        
    def loop(self):

        self.clock.tick()
        self.FPS = self.clock.get_fps()


        # Get the events (POSITION IS IMPORTANT, can conflict with tkinter otherwise)
        self.pg_events = pg.event.get() 

        self.inputs_and_events()
        
        

        

        [exit() for i in self.pg_events if i.type == pg.QUIT]

        
        # if PygameTempData.input_detected : # Only update render if input has been detected
        #     self.render_new_frame()
        if PygameTempData.update_requested >= 1 and ParticlesCache.TexturedParticlesCloud:
            ParticlesCache.TexturedParticlesCloud.modifiers = Modifiers() # Update the modifiers only when needed
            self.render_new_frame()
            PygameTempData.update_requested -= 1


    def render_new_frame(self):

        self.screen.fill(pg.Color('gray9'))

        if PygameData.toggle_render.get() == 1:
            self.draw_frame()
            self.screen.blit(self.InterFont.render(f'FPS: {round(self.FPS)}', True, (255, 255, 255)), (10, 50))

        # self.screen.blit(self.cloud_size_display, (10, 30))
        self.screen.blit(self.cloud_count_display, (10, 30))

        # self.test_index()
        #self.test_animation_2()

        pg.display.flip()



    def test_animation_1(self):
        current_time = pg.time.get_ticks()
        if current_time - self.last_animation_update >= self.animation_cooldown:
            self.animation_frame += 1
            self.last_animation_update = current_time
            if self.animation_frame >= len(td.animation_textures['dust']):
                self.animation_frame = 0
        
        # Show current frame
        self.screen.blit(pg.transform.scale(td.animation_textures['dust'][self.animation_frame], (64,64)), (100,300))

    def test_animation_2(self):
        self.screen.blit(self.test_surface, (100,300),(0,self.test_index*8,8,8))
        self.test_index += 1
        if self.test_index >= 6:
            self.test_index = 0

    def inputs_and_events(self):


        for event in self.pg_events:
            if event.type == pg.VIDEORESIZE:
                self.H_WIDTH, self.H_HEIGHT = self.frame.winfo_width() // 2, self.frame.winfo_height() // 2
                self.aspect_ratio =  self.H_WIDTH / self.H_HEIGHT
                self.projection = Projection(self,self.aspect_ratio)
                PygameTempData.update_requested += 5 # Several frames to be sure it updates (also responsible of the initial refresh)
            if event.type == pg.MOUSEBUTTONDOWN:
                # if self.starting:
                #     self.starting = False
                PygameTempData.update_requested = 1
                if event.button == 3:  # Right mouse button
                    self.last_mouse_pos = event.pos
                elif event.button == 2:  # Middle mouse button for pan
                    self.panning_active = True
                    self.pan_last_mouse_pos = event.pos
                    # pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_HAND)

            if event.type == pg.MOUSEMOTION:
                if self.last_mouse_pos:  # Rotate camera with left mouse
                    PygameTempData.update_requested = 1
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]

                    self.camera.input_rotation(dx, dy)



                    self.last_mouse_pos = event.pos
                elif self.panning_active:  # Pan camera with middle mouse
                    PygameTempData.update_requested = 1

                    input_lateral_motion = event.pos[0] - self.pan_last_mouse_pos[0]
                    input_vertical_motion = event.pos[1] - self.pan_last_mouse_pos[1]
                    self.camera.input_movement(input_lateral_motion, input_vertical_motion)


                    self.pan_last_mouse_pos = event.pos


            if event.type == pg.MOUSEBUTTONUP:
                # if self.starting:
                #     self.starting = False
                # PygameTempData.input_detected = False
                if event.button == 3:   # Right mouse button released
                    self.last_mouse_pos = None
                elif event.button == 2:  # Middle mouse button released
                    self.panning_active = False
                    self.pan_last_mouse_pos = None

            if event.type == pg.MOUSEWHEEL:
                # PygameTempData.input_detected = True
                PygameTempData.update_requested = 1
                # PygameTempData.next_frame_freeze = True
                zoom = event.y  # Zoom control with mouse wheel
                self.camera.input_zoom(zoom)
        


    def DataParticlesCloud_to_TexturedParticlesCloud(self, dataParticlesCloud):
        """Converts a DataParticlesCloud instance to a TexturedParticlesCloud instance."""
        return TexturedParticlesCloud( dataParticlesCloud, PygameData.textures)
