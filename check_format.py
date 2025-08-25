"""
check_format.py
Run this script to make sure your submission is in the correct format
before submitting.
"""

import importlib.util
import sys
import matplotlib.pyplot as plt

REQUIRED_VARIABLES = ["result"]
REQUIRED_FUNCTIONS = ["my_func"]
errors = []

def check_student_file(path):
    global errors

    if not path.endswith(".py"):
        return False, "File must be a .py file"

    try:
        # Clear any existing plots before running student script
        plt.close("all")

        spec = importlib.util.spec_from_file_location("student_module", path)
        student = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(student)
    except Exception as e:
        return False, f"Your script could not run: {e}"

    # Check variables
    for var in REQUIRED_VARIABLES:
        if not hasattr(student, var):
            errors.append(f"Missing required variable: {var}")

    # Check functions
    for func in REQUIRED_FUNCTIONS:
        if not hasattr(student, func):
            errors.append(f"Missing required function: {func}()")

    # Check plot creation
    if not plt.get_fignums():  # no figure windows created
            errors.append("No plot detected")

    if errors:
        return False, errors
    return True, "File format confirmed! You may submit now."

if __name__ == "__main__":
    # Check for correct usage
    if len(sys.argv) != 2:
        print("Usage: python check_format.py your_file.py")
        sys.exit(1)

    student_file = sys.argv[1]
    ok, message = check_student_file(student_file)
    print(message)
    sys.exit(0 if ok else 1)
