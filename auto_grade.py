import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os
import importlib.util
import shutil
import ast

from skimage.metrics import structural_similarity as ssim
from PIL import Image
import io

FORBIDDEN_IMPORTS = {"os", "sys", "subprocess", "shutil"}

# Check for nefarious activites 
def check_forbidden_imports(path, forbidden_imports):
    global errors
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except SyntaxError as e:
        return False, [f"Syntax error while parsing file: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in forbidden_imports:
                    #errors.append(f"Forbidden import detected: {alias.name}")
                    break
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in forbidden_imports:
                #errors.append(f"Forbidden import detected: {node.module}")
                break

    return True, None    

def load_expected_outputs():
    expected_values = np.load("correct_answers/expected_output.npy")
    expected_img = Image.open("correct_answers/expected_plot.png")
    return expected_values, expected_img

def run_student_script(path):
    spec = importlib.util.spec_from_file_location("student_module", path)
    student = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(student)
    return student

def extract_plot():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Image.open(buf)

def compare_values(student_output, correct_output, tol=1e-4):
    return np.allclose(student_output, correct_output, atol=tol)

def compare_images(student_img, correct_img):
    student_img = student_img.convert('L').resize(correct_img.size)
    correct_img = correct_img.convert('L')
    student_arr = np.array(student_img)
    correct_arr = np.array(correct_img)
    score, _ = ssim(student_arr, correct_arr, full=True)
    return score

def grade_student(student_path, expected_values, expected_img): 
    student = run_student_script(student_path)
    
    student_output = getattr(student, "result", None)
    student_plot = extract_plot()

    score = 0
    if compare_values(student_output, expected_values):
        score += 1
        print("Output values correct.")
    else:
        print("Output values incorrect.")

    similarity = compare_images(student_plot, expected_img)
    if similarity > 0.95:
        score += 1
        print("Plot is correct.")
    else:
        print(f"Plot is incorrect. Similarity: {similarity:.2f}")

    return score

if __name__ == "__main__":
    expected_values, expected_img = load_expected_outputs()

    student_dir = "student_scripts"
    for filename in os.listdir(student_dir):
        if filename.endswith(".py"):
            path = os.path.join(student_dir, filename)
            # Check imports first
            print(f"\nChecking {filename} for forbidden imports")
            ok, message = check_forbidden_imports(path)
            if not ok:
                 print(f"\n{filename} has a forbidden import")
                 continue
            # Grade Student
            print(f"\nGrading {filename}:")
            score = grade_student(path, expected_values, expected_img)
            print(f"Total Score: {score}/10")

        # Future Functionality
        # Put all student scores into a data frame and export as a csv