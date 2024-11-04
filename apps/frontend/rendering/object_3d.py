import pygame as pg
from frontend.rendering.matrix_functions import *
from frontend.rendering.particle import *
from numba import njit


@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

@njit(fastmath=True)
def inside_screen(vertex):
    return np.all((vertex[:3] > -1.5) & (vertex[:3] < 1.5))



class TexturedParticlesCloud:
    def __init__(self, render, DataParticlesCloud, texture):
        self.render = render
        self.TexturedParticlesList = [(TexturedParticle(texture, DataParticle.position, DataParticle.color, DataParticle.size)) for DataParticle in DataParticlesCloud.DataParticlesList]
        self.particle_positions = DataParticlesCloud.particle_positions
        self.min_pos = DataParticlesCloud.min_pos
        self.max_pos = DataParticlesCloud.max_pos
        self.center = DataParticlesCloud.center
        self.size = DataParticlesCloud.size
        
    def draw(self):
        positions = self.particle_positions @ self.render.camera.camera_matrix() # Apply camera matrix
        depths = np.array([position[2] for position in positions], dtype=np.float64)
        positions = positions @ self.render.projection.projection_matrix # Project on -1, 1 plane
        positions /= positions[:, -1].reshape(-1, 1) # Normalize

        # MASK CLIPPING METHOD
        visibility = np.array([(v[-2] >= self.render.camera.near_plane) and \
                                (v[-2] <= self.render.camera.far_plane) and \
                                (inside_screen(v)) for v in positions], dtype=bool)
        
        positions = positions @ self.render.projection.to_screen_matrix # Scale to screen size
        positions = positions[:, :2] # Only keep x and y

        sorted_indices = np.argsort(-depths)
        sorted_particles = [self.TexturedParticlesList[i] for i in sorted_indices]
        sorted_positions = positions[sorted_indices]
        sorted_visibility = visibility[sorted_indices]
        sorted_depths = depths[sorted_indices]

        blits_sequence = []
        for index, particle in enumerate(sorted_particles):
            if sorted_visibility[index]:
                scale = 10 / sorted_depths[index] #TODO: find correct scaling value
                if scale <= 0.1 :
                    scale = 0.1
                scaled_particle = pg.transform.scale_by(particle.surface, scale)
                position = np.add(sorted_positions[index], -scale / 2)
                # self.render.screen.blit(scaled_particle, position)
                blits_sequence.append((scaled_particle, position))

        self.render.screen.fblits(blits_sequence)
                


class DataParticlesCloud:
    def __init__(self, DataParticlesList, min_pos, max_pos):
        self.DataParticlesList = DataParticlesList
        self.particle_positions = np.array([particle.position for particle in self.DataParticlesList], dtype=np.float64)
        self.min_pos = min_pos
        self.max_pos = max_pos
        self.center = np.add(self.max_pos, self.min_pos)
        self.size = np.subtract(self.max_pos, self.min_pos)



class Object3D:
    def __init__(self,render, vertices='', faces=''):
        self.render = render
        self.vertices = np.array(vertices if vertices else [], dtype=np.float64)
        self.faces = faces if faces else []  # A list of faces, which are a list of vertex indices
        # self.translate([0.0001, 0.0001, 0.0001]) # Why ??

        self.font = pg.font.SysFont('Inter', 30, bold=True)
        self.color_faces = [(pg.Color('orange'), face) for face in self.faces]
        self.movement_flag, self.draw_vertices, self.draw_faces = True, True, False
        self.label = ''
        
    def draw(self):
        # self.global_rotation()
        self.screen_projection()
        # self.example_rotation()

    def example_rotation(self):
        if self.movement_flag:
            
            self.rotate_y(pg.time.get_ticks() % 0.05) # Example rotation


    def global_rotation(self): # REALLY WEIRD
        
        self.rotate_x(-self.render.camera.global_pitch/10)
        self.rotate_y(self.render.camera.global_yaw/10)


    def screen_projection(self):
        
        vertices = self.vertices @ self.render.camera.camera_matrix() # Apply camera matrix
        vertices = vertices @ self.render.projection.projection_matrix # Project on -1, 1 plane
        # vertices = vertices[vertices[:, 2] > 0] # Filter out vertices behind the near plane (negative z-values after projection)
        vertices /= vertices[:, -1].reshape(-1, 1) # Normalize
        

        # "SCREEN CENTER" CLIPPING METHOD
        # vertices[(vertices > 1) | (vertices < -1)] = 0 # Screen Clipping
        # vertices[vertices[:, -2] < self.render.camera.near_plane,0] = 0 # Near clipping
        # vertices[vertices[:, -2] > self.render.camera.far_plane,0] = 0 # Far clipping

        # MASK CLIPPING METHOD
        vertices_visibility = np.array([(v[-2] >= self.render.camera.near_plane) and \
                                (v[-2] <= self.render.camera.far_plane) and \
                                (inside_screen(v)) for v in vertices], dtype=bool)
        

        

        

        vertices = vertices @ self.render.projection.to_screen_matrix # Scale to screen size
        vertices = vertices[:, :2] # Only keep x and y

        if self.draw_faces:
            for index, color_face in enumerate(self.color_faces):
                color, face = color_face

                # Check if all face indices are valid for current vertices
                if any(i >= len(vertices) for i in face):
                    continue  # Skip faces with out-of-bounds (missing) vertices

                polygon = vertices[face] # Get vertices for current face
                if all (vertices_visibility[i] for i in face):
                    pg.draw.polygon(self.render.screen, color, polygon, 1)
                    if self.label:
                        text = self.font.render(self.label[index], True, pg.Color('white'))
                        self.render.screen.blit(text, polygon[-1])

        if self.draw_vertices:
            for index, vertex in enumerate(vertices):
                if vertices_visibility[index]:
                    pg.draw.circle(self.render.screen, pg.Color('white'), vertex, 2)



    def translate(self, pos):
        self.vertices = self.vertices @ translate(pos)

    def scale(self, scale_to):
        self.vertices = self.vertices @ scale(scale_to)

    def rotate_x(self, angle):
        self.vertices = self.vertices @ rotate_x(angle)

    def rotate_y(self, angle):
        self.vertices = self.vertices @ rotate_y(angle)

    def rotate_z(self, angle):
        self.vertices = self.vertices @ rotate_z(angle)



class Axes(Object3D):
    def __init__(self, render):
        super().__init__(render)
        self.vertices = np.array([
            (0, 0, 0, 1),  # vertex 0
            (1, 0, 0, 1),  # vertex 1
            (0, 1, 0, 1),  # vertex 2
            (0, 0, 1, 1),  # vertex 3
        ])
        self.faces = np.array([
            (0, 1),  # face 0
            (0, 2),  # face 1
            (0, 3),  # face 2
        ])
        # super().__init__(render, self.vertices, self.faces)

        self.color_faces = [pg.Color('red'),pg.Color('green'),pg.Color('blue')]
        self.color_faces = [(color, face) for color, face in zip(self.color_faces, self.faces)]
        self.draw_vertices = False
        self.draw_faces = True
        self.label = 'XYZ'

class Grid(Object3D):
    def __init__(self, render, num_cells, cell_size):
        self.render = render
        self.num_cells = num_cells
        self.cell_size = cell_size
        self.grid_size = self.num_cells * self.cell_size
        self.offset = self.grid_size / 2
        self.vertices = []

        for i in range(0, self.num_cells+1, 1):
            # X axis
            self.vertices.append((i * self.cell_size-self.offset, 0, 0-self.offset, 1))
            self.vertices.append((i * self.cell_size-self.offset, 0, self.grid_size-self.offset, 1))
            # Z axis
            self.vertices.append((0-self.offset, 0, i * self.cell_size-self.offset, 1))
            self.vertices.append((self.grid_size-self.offset, 0, i * self.cell_size-self.offset, 1))

        self.vertices = np.array(self.vertices)
        self.translate([0.001, 0.001, 0.001]) # To avoid division by zero


    def draw(self):


        
        vertices = self.vertices @ self.render.camera.camera_matrix() # Apply camera matrix
        vertices = vertices @ self.render.projection.projection_matrix # Project on -1, 1 plane
        vertices /= vertices[:, -1].reshape(-1, 1) # Normalize


        vertices = vertices @ self.render.projection.to_screen_matrix # Scale to screen size
        vertices = vertices[:, :2] # Only keep x and y

        for i in range(0, (self.num_cells+1)*4, 2):
            pg.draw.line(self.render.screen, pg.Color('white'), vertices[i], vertices[i+1])



class DistanceTest():
    def __init__(self, render):
        self.render = render
        self.vertices = np.array([
            (1, 1, 1, 1),  # vertex 0
        ])
        self.camera_fov_factor = 2 * math.tan(render.camera.v_fov / 2)

    def draw(self):
        vertices = self.vertices @ self.render.camera.camera_matrix() # Apply camera matrix
        z = vertices[0][2]
        vertices = vertices @ self.render.projection.projection_matrix # Project on -1, 1 plane
        vertices /= vertices[:, -1].reshape(-1, 1) # Normalize

        vertices = vertices @ self.render.projection.to_screen_matrix # Scale to screen size
        vertices = vertices # Only keep x and y
        
        for vertice in vertices:
            # pg.draw.rect(self.render.screen, pg.Color('white'), (i,50,50))
            scale = 1150 / z
            pg.draw.rect(self.render.screen, pg.Color('white'), (vertice[0],vertice[1], scale,scale))