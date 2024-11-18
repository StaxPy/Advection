from backend.data_particle import *
from shared.variables import *
# from frontend.rendering.matrix_functions import *
from backend.modifiers import *
import random
import os
from PIL import Image
import time



def create_DataParticlesCloud_from_file_demo(filename) -> DataParticlesCloud:

    """
    Reads an OBJ file and creates a TexturedParticlesCloud instance with particles
    positioned at the vertex coordinates.

    Parameters
    ----------
    filename : str
        Path to the OBJ file.

    Returns
    -------
    TexturedParticlesCloud
        The textured particles cloud created from the OBJ file, with particle positions
        and bounding box coordinates (min and max positions).
    """
    DataParticlesList = []
    min_x, min_y, min_z, max_x, max_y, max_z = 0, 0, 0, 0, 0, 0
    with open(filename) as f:
        for line in f:
            if line.startswith('v '):
                x, y, z, w = [float(i) for i in line.split()[1:]] + [1]
                min_x, min_y, min_z = min(min_x, x), min(min_y, y), min(min_z, z)
                max_x, max_y, max_z = max(max_x, x), max(max_y, y), max(max_z, z)
                DataParticlesList.append(DataParticle(position=(x, y, z, w),color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)))

    return DataParticlesCloud(DataParticlesList, (min_x, min_y, min_z), (max_x, max_y, max_z))


def create_random_DataParticles(count: int):
    DataParticlesList = []
    min_x, min_y, min_z, max_x, max_y, max_z = 0, 0, 0, 0, 0, 0
    for _ in range(count):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        z = random.uniform(0, 1)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        min_x, min_y, min_z = min(min_x, x), min(min_y, y), min(min_z, z)
        max_x, max_y, max_z = max(max_x, x), max(max_y, y), max(max_z, z)
        DataParticlesList.append(DataParticle(position=(x, y, z, 1), color=(r, g, b)))
    return DataParticlesCloud(DataParticlesList, (min_x, min_y, min_z), (max_x, max_y, max_z))


def create_cube_DataParticles():
    DataParticlesList = []
    vertices = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
                (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
    for x, y, z in vertices:
        DataParticlesList.append(DataParticle(position=(x, y, z, 1), color=(255, 255, 255)))
    return DataParticlesCloud(DataParticlesList, (0, 0, 0), (1, 1, 1))


def create_DataParticlesCloud_from_file(file_path):
    print("create_DataParticlesCloud_from_file")
    
    if file_path.endswith('.obj'):
        DataParticlesCloud = create_DataParticlesCloud_from_obj_file(file_path)
    if file_path.endswith('.png') or file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        DataParticlesCloud = create_DataParticlesCloud_from_image(file_path)

    return DataParticlesCloud



def create_DataParticlesCloud_from_obj_file(obj_file_path):
    print("create_DataParticlesCloud_from_obj_file")
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


    # Store particle positions and colors from the mesh data
    dataParticlesList = []
    for face, material in zip(faces, materials):
        # Calculate the geometric center of the face
        face_center = calculate_face_center(vertices, face)

        # Use fixed decimal formatting (5 decimal places)
        face_center = tuple(round(coord, 5) for coord in face_center)+ (1,)

        # Check if the material has a texture
        if material in textures and textures[material]['texture'] is not None:
            texture_path = textures[material]['texture']
            img = Image.open(texture_path)  # Open the texture image

            # Calculate the average texture coordinates for the face
            texcoord_center = calculate_face_texture_center(texture_coords, face)

            # Sample the color from the texture at the center of the face
            color = sample_color_from_texture(texcoord_center, img)
            r, g, b, a = color[:4]  # Get RGBA values
        else:
            # Use the defined color from the material if no texture is available
            r, g, b = textures[material]['color'] if material in textures else (255, 255, 255)  # Default to white
            a = 255  # Set alpha to fully opaque if no texture is used

        # Check the alpha value (skip if less than 50%)
        if a < 128:  # 50% of 255 is 127.5, so we round up to 128
            continue
        # Append the particle to the list
        dataParticlesList.append(DataParticle(face_center, (r, g, b, a)))
        # OLD WAY WITH A TEXTURE
        # # Append the particle to the list
        # particle_list.append(Preview.TexturedParticle(face_center, particle_texture, (r, g, b)))
    # Return the particle list and the size (range) of the original particle cloud


    return DataParticlesCloud(dataParticlesList, (min_x, min_y, min_z), (max_x, max_y, max_z))



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

def sample_color_from_texture(texcoord, img):
    """Samples the color from the texture image based on the texture coordinates, including alpha."""
    u, v = texcoord
    width, height = img.size

    # Convert the texture coordinates from [0, 1] to pixel coordinates
    x = int(u * width)
    y = int((1 - v) * height)  # Invert y-axis (because images in most formats have origin at top-left)

    # Clamp x and y to be within the texture bounds
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))

    return img.getpixel((x, y))  # Return color including alpha



# def write_mcfunction_file(mcfunction_file_path, vertices, texture_coords, faces, materials, textures, size=0.5, deltax=0, deltay=0, deltaz=0, speed=0, count=1):
def write_mcfunction_file(input, output_path, output_name,modifiers):

    if input is isinstance(str):
        """Writes the particle commands to an MCFunction file using colors from the face centers."""
        CurrentDataParticlesCloud = create_DataParticlesCloud_from_file(input)
    elif input is isinstance(DataParticlesCloud):
        CurrentDataParticlesCloud = input
    else:
        print("write_mcfunction_file: input is not a valid file path or DataParticlesCloud object.")
        return

    os.makedirs(output_path, exist_ok=True) # Create the output directory if it doesn't exist
    mcfunction_file_path = os.path.join(output_path, f"{output_name}.mcfunction")

    deltax = 0
    deltay = 0
    deltaz = 0
    speed = 0
    count = 1

    positions = apply_alignment_modifiers(CurrentDataParticlesCloud.particle_positions, modifiers)

    commands = []
    for index, particle in enumerate(CurrentDataParticlesCloud.DataParticlesList):
        # Format the particle command with fixed decimal positions
        x, y, z, _ = positions[index]
        r, g, b, a = particle.color
        commands.append(
            f"particle dust{{color:[{r/255},{g/255},{b/255}],scale:{modifiers.particle_size}}} "
            f"~{x:.5f} ~{y:.5f} ~{z:.5f} {deltax} {deltay} {deltaz} {speed} {count} {modifiers.viewmode}"
        )


    with open(mcfunction_file_path, 'w') as mcfunction_file:
        mcfunction_file.write('\n'.join(commands))

    return f"MCFunction file '{mcfunction_file_path}' created successfully."



def create_DataParticlesCloud_from_image(image_path, threshold=240):
    if sv.DEBUG:
        print("Creating DataParticlesCloud from image...")
    # Open the image and convert it to RGBA
    img = Image.open(image_path).convert('RGBA')
    InputData.image_resolution_x, InputData.image_resolution_y = img.width, img.height #Store original resolution

    if ImageData.reset_to_input: # Reset the image data from input
        ImageData.resolution_x.set(img.width)
        ImageData.resolution_y.set(img.height)
        width = int(ImageData.resolution_x.get())
        height = int(ImageData.resolution_y.get())
        ImageData.resolution_ratio = width/height
        ImageData.size_ratio = width/height
        ImageData.reset_to_input = False
    else :
        width = int(ImageData.resolution_x.get())
        height = int(ImageData.resolution_y.get())
        img = img.resize((width, height), Image.Resampling.BICUBIC)  


    # Get the resolution setting
    # resolution_x, resolution_y = round(float(ImageData.resolution_x.get())), round(float(ImageData.resolution_y.get()))
    # density = float(ImageData.density.get())

    # if (resolution_x, resolution_y) == (0,0):
    #     width = img.width
    #     height = img.height
    #     ImageData.resolution_x.set(width), ImageData.resolution_y.set(height) # Init the image res setting
    #     ImageData.width.set(width/density) # Init the image size
    #     ImageData.height.set(height/density)
        
    # else:
    #     width, height = resolution_x, resolution_y
    #     # Normalize size by resizing the image to fit the grid resolution
    #     img = img.resize((width, height), Image.Resampling.BICUBIC)    

    
    # Create a list to store the grid of colored points (x, y, color)
    dataParticlesList = []
    
    # Get pixel data from the resized image
    pixels = np.array(img)
    min_x, min_y, min_z, max_x, max_y, max_z = 0, -1, 0, 1, 0, 0
    # Loop through each grid cell and sample the color at the center
    for i in range(width):
        for j in range(height):
            # Get the color of the pixel at (i, j)
            color = pixels[j, i]
            
            # Ignore transparent pixels
            if color[3] < threshold:
                continue
            
            # Calculate the normalized (x, y) coordinates
            # normalized_x = i/(max(width, height))
            # normalized_y = j/(max(width, height))
            normalized_x = i/width
            normalized_y = -j/height
            
            # min_x, min_y = min(min_x, normalized_x), min(min_y, normalized_y)
            # max_x, max_y = max(max_x, normalized_x), max(max_y, normalized_y)

            position = normalized_x, normalized_y, 0 , 1
            # Add the position and color to the grid points
            dataParticlesList.append(DataParticle(position, color))
        # OLD WAY WITH A TEXTURE
        # # Append the particle to the list
        # particle_list.append(Preview.TexturedParticle(face_center, particle_texture, (r, g, b)))
    # Return the particle list and the size (range) of the original particle cloud

    print(width, height)
    return DataParticlesCloud(dataParticlesList, (min_x, min_y, min_z), (max_x, max_y, max_z))


