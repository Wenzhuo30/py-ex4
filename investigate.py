## Import the necessary modules
import json
from ollama import chat
## Import the function from the module parse_data
from parse_data import (
    load_items,
    get_unclaimed_items, 
    save_result

    )

## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items 
# list into a JSON string.

def build_prompt(description, available_items):
    system_prompt = """You are a campus lost-and-found matching assistant. Strictly follow these rules:
    1. Only match based on the provided lost-and-found item data. Do not use any external information.
    2. An item does not need all details to match exactly to be considered a possible match.
    3. You must return ONLY a pure JSON object. Do not include any extra text, explanations, markdown formatting, or code blocks.
    4. The JSON structure must strictly follow this format:
    {
        "matches": ["ITEM_ID"],
        "confidence": "LOW"
    }
    5. The matches field is an array of all possibly matching item IDs. If no matches are found, return an empty array [].
    6. The confidence field indicates the confidence level of the match, and must be one of: LOW, MEDIUM, HIGH.
    """

    items_json = json.dumps(available_items, indent=2)
    user_prompt = f"""Description of the lost item: {description}

    Below is all current unclaimed lost-and-found item data:
    {items_json}

    Find all possible matching items based on the user's description, and return the result in the required JSON format."""

    return system_prompt, user_prompt


    

    

## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = chat(
        model="qwen3:8b",
        messages=messages
    )
    
    return response.message.content


## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    result = json.loads(response_text)
    return result
    


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    
    if "matches" not in result or "confidence" not in result:
        return False
    
    if not isinstance(result["matches"], list):
        return False
    
    valid_confidences = {"LOW", "MEDIUM", "HIGH"}
    if result["confidence"] not in valid_confidences:
        return False
    
    valid_ids = {item["id"] for item in available_items}
    
    for item_id in result["matches"]:
        if item_id not in valid_ids:
            return False
    
    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}")
    
    matches = result["matches"]
    if not matches:
        print("\nNo matches found.")
    else:
        print("\nPossible matches:")

        item_map = {item["id"]: item for item in available_items}
        for match_id in matches:
            item = item_map.get(match_id)
            if item:
                print(f"ID: {item['id']}")
                print(f"Item: {item['item']}")
                print(f"Color: {item['color']}")
                print(f"Location: {item['location']}")
                print(f"Date found: {item['date']}")
                print()
    
    
    save_result(result, "output/match_result.json")
    print("Result saved to output/match_result.json")
    

## Control center for the entire program.
def main():
    items = load_items("found_items.json")
    available_items = get_unclaimed_items(items)
    
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    description = input("Describe the item you lost: ")
    print("\nSearching for possible matches...")
    
    system_prompt, user_prompt = build_prompt(description, available_items)
    
    response_text = ask_qwen(system_prompt, user_prompt)
    
    try:
        result = parse_response(response_text)
    except json.JSONDecodeError:
        print("Error: Model returned invalid JSON format.")
        return
    
    if not validate_result(result, available_items):
        print("Error: Invalid result structure or invalid item IDs.")
        return
    
    display_matches(result, available_items)


if __name__ == "__main__":
    main()