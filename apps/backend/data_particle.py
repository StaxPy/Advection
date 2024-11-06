import numpy as np


class DataParticle():
    def __init__(self, position=(0,0,0), color=None):
        self.position = position
        self.color = color


class DataParticlesCloud:
    def __init__(self, DataParticlesList, min_pos, max_pos):
        self.DataParticlesList = DataParticlesList
        self.count = len(DataParticlesList)
        self.particle_positions = np.array([particle.position for particle in self.DataParticlesList], dtype=np.float64)
        self.min_pos = min_pos
        self.max_pos = max_pos
        self.center = np.add(self.max_pos, self.min_pos)
        self.size = np.subtract(self.max_pos, self.min_pos)
