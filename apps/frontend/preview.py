import pygame
import numpy as np
import os
import time
import shared.variables as sv


class Camera:

    default_angle_x = -0.1 * np.pi
    default_angle_y = -0.6 * np.pi
    default_distance = 3

    def __init__(self):
        self.angle_x = self.default_angle_x
        self.angle_y = self.default_angle_y
        self.distance = self.default_distance
    
    def reset(self):
        self.angle_x = self.default_angle_x
        self.angle_y = self.default_angle_y
        self.distance = self.default_distance
    


def initialize(WIDTH, HEIGHT, frame):
    global display
    global camera, last_mouse_pos, pan_offset_x, pan_offset_y, panning_active, pan_last_mouse_pos
    global particle_texture
    os.environ['SDL_WINDOWID'] = str(frame.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    pygame.display.init()
    # display = pygame.display.set_mode((WIDTH/2, HEIGHT))
    display = pygame.display.set_mode((800,500), pygame.RESIZABLE)

    
    
    pygame.font.init()

    camera = Camera()

    last_mouse_pos = None
    pan_offset_x = 0
    pan_offset_y = 0
    panning_active = False
    pan_last_mouse_pos = None


    particle_texture = pygame.image.load(os.path.join(os.path.dirname(__file__), sv.PARTICLE_TEXTURE_PATH)).convert_alpha()  # Load texture with alpha


class TexturedParticle(pygame.sprite.Sprite):
    global particle_texture
    def __init__(self,position, color):
        super().__init__()
        
        # Store the position
        self.position = position


        # Create a new surface with the same size and pixel format as the texture
        self.surface = pygame.Surface(particle_texture.get_size(), pygame.SRCALPHA)
        
        # Fill the new surface with the desired color
        self.surface.fill(color)
        
        
        # Copy the alpha channel from the texture to the new surface
        self.surface.blit(particle_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.rect = self.surface.get_rect()




def loading_animation():
    # Define square properties
    square_size = 50
    squares = []
    # Create positions for the squares in a 2x2 grid
    for row in range(2):
        for col in range(2):
            x = sv.pygame_width // 2 - square_size + col * square_size
            y = sv.pygame_height // 2 - square_size + row * square_size
            squares.append((x, y))

    rotation_angle = 0  # Initial rotation angle
    while not sv.loading_done:
        display.fill((0, 0, 0))

        # Rotate the squares
        for i, (x, y) in enumerate(squares):
            # Rotate square and draw it
            rotated_square = pygame.Surface((square_size, square_size))
            rotated_square.fill((255, 255, 255))  # Fill square with white color
            rotated_square = pygame.transform.rotate(rotated_square, rotation_angle)
            rect = rotated_square.get_rect(center=(x + square_size // 2, y + square_size // 2))
            display.blit(rotated_square, rect.topleft)

        pygame.display.flip()
        # pygame.display.update()

        # Update rotation angle (90 degrees every 0.5 seconds)
        rotation_angle = (rotation_angle + 90 * 0.1) % 360  # 90 degrees * (1/10) seconds = 9 degrees per frame
        time.sleep(0.05)  # Control the speed of the animation


def pygame_loop():
    global last_mouse_pos, camera  # Make last_mouse_pos accessible to this function
    global pan_offset_x, pan_offset_y, panning_active, pan_last_mouse_pos
    sv.pygame_width, sv.pygame_height = display.get_size() 

    # pan_offset_x = 0
    # pan_offset_y = 0
    
    # print(pan_offset_x, pan_offset_y,camera.angle_x, camera.angle_y, camera.distance)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                last_mouse_pos = event.pos
            elif event.button == 2:  # Middle mouse button for pan
                panning_active = True
                pan_last_mouse_pos = event.pos
                # pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)

        if event.type == pygame.MOUSEMOTION:
            if last_mouse_pos:  # Rotate camera with left mouse
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera.angle_y += dx * 0.01  # Sensitivity for Y-axis rotation
                camera.angle_x -= dy * 0.01  # Sensitivity for X-axis rotation
                last_mouse_pos = event.pos
            elif panning_active:  # Pan camera with middle mouse
                dx = event.pos[0] - pan_last_mouse_pos[0]
                dy = event.pos[1] - pan_last_mouse_pos[1]
                pan_offset_x += dx  # Adjust pan offset for X direction
                pan_offset_y += dy  # Adjust pan offset for Y direction
                
                pan_last_mouse_pos = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:   # Right mouse button released
                last_mouse_pos = None
            elif event.button == 2:  # Middle mouse button released
                panning_active = False
                pan_last_mouse_pos = None

        if event.type == pygame.MOUSEWHEEL:
            camera.distance -= event.y * 1  # Zoom control with mouse wheel
            camera.distance = max(1, min(camera.distance, 10))

        if event.type == pygame.QUIT:
            pygame.quit()

        # if event.type == pygame.VIDEORESIZE:
        #     # screen = pygame.display.set_mode((event.w, event.h))
        #     interface.TkApp.columnconfigure(1, minsize=interface.TkApp.winfo_width()/2)

    # print(pan_offset_x,pan_offset_y)
    
    display.fill((0,0,0))



    #pygame.draw.circle(screen, circle_color, (250, 250), 125)
    if sv.textured_particles and sv.preview_boolean.get() == 1:
        draw_particles(sv.PARTICLE_SIZE,sv.textured_particles)

    

    particles_global_amount_display = pygame.font.SysFont('Inter', 15).render(f'Particles: {len(sv.textured_particles)}', True, (255, 255, 255))
    display.blit(particles_global_amount_display, (10, 10))
    particles_global_size_display = pygame.font.SysFont('Inter', 15).render(f'Size: {sv.global_size}', True, (255, 255, 255))
    display.blit(particles_global_size_display, (10, 30))
    pygame.display.flip()
    


origin_x,origin_y,origin_z = 0,0,0

def reset_camera():
    global camera, origin_x,origin_y,origin_z
    if camera is not None:
        camera.reset()

    origin_x,origin_y,origin_z = 0,0,0

def get_camera_direction_vectors():
    global camera
    # Forward vector (direction camera is facing)
    forward = (
        np.sin(camera.angle_y) * np.cos(camera.angle_x),
        -np.sin(camera.angle_x),
        np.cos(camera.angle_y) * np.cos(camera.angle_x)
    )
    # Right vector (perpendicular to forward in the horizontal plane)
    right = (
        np.cos(camera.angle_y),
        0,
        -np.sin(camera.angle_y)
    )
    # Up vector (perpendicular to both forward and right)
    up = np.cross(forward, right)
    
    return forward, right, up


def project_coordinates_on_screen(x, y, z):
    global camera
    scale = 300 / (z + camera.distance)
    x_proj = int(x * scale + sv.pygame_width // 2)
    y_proj = int(-y * scale + sv.pygame_height // 2)
    return (x_proj, y_proj,scale)

def rotate_position_around_camera(position):
    global camera
    # Rotate around the Y-axis (horizontal rotation):
    x = position[0] * np.cos(camera.angle_y) - position[2] * np.sin(camera.angle_y)
    z = position[0] * np.sin(camera.angle_y) + position[2] * np.cos(camera.angle_y)
    # Rotate around the X-axis (vertical rotation):
    y = position[1] * np.cos(camera.angle_x) - z * np.sin(camera.angle_x)
    z = position[1] * np.sin(camera.angle_x) + z * np.cos(camera.angle_x)

    return x, y, z

# Function to draw each particle (called once every frame)
def draw_particles(particle_size, particles):
    """
    Draws particles and axis lines on the screen, projecting 3D positions to 2D.
    """
    global last_mouse_pos, camera
    global pan_offset_x, pan_offset_y, panning_active, pan_last_mouse_pos
    global origin_x,origin_y,origin_z
    projected_objects = []

    # Get the direction vectors for the current camera orientation
    forward, right, up = get_camera_direction_vectors()
    
    pan_multiplier = 0.008
    if panning_active:
        temp_origin_x = origin_x - (right[0] * pan_offset_x + up[0] * pan_offset_y) * pan_multiplier
        temp_origin_y = origin_y - (right[1] * pan_offset_x + up[1] * pan_offset_y) * pan_multiplier
        temp_origin_z = origin_z + (right[2] * pan_offset_x + up[2] * pan_offset_y) * pan_multiplier
    else :
        # Scale pan offsets and apply them in the camera's local space
        origin_x -= (right[0] * pan_offset_x + up[0] * pan_offset_y) * pan_multiplier
        origin_y -= (right[1] * pan_offset_x + up[1] * pan_offset_y) * pan_multiplier
        origin_z += (right[2] * pan_offset_x + up[2] * pan_offset_y) * pan_multiplier
        pan_offset_x,pan_offset_y = 0,0
        temp_origin_x = origin_x
        temp_origin_y = origin_y
        temp_origin_z = origin_z



    


    for i, particle in enumerate(particles):
        position = particle.position

        position = np.add(position, (-temp_origin_x,temp_origin_y,temp_origin_z))

        


        
        """ Rotate particle position based on camera angles """
        x,y,z = rotate_position_around_camera(position)


        # Skip rendering if particle is behind the camera
        if z + camera.distance <= 0:
            continue

        # Project 3D coordinates to 2D with zoom effect and apply pan offset
        x_proj, y_proj,scale = project_coordinates_on_screen(x, y, z)

        # Calculate distance from camera for sorting
        distance = np.sqrt(x**2 + y**2 + (z + camera.distance)**2)
        projected_objects.append(('particle', i, (x_proj, y_proj), distance, scale))

    axis_lines_size = 1
    axis_lines = [
        ('x_axis', (axis_lines_size, 0, 0)),
        ('y_axis', (0, axis_lines_size, 0)),
        ('z_axis', (0, 0, axis_lines_size))
    ]

    

    for axis_name, position in axis_lines:

        position = np.add(position, (-temp_origin_x,temp_origin_y,temp_origin_z))

        # Rotate axis positions based on camera angles
        x,y,z = rotate_position_around_camera(position)
        # Project 3D coordinates to 2D and apply pan offset
        x_proj, y_proj,scale = project_coordinates_on_screen(x, y, z)


        # Calculate distance for sorting
        distance = np.sqrt(x**2 + y**2 + (z + camera.distance)**2)
        projected_objects.append((axis_name, None, (x_proj, y_proj), distance, scale))

    # Sort objects by distance (furthest first) for proper rendering
    projected_objects.sort(key=lambda p: p[3], reverse=True)

    base_particle_size = particle_size

    # Calculate the projected origin
    world_origin = (0,0,0)
    rotate_position_around_camera(world_origin)
    world_origin_x_proj, world_origin_y_proj, _ = project_coordinates_on_screen(world_origin[0], world_origin[1], world_origin[2])

    position = np.add((0,0,0), (-temp_origin_x,temp_origin_y,temp_origin_z))
    x,y,z = rotate_position_around_camera(position)
    origin_x_proj, origin_y_proj, _ = project_coordinates_on_screen(x, y, z)

    for obj_type, index, (x_proj, y_proj), distance, scale in projected_objects:
        if obj_type == 'particle':
            # Scale particle size based on distance
            particle_size_scale = 300 / (distance + camera.distance)
            particle_size = int(base_particle_size * particle_size_scale)
            # particle_size = max(particle_size, 2)

            # Scale and draw the particle image
            particle_image = pygame.transform.scale(particles[index].surface, (particle_size, particle_size))

            # Adjust the x_proj and y_proj to center the image
            display.blit(particle_image, (x_proj - particle_size // 2, y_proj - particle_size // 2))
        elif obj_type == 'x_axis':
            # Draw the X-axis line in red
            pygame.draw.line(display, (255, 0, 0), (origin_x_proj,origin_y_proj), (x_proj, y_proj), 2)
        elif obj_type == 'y_axis':
            # Draw the Y-axis line in green
            pygame.draw.line(display, (0, 255, 0), (origin_x_proj,origin_y_proj), (x_proj, y_proj), 2)
        elif obj_type == 'z_axis':
            # Draw the Z-axis line in blue
            pygame.draw.line(display, (0, 0, 255), (origin_x_proj,origin_y_proj), (x_proj, y_proj), 2)

    # pygame.draw.line(screen, (255, 255, 0), (sv.pygame_width // 2, sv.pygame_height // 2), (pan_x_proj, pan_y_proj), 5)



