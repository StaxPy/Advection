import pygame as pg
from src.backend.modifiers import *
from src.shared.variables import *
import src.shared.color_operations as co
from numba import njit
import random



@njit(fastmath=True)
def any_func(arr, a, b):
    return np.any((arr == a) | (arr == b))

@njit(fastmath=True)
def inside_screen(vertex):
    return np.all((vertex[:3] > -1.5) & (vertex[:3] < 1.5))



    

def color_variation(color, tint_amount, brightness_amount):
    brightness_variation = np.random.uniform(0, brightness_amount)
    return tuple(max(0, color_component_variation(color_component,amount=tint_amount) - brightness_variation) for color_component in color)

def color_component_variation(color_component, amount):
    return max(0,min(255,color_component - np.random.randint(0, amount)))
class TexturedParticle():
    def __init__(self, textures, position=(0,0,0), color=None, size = None):
        self.position = position
        self.color = color
        texture = random.choice(textures)
        if size is None:
            self.size = texture.get_size()
        else :
            self.size = (size, size)
            texture = pg.transform.scale(texture, self.size)
        self.rect = texture.get_rect()
        if color is not None:
            self.surface = pg.Surface(self.size).convert_alpha() # Create an empty RGBA image with the same size as the texture
            color = color_variation(color, tint_amount=20, brightness_amount=50)
            if ParticleData.particle_type.get() == 'dust':
                # change the color alpha to 255
                color = (color[0], color[1], color[2], 255)
            self.surface.fill(color) # Fill it with the desired color

            self.surface.blit(texture, (0,0), special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.surface = texture

# def position_variation(amount=0.02):
#     offset = np.random.normal(-amount, amount, size=3)
#     return tuple(offset) + (0,)

class TexturedParticlesCloud:
    def __init__(self, DataParticlesCloud, textures):
        self.textures = textures
        if ParticleData.force_color_toggle:
            force_color = co.hex_to_rgb(ParticleData.force_color)
            self.TexturedParticlesList = [(TexturedParticle(self.textures, DataParticle.position, force_color)) for DataParticle in ParticlesCache.DataParticlesCloud.DataParticlesList]
        else:
            self.TexturedParticlesList = [(TexturedParticle(self.textures, DataParticle.position, DataParticle.color)) for DataParticle in ParticlesCache.DataParticlesCloud.DataParticlesList]        
        # self.particle_positions = [position_variation(position) for position in DataParticlesCloud.particle_positions]
        self.particle_positions = DataParticlesCloud.particle_positions
        # Generate random position variations
        self.particle_position_variations = np.hstack((np.random.normal(scale=ParticleData.type_pos_variation[ParticleData.particle_type.get()], size=(len(DataParticlesCloud.particle_positions), 3)), np.zeros((len(DataParticlesCloud.particle_positions), 1))))
        self.type_scaling = ParticleData.type_scaling[ParticleData.particle_type.get()]
        self.min_pos = DataParticlesCloud.min_pos
        self.max_pos = DataParticlesCloud.max_pos
        self.center = DataParticlesCloud.center
        self.size = DataParticlesCloud.size
        self.count = DataParticlesCloud.count
        self.modifiers = Modifiers()
        
    def refresh_colors(self):
        if ParticleData.force_color_toggle:
            force_color = co.hex_to_rgb(ParticleData.force_color)
            self.TexturedParticlesList = [(TexturedParticle(self.textures, DataParticle.position, force_color)) for DataParticle in ParticlesCache.DataParticlesCloud.DataParticlesList]
        else:
            self.TexturedParticlesList = [(TexturedParticle(self.textures, DataParticle.position, DataParticle.color)) for DataParticle in ParticlesCache.DataParticlesCloud.DataParticlesList]
        PygameTempData.update_requested += 1
    
    def draw(self,render):
        positions = self.particle_positions
        positions = apply_modifiers(positions, self.modifiers)
        # Apply position variation
        positions = np.add(positions, self.particle_position_variations)
        positions = positions @ render.camera.camera_matrix() # Apply camera matrix
        depths = np.array([position[2] for position in positions], dtype=np.float64)
        positions = positions @ render.projection.projection_matrix # Project on -1, 1 plane
        positions /= positions[:, -1].reshape(-1, 1) # Normalize

        # MASK CLIPPING METHOD
        visibility = np.array([(v[-2] >= render.camera.near_plane) and \
                                (v[-2] <= render.camera.far_plane) and \
                                (inside_screen(v)) for v in positions], dtype=bool)
        
        positions = positions @ render.projection.to_screen_matrix # Scale to screen size
        positions = positions[:, :2] # Only keep x and y

        sorted_indices = np.argsort(-depths)
        sorted_particles = [self.TexturedParticlesList[i] for i in sorted_indices]
        sorted_positions = positions[sorted_indices]
        sorted_visibility = visibility[sorted_indices]
        sorted_depths = depths[sorted_indices]

        blits_sequence = []
        if ParticlesCache.TexturedParticlesCloud.count < 10000:
            for index, particle in enumerate(sorted_particles):
                if sorted_visibility[index]:
                    scale = float(ParticleData.size) * self.type_scaling / sorted_depths[index]
                    if scale <= 0.1 :
                        scale = 0.1
                    scaled_particle = pg.transform.scale_by(particle.surface, scale)
                    position = np.add(sorted_positions[index], np.divide(scaled_particle.get_size(),-2))
                    # position = np.add(sorted_positions[index], -scale / 2)
                    # render.screen.blit(scaled_particle, position)
                    blits_sequence.append((scaled_particle, position))

            render.screen.blits(blits_sequence)
        else:
            for index, particle in enumerate(sorted_particles):
                if sorted_visibility[index]:
                    scale = float(ParticleData.size) * 10 / sorted_depths[index]
                    if scale <= 1 :
                        scale = 1
                    pg.draw.circle(render.screen, particle.color, (sorted_positions[index][0],sorted_positions[index][1]),radius=scale)
                