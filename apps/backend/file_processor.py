from backend.data_particle import *
from shared.variables import *
# from frontend.rendering.matrix_functions import *
from backend.modifiers import *
import random
import os
from PIL import Image
import time
from frontend.color_operations import *



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

def create_DataParticlesCloud_from_file(file_path, modifiers= None, reset_image_data= False):
    print("create_DataParticlesCloud_from_file")
    
    if file_path.endswith('.obj'):
        DataParticlesCloud = create_DataParticlesCloud_from_obj_file(file_path,modifiers)
    if file_path.endswith('.png') or file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        DataParticlesCloud = create_DataParticlesCloud_from_image(file_path, reset_image_data,modifiers)

    return DataParticlesCloud

def create_DataParticlesCloud_from_obj_file(obj_file_path, modifiers):
    def extract_obj_lines(obj_file_path):
        with open(obj_file_path, 'r') as obj_file:
            lines = obj_file.readlines()
        return lines
        
    def parse_vertex(line):
        parts = line.strip().split()
        if len(parts) == 7:
            position = map(float, parts[1:4])
            color = map(float, parts[4:])
            return tuple(position), tuple(color)
        else:
            position = map(float, parts[1:4])
            return tuple(position), None
        
    def parse_texture_coordinate(line):
        # Returns a tuple (u, v)
        return tuple(map(float, line.split()[1:3]))

    def parse_face(line, current_material):
        parts = line.strip().split()[1:]  # Skip the 'f' part
        face = []
        for part in parts:
            vertex_index, texcoord_index = map(int, part.split('/')[0:2])  # Get vertex and texture coordinate indices
            face.append((vertex_index - 1, texcoord_index - 1))  # Store 0-based indices
        faces_materials.append(current_material)  # Associate the current material with the face
        return face
    
    def parse_mtl_reference(line):
        # Returns the path to the MTL file
        return os.path.join(os.path.dirname(obj_file_path), line.strip().split()[1])
    
    def parse_material(line):
        # Returns the name of the material
        return line.strip().split()[1]


    def find_min_max(vertex_positions):
        # Find the min and max coordinates along each axis
        min_x = min(v[0] for v in vertex_positions)
        max_x = max(v[0] for v in vertex_positions)
        min_y = min(v[1] for v in vertex_positions)
        max_y = max(v[1] for v in vertex_positions)
        min_z = min(v[2] for v in vertex_positions)
        max_z = max(v[2] for v in vertex_positions)
        return min_x, max_x, min_y, max_y, min_z, max_z


    def get_face_center(vertices, face):
        """Calculates the geometric center (average) of a face."""
        x = sum(vertices[vi][0] for vi, _ in face) / len(face)
        y = sum(vertices[vi][1] for vi, _ in face) / len(face)
        z = sum(vertices[vi][2] for vi, _ in face) / len(face)
        return tuple(round(coord, 5) for coord in (x, y, z))+ (1,)
    
    def pick_particle_color(face, face_material):

        # TODO
        # for id in face:
        #     print(id)
        # if any(vertex_color[id] is not None for id in face):
        #     # get the average color of each vertex in the face
        #     r = sum(vertex_color[id][0] for id in face) / len(face)
        #     g = sum(vertex_color[id][1] for id in face) / len(face)
        #     b = sum(vertex_color[id][2] for id in face) / len(face)
        #     a = sum(vertex_color[id][3] for id in face) / len(face)
        #     return r*255, g*255, b*255, a*255
        # If the material the face is using exists
        if face_material in materials:
            if materials[face_material]['texture'] is not None:
                img = Image.open(materials[face_material]['texture'])  # Open the texture image

                # Calculate the average texture coordinates for the face
                texcoord_center = calculate_face_texture_center(texture_coordinates, face)

                # Sample the color from the texture at the center of the face
                color = sample_color_from_texture(texcoord_center, img)
                return color[:4]  # Get RGBA values
            else: # Use the defined color from the material if no texture is available
                r, g, b = materials[face_material]['color'] # Default to white
                a = materials[face_material]['transparency'] if materials[face_material]['transparency'] is not None else 255  # Default to opaque
                return r*255, g*255, b*255, a*255
        else: # Use the default color if the material does not exist
            return default_color
            
        # Check the alpha value (skip if less than 50%)
        if a < 128:  # 50% of 255 is 127.5, so we round up to 128
            return None


    filename = os.path.basename(obj_file_path)
    lines = extract_obj_lines(obj_file_path)
    vertex_positions = [] # List to store vertex positions
    vertex_colors = [] # List to store vertex colors (Nones if absent)
    texture_coordinates = [] # List to store texture coordinates
    faces = [] # List to store faces (each face is a list of vertex indices)
    faces_materials = [] # List to store materials
    current_material = None
    mtl_file_path = None
    materials = {}
    default_color = hex_to_rgb(modifiers.force_color)+(255,) if modifiers else (255, 255, 255, 255)



    for line in lines:
        # process line to extract vertex positions, texture coordinates, faces, and materials
        if line.startswith('v '): # Vertex
            vertex_position, vertex_color = parse_vertex(line)
            vertex_positions.append(vertex_position)
            vertex_colors.append(vertex_color)
        elif line.startswith('vt '): # Texture coordinates
            texture_coordinates.append(parse_texture_coordinate(line))
        elif line.startswith('f '): # Face
            faces.append(parse_face(line, current_material))
        elif line.startswith('mtllib '): # MTL file reference
            mtl_file_path = parse_mtl_reference(line)
        elif line.startswith('usemtl '): # Material
            current_material = parse_material(line)
    

    if mtl_file_path and os.path.exists(mtl_file_path):
        materials = read_mtl_file(mtl_file_path)  # Load materials (textures, colors and transparencies)
        if materials:
            print(f"Using materials from MTL file '{mtl_file_path}'.") if sv.DEBUG else None
        else:
            print(f"No material found in MTL file '{mtl_file_path}'. Using default color.") if sv.DEBUG else None
    else:
        print(f"No MTL file found or referenced in the OBJ file '{filename}'.")
        
    if not vertex_positions:
        print(f"No vertices found in the OBJ file '{filename}'.")
        raise ValueError(f"No vertices found in the OBJ file '{filename}'.")

    min_x, max_x, min_y, max_y, min_z, max_z = find_min_max(vertex_positions)

    # Creating the particle cloud
    dataParticlesList = []
    for face, face_material in zip(faces, faces_materials):

        # Find the geometric center of the face, using fixed decimal formatting (5 decimal places)
        face_center = get_face_center(vertex_positions, face)

        # Find the color of the particle
        r, g, b, a = pick_particle_color(face,face_material)

        # Skip the particle if the alpha value is less than 50%
        if (a < int(InputData.alpha_threshold) ):
            continue

        # Append the particle to the list
        dataParticlesList.append(DataParticle(face_center, (r, g, b, a)))

    if len(dataParticlesList) == 0:
        raise ValueError(f'All particles are transparent.')

    return DataParticlesCloud(dataParticlesList, (min_x, min_y, min_z), (max_x, max_y, max_z))


def create_DataParticlesCloud_from_image(image_path, reset_image_data=False,modifiers=None):
    """
    Creates a DataParticlesCloud object from an image file.

    Parameters:
        image_path (str): The path to the image file.
        threshold (int, optional): The minimum alpha value to consider a pixel non-transparent. Defaults to 240.

    Returns:
        DataParticlesCloud: The created DataParticlesCloud object.
    """
    if sv.DEBUG:
        print("Creating DataParticlesCloud from image...")
    # Open the image and convert it to RGBA
    img = Image.open(image_path).convert('RGBA')

    
    # When the program launches or the a new image is loaded the resolution is set to 0,0, so it needs to be updated.
    if reset_image_data:
        print("Initializing resolution...")
        InputData.image_resolution_width, InputData.image_resolution_height = img.width, img.height #Store original resolution
        ImageData.width_resolution.set(img.width)
        ImageData.height_resolution.set(img.height)



    

    if modifiers is None:
        # Use the resolution settings
        width = int(ImageData.width_resolution.get())
        height = int(ImageData.height_resolution.get())
    else:
        # Use the modifiers
        width, height = modifiers.image_resolution

    # Resize the image to the desired resolution
    sampling = modifiers.resampling if modifiers is not None else ImageData.resampling
    print(f"Resampling: {sampling}")
    if sampling == "Nearest":
        img = img.resize((width, height), Image.Resampling.NEAREST)
    elif sampling == "Bilinear":
        img = img.resize((width, height), Image.Resampling.BILINEAR)
    elif sampling == "Bicubic":
        img = img.resize((width, height), Image.Resampling.BICUBIC)
    else:
        img = img.resize((width, height), Image.Resampling.NEAREST) # Default (should not happen)

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
            if color[3] < InputData.alpha_threshold:
                continue
            

            normalized_x = i/width
            normalized_y = -j/height
            
            position = normalized_x, normalized_y, 0 , 1
            # Add the position and color to the grid points


            dataParticlesList.append(DataParticle(position, color))

    return DataParticlesCloud(dataParticlesList, (min_x, min_y, min_z), (max_x, max_y, max_z))

def read_mtl_file(mtl_file_path):
    
    """
    Reads an MTL file and extracts material properties including textures,
    diffuse colors, and transparency values.

    Returns
    -------
    dict
        A dictionary where keys are material names and values are dictionaries
        containing 'texture' (str or None), 'color' (tuple of floats or None),
        and 'transparency' (float or None) for each material.
    """
    materials = {}
    current_material = None
    
    # Get the directory of the MTL file to handle relative paths
    mtl_dir = os.path.dirname(mtl_file_path)

    with open(mtl_file_path, 'r') as mtl_file:
        for line in mtl_file:
            line = line.strip()
            if line.startswith('newmtl '):
                current_material = line.split()[1]
                materials[current_material] = {'texture': None, 'color': None, 'transparency': None}  # Initialize material
            elif line.startswith('map_Kd ') and current_material is not None:
                texture_path = ' '.join(line.split()[1:])
                # Resolve relative texture paths
                full_texture_path = os.path.join(mtl_dir, texture_path)
                materials[current_material]['texture'] = full_texture_path  # Associate texture with the current material
            elif line.startswith('Kd ') and current_material is not None:
                # Read the diffuse color
                parts = line.split()[1:4]
                materials[current_material]['color'] = tuple(map(float, parts))  # Store color as a tuple (r, g, b)
            elif line.startswith('d ') and current_material is not None:
                # Read the transparency value
                transparency = float(line.split()[1])
                materials[current_material]['transparency'] = transparency

    return materials

def calculate_face_center(vertices, face):
    """Calculates the geometric center (average) of a face."""
    x = sum(vertices[vi][0] for vi, _ in face) / len(face)
    y = sum(vertices[vi][1] for vi, _ in face) / len(face)
    z = sum(vertices[vi][2] for vi, _ in face) / len(face)
    return x, y, z

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

def write_mcfunction_file(input, output_path, output_name,modifiers):

    """
    Writes particle commands to an MCFunction file based on input data.

    This function generates particle commands using the positions and colors
    of particles from a DataParticlesCloud object or an input file path. It
    writes these commands to a specified output file in MCFunction format.

    Parameters:
    - input (str or DataParticlesCloud): The source of particle data, either
      a file path or a DataParticlesCloud instance.
    - output_path (str): The directory where the MCFunction file will be saved.
    - output_name (str): The name of the output MCFunction file.
    - modifiers: An object containing various parameters and settings for
      particle alignment and visualization, such as particle size and view mode.

    Returns:
    - str: A message indicating the success of the MCFunction file creation.
    """

    if isinstance(input,str): # If the input is a file path
        """Writes the particle commands to an MCFunction file using colors from the face centers."""
        CurrentDataParticlesCloud = create_DataParticlesCloud_from_file(input,modifiers)
    elif isinstance(input,DataParticlesCloud): # If the input is a DataParticlesCloud object
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
    if modifiers.force_color_toggle: # If force color toggle is enabled, use the force color for all particles
        CurrentDataParticlesCloud.DataParticlesList = [DataParticle(position=position, color=(*hex_to_rgb(modifiers.force_color), 1)) for position in positions]
    commands = []
    particle_type = modifiers.particle_type
    for index, particle in enumerate(CurrentDataParticlesCloud.DataParticlesList):
        # Format the particle command with fixed decimal positions
        x, y, z, _ = positions[index]
        r, g, b, a = particle.color
        if particle_type == "dust":
            commands.append(
                f"particle dust{{color:[{r/255},{g/255},{b/255}],scale:{modifiers.particle_size}}} "
                f"~{x:.5f} ~{y:.5f} ~{z:.5f} {deltax} {deltay} {deltaz} {speed} {count} {modifiers.viewmode} {modifiers.viewers}"
            )
        elif particle_type == "effect":
            commands.append(
                f"particle entity_effect{{color:[{r/255},{g/255},{b/255},{a/255}],scale:{modifiers.particle_size}}} "
                f"~{x:.5f} ~{y:.5f} ~{z:.5f} {deltax} {deltay} {deltaz} {speed} {count} {modifiers.viewmode} {modifiers.viewers}"
            )


    with open(mcfunction_file_path, 'w') as mcfunction_file:
        mcfunction_file.write('\n'.join(commands))

    return f"MCFunction file '{mcfunction_file_path}' created successfully."

