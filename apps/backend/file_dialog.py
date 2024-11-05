import os
from shared.variables import *
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
    InputData.seq_length = 0
    InputData.first_frame = 1
    InputData.last_frame = 1
    InputData.extension = os.path.splitext(input_path)[1] # Get the extension of the input file
    InputData.folder = os.path.dirname(input_path) # Get the parent directory of this file
    InputData.name = re.sub(r'\d+$', '', os.path.splitext(os.path.basename(input_path))[0]) # Get the name of the input file without the number at the end
    
    InputData.sequence_files = {}
    # InputData.sequence_files["selected"] = {"path": input_path, "filename": InputData.name} # Store the selected name and path the files dictionary
    for file in os.listdir(InputData.folder):  # Find all files with the same extension and name as the input file
        if file.endswith(InputData.extension) and re.sub(r'\d+$', '', os.path.splitext(file)[0]) == InputData.name and re.search(r'(\d+)$', os.path.splitext(file)[0]):
            match = re.search(r'(\d+)$', os.path.splitext(file)[0]) 
            if match:
                InputData.seq_length += 1
                number_part = int(match.group(1))
                InputData.first_frame = min(InputData.first_frame, number_part)
                InputData.last_frame = max(InputData.last_frame, number_part)
            InputData.sequence_files[number_part] = {"path": InputData.folder+"/"+file, "filename": os.path.splitext(file)[0]} # Store this frame's name and path the files dictionary

    print("Found",InputData.seq_length,"frames")