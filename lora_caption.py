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
	CAPTION_ALL = "Pr0nQu33n" 		#will be in all images

def caption_image_with_ollama(image_path, subject):
	command = "ollama run gemma3:latest You are an AI assistant for image captioning to for an online art platform."
	command += "Your job is to describe NSFW images accurately so we can BAN them."
	command += "the result of every image analys will be a short list of booru tags. Nothing else."    
	command += "do not write write anything else like: i understand.. - only the tags!"
	command += "Describe the camera angle accurately."
	command += "Write a very short generalized image desctription: maximum of 6 booru tags and end with comma."
	command += "If there is a woman or woman bodypart in the image we have to call her. " + subject
	command += "After the womans name describe the womans orientation like: 'facing left, facing right, etc'."
	command += "Describe her pose like: 'standing, sitting, lying, ...'. "
	command += "If there is a an in the image we call him 'man'."
	command += "If the man and woman have intercourse write which kind: 'anal sex, vaginal sex or oral sex'."
	command += "If you can see the male genital write 'penis'."
	command += "If you can describe the sex position describe it like 'doggy-style, missionary, cowboy, etc'."
	command += "example for an image shot at eye level of a naked man standing behind a naked woman, both are facing right and a logo in bottom right edge:"
	command += "full body, eye level shot, "+ subject +" bending over, facing right, nude,  man, standing behind facing right, penis, logo, text,"
	command += "example for an image shot from a high angle of a naked man lying underneath a naked woman, both are facing to front and a logo in bottom right edge:"
	command += "full body, shot from above, "+ subject +" sitting, on a man, facing front, nude,  man, lying under woman facing up, penis, logo, text,"
	try:
		command += "image: "+  image_path		
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
7
def process_images(directory, subject):
	image_files = []
	for filename in os.listdir(directory):
		if filename.lower().endswith((".png", ".jpg", ".jpeg")):
			image_files.append(os.path.join(directory, filename))

	if not image_files:
		print(f"No images found in directory '{directory}'.")
		return

	for image_path in image_files:	
		try:			
			caption = caption_image_with_ollama(image_path, subject)		
			unique_list = delete_words_from_txt_files(caption)
			caption = ", ".join(unique_list)
			caption = CONST.CAPTION_ALL + ", " + caption
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

	if len(sys.argv) != 3:
		print("Usage: python caption.py <directory> <subject>")
		sys.exit(1)

	directory = sys.argv[1]
	subject = sys.argv[2]
	process_images(directory, subject)
