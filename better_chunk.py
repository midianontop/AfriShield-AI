from pypdf import PdfReader

reader = PdfReader("OWASP_Testing_Guide_v4.pdf")

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

words = text.split()

chunk_size = 200

chunks = []

for i in range(0, len(words), chunk_size):
    chunk = " ".join(words[i:i + chunk_size])
    chunks.append(chunk)

print("Total Chunks:", len(chunks))

print("\nFirst Chunk:\n")
print(chunks[0])