import os
import csv

input_folder = 'S3_Scripts_TXT'
output_file = 'script_dialogues.tsv'

# List of characters to collect lines for
characters_of_interest = ["GUS", "SKYLER", "MIKE", "SAUL"]  # As agreed upon

# Assuming all character names abide by this, if not no biggy, we're not missing any of our big 4
def is_character_name(line):
    return line.isupper() and 2 <= len(line) <= 30

# Open the output file with pipe-separated values
with open(output_file, 'w', newline='', encoding='utf-8') as tsv_file:
    writer = csv.writer(tsv_file, delimiter='\t')  # TSV
    writer.writerow(['character', 'dialogue_line', 'episode'])  # Header

    # Process each text file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            # Extract episode name from the filename
            episode = os.path.splitext(filename)[0]
            txt_path = os.path.join(input_folder, filename)

            # Read the file content
            with open(txt_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Process each line in the script
            i = 0
            while i < len(lines):
                line = lines[i].strip()  # Remove leading and trailing whitespace

                # The line is a character name that we should track
                if is_character_name(line) and line in characters_of_interest:
                    current_character = line
                    dialogue = ""
                    i += 1  # Move to the next line for dialogue

                    # Collect dialogue lines until the next character name or end of file
                    while i < len(lines) and not is_character_name(lines[i].strip()):
                        dialogue += lines[i].strip().replace('\n', ' ').replace('\t', ' ') + " "
                        i += 1  # Move to next line

                    # Done with this dialogue write it
                    writer.writerow([current_character, dialogue.strip(), episode])

                else:
                    i += 1  # Move to the next line since it's not a character name of interest

print(f"Dialogue extraction completed. Output saved to {output_file}")
