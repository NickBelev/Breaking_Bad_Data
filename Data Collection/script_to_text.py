import os
from pypdf import PdfReader

input_folder = 'S3_Scripts_PDF'
output_folder = 'S3_Scripts_TXT'

# Create output folder
os.makedirs(output_folder, exist_ok=True)

# Every pdf script in input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.pdf'):

        # full paths
        pdf_path = os.path.join(input_folder, filename)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(output_folder, txt_filename)
        
        reader = PdfReader(pdf_path)
        
        # Extract text from all pages
        all_text = ''
        for page in reader.pages:
            all_text += page.extract_text() + '\n'
        
        # Write the extracted text to .txt file
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(all_text)
        
        print(f"Converted {filename} to {txt_filename}")
