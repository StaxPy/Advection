import math
import numpy as np


class Projection:
    def __init__(self, render, aspect_ratio):
        NEAR = render.camera.near_plane
        FAR = render.camera.far_plane
        # Adjust horizontal and vertical FOV based on aspect ratio
        if aspect_ratio >= 1:  # Wider screens
            RIGHT = math.tan(render.camera.h_fov / 2)
            LEFT = -RIGHT
            TOP = RIGHT / aspect_ratio
            BOTTOM = -TOP
        else:  # Taller screens
            TOP = math.tan(render.camera.v_fov / 2)
            BOTTOM = -TOP
            RIGHT = TOP * aspect_ratio
            LEFT = -RIGHT

        m00 = 2 / (RIGHT - LEFT)
        m11 = 2 / (TOP - BOTTOM)
        m22 = (FAR + NEAR) / (FAR - NEAR)
        m32 = -2 * NEAR * FAR / (FAR - NEAR)
        self.projection_matrix = np.array([
            [m00, 0, 0, 0],
            [0, m11, 0, 0],
            [0, 0, m22, 1],
            [0, 0, m32, 0]
        ])

        HW, HH = render.H_WIDTH, render.H_HEIGHT
        self.to_screen_matrix = np.array([
            [HW, 0, 0, 0],
            [0, -HH, 0, 0],
            [0, 0, 1, 0],
            [HW, HH, 0, 1]
        ])