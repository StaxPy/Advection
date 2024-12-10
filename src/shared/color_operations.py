import numpy as np


def hex_to_rgb(hexa):
    hexa = hexa.lstrip('#')
    return tuple(int(hexa[i:i+2], 16)  for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def interpolate_colors(hex_color1, hex_color2, ratio):
    ratio = np.clip(ratio, 0, 1)
    rgb_color1 = hex_to_rgb(hex_color1)
    rgb_color2 = hex_to_rgb(hex_color2)
    interpolated = np.array(rgb_color1) + (np.array(rgb_color2) - np.array(rgb_color1)) * ratio
    return '#'+rgb_to_hex(tuple(interpolated.astype(int)))


