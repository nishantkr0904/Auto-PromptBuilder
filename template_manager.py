import json
import os
from firebase_auth import db


def load_templates(user_id=None):
    """
    Loads templates from Firebase (if user_id provided)
    and local JSON files.

    Args:
        user_id (str, optional): User ID for fetching templates from Firebase

    Returns:
        dict: Combined dictionary of templates
    """

    templates = {}

    # 🔹 1. Load from Firebase
    if user_id:
        try:
            firebase_templates = db.child("templates").child(user_id).get()

            if firebase_templates.each():
                for item in firebase_templates.each():
                    if item.val():  # validation
                        templates[item.key()] = item.val()

        except Exception as e:
            print(f"[Firebase Error]: {str(e)}")

    # 🔹 2. Load from local directory
    template_dir = "templates"

    if not os.path.exists(template_dir):
        print(f"[Warning]: '{template_dir}' directory not found")
        return templates

    for file in os.listdir(template_dir):
        if file.endswith(".json"):
            file_path = os.path.join(template_dir, file)

            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                    if isinstance(data, dict):  # validation
                        templates[file.split(".")[0]] = data
                    else:
                        print(f"[Invalid JSON format]: {file}")

            except json.JSONDecodeError:
                print(f"[JSON Error]: Failed to parse {file}")
            except Exception as e:
                print(f"[File Error]: {file} - {str(e)}")

    return templates
