import json

import ollama

from parse_data import load_items, get_unclaimed_items, save_result


def build_prompt(description, available_items):
    """
    Build the system prompt and user prompt based on the user's description
    and the available items in the lost-and-found database.
    Returns a tuple of (system_prompt, user_prompt).
    """
    system_prompt = """You are a campus lost-and-found assistant.

Rules:
- You must use only the given JSON data.
- Not all details of an item must match to be a possible match.
- You must return ONLY valid JSON, with exactly this structure:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}
- "matches" contains all possible matching item IDs.
- "confidence" must be exactly one of: LOW, MEDIUM, HIGH.
- If there is no match, return an empty list for "matches".
- Do not include any explanation, markdown, or extra text.
"""

    items_json = json.dumps(available_items, indent=2, ensure_ascii=False)

    user_prompt = f"""The user lost an item described as:
"{description}"

Here are the available unclaimed items in the lost-and-found database:
{items_json}

Find all possible matches and return the result as JSON only.
"""

    return system_prompt, user_prompt


def ask_qwen(system_prompt, user_prompt):
    """
    Call the Qwen model through Ollama and return the response text.
    """
    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]


def parse_response(response_text):
    """
    Parse the JSON string returned by Qwen.
    Return None if parsing fails.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return None


def validate_result(result, available_items):
    """
    Validate the result returned by Qwen.
    - Must be a dictionary.
    - Must contain "matches" and "confidence".
    - "matches" must be a list of strings.
    - "confidence" must be one of LOW, MEDIUM, HIGH.
    - All IDs in "matches" must exist in available_items.
    """
    if not isinstance(result, dict):
        return False

    if "matches" not in result or "confidence" not in result:
        return False

    matches = result["matches"]
    confidence = result["confidence"]

    if not isinstance(matches, list):
        return False

    if not all(isinstance(item_id, str) for item_id in matches):
        return False

    if confidence not in ("LOW", "MEDIUM", "HIGH"):
        return False

    valid_ids = {item["id"] for item in available_items}
    if not all(item_id in valid_ids for item_id in matches):
        return False

    return True


def display_matches(result, available_items):
    """
    Display the matches found by Qwen in a user-friendly format.
    """
    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}")
    print()

    matches = result["matches"]

    if not matches:
        print("No matches were found.")
        print("Possible matches: []")
        return

    print("Possible matches:")
    print()

    item_map = {item["id"]: item for item in available_items}

    for item_id in matches:
        item = item_map.get(item_id)
        if not item:
            continue
        print(f"ID: {item['id']}")
        print(f"Item: {item['item']}")
        print(f"Color: {item['color']}")
        print(f"Location: {item['location']}")
        print(f"Date found: {item['date']}")
        print()


def main():
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()

    description = input("Describe the item you lost: ")

    print("\nSearching for possible matches...\n")

    # Load data
    all_items = load_items("found_items.json")
    available_items = get_unclaimed_items(all_items)

    # Build prompt
    system_prompt, user_prompt = build_prompt(description, available_items)

    # Ask Qwen
    response_text = ask_qwen(system_prompt, user_prompt)

    # Parse response
    result = parse_response(response_text)

    # Fall back to an empty result if parsing or validation fails
    if result is None or not validate_result(result, available_items):
        result = {"matches": [], "confidence": "LOW"}

    # Display matches
    display_matches(result, available_items)

    # Save result
    output_file = "output/match_result.json"
    save_result(result, output_file)
    print(f"Result saved to {output_file}")


if __name__ == "__main__":
    main()