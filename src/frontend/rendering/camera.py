from src.frontend.rendering.matrix_functions import *


class Camera:
    def __init__(self, render, position, pitch_yaw_roll):
        self.render = render
        self.position = np.array([*position, 1.0])
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])
        self.h_fov = math.pi / 3
        self.v_fov = self.h_fov * (render.HEIGHT / render.WIDTH)
        self.near_plane = 0.1
        self.far_plane = 10
        self.moving_speed = 0.002
        self.zoom_speed = 0.05
        self.rotation_speed = 0.005

        self.anglePitch, self.angleYaw, self.angleRoll = pitch_yaw_roll

        self.offset = 1



        self.orbit_center = [0, 0, 0]
        self.orbit_radius = 10.0
        self.orbit_angle = 0.0



    def control(self,events):
        
        """     
        key = pg.key.get_pressed()
        if key[pg.K_q]:
            self.position -= self.right * self.moving_speed
        if key[pg.K_d]:
            self.position += self.right * self.moving_speed
        if key[pg.K_z]:
            self.position += self.forward * self.moving_speed
        if key[pg.K_s]:
            self.position -= self.forward * self.moving_speed
        if key[pg.K_a]:
            self.position += self.up * self.moving_speed
        if key[pg.K_e]:
            self.position -= self.up * self.moving_speed

        if key[pg.K_LEFT]:
            self.camera_yaw(-self.rotation_speed)
        if key[pg.K_RIGHT]:
            self.camera_yaw(self.rotation_speed)
        if key[pg.K_UP]:
            self.camera_pitch(-self.rotation_speed)
        if key[pg.K_DOWN]:
            self.camera_pitch(self.rotation_speed)
        """
    
    def input_movement(self, lateral_motion, vertical_motion):
        rotate = rotate_y(-self.angleYaw) @ rotate_x(-self.anglePitch)  # Align this vector with the camera orientation
        distance_factor = max(np.linalg.norm(self.position[:3])-2 /3 ,0.5) # Decelerate zoom approaching origin
        self.position -= self.right @ rotate * lateral_motion * self.moving_speed * distance_factor
        self.position += self.up @ rotate * vertical_motion * self.moving_speed * distance_factor
  
    def input_zoom(self, zoom):  
        rotate =  rotate_y(-self.angleYaw) @ rotate_x(-self.anglePitch) # Align this vector with the camera orientation
        distance_factor = max(np.linalg.norm(self.position[:3])-1 ,0.5) # Decelerate zoom approaching origin
        self.position += self.forward @ rotate * zoom * self.zoom_speed * distance_factor
    
    def input_rotation(self, yaw, pitch):
        self.camera_yaw(yaw * self.rotation_speed)
        self.camera_pitch(pitch * self.rotation_speed)




    def set_position(self, x, y, z):
        self.position = np.array([x, y, z, 1.0])

    def translate(self, vector):
        self.position += np.array([vector[0], vector[1], vector[2], 0])



    def camera_yaw(self, angle):
        self.angleYaw += angle

    def camera_pitch(self, angle):
        self.anglePitch += angle

    def axiiIdentity(self):
        self.forward = np.array([0, 0, 1, 1])
        self.up = np.array([0, 1, 0, 1])
        self.right = np.array([1, 0, 0, 1])

    def camera_update_axii(self):
        # rotate = rotate_y(self.angleYaw) @ rotate_x(self.anglePitch)
        """
        Update the camera's axii (forward, up, right) after a pitch and yaw rotation
        """
        
        rotate = rotate_x(self.anglePitch) @ rotate_y(self.angleYaw)  # this concatenation gives right visual
        self.axiiIdentity()
        self.forward = self.forward @ rotate
        self.right = self.right @ rotate
        self.up = self.up @ rotate

    def camera_matrix(self):
        self.camera_update_axii()
        # return self.translate_matrix()
        # return self.translate_matrix() @ self.rotate_matrix()
        return self.rotate_matrix() @ self.translate_matrix() # not working lol

    def translate_matrix(self):
        x, y, z, w = self.position
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [-x, -y, -z, 1]
        ])

    def rotate_matrix(self):
        rx, ry, rz, w = self.right
        fx, fy, fz, w = self.forward
        ux, uy, uz, w = self.up
        return np.array([
            [rx, ux, fx, 0],
            [ry, uy, fy, 0],
            [rz, uz, fz, 0],
            [0, 0, 0, 1]
        ])