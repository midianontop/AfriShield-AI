from pypdf import PdfReader

reader = PdfReader("OWASP_Testing_Guide_v4.pdf")

print("Pages:", len(reader.pages))

print("\nFirst page preview:\n")

text = reader.pages[0].extract_text()

print(text[:500])