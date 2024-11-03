import pygame as pg
import frontend.rendering.texture_data as td





class TexturedParticle():
    def __init__(self, texture, size, color):
        scaledTexture = pg.transform.scale(texture, size)
        self.rect = scaledTexture.get_rect()
        if color is not None:
            self.surface = pg.Surface(size).convert_alpha() # Create an empty RGBA image with the same size as the texture
            self.surface.fill(color) # Fill it with the desired color
            self.surface.blit(scaledTexture, (0,0), special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.surface = scaledTexture
    
    # def update(self):
    #     pass
    # def draw(self):
    #     pass