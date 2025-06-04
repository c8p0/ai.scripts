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

class CONST(object):
	BLACKLIST = ['pose', 'woman', 'female', 'girl', 'no-clothing', 'relaxed',
	'neutral', 'room', 'interior', 'furniture', 'light', 'natural light', 'casual']
	UNIQUE_CAPTION = "3x4mple, " 

	

def caption_image_with_ollama(image_path):
	command = """ollama run gemma3:latest you are an AI assistant for image captioning 
	in a comma sepparated very short list of booru tags. do not describe the woman. 
	In order to ban NSFW images, write any important NSFW caption. 
	Do not write something like 'no-clothes' if there are not clothes in the image.
	Describe the camera angle for example 'frontal, from the front, ...'. 
	Describe the womans orientation like: 'facing left, facing right, ...'. 
	Describe her pose like: 'standing, sitting, lying, ...'. 
	When a man is visible describe him.
	If you see male genitals, describe them.
	Write nothing else. 
	do not write the captions: 'camera angle, pose, subject orientation, breast size, no clothing, woman, no-clothing,  female, girl woman'.  
	Do not describe hair. 
	Do not repeat any word.
	Do not describe things which are not present in the picture """

	try:
		command = command + image_path
		result = subprocess.run(command, capture_output=True, text=True, check=True)
		return result.stdout.strip()  # Remove leading/trailing whitespace
	except subprocess.CalledProcessError as e:
		print(f"Error captioning image {image_path}:")
		print(e.stderr)
		return None

def delete_words_from_txt_files(caption):  
	#Replace all occurrences of words in the file
	for word in CONST.BLACKLIST:
		caption = caption.replace(word + ",", "")

	caption = caption.split(",")
	seen = set()
	unique_list = []
	for word in caption:
		if word not in seen:
			unique_list.append(word)
		seen.add(word)

	return seen

def process_images(directory):
	image_files = []
	for filename in os.listdir(directory):
		if filename.lower().endswith((".png", ".jpg", ".jpeg")):
			image_files.append(os.path.join(directory, filename))

	if not image_files:
		print(f"No images found in directory '{directory}'.")
		return

	for image_path in image_files:	
		try:			
			caption = caption_image_with_ollama(image_path)		
			unique_list = delete_words_from_txt_files(caption)
			caption = ", ".join(unique_list)
			caption = CONST.UNIQUE_CAPTION + caption
			print(caption+'\n')
			if caption is not None:                
				filename = os.path.basename(image_path)
				filename_without_ext, ext = os.path.splitext(filename)
				output_filename =  f"{directory + "\\" + filename_without_ext}.txt"
				with open(output_filename, "w") as f:  # Use 'with' for file handling
					f.write(caption)
				print(f"Caption saved to: {output_filename}")  # Added print statement				
			else:
				print(f"Failed to generate caption for: {image_path}")
		except Exception as e:
			print(f"Error processing {image_path}: {e}")


if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("Usage: python caption.py <directory>")
		sys.exit(1)

	directory = sys.argv[1]
	process_images(directory)
