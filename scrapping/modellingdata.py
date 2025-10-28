import json
import random
from typing import Dict, List

def generate_qa_pairs(content: Dict) -> List[Dict[str, str]]:
    """
    Generate question-answer pairs from the scraped website content.
    This uses simple rule-based generation for fine-tuning datasets.
    For more advanced synthetic Q&A, consider integrating an LLM API.
    """
    qa_pairs = []
    
    # Basic metadata Q&A
    if 'url' in content:
        qa_pairs.append({
            "question": "What is the URL of the webpage?",
            "answer": content['url']
        })
    
    if 'metadata' in content and 'title' in content['metadata']:
        qa_pairs.append({
            "question": "What is the title of the webpage?",
            "answer": content['metadata']['title']
        })
    
    # Headings Q&A (one per level if present)
    if 'headings' in content:
        for level, hs in content['headings'].items():
            if hs:
                qa_pairs.append({
                    "question": f"What are the {level} headings on the webpage?",
                    "answer": "; ".join(hs)
                })
    
    # Paragraphs Q&A (sample a few)
    if 'paragraphs' in content:
        for i, p in enumerate(content['paragraphs'][:5]):  # Limit to first 5
            qa_pairs.append({
                "question": f"What does the {i+1}th paragraph on the webpage say?",
                "answer": p
            })
    
    # Links Q&A (overview)
    if 'links' in content:
        link_texts = [link['text'] for link in content['links'][:3]]  # First 3
        qa_pairs.append({
            "question": "What are some key links on the webpage?",
            "answer": "; ".join(link_texts)
        })
    
    # Images Q&A
    if 'images' in content:
        img_alts = [img['alt'] for img in content['images'] if img['alt']]
        if img_alts:
            qa_pairs.append({
                "question": "What are the alt texts of images on the webpage?",
                "answer": "; ".join(img_alts[:3])  # First 3
            })
    
    # Lists Q&A (sample)
    if 'lists' in content:
        for i, lst in enumerate(content['lists'][:2]):
            qa_pairs.append({
                "question": f"What are the items in the {i+1}th list on the webpage?",
                "answer": "; ".join(lst['items'])
            })
    
    # Tables Q&A (basic summary)
    if 'tables' in content:
        for i, table in enumerate(content['tables'][:1]):  # First table
            flat_table = [", ".join(row) for row in table['rows'][:3]]  # First 3 rows
            qa_pairs.append({
                "question": f"What is a summary of the first table on the webpage?",
                "answer": "\n".join(flat_table)
            })
    
    # Full text summary Q&A (simple excerpt)
    if 'full_text' in content:
        sentences = content['full_text'].split('. ')[:3]  # First 3 sentences
        qa_pairs.append({
            "question": "Provide a brief summary of the webpage content.",
            "answer": ". ".join(sentences) + "."
        })
    
    # Add some synthetic questions for variety (e.g., extraction tasks)
    qa_pairs.append({
        "question": "Extract the main content text from this webpage data: [insert full_text here]",
        "answer": content.get('full_text', 'No text available')
    })
    
    return qa_pairs

# Load the scraped JSON (from previous script)
input_file = 'Frontend.sh.json'
with open(input_file, 'r', encoding='utf-8') as f:
    content = json.load(f)

# Generate Q&A pairs
qa_pairs = generate_qa_pairs(content)

# Save as JSONL for fine-tuning (one object per line)
output_file = 'qa_dataset.jsonl'
with open(output_file, 'w', encoding='utf-8') as f:
    for pair in qa_pairs:
        # Format for fine-tuning (e.g., OpenAI style: prompt/completion)
        line = {
            "prompt": pair["question"],
            "completion": pair["answer"]
        }
        f.write(json.dumps(line, ensure_ascii=False) + '\n')

print(f"Generated {len(qa_pairs)} Q&A pairs and saved to {output_file}")
print("Sample pair:")
print(json.dumps(qa_pairs[0], indent=2, ensure_ascii=False))