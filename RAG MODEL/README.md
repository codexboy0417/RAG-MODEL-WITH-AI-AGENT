# 🤖 RAG Model — Document Q&A System

> **Ask questions about your documents and get accurate, source-labeled answers
> powered by Retrieval-Augmented Generation.**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLM%20API-orange)](https://console.groq.com/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-green)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📑 Table of Contents

| # | Section |
|---|---------|
| 1 | [What is RAG?](#-what-is-rag) |
| 2 | [Architecture & How It Works](#-architecture--how-it-works) |
| 3 | [Tech Stack](#-tech-stack) |
| 4 | [Setup & Installation](#-setup--installation) |
| 5 | [Project Structure](#-project-structure) |
| 6 | [How to Use](#-how-to-use) |
| 7 | [Key Concepts Explained](#-key-concepts-explained) |
| 8 | [Troubleshooting](#-troubleshooting) |
| 9 | [Contributing](#-contributing) |
| 10 | [License](#-license) |

---

## 🧠 What is RAG?

**RAG** stands for **Retrieval-Augmented Generation**. It is a technique that
makes Large Language Models (LLMs) *much smarter* by letting them look up
information from **your own documents** before they answer a question.

### 📖 The Library Analogy

Imagine you walk into a **library** and ask the librarian a question:

| Without RAG (Pure LLM) | With RAG |
|------------------------|----------|
| The librarian answers **from memory only**. They may be confident but sometimes **make things up** (hallucinate). | The librarian first **searches the shelves**, finds the most relevant books, reads the key pages, and **then** answers your question — citing exactly where they found the information. |

> **In short:** RAG = *"Look it up first, then answer."*

A pure LLM is limited to whatever it learned during training (which has a
knowledge cut-off date and knows nothing about *your* private data). RAG solves
this by **retrieving** relevant context from your documents and **augmenting**
the LLM's prompt with that context before it **generates** a response.

---

## 🏗️ Architecture & How It Works

### High-Level Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE — OVERVIEW                        │
└─────────────────────────────────────────────────────────────────────────┘

  📄 Document Upload                    ❓ User Question
       │                                       │
       ▼                                       ▼
 ┌───────────┐                          ┌──────────────┐
 │  Extract   │ PyPDF2 / Tesseract OCR  │  Embed Query │  sentence-transformers
 │   Text     │                         │  into Vector │
 └─────┬─────┘                          └──────┬───────┘
       │                                       │
       ▼                                       │
 ┌───────────┐                                 │
 │  Chunk    │ Split into overlapping          │
 │  Text     │ passages (500 chars,            │
 │           │ 50-char overlap)                │
 └─────┬─────┘                                 │
       │                                       │
       ▼                                       │
 ┌───────────┐                                 │
 │  Embed    │ sentence-transformers           │
 │  Chunks   │ → 384-dim vectors               │
 └─────┬─────┘                                 │
       │                                       │
       ▼                                       ▼
 ┌─────────────────────────────────────────────────┐
 │              FAISS Vector Store                 │
 │         (Similarity Search Index)               │
 │                                                 │
 │   Query vector ──cosine similarity──► Top-K     │
 │                                     chunks      │
 └────────────────────────┬────────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Groq LLM API   │
                 │  (llama-3.1-8b) │
                 │                 │
                 │  Prompt:        │
                 │  "Given this    │
                 │   context …     │
                 │   answer the    │
                 │   question."    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  📝 Answer +    │
                 │  📚 Source Label │
                 │  (RAG or LLM)   │
                 └─────────────────┘
```

### 🔍 Step-by-Step Breakdown

#### Step 1 — 📄 Document Upload (PDF / Image)

The user uploads a **PDF** or an **image** (PNG, JPG, JPEG) through the
Streamlit sidebar. The file is temporarily saved to disk so the processing
pipeline can read it.

#### Step 2 — 📝 Text Extraction

| File Type | Tool Used | How It Works |
|-----------|-----------|--------------|
| **PDF** | `PyPDF2` | Reads the PDF page by page and extracts embedded text directly. Fast and reliable for digital PDFs. |
| **Image / Scanned PDF** | `Tesseract OCR` via `pytesseract` | Performs **Optical Character Recognition** — the AI "reads" the pixels of the image and converts them to text. Essential for scanned documents, photos of pages, screenshots, etc. |

#### Step 3 — ✂️ Text Chunking

Raw extracted text can be thousands of characters long. LLMs have **context
window limits** and perform better with focused input, so we **split** the text
into smaller, overlapping pieces called **chunks**.

```
Original Text (2,000 chars):
┌───────────────────────────────────────────────────────────────┐
│ The quick brown fox jumps over the lazy dog. The dog then ... │
└───────────────────────────────────────────────────────────────┘

After Chunking (chunk_size=500, overlap=50):
┌──────────────────┐
│    Chunk 1       │  chars 0–499
└────────┬─────────┘
         │ overlap (50 chars)
    ┌────┴─────────────┐
    │    Chunk 2       │  chars 450–949
    └────────┬─────────┘
             │ overlap
        ┌────┴─────────────┐
        │    Chunk 3       │  chars 900–1399
        └────────┬─────────┘
                 │ overlap
            ┌────┴─────────────┐
            │    Chunk 4       │  chars 1350–1849
            └──────────────────┘
```

**Why chunk?**
- LLMs work better with **focused** context rather than entire books.
- Smaller chunks allow **precise retrieval** — we find *exactly* the relevant
  paragraph, not the entire 50-page document.

**Why overlap?**
- Important information might sit **at the boundary** between two chunks.
- Overlapping by ~10 % ensures no sentence is split without the neighbouring
  chunk also containing it.

#### Step 4 — 🔢 Embedding Generation

Each chunk is converted into a **numerical vector** (a list of numbers) using a
**sentence-transformer** model. These vectors capture the *semantic meaning* of
the text — similar meanings produce similar vectors.

```
"The cat sat on the mat"  →  [0.12, -0.45, 0.78, 0.03, ..., 0.56]  (384 dimensions)
"A kitten rested on a rug" →  [0.11, -0.44, 0.77, 0.04, ..., 0.55]  (very similar!)
"Stock market crashed"     →  [0.89, 0.23, -0.67, 0.44, ..., -0.12] (very different!)
```

**Model used:** `all-MiniLM-L6-v2` — a lightweight, fast, and accurate
sentence-transformer that runs **100 % locally** (no API key needed for
embeddings).

#### Step 5 — 🗄️ Vector Storage (FAISS)

The embedding vectors are stored in a **FAISS** index. FAISS (Facebook AI
Similarity Search) is an extremely efficient library for searching through
millions of vectors in milliseconds.

```
FAISS Index
┌─────────────────────────────┐
│  Vector 1  →  Chunk 1 text  │
│  Vector 2  →  Chunk 2 text  │
│  Vector 3  →  Chunk 3 text  │
│  ...                        │
│  Vector N  →  Chunk N text  │
└─────────────────────────────┘
```

#### Step 6 — ❓ Query Processing

When the user types a question, the same embedding model converts it into a
vector. This "question vector" is then compared against every stored chunk
vector to find the most relevant matches.

```
User: "What are the side effects of aspirin?"
                │
                ▼
        Embed question
                │
                ▼
    [0.34, -0.21, 0.67, ...]   ← question vector
                │
                ▼
     Search FAISS index for
     nearest neighbours (top-k)
```

#### Step 7 — 📚 Context Retrieval (Top-K)

FAISS returns the **top-K** (typically 3–5) most similar chunks. These are the
passages from your documents that are most likely to contain the answer.

The system also decides whether the retrieved chunks are **relevant enough**:
- ✅ **High similarity score** → use the chunks as context → label answer as
  `📚 From Your Documents (RAG)`
- ❌ **Low similarity score** → no good match found → let the LLM answer from
  general knowledge → label answer as `🤖 From LLM General Knowledge`

#### Step 8 — 🧠 LLM Generation (Groq API)

The retrieved context chunks are injected into a prompt template and sent to the
**Groq API**, which hosts blazing-fast LLM inference (e.g., Llama 3.1 8B).

```
┌──────────────────────────────────────────────────────────────────┐
│ PROMPT TO LLM                                                    │
│                                                                  │
│ You are a helpful assistant. Use the following context to answer  │
│ the user's question. If the context doesn't contain the answer,  │
│ say so.                                                          │
│                                                                  │
│ Context:                                                         │
│ """                                                              │
│ [Chunk 1 text here]                                              │
│ [Chunk 2 text here]                                              │
│ [Chunk 3 text here]                                              │
│ """                                                              │
│                                                                  │
│ Question: What are the side effects of aspirin?                  │
│                                                                  │
│ Answer:                                                          │
└──────────────────────────────────────────────────────────────────┘
```

#### Step 9 — 🏷️ Source Detection (RAG vs LLM)

Every answer is labelled so you always know **where** it came from:

| Badge | Meaning |
|-------|---------|
| 📚 **From Your Documents (RAG)** | The answer was grounded in content you uploaded. You can expand the "context snippets" panel to see the exact passages used. |
| 🤖 **From LLM General Knowledge** | No relevant chunks were found in your documents. The LLM answered from its own training data. |

---

## ⚙️ Tech Stack

| Technology | Role | Why This Choice? |
|-----------|------|------------------|
| **[Streamlit](https://streamlit.io/)** | 🖥️ Web UI | Fastest way to build interactive Python web apps. Zero HTML/JS needed. Built-in chat components. |
| **[Groq API](https://console.groq.com/)** | 🧠 LLM Inference | Ultra-fast inference on open-source models (Llama 3.1). Free tier available. 10× faster than competitors. |
| **[LangChain](https://python.langchain.com/)** | 🔗 Orchestration | Industry-standard framework for chaining retrieval → generation. Handles prompt templates, text splitting, and vector store integration. |
| **[Sentence-Transformers](https://www.sbert.net/)** | 🔢 Embeddings | Runs **100 % locally** — no API key needed. Model `all-MiniLM-L6-v2` is fast, small (80 MB), and surprisingly accurate. |
| **[FAISS](https://github.com/facebookresearch/faiss)** | 🗄️ Vector Store | Facebook's battle-tested library for billion-scale similarity search. CPU version works everywhere. |
| **[PyPDF2](https://pypi.org/project/PyPDF2/)** | 📄 PDF Parsing | Lightweight, pure-Python PDF text extraction. No external dependencies. |
| **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** | 🖼️ Image-to-Text | Best open-source OCR engine. Supports 100+ languages. Essential for scanned documents. |
| **[pytesseract](https://pypi.org/project/pytesseract/)** | 🔌 OCR Bridge | Python wrapper around Tesseract. Makes OCR a one-liner. |
| **[Pillow](https://python-pillow.org/)** | 🎨 Image Processing | Industry-standard Python imaging library. Loads and preprocesses images before OCR. |
| **[ChromaDB](https://www.trychroma.com/)** | 🗃️ Alt. Vector Store | Lightweight, embedded vector database. Used as a secondary/alternative store. |
| **[python-dotenv](https://pypi.org/project/python-dotenv/)** | 🔐 Config | Loads API keys from `.env` files — keeps secrets out of source code. |

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.8+** — [Download here](https://www.python.org/downloads/)
- **Tesseract OCR** — Required for image/scanned-PDF processing
- **Groq API Key** — Free at [console.groq.com](https://console.groq.com/)

### Step 1 — Clone / Download the Project

```bash
# Clone the repository
git clone https://github.com/your-username/rag-model.git
cd rag-model

# Or download as ZIP and extract
```

### Step 2 — Install Python 3.8+

Make sure Python is installed and on your PATH:

```bash
python --version
# Should show Python 3.8.x or higher
```

> 💡 **Tip:** On Windows, check "Add Python to PATH" during installation.

### Step 3 — Install Tesseract OCR

Tesseract is an **external program** (not a Python package) that must be
installed separately.

<details>
<summary>🪟 <strong>Windows</strong></summary>

1. Download the installer from
   [UB Mannheim's Tesseract builds](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer (default path: `C:\Program Files\Tesseract-OCR`)
3. **Add to PATH:** During installation, check *"Add to system PATH"* — or
   manually add `C:\Program Files\Tesseract-OCR` to your system `PATH`
   environment variable.

</details>

<details>
<summary>🍎 <strong>macOS</strong></summary>

```bash
brew install tesseract
```

</details>

<details>
<summary>🐧 <strong>Linux (Ubuntu / Debian)</strong></summary>

```bash
sudo apt update
sudo apt install tesseract-ocr
```

</details>

Verify the installation:

```bash
tesseract --version
# Should show tesseract 4.x or 5.x
```

### Step 4 — Install Python Dependencies

```bash
# (Recommended) Create a virtual environment first
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install all requirements
pip install -r requirements.txt
```

### Step 5 — Get a Groq API Key

1. Go to **[console.groq.com](https://console.groq.com/)**
2. Sign up / log in (free)
3. Navigate to **API Keys** → **Create API Key**
4. Copy the key (starts with `gsk_...`)
5. You'll paste it into the app's sidebar when you run it

> 🔐 **Optional:** Create a `.env` file in the project root:
> ```env
> GROQ_API_KEY=gsk_your_key_here
> ```

### Step 6 — Run the Application 🎉

```bash
streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**.

```
  You can now view your Streamlit app in your browser.

  Local URL:  http://localhost:8501
  Network URL:  http://192.168.x.x:8501
```

---

## 📂 Project Structure

```
RAG MODEL/
│
├── 📄 app.py               # Streamlit web interface
│                            #   → Page config, sidebar, chat UI
│                            #   → File upload handling
│                            #   → Query/answer rendering with source badges
│
├── 🧠 rag_engine.py         # Core RAG engine (back-end)
│                            #   → Text extraction (PDF + OCR)
│                            #   → Text chunking with overlap
│                            #   → Embedding generation
│                            #   → FAISS vector store management
│                            #   → Query processing & LLM calls
│                            #   → Source classification (RAG vs LLM)
│
├── 📋 requirements.txt      # Python dependencies with comments
│                            #   → All packages needed to run the project
│
├── 📖 README.md             # This file — documentation & guide
│
└── 🔐 .env (optional)       # Environment variables (API keys)
                             #   → Not committed to version control
```

---

## 🎯 How to Use

### 1️⃣ Enter Your API Key

- Open the app in your browser
- In the **sidebar**, paste your Groq API key into the `🔑 API Configuration`
  field
- The key is masked for security (password field)

### 2️⃣ Upload Documents

- Click **📁 Upload Documents** in the sidebar
- Select a **PDF** or **image** file (PNG, JPG, JPEG)
- Click **⬆️ Upload & Process**
- Wait for the spinner — the system is extracting, chunking, embedding, and
  indexing your document
- You'll see a ✅ confirmation and the document count will update

### 3️⃣ Ask Questions

- Type your question in the chat input at the bottom:
  *"What are the main findings of the report?"*
- Press **Enter** and wait for the answer

### 4️⃣ Read Labeled Answers

Every answer comes with a **source label**:

- **📚 From Your Documents (RAG)** — click *"📄 View retrieved context
  snippets"* to see the exact passages used
- **🤖 From LLM General Knowledge** — the answer came from the model's
  training data, not your documents

### 5️⃣ Manage Your Knowledge Base

- **📊 Knowledge Base Status** — see how many documents are loaded
- **🗑️ Clear Knowledge Base** — reset everything and start fresh

---

## 📘 Key Concepts Explained

### 🔢 Embeddings — Turning Words into Numbers

An **embedding** is a list of numbers (a **vector**) that represents the
*meaning* of a piece of text. Think of it as a "fingerprint" for meaning.

```
"I love dogs"       →  [0.82, -0.15, 0.43, ...]   ┐
"I adore puppies"   →  [0.80, -0.14, 0.45, ...]   ├ Similar vectors!
                                                    ┘
"Quantum physics"   →  [-0.67, 0.91, -0.12, ...]   ← Very different vector
```

**Why not just match keywords?** Because keyword matching fails when the user
says "car" but the document says "automobile". Embeddings understand that these
mean the same thing.

---

### 📐 Vector Similarity & Cosine Similarity

Once we have vectors, we need a way to measure **how similar** two vectors are.
The most common method is **cosine similarity**.

```
                    Vector A
                   ╱
                  ╱  θ (small angle = high similarity)
                 ╱───────── Vector B
                ╱
               O

  cosine(θ) = 1.0  →  Identical meaning
  cosine(θ) = 0.0  →  Completely unrelated
  cosine(θ) = -1.0 →  Opposite meaning
```

| Cosine Value | Interpretation | Example |
|:---:|---|---|
| **0.95 – 1.0** | Nearly identical | "happy" vs "joyful" |
| **0.70 – 0.95** | Very similar | "dog" vs "puppy" |
| **0.30 – 0.70** | Somewhat related | "dog" vs "animal" |
| **0.00 – 0.30** | Unrelated | "dog" vs "algebra" |

---

### ✂️ Chunking Strategy

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Chunk size** | ~500 characters | Large enough to contain a full idea, small enough for precise retrieval |
| **Overlap** | ~50 characters (10 %) | Prevents losing context at chunk boundaries |
| **Splitter** | `RecursiveCharacterTextSplitter` | Tries to split on paragraphs → sentences → words (preserves natural breaks) |

**Why not just send the whole document?**
- LLMs have token limits (e.g., 8,192 tokens for Llama 3.1 8B)
- Searching through smaller chunks is **faster** and **more precise**
- The LLM can focus on the *exact* relevant passage instead of wading through
  pages of irrelevant text

---

### ⚖️ RAG vs Pure LLM

| Feature | Pure LLM | RAG (This Project) |
|---------|----------|--------------------|
| **Knowledge source** | Training data only | Your documents + training data |
| **Up-to-date?** | ❌ Frozen at training cut-off | ✅ As fresh as your uploads |
| **Private data?** | ❌ Knows nothing about your files | ✅ Reads and searches your files |
| **Hallucination risk** | ⚠️ High — may invent facts | ✅ Low — grounded in real text |
| **Source attribution** | ❌ Can't cite sources | ✅ Shows exact passages used |
| **Cost** | 💰 Every token through API | 💰 Only query + context through API |

---

### 🔍 How Source Detection Works

The system classifies every answer into one of two categories:

```
User asks a question
        │
        ▼
  Search FAISS for similar chunks
        │
        ▼
  ┌─────────────────────────┐
  │ Similarity score > threshold?│
  └─────────┬───────────────┘
            │
     Yes ◄──┴──► No
      │            │
      ▼            ▼
  Send context   Send question
  + question     alone to LLM
  to LLM         │
      │            │
      ▼            ▼
  📚 RAG        🤖 LLM
  badge          badge
```

---

## 🔧 Troubleshooting

### ❌ `TesseractNotFoundError` or `tesseract is not installed`

**Problem:** Tesseract OCR is not installed or not on PATH.

**Solution:**
```bash
# Verify installation
tesseract --version

# Windows: Add to PATH
# System Properties → Environment Variables → PATH → Add:
# C:\Program Files\Tesseract-OCR

# Or set it in Python before running:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

### ❌ `ModuleNotFoundError: No module named 'xxx'`

**Problem:** A Python dependency is missing.

**Solution:**
```bash
pip install -r requirements.txt

# If a specific package fails, install it individually:
pip install streamlit groq langchain faiss-cpu sentence-transformers
```

---

### ❌ `Invalid API Key` or `Authentication Error`

**Problem:** The Groq API key is incorrect or expired.

**Solution:**
1. Go to [console.groq.com](https://console.groq.com/)
2. Generate a **new** API key
3. Make sure you're copying the full key (starts with `gsk_`)
4. Check for accidental spaces before/after the key

---

### ❌ `FAISS index not found` or empty search results

**Problem:** No documents have been uploaded yet.

**Solution:**
- Upload at least one document before asking questions
- Check that the document contains extractable text (not just images in a PDF
  without OCR)

---

### ❌ Slow first query / "Downloading model…"

**Problem:** The embedding model (`all-MiniLM-L6-v2`) is being downloaded for
the first time (~80 MB).

**Solution:**
- This is normal and only happens once
- Subsequent runs use the cached model
- Ensure a stable internet connection for the first run

---

### ❌ `RuntimeError: CUDA not available` (or similar GPU errors)

**Problem:** Some packages try to use GPU, but you're on CPU.

**Solution:**
- This project uses `faiss-cpu` — no GPU required
- If you see CUDA errors from sentence-transformers, it will automatically
  fall back to CPU. No action needed.

---

### ❌ OCR produces garbled / low-quality text

**Problem:** The image quality is too low for accurate OCR.

**Solution:**
- Use higher-resolution images (300 DPI minimum)
- Ensure the image is well-lit and the text is clearly visible
- Pre-process images: increase contrast, convert to grayscale, de-skew

---

### ❌ Port 8501 already in use

**Problem:** Another Streamlit app (or process) is using the default port.

**Solution:**
```bash
# Run on a different port
streamlit run app.py --server.port 8502
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Commit** your changes: `git commit -m "Add my feature"`
4. **Push** to the branch: `git push origin feature/my-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

| Resource | Credit |
|----------|--------|
| [Streamlit](https://streamlit.io/) | Beautiful, effortless web apps for ML |
| [Groq](https://groq.com/) | Lightning-fast LLM inference |
| [LangChain](https://langchain.com/) | LLM application framework |
| [FAISS](https://github.com/facebookresearch/faiss) | Efficient similarity search by Meta AI |
| [Hugging Face](https://huggingface.co/) | Open-source ML models & datasets |
| [Tesseract](https://github.com/tesseract-ocr/tesseract) | Open-source OCR engine by Google |

---

<div align="center">

**Built with ❤️ by Codex_boy**

*If this project helped you, consider giving it a ⭐!*

</div>
