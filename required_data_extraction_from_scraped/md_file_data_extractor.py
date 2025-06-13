import os
import re
import json

def extract_md_data_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Extract YAML front matter
    yaml_match = re.search(r"---\n(.*?)\n---", raw, re.DOTALL)
    metadata = {}
    if yaml_match:
        yaml_text = yaml_match.group(1)
        for line in yaml_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"')

    # Remove YAML front matter from content
    content = re.sub(r"---\n.*?\n---", '', raw, flags=re.DOTALL).strip()

    return {
        "title": metadata.get("title", "Untitled"),
        "original_url": metadata.get("original_url", ""),
        "content": content,
        "downloaded_at": metadata.get("downloaded_at", ""),
        "source_file": os.path.basename(filepath)
    }

def process_all_md_files(folder_path):
    all_docs = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            doc_data = extract_md_data_from_file(file_path)
            all_docs.append(doc_data)

    return all_docs

def extract_md_filenames():
    # Run it
    folder = "tds_pages_md" 
    parsed_data = process_all_md_files(folder)

    # Save as JSON
    with open("tds_markdown_data.json", "w", encoding='utf-8') as f:
        json.dump(parsed_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed and saved {len(parsed_data)} markdown files to tds_markdown_data.json")


# making the chucks of the contents in the JSON file created by the above function
# tds_markdown_data.json

import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_with_recursive_splitter(input_json_path, output_json_path):
    with open(input_json_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []

    for doc in docs:
        raw_text = doc["content"]
        chunks = text_splitter.split_text(raw_text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "title": doc["title"],
                "original_url": doc["original_url"],
                "chunk_id": f"{doc['title']}_chunk_{i+1}",
                "content_chunk": chunk
            })

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully chunked {len(docs)} documents into {len(all_chunks)} chunks.")

# Usage
chunk_with_recursive_splitter("data/tds_markdown_data.json", "tds_markdown_chunks.json")
