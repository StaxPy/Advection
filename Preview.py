import pygame
import numpy as np
import time

""" OUTDATED
# Function to create a tinted surface
def create_particle_surface(particle_texture, tint_color):
    tinted_surface = pygame.Surface(particle_texture.get_size(), pygame.SRCALPHA)  # Create a new surface with transparency
    tinted_surface.fill((0, 0, 0, 0))  # Clear surface
    tinted_surface.blit(particle_texture, (0, 0))  # Blit the texture onto the tinted surface

    # Apply tint
    for x in range(tinted_surface.get_width()):
        for y in range(tinted_surface.get_height()):
            pixel_color = tinted_surface.get_at((x, y))
            # If the pixel is not fully transparent, apply tint
            if pixel_color[3] > 0:  # Check alpha channel
                print(pixel_color[0] * tint_color[0] // 255, 255)
                tinted_color = (
                    min(pixel_color[0] * tint_color[0] // 255, 255),
                    min(pixel_color[1] * tint_color[1] // 255, 255),
                    min(pixel_color[2] * tint_color[2] // 255, 255),
                    pixel_color[3]
                )
                tinted_surface.set_at((x, y), tinted_color)  # Set the tinted color

    return tinted_surface
"""

class TexturedParticle(pygame.sprite.Sprite):
    def __init__(self,position, texture, color):
        super().__init__()
        
        # Store the position
        self.position = position


        # Create a new surface with the same size and pixel format as the texture
        self.surface = pygame.Surface(texture.get_size(), pygame.SRCALPHA)
        
        # Fill the new surface with the desired color
        self.surface.fill(color)
        
        
        # Copy the alpha channel from the texture to the new surface
        self.surface.blit(texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.rect = self.surface.get_rect()




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



