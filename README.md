
# 🧠 Virtual TA for TDS Course (IIT Madras B.S. Degree)

This is a **Retrieval-Augmented Generation (RAG)** based Virtual Teaching Assistant built specifically for the **TDS (Tools in Data Science)** course of the **IIT Madras B.S. Degree program**.

It helps students by answering their doubts based **strictly on the official course content** (from [tds.s-anand.net](https://tds.s-anand.net/#/)) and the **Discourse discussion forum posts** (from [TDS-Discourse](https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34), dated between **1 Jan 2025 to 14 Apr 2025**). Each answer includes relevant reference links to ensure transparency and traceability.

---

## 🧠 What Can It Do?

- Accept **student doubts/questions** (even with image input)
- Provide **precise answers** based on course material and community discussions
- Return **reference links** to the exact content/discussion
- Offers a simple **web UI**
- Also provides an **API end point** to get responses in JSON format

Example API response:
```json
{
  "answer": "Here is your answer...",
  "links": [
    {
      "url": "https://tds.s-anand.net/#/lecture/123",
      "text": "Relevant Video Lecture"
    },
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/example-post",
      "text": "Discourse Post"
    }
  ]
}
```

---

## 🎯 Purpose

- Reduces the burden on human Teaching Assistants by answering **already-answered doubts**
- Assists both **students** and **TAs** in getting quick, consistent responses
- Ensures that answers are **grounded in official material**, avoiding hallucinated responses

---

## 🗂 Project Structure

```
📁 required_data_extraction_from_scraped/   # JSON files with processed, model-ready data
📁 scraped_full_data/                       # Full scraped data (Discourse + Course content + scraping scripts)
📁 static/                                  # Static files for frontend (CSS, JS)
📁 templates/                               # HTML templates for frontend
📄 app.py                                   # Main Flask app (API + Web interface)
📄 rag_data.npz                             # Preprocessed embeddings and data used for retrieval
📄 requirements.txt                         # Dependencies list
📄 LICENSE                                  # MIT License
```

---

## 🧠 How It Works

- `rag_data.npz` contains:
  - `contents`: the actual text chunks from course and Discourse
  - `title`: titles of the source material (video title or post topic)
  - `url`: URLs pointing to the source content
  - `embeddings`: vector embeddings of contents, used for semantic similarity search using cosine similarity

- When a user submits a question:
  - The app converts the question into an embedding using **OpenAI text-embedding-3-small**
  - It compares this to stored embeddings to find the most relevant chunks
  - It forms a prompt using these top chunks and asks **OpenAI GPT-4o-mini** to generate an answer
  - The result is returned with the relevant reference links

---

## 💻 Tech Stack

- **Flask** (for backend + frontend)
- **OpenAI API** (with GPT-4o-mini)
- **NumPy**, **scikit-learn** (for embedding handling & cosine similarity)
- HTML/CSS (for simple UI)

---

## 🚀 Getting Started

### 🔧 Prerequisites
- Python 3.8+
- An [OpenAI API Key](https://platform.openai.com/account/api-keys)
- A proxy (if needed) like `https://aiproxy.sanand.workers.dev/openai/v1/`

### 📥 Installation

1. Clone or download this repo.
2. Make sure to get the following files:
   - `app.py`
   - `requirements.txt`
   - `rag_data.npz`

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the same directory and add:
```env
OPENAI_API_KEY=your_openai_key_here
openai_api_base=https://your_proxy_url_here (optional)
```

5. Run the Flask app:
```bash
python app.py
```

Then visit `http://localhost:5000` in your browser.

---

## 🌐 Deployment

You can deploy this on platforms like:
- **Render**
- **PythonAnywhere**
- **Vercel (with limitations)**

For lightweight deployment, ensure only essential files (`app.py`, `rag_data.npz`, etc.) are included.

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use, modify, and share it with proper credit.

---

## 🙌 Acknowledgements

- IIT Madras B.S. Program TDS Course
- OpenAI API
- Discourse Forum of IITM Online Degree
- Anand S (for [tds.s-anand.net](https://tds.s-anand.net/#/))

---

## 📬 Feedback & Contributions

Pull requests, issues, and suggestions are welcome. Let’s make this better for all TDS students!
