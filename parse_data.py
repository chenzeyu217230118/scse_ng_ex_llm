import json
import os


def load_items(filename):
    """
    Load a JSON file and return only the items list.
    Raises an error if the file is missing or malformed.
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "items" not in data:
        raise ValueError("JSON file must contain an 'items' key.")

    return data["items"]


def get_unclaimed_items(items):
    """
    Return only items whose status is 'unclaimed'.
    """
    return [item for item in items if item.get("status") == "unclaimed"]


def save_result(result, filename):
    """
    Save the result to a JSON file.
    Create the directory if it does not exist.
    """
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)