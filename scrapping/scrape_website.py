import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse

# URL of the website to scrape
url = "https://medium.com/data-science-collective/youre-using-chatgpt-wrong-here-s-how-to-prompt-like-a-pro-1814b4243064"  # Replace with your target URL

# Send a GET request with browser-like headers to avoid blocks
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code != 200:
    print(f"Failed to retrieve website: {response.status_code}")
    exit()

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Remove non-content elements (scripts, styles, nav, etc.) to focus on main content
for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
    element.decompose()

# Extract metadata (title, meta tags like description, keywords, OpenGraph, etc.)
metadata = {}
title_tag = soup.find('title')
if title_tag:
    metadata['title'] = title_tag.get_text().strip()

meta_tags = soup.find_all('meta')
for meta in meta_tags:
    name = meta.get('name') or meta.get('property')
    content = meta.get('content')
    if name and content:
        metadata[name] = content

# Extract full visible text content (all text, cleaned up)
full_text = soup.get_text()
lines = (line.strip() for line in full_text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
full_text = '\n'.join(chunk for chunk in chunks if len(chunk) > 0)

# Extract headings (h1 through h6)
headings = {}
for level in range(1, 7):
    tag = f'h{level}'
    headings[tag] = [h.get_text().strip() for h in soup.find_all(tag)]

# Extract paragraphs
paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]

# Extract links (with text and absolute URLs)
links = []
for a in soup.find_all('a', href=True):
    link = {
        'text': a.get_text().strip(),
        'href': urljoin(url, a['href'])
    }
    links.append(link)

# Extract images (with alt text and absolute URLs)
images = []
for img in soup.find_all('img', src=True):
    image = {
        'src': urljoin(url, img['src']),
        'alt': img.get('alt', '').strip()
    }
    images.append(image)

# Extract lists (unordered/ordered, with items)
lists = []
for list_tag in soup.find_all(['ul', 'ol']):
    list_items = [li.get_text().strip() for li in list_tag.find_all('li') if li.get_text().strip()]
    if list_items:
        lists.append({
            'type': list_tag.name,
            'items': list_items
        })

# Extract tables (basic row/cell structure)
tables = []
for table in soup.find_all('table'):
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.get_text().strip() for td in tr.find_all(['td', 'th'])]
        if cells:
            rows.append(cells)
    if rows:
        tables.append({'rows': rows})

# Compile everything into a structured dictionary
content = {
    "url": url,
    "metadata": metadata,
    "full_text": full_text,
    "headings": headings,
    "paragraphs": paragraphs,
    "links": links,
    "images": images,
    "lists": lists,
    "tables": tables
}

# Save to JSON file (with UTF-8 encoding for international text)
output_file = 'website_everything.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(content, f, ensure_ascii=False, indent=4)

print(f"Everything extracted from {url} and saved to {output_file}")
print(f"Full text length: {len(full_text)} characters")
print(f"Found {len(links)} links, {len(images)} images, {len(lists)} lists, {len(tables)} tables")