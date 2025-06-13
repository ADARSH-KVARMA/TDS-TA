import json
from bs4 import BeautifulSoup


def extract_posts(input_file, chucks):
    """Open the input file(json) and extract the username, created_at, raw_html content , and post_url 
    AND uppend it to the chuck with formated html content and only required ifromation from .json input file """

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    posts = data.get("post_stream", {}).get("posts", [])
    if not posts:
        print("No posts found in the JSON.")
        return
    
    # get the topic title of the post_stream
    topic_title = data.get("title", "Untitled Topic")
    print(f"Extracting posts from topic: {topic_title}")


    for i, post in enumerate(posts):
        username = post.get("username", "unknown")
        created_at = post.get("created_at", "")
        raw_html = post.get("cooked", "")
        post_url = post.get("post_url", "")

        # extracting image urls from the cooked content
        images = []

        soup = BeautifulSoup(raw_html, "html.parser")
        for img_tag in soup.find_all("img"):
            src = img_tag.get("src")
            if src:
                full_url = src
                images.append(full_url)

        # Convert HTML to plain text
        plain_text = soup.get_text().strip()

        chunk_data = {
            "topic_title": topic_title,
            "username": username,
            "created_at": created_at,
            "content": plain_text,
            "post_url":f"https://discourse.onlinedegree.iitm.ac.in{post_url}" if post_url else "",
            "images": images,

        }

        # Save each post to its own file
        # chunk_filename = os.path.join(output_folder, f"post_{i+1:03d}_{username}.json")
        # with open(chunk_filename, "w", encoding="utf-8") as f_out:
        #     json.dump(chunk_data, f_out, indent=2, ensure_ascii=False)

        #save the chuck in a list
        chucks.append(chunk_data)

    
    

# Extract the name of each json file from the txt file named name_of_json.txt and it contains the name of the json file in each line
def extract_json_filenames(txt_file):
    with open(txt_file, "r") as f:
        filenames = [line.strip() for line in f if line.strip()]
    return filenames



def extract_all_posts(chucks):
    """Extracts posts from all JSON files listed in name_of_json.txt.
    This function reads the filenames from the text file, processes each JSON file,"""

    
    # Loop through each filename and extract posts
    filenames = extract_json_filenames("name_of_json.txt")
    for filename in filenames:
        input_file = f"discourse_json/{filename}"
        print(f"Processing file: {input_file}")
        extract_posts(input_file, chucks)
    

if __name__ == "__main__":
    chucks = []
    extract_all_posts(chucks)
    
    # Print the number of posts extracted
    print(f"Total posts extracted: {len(chucks)}")
    print("Sample post data:", chucks[0] if chucks else "No posts extracted.")
    # Save the extracted posts to a JSON file
    output_file = "extracted_posts.json"
    with open(output_file, "w", encoding="utf-8") as f_out:
        json.dump(chucks, f_out, indent=2, ensure_ascii=False)