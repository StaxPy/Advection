import pygame as pg

solo_textures_data = {
    'dust': {'file_path':'assets/particle_dust.png'},
    'effect': {'file_path':'assets/particle_effect.png'},
}

atlas_textures_data = {
    'dust': {'file_path':'assets/particle_dust_atlas.png'},
    'effect': {'file_path':'assets/particle_effect_atlas.png'},
}

spritesheet_animations_data = {
    'dust': {'spritesheet':'dust', 'frames':6, 'width':8, 'height':8, 'start_pos':(0,16), 'offset_x':0, 'offset_y':8},
    'effect': {'spritesheet':'effect', 'frames':7, 'width':8, 'height':8, 'start_pos':(0,0), 'offset_x':0, 'offset_y':8},
}


def load_textures() -> dict:
    global solo_textures_data,atlas_textures_data, solo_textures,spritesheet_textures
    solo_textures = {}
    spritesheet_textures = {}

    # Load solo textures
    for name,data in solo_textures_data.items():
        solo_textures[name] = pg.image.load(data['file_path']).convert_alpha()

     # Load spritesheet textures
    for name,data in atlas_textures_data.items():
        spritesheet_textures[name] = pg.image.load(data['file_path']).convert_alpha() 

def load_atlas_animations():
    global atlas_frames
    atlas_frames = {}

    for name,data in spritesheet_animations_data.items():
        atlas_frames[name] = []
        start_pos_x, start_pos_y = data['start_pos']
        for i in range(data['frames']): # For each frame
            atlas_frames[name].append(get_atlas_frame(spritesheet_textures[data['spritesheet']], data['offset_x']*i+start_pos_x, data['offset_y']*i+start_pos_y, data['width'], data['height'], 1))



def get_atlas_frame(spritesheet, pos_x, pos_y, width, height, scale):
    image = pg.Surface((width, height), pg.SRCALPHA).convert_alpha()
    image.blit(spritesheet, (0, 0), (pos_x, pos_y, width, height))
    image = pg.transform.scale(image, (width * scale, height * scale))
    return image
