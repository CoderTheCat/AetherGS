import subprocess
import sys

scene_path = r"e:\Code\LiteGS\data\360_v2\garden"
output_path = r"e:\Code\LiteGS\output\garden_test"
image_folder = "images_4"

command = [
    sys.executable,
    "example_train.py",
    "-s", scene_path,
    "-m", output_path,
    "-i", image_folder,
    "--sh_degree", "3",
    "--iterations", "100",
    "--eval"
]

print(f"Running command: {' '.join(command)}")
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in process.stdout:
    print(line, end='')

process.wait()
print(f"\nExit code: {process.returncode}")
