import pygame as pg

solo_texture_data = {
    'dust': {'file_path':'apps/frontend/assets/particle_dust.png'},
}

atlas_texture_data = {
    'dust': {'file_path':'apps/frontend/assets/particle_dust_atlas.png'},
}


def load_textures() -> dict:
    global solo_texture_data,solo_textures,atlas_textures
    solo_textures = {}
    atlas_textures = {}
    for name,data in solo_texture_data.items():
        solo_textures[name] = pg.image.load(data['file_path']).convert_alpha().premul_alpha_ip()
    for name,data in atlas_texture_data.items():
        atlas_textures[name] = pg.image.load(data['file_path']).convert_alpha().premul_alpha_ip()
    return solo_textures, atlas_textures

def get_atlas_frame(atlas, frame, width, height, scale):
    image = pg.Surface((width, height)).convert_alpha()
    image.blit(atlas, (0, 0), (0, frame * height, width, height))
    image = pg.transform.scale(image, (width * scale, height * scale))

    # NOT WORKING WITH ALPHA YET
    return image