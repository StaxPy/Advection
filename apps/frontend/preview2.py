from frontend.rendering.object_3d import *
from frontend.rendering.camera import *
from frontend.rendering.projection import *
import frontend.rendering.texture_data as td
import frontend.rendering.particle as particle
import shared.variables as sv
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
        self.create_object()
        self.limit = 0
        # self.camera_angle_x = 0
        # self.camera_angle_y = 0
        # self.pan_offset_x = 0
        # self.pan_offset_y = 0
        # self.camera_distance = 3
        # self.panning_active = False
        # self.pan_last_mouse_pos = None
        # self.last_mouse_pos = None

        self.last_mouse_pos = None
        self.panning_active = False
        self.pan_last_mouse_pos = None

        ''' TESTS'''
        self.solo_textures, self.atlas_textures = td.load_textures()
        # self.particle_texture = self.solo_textures['dust']
        # self.particle_texture_atlas = self.atlas_textures['dust']
        self.base_particle_size = (20,20)

        self.frame_0 = td.get_atlas_frame(td.atlas_textures['dust'], 2, 8,8, 10).convert_alpha()

        print(self.frame_0)
        # self.surface = particle.TexturedParticle(self.particle_texture, self.base_particle_size, (255,0,0))


        # self.surface = pg.Surface((50,50)).convert_alpha()
        # self.surface.fill(pg.Color('red'))
        # self.surface.blit(self.image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        ''''''


    def create_object(self):
        self.camera = Camera(self, [1, 1, -5]) # Initialize the camera
        self.projection = Projection(self) # Instanciate the projection
        
        # self.object = Object3D(self) # Instanciate the object
        # self.object.translate([0.2,0.4,0.2]) # Move the object
        # # self.object.rotate_y(math.pi / 6) # Rotate the object
        # self.axes = Axes(self)
        # self.axes.translate([0.7,0.9,0.7])
        self.world_axes = Axes(self)
        self.world_axes.movement_flag = False
        self.world_axes.scale(2.5)
        # self.world_axes.translate([0.7,0.9,0.7])

        self.grid = Grid(self, 10, 1.0)

        # self.model = self.get_object_from_file('Testing_files/character_1.obj')
        self.model = self.get_object_from_file('Testing_files/cube.obj')
        # self.model.translate([1,1,1])

    def get_object_from_file(self, filename):
            vertex, faces = [], []
            with open(filename) as f:
                for line in f:
                    if line.startswith('v '):
                        vertex.append([float(i) for i in line.split()[1:]] + [1])
                    elif line.startswith('f'):
                        faces_ = line.split()[1:]
                        faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
            return Object3D(self, vertex, faces)

    def draw(self):
        self.screen.fill(pg.Color('gray15'))
        # self.model.example_rotation()

        # self.model.rotate_y(pg.time.get_ticks() % 0.05)
        # self.model.translate([0.002, 0.002, 0.002])

        self.model.draw()
        self.world_axes.draw()
        self.grid.draw()
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
        # pg.event.pump() not necessary after using .get() once

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
        

        self.draw()
        
        ''' TESTS '''
        # self.screen.blit(self.surface, (10,10))
        self.screen.blit(self.frame_0, (100,100), special_flags=pg.BLEND_PREMULTIPLIED)
        ''''''

        # pg.display.set_caption(str(self.clock.get_fps()))
        pg.display.flip()

        # self.clock.tick(self.FPS)

    def inputs_and_events(self):

        self.camera.global_yaw = 0
        self.camera.global_pitch = 0

        for event in self.pg_events:
            if event.type == pg.MOUSEBUTTONDOWN:
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
                    self.camera.global_yaw = dx
                    self.camera.global_pitch = dy
                    # NOT INTENTED EFFECT ?
                    self.camera.input_rotation(dx, dy)
                    # self.camera.rotate_around_center(dx,dy)
                    # self.camera.input_orbit(dx, dy)


                    self.last_mouse_pos = event.pos
                elif self.panning_active:  # Pan camera with middle mouse
                    input_lateral_motion = event.pos[0] - self.pan_last_mouse_pos[0]
                    input_vertical_motion = event.pos[1] - self.pan_last_mouse_pos[1]
                    self.camera.input_movement(input_lateral_motion, input_vertical_motion)


                    self.pan_last_mouse_pos = event.pos


            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 3:   # Right mouse button released
                    self.last_mouse_pos = None
                elif event.button == 2:  # Middle mouse button released
                    self.panning_active = False
                    self.pan_last_mouse_pos = None

            if event.type == pg.MOUSEWHEEL:
                zoom = event.y  # Zoom control with mouse wheel
                self.camera.input_zoom(zoom)



# if __name__ == '__main__':
#     app = PygameRender()
#     app.run()