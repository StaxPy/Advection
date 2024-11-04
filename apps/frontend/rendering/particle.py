import pygame as pg
import frontend.rendering.texture_data as td





class TexturedParticle():
    def __init__(self, texture, position=(0,0,0), color=None, size = None):
        self.position = position
        if size is None:
            size = texture.get_size()
        else :
            size = (size, size)
            texture = pg.transform.scale(texture, size)
        self.rect = texture.get_rect()
        if color is not None:
            self.surface = pg.Surface(size).convert_alpha().premul_alpha_ip() # Create an empty RGBA image with the same size as the texture
            self.surface.fill(color) # Fill it with the desired color
            self.surface.blit(texture, (0,0), special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.surface = texture
    
class DataParticle():
    def __init__(self, position=(0,0,0), color=None, size = None):
        self.position = position
        self.color = color
        self.size = size










"""  IDEA FOR ANIMATED PARTICLE
class TexturedParticle:
    def __init__(self, sprite_sheet, frame_duration, color):
        self.sprite_sheet = sprite_sheet
        self.frame_duration = frame_duration
        self.color = color
        self.frame_index = 0
        self.last_update_time = pg.time.get_ticks()
        self.surface = self.get_frame_surface()

    def update(self):
        current_time = pg.time.get_ticks()
        if current_time - self.last_update_time >= self.frame_duration:
            self.frame_index = (self.frame_index + 1) % self.sprite_sheet.get_width() // self.sprite_sheet.get_height()
            self.surface = self.get_frame_surface()
            self.last_update_time = current_time

    def get_frame_surface(self):
        frame_width = self.sprite_sheet.get_width() // self.sprite_sheet.get_height()
        frame_rect = pg.Rect(self.frame_index * frame_width, 0, frame_width, self.sprite_sheet.get_height())
        frame_surface = self.sprite_sheet.subsurface(frame_rect)
        colored_surface = pg.Surface(frame_surface.get_size()).convert_alpha()
        colored_surface.fill(self.color)
        colored_surface.blit(frame_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        return colored_surface
         
 """