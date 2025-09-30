import fitz  # PyMuPDF
doc = fitz.open("MEE_342.pdf")
text = ""
for page in doc:
    text += page.get_text()
with open("book.txt", "w", encoding="utf-8") as f:
    f.write(text)