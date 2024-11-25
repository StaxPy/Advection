from frontend.rendering.object_3d import *
from frontend.rendering.camera import *
from frontend.rendering.projection import *
from shared.variables import *
from frontend.textured_particle import *
import frontend.rendering.texture_data as td
import backend.file_processor as fp
import pygame as pg
import os

class PygameRender:
    def __init__(self,WIDTH, HEIGHT, frame):
        
        self.RES = self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60

        os.environ['SDL_WINDOWID'] = str(frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        pg.display.init()
        self.screen = pg.display.set_mode(self.RES, pg.RESIZABLE)
        self.clock = pg.time.Clock()
        pg.font.init()

        self.InterFont = pg.font.SysFont('Inter', 15)

        td.load_textures()
        td.load_spritesheet_animations()

        PygameData.texture = td.solo_textures['dust'] # Define the texture used of render (temporary, until a real setting is implemented)
        self.test_surface = td.spritesheet_textures['dust'] #test
        self.test_index = 0

        self.create_object()

        self.last_mouse_pos = None
        self.panning_active = False
        self.pan_last_mouse_pos = None

        self.starting = True
        
        ''' TESTS'''

        

        # self.animation_cooldown = 50
        # self.animation_frame = 0
        # self.last_animation_update = pg.time.get_ticks()


        # self.test_particle = particle.TexturedParticle(td.solo_textures['dust'], position=[0,0,0], color=(255,0,0), size=32)



        # self.surface = pg.Surface((50,50)).convert_alpha()
        # self.surface.fill(pg.Color('red'))
        # self.surface.blit(self.image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        ''''''


    def create_object(self):
        self.camera = Camera(self, [0, 1, -5]) # Initialize the camera
        self.projection = Projection(self) # Instanciate the projection

        self.world_axes = Axes(self)
        self.world_axes.movement_flag = False

        # self.grid = Grid(self, 10, 1.0) #Unused

    def DataParticlesCloud_to_TexturedParticlesCloud(self, dataParticlesCloud):
        """Converts a DataParticlesCloud instance to a TexturedParticlesCloud instance."""
        return TexturedParticlesCloud(self, dataParticlesCloud, PygameData.texture)

    def draw_frame(self):
        # self.model.example_rotation()

        # self.model.rotate_y(pg.time.get_ticks() % 0.05)
        # self.model.translate([0.002, 0.002, 0.002])

        # self.model.draw()
        self.world_axes.draw()
        # self.test_texturedcloud.draw()
        if ParticlesCache.TexturedParticlesCloud:
            ParticlesCache.TexturedParticlesCloud.draw()
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
        self.cloud_size = tuple(float(x) for x in np.round(ParticlesCache.TexturedParticlesCloud.size, 2))
        self.cloud_size_display = self.InterFont.render(f'Size: {self.cloud_size}', True, (255, 255, 255))
        
        self.cloud_count = ParticlesCache.TexturedParticlesCloud.count
        self.cloud_count_display = self.InterFont.render(f'Count: {self.cloud_count}', True, (255, 255, 255))

        
    def loop(self):
        sv.pygame_width, sv.pygame_height = self.screen.get_size() 

        """ TEST TO NOT UPDATE THE RENDER IF NOTHING HAPPENS
        self.limit += 1
        [print("button !",i.type) for i in pg.event.get(pump=False) if i.type == pg.MOUSEBUTTONDOWN]
        if self.limit > 100:
            return """
        self.clock.tick()
        self.FPS = self.clock.get_fps()


        # Triggers an initial refresh when the render is stabilized
        if self.starting and self.clock.get_time() < 50: # If the frame was rendered in less than 50ms
            self.starting = False
            PygameTempData.update_requested += 1


        # Get the events (POSITION IS IMPORTANT, can conflict with tkinter otherwise)
        self.pg_events = pg.event.get() 

        self.inputs_and_events()
        
        

        

        [exit() for i in self.pg_events if i.type == pg.QUIT]

        
        # if PygameTempData.input_detected : # Only update render if input has been detected
        #     self.render_new_frame()
        if PygameTempData.update_requested >= 1:
            ParticlesCache.TexturedParticlesCloud.modifiers = Modifiers() # Update the modifiers only when needed
            self.render_new_frame()
            PygameTempData.update_requested -= 1


    def render_new_frame(self):
        #TODO : Render only 1 frame then freezebefore first camera movement.

        self.screen.fill(pg.Color('gray9'))

        if PygameData.toggle.get() == 1:
            self.draw_frame()

        self.screen.blit(self.cloud_size_display, (10, 30))
        self.screen.blit(self.cloud_count_display, (10, 50))
        fps_display = self.InterFont.render(f'FPS: {round(self.FPS)}', True, (255, 255, 255))
        self.screen.blit(fps_display, (10, 70))

        

        
        ''' TEST ANIMATION 1'''
        # current_time = pg.time.get_ticks()
        # if current_time - self.last_animation_update >= self.animation_cooldown:
        #     self.animation_frame += 1
        #     self.last_animation_update = current_time
        #     if self.animation_frame >= len(td.animation_textures['dust']):
        #         self.animation_frame = 0
        
        # # Show current frame
        # self.screen.blit(pg.transform.scale(td.animation_textures['dust'][self.animation_frame], (64,64)), (100,300))

        

        ''' TEST ANIMATION 2 
        # self.screen.blit(self.test_surface, (100,300),(0,self.test_index*8,8,8))
        # self.test_index += 1
        # if self.test_index >= 6:
        #     self.test_index = 0
        '''

        # pg.display.set_caption(str(self.clock.get_fps()))
        pg.display.flip()


        # self.clock.tick(self.FPS)


    def inputs_and_events(self):


        # if self.starting:
        #     PygameTempData.update_requested += 1


        # if PygameTempData.next_frame_freeze:
        #     PygameTempData.input_detected = False
        #     PygameTempData.next_frame_freeze = False

        for event in self.pg_events:
            if event.type == pg.VIDEORESIZE:
                PygameTempData.update_requested += 2
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
        


