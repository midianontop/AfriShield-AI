from pypdf import PdfReader
import json
import os

all_text = ""

documents_folder = "documents"

for filename in os.listdir(documents_folder):

    filepath = os.path.join(documents_folder, filename)

    # Read PDFs
    if filename.endswith(".pdf"):
        print(f"Reading PDF: {filename}")

        reader = PdfReader(filepath)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                all_text += page_text + "\n"

    # Read TXT files
    elif filename.endswith(".txt"):
        print(f"Reading TXT: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            all_text += f.read() + "\n"


# Split into words
words = all_text.split()

chunk_size = 200
chunks = []

for i in range(0, len(words), chunk_size):
    chunk = " ".join(words[i:i + chunk_size])
    chunks.append(chunk)

# Save chunks
with open("documents/chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)

print(f"\nSaved {len(chunks)} chunks")