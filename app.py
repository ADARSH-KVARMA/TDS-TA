import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
import re
from dotenv import load_dotenv
import requests
import base64
from io import BytesIO
from flask import Flask, request, render_template
from flask_cors import CORS

load_dotenv()



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_api_base = "https://aiproxy.sanand.workers.dev/openai/v1/"

def get_top_chunks(question_embedding, npz_path='rag_data.npz', top_k=5):
    # Load the .npz file
    data = np.load(npz_path, allow_pickle=True, mmap_mode='r')
    contents = data['contents']
    titles = data['title']
    urls = data['url']
    embeddings = data['embeddings']

    # Convert question_embedding to 2D array if it's 1D
    question_embedding = np.array(question_embedding).reshape(1, -1)
    embeddings = np.vstack(embeddings)  # Ensure embeddings are a 2D array

    # Compute cosine similarity
    similarities = cosine_similarity(question_embedding, embeddings)[0]

    # Get indices of top_k most similar chunks
    top_indices = np.argsort(similarities)[::-1][:top_k]

    # Retrieve top contents, titles, and urls
    top_chunks = contents[top_indices]
    top_titles = titles[top_indices]
    top_urls = urls[top_indices]

    return top_chunks.tolist(), top_titles.tolist(), top_urls.tolist()

def get_embeddings(text: str):
    openai.api_key = OPENAI_API_KEY
    openai.base_url = openai_api_base

    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    return embedding

def describe_image(base64_image: str, openai_api_base=openai_api_base, api_key=None):
    """
    Takes a base64-encoded image string and returns a short description using OpenAI Vision.
    Automatically handles different image MIME types if present.
    """
    client = openai.OpenAI(
        api_key=api_key or OPENAI_API_KEY,
        base_url=openai_api_base
    )

    # Try to detect MIME type from base64 string
    mime_match = re.match(r'data:(image/\w+);base64,', base64_image)
    if mime_match:
        mime_type = mime_match.group(1)
        # Remove header to keep only the base64 data
        base64_data = re.sub(r'^data:image/\w+;base64,', '', base64_image)
    else:
        # Default to jpeg if MIME type not provided
        mime_type = "image/jpeg"
        base64_data = base64_image

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": "Describe this image in 1-2 short sentences." },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=100,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"

def image_url_to_base64(image_url: str) -> str | None:   
    try:
        # Send a GET request to the image URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Read the image content
        image_content = BytesIO(response.content)

        # Encode the image content to base64
        base64_encoded_data = base64.b64encode(image_content.read())

        # Decode to a UTF-8 string to make it readable
        base64_string = base64_encoded_data.decode('utf-8')

        return base64_string
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - for URL: {image_url}")
        return None
    
def answer_with_context(question: str, api_key=OPENAI_API_KEY, openai_api_base=openai_api_base,):
    """
    Uses GPT-4o-mini to answer a question based on a list of text chunks as context.
    """
    question_embeddings = get_embeddings(question)
    top_chunks, top_titles, top_urls = get_top_chunks(question_embedding=question_embeddings, top_k=4)
    chunks = top_chunks

    # Prepare the prompt
    context_text = "\n".join(chunks)
    prompt_template = f""" Answer the following question in short from the context given.

Question: {question}

Context:
{context_text}
"""
    
    # Set reference links
    links = [{"text": t, "url": u} for t, u in zip(top_titles, top_urls)]


    # Set up OpenAI client
    client = openai.OpenAI(
        api_key=api_key or OPENAI_API_KEY,
        base_url=openai_api_base
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are helpful expert teaching assistant of IIT Madras DS.TDS course."},
                {"role": "user", "content": prompt_template}
            ],
            max_tokens=500,
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()

        return {
            "answer": answer,
            "links": links
        }
    
    except Exception as e:
        return f"Error: {e}"





app = Flask(__name__)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

@app.route("/", methods=["POST","GET"])
def chat():
    if request.method == "POST":
        question = request.form["question"]
        image = request.form.get("image_url", "")
        

        if image == "":
            resp = answer_with_context(question=question)

        else :
            image_base64  = image_url_to_base64(image)
            image_string = describe_image(base64_image=image_base64)
            combined_question = question + "\n" + image_string

            resp = answer_with_context(question=combined_question)

        return render_template("chat.html", question=question, answer=resp["answer"], links=resp["links"])

    return render_template("chat.html", question="", answer="", links="")


@app.route("/api/", methods=["POST", "GET"])
def receive_data():
    if request.is_json:
        data = request.get_json()
        question = data.get("question")

        # Check if 'image' key is present
        if "image" in data:
            image_base64 = data["image"]
            image_string = describe_image(base64_image=image_base64)
            combined_question = question + "\n" + image_string
            resp = answer_with_context(question=combined_question)
            return resp
        else:
            answer = answer_with_context(question=question)
            return answer

    return {"error": "Request content type must be application/json"}


if __name__ == '__main__':
    app.run()
