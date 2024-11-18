import pygame as pg
from backend.modifiers import *
from shared.variables import *
from numba import njit



@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

@njit(fastmath=True)
def inside_screen(vertex):
    return np.all((vertex[:3] > -1.5) & (vertex[:3] < 1.5))

class TexturedParticle():
    def __init__(self, texture, position=(0,0,0), color=None, size = None):
        self.position = position
        if size is None:
            self.size = texture.get_size()
        else :
            self.size = (size, size)
            texture = pg.transform.scale(texture, self.size)
        self.rect = texture.get_rect()
        if color is not None:
            self.surface = pg.Surface(self.size).convert_alpha().premul_alpha_ip() # Create an empty RGBA image with the same size as the texture
            self.surface.fill(color) # Fill it with the desired color
            self.surface.blit(texture, (0,0), special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.surface = texture

class TexturedParticlesCloud:
    def __init__(self, render, DataParticlesCloud, texture):
        self.render = render
        self.TexturedParticlesList = [(TexturedParticle(texture, DataParticle.position, DataParticle.color)) for DataParticle in DataParticlesCloud.DataParticlesList]
        self.particle_positions = DataParticlesCloud.particle_positions
        self.min_pos = DataParticlesCloud.min_pos
        self.max_pos = DataParticlesCloud.max_pos
        self.center = DataParticlesCloud.center
        self.size = DataParticlesCloud.size
        self.count = DataParticlesCloud.count
        self.modifiers = Modifiers()
        
    
    def draw(self):
        positions = self.particle_positions
        positions = apply_modifiers(positions, self.modifiers)
        positions = positions @ self.render.camera.camera_matrix() # Apply camera matrix
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
                scale = float(ParticleData.size) * 30 / sorted_depths[index] #TODO: find correct scaling value
                if scale <= 0.1 :
                    scale = 0.1
                scaled_particle = pg.transform.scale_by(particle.surface, scale)
                position = np.add(sorted_positions[index], np.divide(scaled_particle.size,-2))
                # position = np.add(sorted_positions[index], -scale / 2)
                # self.render.screen.blit(scaled_particle, position)
                blits_sequence.append((scaled_particle, position))

        self.render.screen.fblits(blits_sequence)
                