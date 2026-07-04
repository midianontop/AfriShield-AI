from pypdf import PdfReader

reader = PdfReader("OWASP_Testing_Guide_v4.pdf")

text = ""

for page in reader.pages:
    text += page.extract_text() + "\n"

chunk_size = 500

chunks = []

for i in range(0, len(text), chunk_size):
    chunk = text[i:i + chunk_size]
    chunks.append(chunk)

print("Total Chunks:", len(chunks))

print("\nFirst Chunk:\n")
print(chunks[0])