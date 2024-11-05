from frontend.rendering.object_3d import *
from frontend.rendering.camera import *
from frontend.rendering.projection import *
import frontend.rendering.texture_data as td
import frontend.rendering.particle as particle
import shared.variables as sv
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

        td.load_textures()
        td.load_spritesheet_animations()

        self.need_update = True

        self.create_object()

        self.last_mouse_pos = None
        self.panning_active = False
        self.pan_last_mouse_pos = None

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
        



        # self.object = Object3D(self) # Instanciate the object
        # self.object.translate([0.2,0.4,0.2]) # Move the object
        # # self.object.rotate_y(math.pi / 6) # Rotate the object
        # self.axes = Axes(self)
        # self.axes.translate([0.7,0.9,0.7])
        self.world_axes = Axes(self)
        self.world_axes.movement_flag = False
        # self.world_axes.scale(2.5)
        # self.world_axes.translate([0.7,0.9,0.7])

        self.grid = Grid(self, 10, 1.0)

        # self.model = fp.get_object_from_file(self,'Testing_files/character_1.obj')
        # self.model = fp.get_object_from_file(self,'Testing_files/cube.obj')
        self.test_texturedcloud = TexturedParticlesCloud(self, fp.create_DataParticlesCloud_from_file_demo('Testing_files/character_1.obj'), td.solo_textures['dust'])

        self.texturedcloud = TexturedParticlesCloud(self, fp.create_DataParticlesCloud_from_obj_file('Testing_files/character_1.obj'), td.solo_textures['dust'])

        self.cloudsize = self.texturedcloud.size
        # self.model.translate([1,1,1])


        

    def draw(self):
        self.screen.fill(pg.Color('gray9'))
        # self.model.example_rotation()

        # self.model.rotate_y(pg.time.get_ticks() % 0.05)
        # self.model.translate([0.002, 0.002, 0.002])

        # self.model.draw()
        self.world_axes.draw()
        # self.test_texturedcloud.draw()
        self.texturedcloud.draw()
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


    def loop(self):
        sv.pygame_width, sv.pygame_height = self.screen.get_size() 

        """ TEST TO NOT UPDATE THE RENDER IF NOTHING HAPPENS
        self.limit += 1
        [print("button !",i.type) for i in pg.event.get(pump=False) if i.type == pg.MOUSEBUTTONDOWN]
        if self.limit > 100:
            return """
        self.clock.tick()
        self.FPS = self.clock.get_fps()

        # Get the events (POSITION IS IMPORTANT, can conflict with tkinter otherwise)
        self.pg_events = pg.event.get() 

        self.inputs_and_events()
        

        

        [exit() for i in self.pg_events if i.type == pg.QUIT]

        if not self.need_update: # Only update render if input has been detected
            return
        

        # for event in pg.event.get(pump=False):
        #     if event.type == pg.MOUSEBUTTONDOWN:
        #         if event.button == 3:  # Right mouse button
        #             self.last_mouse_pos = event.pos
        #         elif event.button == 2:  # Middle mouse button for pan
        #             self.panning_active = True
        #             self.pan_last_mouse_pos = event.pos
        #             # pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_HAND)

        #     if event.type == pg.MOUSEMOTION:
        #         if self.last_mouse_pos:  # Rotate camera with left mouse
        #             dx = event.pos[0] - self.last_mouse_pos[0]
        #             dy = event.pos[1] - self.last_mouse_pos[1]
        #             self.camera_angle_y += dx * 0.01  # Sensitivity for Y-axis rotation
        #             self.camera_angle_x -= dy * 0.01  # Sensitivity for X-axis rotation
        #             self.last_mouse_pos = event.pos
        #         elif self.panning_active:  # Pan camera with middle mouse
        #             dx = event.pos[0] - self.pan_last_mouse_pos[0]
        #             dy = event.pos[1] - self.pan_last_mouse_pos[1]
        #             self.pan_offset_x += dx  # Adjust pan offset for X direction
        #             self.pan_offset_y += dy  # Adjust pan offset for Y direction
                    
        #             self.pan_last_mouse_pos = event.pos

        #             print(self.pan_offset_x, self.pan_offset_y)

        #     if event.type == pg.MOUSEBUTTONUP:
        #         if event.button == 3:   # Right mouse button released
        #             self.last_mouse_pos = None
        #         elif event.button == 2:  # Middle mouse button released
        #             self.panning_active = False
        #             self.pan_last_mouse_pos = None

        #     if event.type == pg.MOUSEWHEEL:
        #         self.camera_distance -= event.y * 1  # Zoom control with mouse wheel
        #         self.camera_distance = max(1, min(self.camera_distance, 10))

        #     if event.type == pg.QUIT:
        #         pg.quit()
        
        if sv.preview_boolean.get() == 1: # NOT WORKING ?
            self.draw()

        
        font = pg.font.SysFont('Inter', 15)
        # particles_global_amount_display = font.render(f'Particles: {len(sv.textured_particles)}', True, (255, 255, 255))
        # self.screen.blit(particles_global_amount_display, (10, 10))
        
        size = tuple(float(x) for x in np.round(self.texturedcloud.size, 2))
        particles_global_size_display = font.render(f'Size: {size}', True, (255, 255, 255))
        self.screen.blit(particles_global_size_display, (10, 30))
        fps_display = font.render(f'FPS: {round(self.FPS)}', True, (255, 255, 255))
        self.screen.blit(fps_display, (10, 50))


        # Test texture blit
        # self.screen.blit(self.test_particle.surface, (100,100)) # Show a single texture

        ''' TEST ANIMATION'''
        # current_time = pg.time.get_ticks()
        # if current_time - self.last_animation_update >= self.animation_cooldown:
        #     self.animation_frame += 1
        #     self.last_animation_update = current_time
        #     if self.animation_frame >= len(td.animation_textures['dust']):
        #         self.animation_frame = 0
        
        # # Show current frame
        # self.screen.blit(pg.transform.scale(td.animation_textures['dust'][self.animation_frame], (64,64)), (100,300))

        ''''''



        # pg.display.set_caption(str(self.clock.get_fps()))
        pg.display.flip()

        # self.clock.tick(self.FPS)

    def inputs_and_events(self):


        for event in self.pg_events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.need_update = True
                if event.button == 3:  # Right mouse button
                    self.last_mouse_pos = event.pos
                elif event.button == 2:  # Middle mouse button for pan
                    self.panning_active = True
                    self.pan_last_mouse_pos = event.pos
                    # pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_HAND)

            if event.type == pg.MOUSEMOTION:
                if self.last_mouse_pos:  # Rotate camera with left mouse
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]

                    self.camera.input_rotation(dx, dy)



                    self.last_mouse_pos = event.pos
                elif self.panning_active:  # Pan camera with middle mouse
                    input_lateral_motion = event.pos[0] - self.pan_last_mouse_pos[0]
                    input_vertical_motion = event.pos[1] - self.pan_last_mouse_pos[1]
                    self.camera.input_movement(input_lateral_motion, input_vertical_motion)


                    self.pan_last_mouse_pos = event.pos


            if event.type == pg.MOUSEBUTTONUP:
                self.need_update = False
                if event.button == 3:   # Right mouse button released
                    self.last_mouse_pos = None
                elif event.button == 2:  # Middle mouse button released
                    self.panning_active = False
                    self.pan_last_mouse_pos = None

            if event.type == pg.MOUSEWHEEL:
                self.need_update = True
                zoom = event.y  # Zoom control with mouse wheel
                self.camera.input_zoom(zoom)
        


# if __name__ == '__main__':
#     app = PygameRender()
#     app.run()