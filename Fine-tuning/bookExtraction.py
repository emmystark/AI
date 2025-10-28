import requests
import json
from transformers import T5ForConditionalGeneration, T5Tokenizer
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

# Step 1: Download a smaller portion of the book from Project Gutenberg with retry
def download_book(url, output_file="/Volumes/Stark/Repo/AI/Fine-tuning/book.txt", max_lines=500, retries=5):
    # Configure session with retry logic
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        print(f"Attempting to download from {url}")
        response = session.get(url, timeout=60, stream=True)  # Stream to handle large files
        response.raise_for_status()  # Check for request errors
        lines = response.text.splitlines()
        
        # Skip Project Gutenberg header and footer
        start_marker = "Chapter 1"  # Start of main content
        end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
        content = []
        capture = False
        
        for line in lines[:max_lines]:  # Limit to max_lines
            if start_marker in line:
                capture = True
            if end_marker in line:
                break
            if capture:
                content.append(line)
        
        text = "\n".join(content)
        if not text:
            print("No content captured. Check start_marker or max_lines.")
            return ""
        
        # Save to external drive
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Saved {len(text)} characters to {output_file}")
        return text
    except requests.exceptions.RequestException as e:
        print(f"Failed to download book after {retries} retries: {e}")
        return ""

# Step 2: Chunk the text
def chunk_text(text, chunk_size=500):
    if not text:
        return []
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

# Step 3: Generate Q&A pairs
def generate_qa(context, model, tokenizer, max_length=512, num_questions=3, cache_dir="/Volumes/Stark/huggingface_cache"):
    qa_pairs = []
    prompt_template = (
        "Generate {} question-answer pairs based on the following context:\n\n{}\n\n"
        "Output as a list of dictionaries with 'question' and 'answer' keys in valid JSON format."
    )
    prompt = prompt_template.format(num_questions, context[:1000])  # Truncate context if too long
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_length)
    outputs = model.generate(inputs.input_ids, max_length=500, num_beams=5)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Parse response
    try:
        qa_list = json.loads(response)  # Safely parse JSON
        qa_pairs.extend(qa_list)
    except json.JSONDecodeError:
        print("Error parsing model output for context:", context[:50])
        return []
    
    return qa_pairs

# Main workflow
def main():
    # Set environment variables for external drive
    os.environ["HF_HOME"] = "/Volumes/Stark/huggingface_cache"
    os.environ["TMPDIR"] = "/Volumes/Stark/tmp"
    
    # Create directories if they don't exist
    os.makedirs("/Volumes/Stark/huggingface_cache", exist_ok=True)
    os.makedirs("/Volumes/Stark/tmp", exist_ok=True)
    
    # Download Pride and Prejudice (limited portion)
    book_url = "https://www.gutenberg.org/files/1342/1342-0.txt"
    text = download_book(book_url, max_lines=500)  # Reduced for smaller file
    if not text:
        print("Exiting due to download failure.")
        return
    
    # Chunk the text
    chunks = chunk_text(text)
    
    # Load model and tokenizer
    model_name = "google/flan-t5-base"
    cache_dir = "/Volumes/Stark/huggingface_cache"
    tokenizer = T5Tokenizer.from_pretrained(model_name, cache_dir=cache_dir, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(model_name, cache_dir=cache_dir)
    
    # Generate Q&A for first 5 chunks (reduced for testing)
    dataset = []
    for chunk in chunks[:5]:  # Process only 5 chunks
        qa_pairs = generate_qa(chunk, model, tokenizer, cache_dir=cache_dir)
        for qa in qa_pairs:
            dataset.append({
                "instruction": qa["question"],
                "output": qa["answer"]
            })
    
    # Save to JSONL on external drive
    output_file = "/Volumes/Stark/Repo/AI/Fine-tuning/qa_dataset.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for entry in dataset:
            f.write(json.dumps(entry) + "\n")
    
    print(f"Dataset generated and saved to {output_file}")

if __name__ == "__main__":
    main()