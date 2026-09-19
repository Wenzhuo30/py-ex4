## Import the necessary modules
import json
import os
## Logic for loading and reading from a JSON file. 
## The function must return only the items
def load_items(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    
    items = data.get("items", [])
    
    if not isinstance(items, list):
        raise ValueError(f"JSON format error: 'items' field in {filename} must be an array.")
    
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"JSON format error: item at index {i} is not a dictionary.")
    
    return items



## Logic for getting only those items that are not yet claimed 
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    unclaimed_items = [item for item in items if not item.get("claimed", False)]
    return unclaimed_items
    

## Logic to save the result to a JSON file.
## The function should create the directory 
# if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    
    with open(filename, "w") as file:
        json.dump(result, file, indent=4)
        