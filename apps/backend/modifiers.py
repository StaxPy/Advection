from frontend.rendering.matrix_functions import *

def center_to_origin(positions,modifiers):
    return positions @ translate(-modifiers.center)

def origin_to_center(positions,modifiers):
    if modifiers.vertical_align == 'None':
        positions = positions @ translate([0,modifiers.center[1],0])
    if modifiers.horizontal_align == 'None':
        positions = positions @ translate([modifiers.center[0],0,0])
    return positions

def apply_alignment_rotate(positions, modifiers):
    return positions @ rotate_z(float(modifiers.rotate))

def apply_vertical_align(positions,modifiers):
    return positions @ translate([0,modifiers.size[1]/2*modifiers.vertical_align_offset,0])

def apply_horizontal_align(positions,modifiers):
    return positions @ translate([modifiers.size[0]/2*modifiers.horizontal_align_offset,0,0])

def apply_alignment_coordinate_axis(positions,modifiers):
    positions = positions @ rotate_y(modifiers.coordinate_axis_y)
    positions = positions @ rotate_x(modifiers.coordinate_axis_x)
    return positions


def apply_modifiers(positions, modifiers):
    positions = center_to_origin(positions, modifiers)
    positions = origin_to_center(positions, modifiers)
    positions = apply_alignment_rotate(positions, modifiers)
    positions = apply_vertical_align(positions, modifiers)
    positions = apply_horizontal_align(positions, modifiers)
    if modifiers.mode == 'model':
        positions = np.multiply(positions, np.array(np.divide(modifiers.model_resize,modifiers.size), dtype=np.float64))
    elif modifiers.mode == 'image':
        positions = np.multiply(positions, np.array(modifiers.image_size, dtype=np.float64))
    positions = apply_alignment_coordinate_axis(positions, modifiers)
    return positions

def apply_alignment_modifiers(positions, modifiers):
    positions = center_to_origin(positions, modifiers)
    positions = origin_to_center(positions, modifiers)
    positions = apply_alignment_rotate(positions, modifiers)
    positions = apply_vertical_align(positions, modifiers)
    positions = apply_horizontal_align(positions, modifiers)
    positions = apply_alignment_coordinate_axis(positions, modifiers)
    return positions

def apply_model_resize_modifiers(positions, modifiers):
    return np.multiply(positions, np.array(np.divide(modifiers.model_resize,modifiers.size), dtype=np.float64))