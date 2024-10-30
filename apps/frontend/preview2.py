from frontend.rendering.object_3d import *
from frontend.rendering.camera import *
from frontend.rendering.projection import *
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
        # pg.display.init()
        pg.display.init()
        self.screen = pg.display.set_mode(self.RES, pg.RESIZABLE)
        self.clock = pg.time.Clock()
        pg.font.init()
        self.create_object()
        # self.camera_angle_x = 0
        # self.camera_angle_y = 0
        # self.pan_offset_x = 0
        # self.pan_offset_y = 0
        # self.camera_distance = 3
        # self.panning_active = False
        # self.pan_last_mouse_pos = None
        # self.last_mouse_pos = None


    def create_object(self):
        self.camera = Camera(self, [1, 1, -5]) # Initialize the camera
        self.projection = Projection(self) # Instanciate the projection
        
        # self.object = Object3D(self) # Instanciate the object
        # self.object.translate([0.2,0.4,0.2]) # Move the object
        # # self.object.rotate_y(math.pi / 6) # Rotate the object
        self.axes = Axes(self)
        # self.axes.translate([0.7,0.9,0.7])
        self.world_axes = Axes(self)
        self.world_axes.movement_flag = False
        self.world_axes.scale(2.5)
        # self.world_axes.translate([0.7,0.9,0.7])

        self.model = self.get_object_from_file('apps/tutorial/testing_files/character_1.obj')
        self.model.translate([1,1,1])

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
        self.model.rotate_y(pg.time.get_ticks() % 0.005)
        # self.model.translate([0.002, 0.002, 0.002])
        self.model.draw()
        self.world_axes.draw()
        # self.axes.example_rotation()
        # self.axes.translate([0.002, 0.002, 0.002])
        self.axes.draw()
        # self.axes.draw()
        # self.object.draw()


    def run(self):
        while True:
            self.draw()
            self.camera.control()
            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick(self.FPS)


    def loop(self):
        sv.pygame_width, sv.pygame_height = self.screen.get_size() 
        

        # for event in pg.event.get():
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
        self.camera.control()


        [exit() for i in pg.event.get() if i.type == pg.QUIT]
        # pg.display.set_caption(str(self.clock.get_fps()))
        pg.display.flip()
        # self.clock.tick(self.FPS)


if __name__ == '__main__':
    app = PygameRender()
    app.run()