# Usage: "python lora_caption.py d:\exampledir\images\"
# For lora captioning - you need one unique caption like '3x4mple'.
# You caption everything except the subject your lora is about
# The command for the LLM is specific for a NSFW female character training
# the llm prompt is ok'ish but could certainly be approved upon - pls create PR

import os
import subprocess
import time
import glob
import sys
import shutil
def remove_unsuitable(image_path):
	
	command = "ollama run gemma3:latest \"Analyze the image for sharpness,  rate from 1-10, 1 is completely blurred, 6 = medium blurr, 10 = no blurr. Respond with rating and 'OK' if rating > 5  or 'FAIL'.\""

	try:
		command += "image: "+  image_path		
		result = subprocess.run(command, capture_output=True, text=True, check=True)
		output = result.stdout.strip()  # Remove leading/trailing whitespace

		if 'FAIL' in output:
			blurred_folder = os.path.join(os.path.dirname(image_path), "blurred")
			if not os.path.exists(blurred_folder):
				os.makedirs(blurred_folder)
				print(f"Created folder: {blurred_folder}")
			# Move the file to the 'blurred' folder
			destination_path = os.path.join(blurred_folder, os.path.basename(image_path))
			try:
				shutil.move(image_path, destination_path)
				print(f"Moved {os.path.basename(image_path)} to {blurred_folder}")
			except Exception as e:
				print(f"Error moving file: {e}")
		return output
	except subprocess.CalledProcessError as e:
		print(f"Error captioning image {image_path}:")
		print(e.stderr)
		return None


def process_images(directory):
	image_files = []
	for filename in os.listdir(directory):
		if filename.lower().endswith((".png", ".jpg", ".jpeg")):
			image_files.append(os.path.join(directory, filename))

	if not image_files:
		print(f"No images found in directory '{directory}'.")
		return

	for image_path in image_files:			
		remove_unsuitable(image_path)					
					
if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("Usage: python caption.py <directory>")
		sys.exit(1)

	directory = sys.argv[1]
	process_images(directory)
