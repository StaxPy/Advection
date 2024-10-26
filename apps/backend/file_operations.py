import os
import shared.variables as sv
import json
import re

def update_json_memory(parameter,value):
    # Read the JSON file
    with open(os.path.join(os.path.dirname(__file__), sv.MEMORY_PATH), 'r') as f:
        data = json.load(f)

    # Modify the desired value
    data[parameter] = value

    # Write the modified data back to the JSON file
    with open(os.path.join(os.path.dirname(__file__), sv.MEMORY_PATH), "w") as f:
        json.dump(data, f)

def get_json_memory(parameter):
    # Read the JSON file
    with open(os.path.join(os.path.dirname(__file__), sv.MEMORY_PATH), 'r') as f:
        data = json.load(f)
    return data.get(parameter)


def find_file_sequence(input_path):
    sv.seq_length = 0
    sv.first_frame = 1
    sv.last_frame = 1
    sv.input_extension = os.path.splitext(input_path)[1] # Get the extension of the input file
    sv.input_folder = os.path.dirname(input_path) # Get the parent directory of this file
    sv.input_name = re.sub(r'\d+$', '', os.path.splitext(os.path.basename(input_path))[0]) # Get the name of the input file without the number at the end
    
    sv.sequence_files["selected"] = {"path": input_path, "filename": sv.input_name} # Store the selected name and path the files dictionary
    # global_var.input.files["selected"] = {"path": input_path, "filename": input_name} # Store the selected name and path the files dictionary
    for file in os.listdir(sv.input_folder):  # Find all files with the same extension and name as the input file
        if file.endswith(sv.input_extension) and re.sub(r'\d+$', '', os.path.splitext(file)[0]) == sv.input_name and re.search(r'(\d+)$', os.path.splitext(file)[0]):
            match = re.search(r'(\d+)$', os.path.splitext(file)[0]) 
            if match:
                sv.seq_length += 1
                number_part = int(match.group(1))
                sv.first_frame = min(sv.first_frame, number_part)
                sv.last_frame = max(sv.last_frame, number_part)
            sv.sequence_files[number_part] = {"path": sv.input_folder+"/"+file, "filename": os.path.splitext(file)[0]} # Store this frame's name and path the files dictionary

