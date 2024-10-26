import pygame
import numpy as np
import os
import time
import shared.variables as sv


def initialize(WIDTH, HEIGHT, pygame_frame):
    global display
    global camera_angle_x, camera_angle_y,camera_distance, last_mouse_pos, pan_offset_x, pan_offset_y, panning_active, pan_last_mouse_pos
    global particle_texture
    os.environ['SDL_WINDOWID'] = str(pygame_frame.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    pygame.display.init()
    display = pygame.display.set_mode((WIDTH/2, HEIGHT))
    
    pygame.font.init()

    # Initialize camera variables
    camera_angle_x = -0.5
    camera_angle_y = 180
    camera_distance = 3

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

def loading_animation_mp():
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


def animation(current_square, squares, square_size):
    # Define square properties


    display.fill((0, 0, 0))

    # Draw the current square
    pygame.draw.rect(display, (255, 255, 255), (squares[current_square][0], squares[current_square][1], square_size, square_size))

    # Update the current square index (clockwise rotation)
    current_square = (current_square + 1) % 4

    pygame.display.flip()
    time.sleep(0.5)  # Control the speed of the animation


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

# Function to draw each particle (called once every frame)
def draw_particles(screen, window_width, window_height, camera_angle_x, camera_angle_y, camera_distance, pan_offset_x, pan_offset_y, particle_size, particles):
    """
    Draws particles and axis lines on the screen, projecting 3D positions to 2D.
    """
    projected_objects = []

    for i, particle in enumerate(particles):
        position = particle.position

        


        # Rotate particle position based on camera angles
        x = position[0] * np.cos(camera_angle_y) - position[2] * np.sin(camera_angle_y)
        z = position[0] * np.sin(camera_angle_y) + position[2] * np.cos(camera_angle_y)
        y = position[1] * np.cos(camera_angle_x) - z * np.sin(camera_angle_x)
        z = position[1] * np.sin(camera_angle_x) + z * np.cos(camera_angle_x)


        # Skip rendering if particle is behind the camera
        if z + camera_distance <= 0:
            continue

        # Project 3D coordinates to 2D with zoom effect and apply pan offset
        scale = 300 / (z + camera_distance)
        x_proj = int(x * scale + window_width // 2 + pan_offset_x)
        y_proj = int(-y * scale + window_height // 2 + pan_offset_y)

        # Calculate distance from camera for sorting
        distance = np.sqrt(x**2 + y**2 + (z + camera_distance)**2)
        projected_objects.append(('particle', i, (x_proj, y_proj), distance, scale))

    axis_lines_size = 1
    axis_lines = [
        ('x_axis', (axis_lines_size, 0, 0)),
        ('y_axis', (0, axis_lines_size, 0)),
        ('z_axis', (0, 0, axis_lines_size))
    ]

    for axis_name, position in axis_lines:
        # Rotate axis positions based on camera angles
        x = position[0] * np.cos(camera_angle_y) - position[2] * np.sin(camera_angle_y)
        z = position[0] * np.sin(camera_angle_y) + position[2] * np.cos(camera_angle_y)
        y = position[1] * np.cos(camera_angle_x) - z * np.sin(camera_angle_x)
        z = position[1] * np.sin(camera_angle_x) + z * np.cos(camera_angle_x)

        # Project 3D coordinates to 2D and apply pan offset
        scale = 300 / (z + camera_distance)
        x_proj = int(x * scale + window_width // 2 + pan_offset_x)
        y_proj = int(-y * scale + window_height // 2 + pan_offset_y)

        # Calculate distance for sorting
        distance = np.sqrt(x**2 + y**2 + (z + camera_distance)**2)
        projected_objects.append((axis_name, None, (x_proj, y_proj), distance, scale))

    # Sort objects by distance (furthest first) for proper rendering
    projected_objects.sort(key=lambda p: p[3], reverse=True)

    base_particle_size = particle_size

    for obj_type, index, (x_proj, y_proj), distance, scale in projected_objects:
        if obj_type == 'particle':
            # Scale particle size based on distance
            particle_size_scale = 300 / (distance + camera_distance)
            particle_size = int(base_particle_size * particle_size_scale)
            # particle_size = max(particle_size, 2)

            # Scale and draw the particle image
            particle_image = pygame.transform.scale(particles[index].surface, (particle_size, particle_size))

            # Adjust the x_proj and y_proj to center the image
            screen.blit(particle_image, (x_proj - particle_size // 2, y_proj - particle_size // 2))
        elif obj_type == 'x_axis':
            # Draw the X-axis line in red
            pygame.draw.line(screen, (255, 0, 0), (window_width // 2 + pan_offset_x, window_height // 2 + pan_offset_y), (x_proj, y_proj), 2)
        elif obj_type == 'y_axis':
            # Draw the Y-axis line in green
            pygame.draw.line(screen, (0, 255, 0), (window_width // 2 + pan_offset_x, window_height // 2 + pan_offset_y), (x_proj, y_proj), 2)
        elif obj_type == 'z_axis':
            # Draw the Z-axis line in blue
            pygame.draw.line(screen, (0, 0, 255), (window_width // 2 + pan_offset_x, window_height // 2 + pan_offset_y), (x_proj, y_proj), 2)

def pygame_loop():
    global last_mouse_pos, camera_angle_x, camera_angle_y, camera_distance  # Make last_mouse_pos accessible to this function
    global pan_offset_x, pan_offset_y, panning_active, pan_last_mouse_pos  # Access pan variables

    # print(pan_offset_x, pan_offset_y,camera_angle_x, camera_angle_y, camera_distance)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                last_mouse_pos = event.pos
            elif event.button == 2:  # Middle mouse button for pan
                panning_active = True
                pan_last_mouse_pos = event.pos

        if event.type == pygame.MOUSEMOTION:
            if last_mouse_pos:  # Rotate camera with left mouse
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                camera_angle_y += dx * 0.01  # Sensitivity for Y-axis rotation
                camera_angle_x -= dy * 0.01  # Sensitivity for X-axis rotation
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
            camera_distance -= event.y * 1  # Zoom control with mouse wheel
            camera_distance = max(1, min(camera_distance, 10))

        if event.type == pygame.QUIT:
            pygame.quit()

        # if event.type == pygame.VIDEORESIZE:
        #     # screen = pygame.display.set_mode((event.w, event.h))
        #     interface.TkApp.columnconfigure(1, minsize=interface.TkApp.winfo_width()/2)

    # interface.Warning_OutputFolderRequired() Pourquoi ici??

    
    display.fill((0,0,0))



    #pygame.draw.circle(screen, circle_color, (250, 250), 125)
    if sv.textured_particles and sv.preview_boolean.get() == 1:
        draw_particles(display,sv.pygame_width, sv.pygame_height,camera_angle_x,camera_angle_y,camera_distance,pan_offset_x,pan_offset_y,sv.PARTICLE_SIZE,sv.textured_particles)

    

    particles_global_amount_display = pygame.font.SysFont('Inter', 15).render(f'Particles: {len(sv.textured_particles)}', True, (255, 255, 255))
    display.blit(particles_global_amount_display, (10, 10))
    particles_global_size_display = pygame.font.SysFont('Inter', 15).render(f'Size: {sv.global_size}', True, (255, 255, 255))
    display.blit(particles_global_size_display, (10, 30))
    pygame.display.flip()
    # root.update()  
    



