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
	CAPTION_ALL = "b3cky" 		#will be in all images

def caption_image_with_ollama(image_path, subject):

	print(image_path)

	command =  "ollama run gemma3:latest \"\"\"you're an AI assistant rating the content of images from 1-10 "
	command += "in order to ban NSFW images from lora caption. Strictly obey the following rules. " 
	command += "rule 1: a woman in the image is always called: " + subject +". "
	command += "rule 2: rate between 1-3 only if the image certainly contains sex between 2 or more persons. "
	command += "rule 3: rate with 4-7 only if you see naked bodyparts breasts, or genitals. " 
	command += "rule 4: rate 7-10 if no naked bodyparts are visible or you are uncertain. "
	command += "rule 5: rate with 8 if you are uncertain about nudity. "

	command += "Here are some examples: "
	command += "example with rating 10: a woman sitting on a sofa wearing a t-shirt with the text 'fuck you' and jeans. \n"
	command += "example with rating 8: a woman leaning on a sofa in a sensual pose wearing a t-shirt and jeans. \n " 
	command += "example with rating 6: a topless woman with pants walking. \n"
	command += "example with rating 4: topless women without pants kissing.\n " 
	command += "example with rating 3: a man and woman having oral sex. \n"
	command += "example with rating 1: a man and woman having missionary, vaginal sex. \n"
	command += "example with rating 8: a naked woman but you are uncertain if she is really naked. \n"
	command += "Based on the ratings, Write a short formal comma sepparated list of booru. \n" 	
	command += "always write the camera angle\n"
	command += "If the rating is between 1 and 3, you write: sex, nude \n"
	command += "If the rating is between 4 and 7, you describe: the naked body parts and persons pose \n"
	command += "If the rating is between 7 and 10, you describe: the clothes the persons are wearing and the persons pose \n"
	command += "example an image with rating 10:upper_body_shot, a woman on sitting on a sofa wearing jeans and tshirt. Output: 'upper_body_shot, "+ subject + ", sitting pose, sofa, jeans, t-shirt, '\n"	
	command += "example an image with rating 9: full_body_shot, a woman walking in a park wearing a gown. Output: full_body_shot, '"+ subject + ", walking pose, gown, park, ' \n"
	command += "example an image with rating 9: close-up a wearing a tank-top. Output: close '"+ subject + ", tank-top, close-up, ' "
	command += "example an image with rating 7: full_body_shot of a woman and man having sex in bed. Output: full_body_shot, '"+ subject + ", man, lying pose, bed, nude, sex, ' \n"
	command += "example an image with rating 8: from_above shot of a naked woman 'but you are uncertain if she is really naked'. Output: from_above, '"+ subject + ",' \n"
	command += "restrict the output to the booru tags and write NOTHING ELSE \"\"\" \n"

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
