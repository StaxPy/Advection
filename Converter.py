import os
import re
from PIL import Image
from PIL import ImageDraw
import numpy as np
import Preview

# Define paths for the OBJ file and the output MCFunction file
INPUT_PATH = 'SimpleRig/animation'  # Change this to your OBJ files directory
OUTPUT_PATH = 'out'  # Change this to your desired output folder path

class ParticleData():
    def __init__(self,position, color):        
        # Store the data
        self.position = position
        self.color = color

        
def read_mtl_file(mtl_file_path):
    """Reads an MTL file and extracts materials with their diffuse textures (map_Kd)."""
    materials = {}
    current_material = None
    
    # Get the directory of the MTL file to handle relative paths
    mtl_dir = os.path.dirname(mtl_file_path)

    with open(mtl_file_path, 'r') as mtl_file:
        for line in mtl_file:
            line = line.strip()
            if line.startswith('newmtl '):
                current_material = line.split()[1]
                materials[current_material] = {'texture': None, 'color': None}  # Initialize material
            elif line.startswith('map_Kd ') and current_material is not None:
                texture_path = ' '.join(line.split()[1:])
                # Resolve relative texture paths
                full_texture_path = os.path.join(mtl_dir, texture_path)
                materials[current_material]['texture'] = full_texture_path  # Associate texture with the current material
            elif line.startswith('Kd ') and current_material is not None:
                # Read the diffuse color
                parts = line.split()[1:4]
                materials[current_material]['color'] = tuple(map(float, parts))  # Store color as a tuple (r, g, b)

    return materials


def read_obj_file(obj_file_path):
    """Reads an OBJ file and extracts vertex positions, texture coordinates, faces, and materials."""
    vertices = []
    texture_coords = []
    faces = []
    materials = []  # List of materials used in faces
    mtl_file_path = None
    current_material = None

    with open(obj_file_path, 'r') as obj_file:
        for line in obj_file:
            if line.startswith('v '):
                # Split the line into parts
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))
            elif line.startswith('vt '):
                # Read texture coordinates
                parts = line.strip().split()
                u, v = map(float, parts[1:3])
                texture_coords.append((u, v))
            elif line.startswith('f '):
                # Read faces (indices are 1-based in OBJ)
                parts = line.strip().split()[1:]  # Skip the 'f' part
                face = []
                for part in parts:
                    vertex_index, texcoord_index = map(int, part.split('/')[0:2])  # Get vertex and texture coordinate indices
                    face.append((vertex_index - 1, texcoord_index - 1))  # Store 0-based indices
                faces.append(face)
                materials.append(current_material)  # Associate the current material with the face
            elif line.startswith('mtllib '):
                # If the OBJ references an MTL file
                mtl_file_name = line.strip().split()[1]
                mtl_file_path = os.path.join(os.path.dirname(obj_file_path), mtl_file_name)
            elif line.startswith('usemtl '):
                # Update the current material to be used
                current_material = line.strip().split()[1]

    return vertices, texture_coords, faces, materials, mtl_file_path

def sample_color_from_texture(texcoord, img, draw):
    """Samples the color from the texture image based on the texture coordinates, including alpha."""
    u, v = texcoord
    width, height = img.size

    # Convert the texture coordinates from [0, 1] to pixel coordinates
    x = int(u * width)
    y = int((1 - v) * height)  # Invert y-axis (because images in most formats have origin at top-left)

    # Clamp x and y to be within the texture bounds
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))

    draw.ellipse((x-1, y-1, x+1, y+1), fill=(img.getpixel((x, y))))  # Draw a red dot
    return img.getpixel((x, y))  # Return color including alpha

def write_mcfunction_file(mcfunction_file_path, vertices, texture_coords, faces, materials, textures, size=0.5, deltax=0, deltay=0, deltaz=0, speed=0, count=1):
    """Writes the particle commands to an MCFunction file using colors from the face centers."""
    with open(mcfunction_file_path, 'w') as mcfunction_file:
        for face, material in zip(faces, materials):
            # Calculate the geometric center of the face
            face_center = calculate_face_center(vertices, face)

            # Use fixed decimal formatting (5 decimal places) instead of rounding
            face_center = tuple(format(coord, ".5f") for coord in face_center)

            # Check if the material has a texture
            if material in textures and textures[material]['texture'] is not None:
                texture_path = textures[material]['texture']
                img = Image.open(texture_path)  # Open the texture image
                draw = ImageDraw.Draw(img)

                # Calculate the average texture coordinates for the face
                texcoord_center = calculate_face_texture_center(texture_coords, face)

                # Sample the color from the texture at the center of the face
                color = sample_color_from_texture(texcoord_center, img, draw)
                r, g, b, a = color[:4]  # Get RGBA values
            else:
                # Use the defined color from the material if no texture is available
                r, g, b = textures[material]['color'] if material in textures else (255, 255, 255)  # Default to white
                a = 255  # Set alpha to fully opaque if no texture is used

            # Check the alpha value (skip if less than 50%)
            if a < 128:  # 50% of 255 is 127.5, so we round up to 128
                continue
            
            # Format the particle command with fixed decimal positions
            command = (
                f"particle dust{{color:[{r/255},{g/255},{b/255}],scale:{size}}} "
                f"~{face_center[0]} ~{face_center[1]} ~{face_center[2]} {deltax} {deltay} {deltaz} {speed} {count} force"
            )
            mcfunction_file.write(command + '\n')

    # Save the image showing the sampling points
    img.save("sampling_check.png")
    print(f"MCFunction file '{mcfunction_file_path}' created with face-centered particles.")


# NOTE : SHOULD MOVE THE SURFACE CREATION TO AN INDEPENDENT PROCESS, DONT NEED IT FOR MCFUNCTIONS
def create_ParticleData_list_from_file(file_path, normalize=False, target_size=1.0):
    particles = []
    
    if file_path.endswith('.obj'):
        particles_data = create_ParticleData_list_from_obj_file(file_path,normalize,target_size)
        particles += particles_data[0]
        global_size = particles_data[1]
    return particles, global_size



def create_ParticleData_list_from_obj_file(obj_file_path, normalize=False, target_size=1.0):
    """Reads an OBJ file and extracts vertex positions, texture coordinates, faces, and materials.
       If `normalize=True`, scales the particle cloud to fit within a box of size `target_size`."""
    vertices = []
    texture_coords = []
    faces = []
    materials = []  # List of materials used in faces
    mtl_file_path = None
    current_material = None
    filename = os.path.basename(obj_file_path)

    with open(obj_file_path, 'r') as obj_file:
        for line in obj_file:
            if line.startswith('v '):
                # Split the line into parts
                parts = line.strip().split()
                x, y, z = map(float, parts[1:4])
                vertices.append((x, y, z))
            elif line.startswith('vt '):
                # Read texture coordinates
                parts = line.strip().split()
                u, v = map(float, parts[1:3])
                texture_coords.append((u, v))
            elif line.startswith('f '):
                # Read faces (indices are 1-based in OBJ)
                parts = line.strip().split()[1:]  # Skip the 'f' part
                face = []
                for part in parts:
                    vertex_index, texcoord_index = map(int, part.split('/')[0:2])  # Get vertex and texture coordinate indices
                    face.append((vertex_index - 1, texcoord_index - 1))  # Store 0-based indices
                faces.append(face)
                materials.append(current_material)  # Associate the current material with the face
            elif line.startswith('mtllib '):
                # If the OBJ references an MTL file
                mtl_file_name = line.strip().split()[1]
                mtl_file_path = os.path.join(os.path.dirname(obj_file_path), mtl_file_name)
            elif line.startswith('usemtl '):
                # Update the current material to be used
                current_material = line.strip().split()[1]

    # Find the textures from the MTL file if it exists
    textures = {}
    if mtl_file_path and os.path.exists(mtl_file_path):
        textures = read_mtl_file(mtl_file_path)  # Get all textures
        if textures:
            print(f"Using textures from MTL file '{mtl_file_path}'.")
        else:
            print(f"No textures found in MTL file '{mtl_file_path}'.")
            return
    else:
        print(f"No MTL file found or referenced in the OBJ file '{filename}'.")
        return

    # Check if any vertices were found
    if not vertices:
        print(f"No vertices found in the OBJ file '{filename}'.")
        return

    # Normalize the vertex positions if needed
    particle_list = []
    if normalize:
        # Find the min and max coordinates along each axis
        min_x = min(v[0] for v in vertices)
        max_x = max(v[0] for v in vertices)
        min_y = min(v[1] for v in vertices)
        max_y = max(v[1] for v in vertices)
        min_z = min(v[2] for v in vertices)
        max_z = max(v[2] for v in vertices)

        # Compute the ranges (width, height, depth)
        range_x = max_x - min_x
        range_y = max_y - min_y
        range_z = max_z - min_z

        # Find the largest dimension to scale uniformly
        max_range = max(range_x, range_y, range_z)

        # Scale factor to fit the particle cloud into the target size
        scale_factor = target_size / max_range

        # Normalize vertices to fit within a box of size target_size
        normalized_vertices = [
            (
                (v[0] - min_x) * scale_factor,  # Normalize x
                (v[1] - min_y) * scale_factor,  # Normalize y
                (v[2] - min_z) * scale_factor   # Normalize z
            )
            for v in vertices
        ]
    else:
        normalized_vertices = vertices

    # Store particle positions and colors from the mesh data
    for face, material in zip(faces, materials):
        # Calculate the geometric center of the face
        face_center = calculate_face_center(normalized_vertices, face)

        # Use fixed decimal formatting (5 decimal places)
        face_center = tuple(round(coord, 5) for coord in face_center)

        # Check if the material has a texture
        if material in textures and textures[material]['texture'] is not None:
            texture_path = textures[material]['texture']
            img = Image.open(texture_path)  # Open the texture image
            draw = ImageDraw.Draw(img)

            # Calculate the average texture coordinates for the face
            texcoord_center = calculate_face_texture_center(texture_coords, face)

            # Sample the color from the texture at the center of the face
            color = sample_color_from_texture(texcoord_center, img, draw)
            r, g, b, a = color[:4]  # Get RGBA values
        else:
            # Use the defined color from the material if no texture is available
            r, g, b = textures[material]['color'] if material in textures else (255, 255, 255)  # Default to white
            a = 255  # Set alpha to fully opaque if no texture is used

        # Check the alpha value (skip if less than 50%)
        if a < 128:  # 50% of 255 is 127.5, so we round up to 128
            continue

        # Append the particle to the list
        particle_list.append(ParticleData(face_center, (r, g, b)))
        # OLD WAY WITH A TEXTURE
        # # Append the particle to the list
        # particle_list.append(Preview.TexturedParticle(face_center, particle_texture, (r, g, b)))

    # Return the particle list and the size (range) of the original particle cloud
    total_size = (range_x, range_y, range_z) if normalize else (
        round(max(coord[0] for coord in normalized_vertices) - min(coord[0] for coord in normalized_vertices), 1),
        round(max(coord[1] for coord in normalized_vertices) - min(coord[1] for coord in normalized_vertices), 1),
        round(max(coord[2] for coord in normalized_vertices) - min(coord[2] for coord in normalized_vertices), 1),
    )

    # # CENTERING 
    # for particle in particle_list:
    #     particle.position[0] = particle.position[0] - total_size[0]/2
    #     particle.position[1] = particle.position[1] - total_size[1]/2
    #     particle.position[2] = particle.position[2] - total_size[2]/2

    return particle_list, total_size

def calculate_face_center(vertices, face):
    """Calculates the geometric center (average) of a face."""
    x = sum(vertices[vi][0] for vi, _ in face) / len(face)
    y = sum(vertices[vi][1] for vi, _ in face) / len(face)
    z = sum(vertices[vi][2] for vi, _ in face) / len(face)
    return (x, y, z)

def calculate_face_texture_center(texture_coords, face):
    """Calculates the average texture coordinate of a face."""
    u = sum(texture_coords[ti][0] for _, ti in face) / len(face)
    v = sum(texture_coords[ti][1] for _, ti in face) / len(face)
    return (u, v)

def old_main(input_directory,output_directory):
    
    os.makedirs(output_directory, exist_ok=True) # Create the output directory if it doesn't exist

    for file in os.listdir(input_directory): # Loop through all files in the input directory
        if file.endswith('.obj'):
            file_type = 'obj'
            file_path = os.path.join(input_directory, file) # Get the full path to that OBJ file
            match = re.search(r'(\d+)$', os.path.splitext(file)[0]) # Extract the number from the OBJ file name
            if match:
                number_part = str(int(match.group(1)))
                mcfunction_file_path = os.path.join(output_directory, f"{number_part}.mcfunction")
            else:
                print(f"No number found in the file name '{file}'. Skipping...")
                continue

            # Read the OBJ file
            vertices, texture_coords, faces, materials, mtl_file_path = read_obj_file(file_path)

            # Find the textures from the MTL file if it exists
            textures = {}
            if mtl_file_path and os.path.exists(mtl_file_path):
                textures = read_mtl_file(mtl_file_path)  # Get all textures
                if textures:
                    print(f"Using textures from MTL file '{mtl_file_path}'.")
                else:
                    print(f"No textures found in MTL file '{mtl_file_path}'.")
                    continue
            else:
                print(f"No MTL file found or referenced in the OBJ file '{file}'.")
                continue

            # Check if any vertices were found
            if not vertices:
                print(f"No vertices found in the OBJ file '{file}'.")
                continue

            # Write to the MCFunction file
            write_mcfunction_file(mcfunction_file_path, vertices, texture_coords, faces, materials, textures)

def write_mc_function(sequence,frame,output_path,file_name,particle_data_list,particle_size=1,deltax=0,deltay=0,deltaz=0,speed=0, count=1,viewmode="force"):
    print("write_mc_function")
    os.makedirs(output_path, exist_ok=True) # Create the output directory if it doesn't exist
    if sequence:
        file_name = str(frame)

    mcfunction_file_path = os.path.join(output_path, f"{file_name}.mcfunction")


    """ OLD
    # Read the OBJ file
    vertices, texture_coords, faces, materials, mtl_file_path = read_obj_file(input_path)

    # Find the textures from the MTL file if it exists
    textures = {}
    if mtl_file_path and os.path.exists(mtl_file_path):
        textures = read_mtl_file(mtl_file_path)  # Get all textures
        if textures:
            print(f"Using textures from MTL file '{mtl_file_path}'.")
        else:
            print(f"No textures found in MTL file '{mtl_file_path}'.")
            return
    else:
        print(f"No MTL file found or referenced in the OBJ file '{input_path}'.")
        return

    # Check if any vertices were found
    if not vertices:
        print(f"No vertices found in the OBJ file '{input_path}'.")
        return

    # Write to the MCFunction file
    write_mcfunction_file(mcfunction_file_path, vertices, texture_coords, faces, materials, textures)
    """
    commands = []
    for particle in particle_data_list:
        # Format the particle command with fixed decimal positions
        x, y, z = particle.position
        r, g, b = particle.color
        command = (
            f"particle dust{{color:[{r/255},{g/255},{b/255}],scale:{particle_size}}} "
            f"~{x} ~{y} ~{z} {deltax} {deltay} {deltaz} {speed} {count} {viewmode}"
        )
        commands.append(command)

    with open(mcfunction_file_path, 'w') as mcfunction_file:
        mcfunction_file.write('\n'.join(commands))


def read_file(file_path):
    print("read file")

if __name__ == "__main__":
    # main(INPUT_PATH, OUTPUT_PATH)
    print("Done!")
