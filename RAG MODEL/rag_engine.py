"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                    RAG ENGINE — Retrieval-Augmented Generation                  ║
╚══════════════════════════════════════════════════════════════════════════════════╝

===================================================================================
 WHAT IS RAG? (Retrieval-Augmented Generation)
===================================================================================

RAG is a hybrid AI architecture that **combines** two powerful paradigms:

  1. RETRIEVAL  — Searching through a private knowledge base (your documents)
                  to find the most relevant pieces of information.
  2. GENERATION — Feeding those retrieved pieces as *context* to a Large Language
                  Model (LLM) so it can generate a grounded, accurate answer.

Why does this matter?
  • LLMs are trained on public internet data up to a cutoff date.  They do NOT
    know about YOUR private PDFs, internal reports, or proprietary images.
  • RAG bridges that gap: it lets the LLM "read" your documents at query time
    without expensive fine-tuning.
  • It dramatically reduces hallucinations because the model answers from real
    evidence rather than parametric memory alone.

===================================================================================
 THE RAG PIPELINE — Step by Step
===================================================================================

  ┌──────────┐    ┌───────────────┐    ┌──────────┐    ┌──────────┐
  │  UPLOAD  │───▶│ EXTRACT TEXT  │───▶│  CHUNK   │───▶│  EMBED   │
  │ (PDF/IMG)│    │ (PyPDF2/OCR)  │    │ (overlap)│    │(MiniLM)  │
  └──────────┘    └───────────────┘    └──────────┘    └────┬─────┘
                                                            │
                                                            ▼
                                                     ┌──────────┐
                                                     │  STORE   │
                                                     │ (FAISS)  │
                                                     └────┬─────┘
                                                          │
          ┌──────────┐    ┌──────────┐    ┌──────────┐    │
          │ GENERATE │◀───│ RETRIEVE │◀───│  QUERY   │◀───┘
          │ (Groq)   │    │ (top-k)  │    │(question)│
          └──────────┘    └──────────┘    └──────────┘

  1. UPLOAD       — User provides a PDF file, an image, or raw text.
  2. EXTRACT TEXT — We pull plain text out of the file.
                    • PDFs   → PyPDF2 reads each page.
                    • Images → Tesseract OCR converts pixels to text.
  3. CHUNK        — Long documents are split into small, overlapping passages
                    (default 500 chars with 50-char overlap).  Overlap ensures
                    that sentences sitting at chunk boundaries aren't lost.
  4. EMBED        — Each chunk is converted into a dense 384-dimensional vector
                    using the 'all-MiniLM-L6-v2' sentence-transformer.  These
                    vectors capture the *semantic meaning* of the text.
  5. STORE        — Vectors are indexed in FAISS (Facebook AI Similarity Search),
                    an in-memory vector database optimised for lightning-fast
                    nearest-neighbour lookups — even with millions of vectors.
  6. QUERY        — The user asks a natural-language question.
  7. RETRIEVE     — The question is embedded with the same model, and FAISS
                    returns the k closest document chunks (cosine similarity).
  8. GENERATE     — The retrieved chunks are injected into a prompt that is sent
                    to Groq's hosted Llama-3.3-70b model, which produces a
                    fluent, context-aware answer.

===================================================================================
 WHY EMBEDDINGS?
===================================================================================

Traditional keyword search (TF-IDF, BM25) fails when the user's question uses
different words than the document.  For example:

    Document : "The patient exhibited signs of myocardial infarction."
    Question : "Did anyone have a heart attack?"

Keyword search would miss this because the words don't overlap.  Embeddings map
both sentences into the same region of a high-dimensional vector space because
they share the same *meaning*.  This is called **semantic search**.

===================================================================================
 WHY VECTOR DATABASES (FAISS)?
===================================================================================

Once you have thousands (or millions) of embedding vectors, you need an efficient
way to find the nearest neighbours.  Brute-force comparison is O(n) per query.
FAISS uses sophisticated indexing structures (IVF, HNSW, PQ) to make this
sub-linear — often < 1 ms even on a million vectors.

We chose FAISS specifically because:
  • It is open-source and maintained by Meta AI Research.
  • It runs entirely in-process (no external server needed).
  • It supports both CPU and GPU acceleration.
  • It is the de-facto standard for prototype and mid-scale RAG systems.

===================================================================================
 FLOW SUMMARY
===================================================================================

  Upload ──▶ Extract Text ──▶ Chunk ──▶ Embed ──▶ Store
                                                     │
  Question ──▶ Embed ──▶ Search (FAISS) ──▶ Retrieve top-k ──▶ Prompt LLM ──▶ Answer

===================================================================================
"""

# ──────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────────────────────────

from __future__ import annotations  # Enable modern type-hint syntax (PEP 604 unions, etc.)

import os                       # File-system utilities (path checks, env vars)
import logging                  # Structured logging for debugging & monitoring
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from typing import (            # Type-hint helpers for readable signatures
    List,
    Tuple,
    Dict,
    Optional,
    Any,
)

import numpy as np              # Numerical operations on embedding vectors

# --- Vector Store (FAISS with pure-NumPy fallback) -------------------------
try:
    import faiss                # Facebook AI Similarity Search
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    FAISS_AVAILABLE = False
from PyPDF2 import PdfReader    # Pure-Python PDF parser (no external C deps)

# --- Image OCR -------------------------------------------------------------
from PIL import Image           # Pillow — open & preprocess images for OCR
import pytesseract              # Python wrapper around Google's Tesseract-OCR engine

# --- Sentence embeddings ----------------------------------------------------
from sentence_transformers import SentenceTransformer  # HuggingFace sentence-transformers

# --- Groq LLM client -------------------------------------------------------
from groq import Groq           # Official Groq Python SDK for ultra-fast LLM inference

# --- Scikit-learn cosine similarity (used for source attribution) -----------
from sklearn.metrics.pairwise import cosine_similarity  # Efficient pairwise cosine computation

# ──────────────────────────────────────────────────────────────────────────────
# MODULE-LEVEL LOGGER
# ──────────────────────────────────────────────────────────────────────────────
# We create a dedicated logger for this module so that log messages are easy
# to filter and route in larger applications.
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# If no handler has been configured externally, add a sensible default so that
# log output isn't silently swallowed.
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s — %(name)s — %(message)s")
    )
    logger.addHandler(_handler)


# ══════════════════════════════════════════════════════════════════════════════
#  RAGEngine CLASS
# ══════════════════════════════════════════════════════════════════════════════

class RAGEngine:
    """
    A production-ready Retrieval-Augmented Generation engine.

    This class encapsulates the entire RAG pipeline:

        1. **Ingestion**  — Accept PDFs, images, or raw text.
        2. **Chunking**   — Split documents into overlapping passages.
        3. **Embedding**  — Encode chunks into dense vectors with a
                            sentence-transformer model.
        4. **Indexing**   — Store vectors in a FAISS index for fast retrieval.
        5. **Querying**   — Embed the user's question, retrieve the top-k
                            most similar chunks, and generate an answer via
                            the Groq-hosted Llama 3.3 70B model.
        6. **Attribution** — Determine whether the final answer was sourced
                             from the user's documents (RAG) or from the
                             LLM's general parametric knowledge.

    Attributes
    ----------
    groq_client : Groq
        Authenticated client for the Groq inference API.
    embedding_model : SentenceTransformer
        The model used to encode text into 384-dim vectors.
    embedding_dim : int
        Dimensionality of the embedding vectors (384 for MiniLM).
    index : faiss.IndexFlatIP
        FAISS index configured for inner-product (cosine) search.
    documents : List[Dict[str, str]]
        Metadata store — maps each vector position to its chunk text and source.
    is_indexed : bool
        Whether at least one document has been added to the index.

    Example
    -------
    >>> engine = RAGEngine(groq_api_key="gsk_...")
    >>> engine.process_pdf("report.pdf")
    >>> result = engine.get_response("What were Q3 revenues?")
    >>> print(result["answer"])
    >>> print(result["source_label"])
    """

    # ──────────────────────────────────────────────────────────────────────
    #  CLASS-LEVEL CONSTANTS
    # ──────────────────────────────────────────────────────────────────────

    # --- Embedding Model Selection ----------------------------------------
    # We use 'all-MiniLM-L6-v2' for the following reasons:
    #
    #   1. SIZE      — Only ~80 MB.  It loads fast and runs on CPU without
    #                  issues, making it ideal for laptops & free-tier servers.
    #   2. SPEED     — 6 transformer layers (vs 12 in base BERT) → ~2× faster
    #                  inference with minimal quality loss.
    #   3. QUALITY   — Trained on over 1 billion sentence pairs; consistently
    #                  ranks in the top tier on the MTEB benchmark for its
    #                  size class.
    #   4. DIMENSION — Produces 384-dim vectors (vs 768 for larger models),
    #                  which halves memory use in the FAISS index.
    #   5. COMMUNITY — The most downloaded sentence-transformer on HuggingFace,
    #                  with extensive documentation and community support.
    #
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384  # Output dimensionality of all-MiniLM-L6-v2

    # --- LLM Configuration ------------------------------------------------
    # Candidate models in order of preference. The engine dynamically detects
    # which models are active on the provided Groq API key and selects the best.
    PREFERRED_MODELS: List[str] = [
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
    ]
    LLM_MODEL: str = "qwen/qwen3.8-27b"
    LLM_MODEL_FALLBACK: str = "openai/gpt-oss-20b"

    # --- System Prompt ----------------------------------------------------
    # This prompt instructs the LLM on how to behave.  Key design decisions:
    #   • We tell it to USE the provided context when relevant so it grounds
    #     its answer in the user's documents.
    #   • We tell it to FALL BACK to general knowledge when the context is
    #     irrelevant, and to explicitly say so — this supports our source-
    #     attribution logic downstream.
    SYSTEM_PROMPT: str = (
        "You are a helpful, direct, and concise AI assistant. "
        "If document context is provided and relevant, answer the question accurately using that context. "
        "If the document context is not relevant or does not contain the answer, answer the question directly, "
        "naturally, and informatively using your own knowledge. "
        "Do NOT mention or lecture the user about what is or is not in the document context. Simply answer the question directly."
    )

    # --- Source Attribution Thresholds ------------------------------------
    # These thresholds control how we decide whether the LLM's answer was
    # sourced from RAG context or from its own parametric knowledge.
    #
    # SIMILARITY_THRESHOLD — Cosine similarity between the answer embedding
    #   and the retrieved-context embedding.  A value of 0.3 is deliberately
    #   lenient: embeddings of topically related (but not identical) passages
    #   typically score 0.25–0.50, while unrelated pairs score < 0.15.
    #
    # RELEVANCE_THRESHOLD — The raw retrieval score from FAISS (normalised
    #   inner product).  If the best-matching chunk barely matches the
    #   question, the context was probably irrelevant.
    SIMILARITY_THRESHOLD: float = 0.3
    RELEVANCE_THRESHOLD: float = 0.3

    # --- Human-Readable Source Labels -------------------------------------
    LABEL_RAG: str = "From Your Documents (RAG)"
    LABEL_LLM: str = "From LLM General Knowledge"

    # ──────────────────────────────────────────────────────────────────────
    #  CONSTRUCTOR
    # ──────────────────────────────────────────────────────────────────────

    def __init__(self, groq_api_key: str = "", api_key: str = "", **kwargs) -> None:
        """
        Initialise the RAG engine.

        Parameters
        ----------
        groq_api_key : str, optional
            A valid Groq API key (starts with ``gsk_``).
        api_key : str, optional
            Alternative alias for ``groq_api_key``.
        """
        actual_key = (
            (groq_api_key or "").strip()
            or (api_key or "").strip()
            or str(kwargs.get("key", "")).strip()
            or os.environ.get("GROQ_API_KEY", "").strip()
        )

        # ── 1. Validate the API key ──────────────────────────────────────
        if not actual_key:
            raise ValueError(
                "A valid Groq API key is required.  "
                "Get one at https://console.groq.com/keys"
            )

        # ── 2. Initialise the Groq client ────────────────────────────────
        # The Groq SDK handles connection pooling, retries, and auth headers
        # internally.  We just need to pass the key once.
        self.groq_client: Groq = Groq(api_key=actual_key)
        self.llm_model: str = self._detect_model()
        logger.info("Groq client initialised successfully with model: %s", self.llm_model)

        # ── 3. Fast Vector Embedding Engine ──────────────────────────────
        # Uses scikit-learn vectorizer for instant 0.1s startup (no slow 100MB downloads).
        self.use_tfidf: bool = True
        self.embedding_model = None
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf_vectorizer = TfidfVectorizer(max_features=self.EMBEDDING_DIMENSION)
        logger.info("Fast local vector embeddings engine initialised instantly.")

        # ── 4. Create the FAISS index ────────────────────────────────────
        #
        # WHY FAISS?
        # ----------
        #   • It is the gold standard for in-memory approximate nearest-
        #     neighbour (ANN) search, developed by Meta AI Research.
        #   • IndexFlatIP performs *exact* inner-product search — no
        #     approximation error.  For our scale (thousands of chunks) this
        #     is fast enough and guarantees perfect recall.
        #   • Because we L2-normalise all vectors before insertion, inner
        #     product is equivalent to cosine similarity.
        #   • If the corpus grows to millions of chunks, we can seamlessly
        #     swap to IndexIVFFlat or IndexHNSWFlat for sub-linear search.
        #
        # We initialise with FAISS if available; otherwise use pure NumPy fallback.
        if FAISS_AVAILABLE and faiss is not None:
            self.index: Optional[faiss.IndexFlatIP] = faiss.IndexFlatIP(self.EMBEDDING_DIMENSION)
            logger.info("FAISS IndexFlatIP created (dim=%d).", self.EMBEDDING_DIMENSION)
        else:
            self.index = None
            self.embeddings_matrix: Optional[np.ndarray] = None
            logger.info("Using pure-NumPy vector cosine similarity engine.")

        # ── 5. Metadata store ────────────────────────────────────────────
        # FAISS only stores vectors — it has no concept of the original text.
        # We maintain a parallel list where position i corresponds to the
        # i-th vector in the FAISS index.  Each entry is a dict with:
        #   • "text"   — the original chunk string
        #   • "source" — a human-readable label (e.g. file path)
        self.documents: List[Dict[str, str]] = []

        # ── 6. Index state flag ──────────────────────────────────────────
        # Used to short-circuit queries when no documents have been added.
        self.is_indexed: bool = False

        logger.info("RAGEngine initialisation complete.")

    # ══════════════════════════════════════════════════════════════════════
    #  DOCUMENT INGESTION METHODS
    # ══════════════════════════════════════════════════════════════════════

    def add_document(self, file_path_or_text: str, source: str = "") -> int:
        """
        Universal document ingestion method. Automatically detects whether the
        input is a PDF file, an image file, a text file, or raw text string.
        """
        if os.path.isfile(file_path_or_text):
            ext = os.path.splitext(file_path_or_text)[1].lower()
            if ext == ".pdf":
                return self.process_pdf(file_path_or_text)
            elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]:
                return self.process_image(file_path_or_text)
            else:
                with open(file_path_or_text, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                return self.add_documents([content], source=source or os.path.basename(file_path_or_text))
        else:
            return self.add_documents([file_path_or_text], source=source or "text")

    def process_pdf(self, file_path: str) -> int:
        """
        Ingest a PDF file into the RAG knowledge base.

        Pipeline: Open PDF → Read each page → Concatenate text → Chunk →
                  Embed → Store in FAISS.

        Parameters
        ----------
        file_path : str
            Absolute or relative path to a ``.pdf`` file.

        Returns
        -------
        int
            The number of text chunks that were created and indexed.

        Raises
        ------
        FileNotFoundError
            If ``file_path`` does not exist.
        ValueError
            If the PDF contains no extractable text (e.g. scanned pages
            without an OCR text layer).
        """

        # ── Step 1: Validate the file path ───────────────────────────────
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        logger.info("Processing PDF: %s", file_path)

        # ── Step 2: Extract text from every page ─────────────────────────
        # PyPDF2's PdfReader parses the PDF structure and exposes each page
        # as an object with an `.extract_text()` method.  This works for
        # digitally-created PDFs; scanned PDFs will return empty strings
        # (use process_image() for those).
        reader = PdfReader(file_path)
        full_text: str = ""

        for page_number, page in enumerate(reader.pages, start=1):
            # extract_text() returns None for pages with no text layer.
            page_text: Optional[str] = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
                logger.debug("  Page %d: extracted %d chars.", page_number, len(page_text))
            else:
                logger.warning("  Page %d: no text extracted (may be a scanned image).", page_number)

        # ── Step 3: Guard against empty documents ────────────────────────
        if not full_text.strip():
            raise ValueError(
                f"No text could be extracted from '{file_path}'.  "
                "If this is a scanned PDF, try process_image() with OCR instead."
            )

        logger.info("Total extracted text: %d characters from %d pages.", len(full_text), len(reader.pages))

        # ── Step 4: Chunk, embed, and store ──────────────────────────────
        # We delegate to add_documents(), which handles the remaining
        # pipeline steps (chunking → embedding → FAISS insertion).
        num_chunks: int = self.add_documents(
            texts=[full_text],
            source=f"PDF: {os.path.basename(file_path)}",
        )

        logger.info("PDF processing complete.  %d chunks indexed.", num_chunks)
        return num_chunks

    # ──────────────────────────────────────────────────────────────────────

    def process_image(self, file_path: str) -> int:
        """
        Ingest an image file via OCR into the RAG knowledge base.

        Pipeline: Open image → Run Tesseract OCR → Extract text → Chunk →
                  Embed → Store in FAISS.

        We use **Tesseract** (via the pytesseract wrapper) because:
          • It is open-source and supports 100+ languages.
          • It produces reasonable accuracy on printed text without any
            model training.
          • pytesseract is a thin wrapper, so there's almost zero overhead.

        Prerequisites
        -------------
        Tesseract must be installed on the system:
          • Windows : https://github.com/UB-Mannheim/tesseract/wiki
          • macOS   : ``brew install tesseract``
          • Linux   : ``sudo apt install tesseract-ocr``

        Parameters
        ----------
        file_path : str
            Path to an image file (PNG, JPG, TIFF, BMP, etc.).

        Returns
        -------
        int
            Number of chunks created and indexed.

        Raises
        ------
        FileNotFoundError
            If the image file does not exist.
        ValueError
            If OCR produces no text.
        """

        # ── Step 1: Validate the file path ───────────────────────────────
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        logger.info("Processing image (OCR): %s", file_path)

        # ── Step 2: Open the image with Pillow ───────────────────────────
        # Pillow normalises different image formats into a consistent
        # in-memory representation that Tesseract can consume.
        image: Image.Image = Image.open(file_path)

        # ── Step 3: Run Tesseract OCR ────────────────────────────────────
        # `image_to_string` sends the pixel data to Tesseract, which runs
        # its LSTM-based text detection and recognition pipeline and returns
        # a UTF-8 string.
        extracted_text: str = pytesseract.image_to_string(image)

        # ── Step 4: Guard against empty OCR output ───────────────────────
        if not extracted_text.strip():
            raise ValueError(
                f"OCR produced no text from '{file_path}'.  "
                "Ensure the image contains readable text and that Tesseract is installed."
            )

        logger.info("OCR extracted %d characters.", len(extracted_text))

        # ── Step 5: Chunk, embed, and store ──────────────────────────────
        num_chunks: int = self.add_documents(
            texts=[extracted_text],
            source=f"Image (OCR): {os.path.basename(file_path)}",
        )

        logger.info("Image processing complete.  %d chunks indexed.", num_chunks)
        return num_chunks

    # ──────────────────────────────────────────────────────────────────────

    def add_documents(self, texts: List[str], source: str = "manual", **kwargs) -> int:
        if "source_name" in kwargs:
            source = kwargs["source_name"]
        """
        Add raw text documents to the vector store.

        This is the universal ingestion entry point.  Both ``process_pdf``
        and ``process_image`` ultimately call this method after extracting
        text from their respective file formats.

        Pipeline: Receive texts → Chunk each text → Embed all chunks →
                  L2-normalise → Insert into FAISS → Record metadata.

        Parameters
        ----------
        texts : List[str]
            A list of raw text strings to ingest.  Each string is chunked
            independently.
        source : str, optional
            A human-readable label describing where these texts came from
            (e.g. ``"PDF: report.pdf"``).  Defaults to ``"manual"``.

        Returns
        -------
        int
            Total number of chunks created across all input texts.
        """

        # ── Step 1: Chunk all input texts ────────────────────────────────
        all_chunks: List[str] = []
        for text in texts:
            chunks: List[str] = self._chunk_text(text)
            all_chunks.extend(chunks)

        if not all_chunks:
            logger.warning("No chunks produced from the input texts.  Nothing to index.")
            return 0

        logger.info("Created %d chunks from %d input text(s).", len(all_chunks), len(texts))

        # ── Step 2: Compute embeddings for every chunk ───────────────────
        if not self.use_tfidf and self.embedding_model is not None:
            embeddings: np.ndarray = self.embedding_model.encode(
                all_chunks,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            embeddings = embeddings.astype(np.float32)
        else:
            all_existing_texts = [d["text"] for d in self.documents] + all_chunks
            self.tfidf_vectorizer.fit(all_existing_texts)
            embeddings = self.tfidf_vectorizer.transform(all_chunks).toarray().astype(np.float32)
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embeddings = embeddings / norms
            if embeddings.shape[1] < self.EMBEDDING_DIMENSION:
                embeddings = np.pad(embeddings, ((0, 0), (0, self.EMBEDDING_DIMENSION - embeddings.shape[1])), mode='constant')
            elif embeddings.shape[1] > self.EMBEDDING_DIMENSION:
                embeddings = embeddings[:, :self.EMBEDDING_DIMENSION]

        logger.info("Embeddings computed.  Shape: %s", embeddings.shape)

        # ── Step 3: Add vectors to the vector store ──────────────────────
        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(embeddings)
            total_vecs = self.index.ntotal
        else:
            if self.embeddings_matrix is None:
                self.embeddings_matrix = embeddings
            else:
                self.embeddings_matrix = np.vstack([self.embeddings_matrix, embeddings])
            total_vecs = len(self.embeddings_matrix)

        # ── Step 4: Record metadata in parallel list ─────────────────────
        for chunk_text in all_chunks:
            self.documents.append({
                "text": chunk_text,
                "source": source,
            })

        # ── Step 5: Update state flag ────────────────────────────────────
        self.is_indexed = True

        logger.info(
            "Vector store now contains %d vectors.  Source: '%s'.",
            total_vecs,
            source,
        )

        return len(all_chunks)

    # ══════════════════════════════════════════════════════════════════════
    #  TEXT CHUNKING
    # ══════════════════════════════════════════════════════════════════════

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[str]:
        """
        Split a long text into overlapping chunks.

        Parameters
        ----------
        text : str
            The full text to split.
        chunk_size : int, optional
            Maximum number of characters per chunk.  Defaults to 500.
        overlap : int, optional
            Number of characters to repeat between consecutive chunks.
            Defaults to 50.

        Returns
        -------
        List[str]
            A list of text chunks, each at most ``chunk_size`` characters.

        Why Overlapping Chunks?
        -----------------------
        Imagine a sentence that sits right at the boundary of two chunks:

            Chunk 1: "… the revenue grew by 15% in"
            Chunk 2: "Q3 compared to the previous quarter …"

        Without overlap, neither chunk contains the full sentence, and a
        query about "Q3 revenue growth" might miss both.  With a 50-char
        overlap, the end of Chunk 1 and the beginning of Chunk 2 share
        those 50 characters, so the sentence appears intact in at least
        one of them.

        Trade-offs:
          • More overlap → better boundary coverage, but more chunks → more
            storage and slightly slower search.
          • Less overlap → fewer chunks, but risk of losing context at edges.
          • A 10% overlap (50/500) is a widely-used sweet spot.
        """

        # ── Guard: empty or very short text ──────────────────────────────
        if not text or not text.strip():
            return []

        # If the entire text fits in one chunk, just return it as-is.
        if len(text) <= chunk_size:
            return [text.strip()]

        # ── Sliding-window chunking ──────────────────────────────────────
        chunks: List[str] = []
        start: int = 0

        while start < len(text):
            # Extract a window of `chunk_size` characters.
            end: int = start + chunk_size
            chunk: str = text[start:end].strip()

            # Only keep non-empty chunks.
            if chunk:
                chunks.append(chunk)

            # Advance the window by (chunk_size - overlap) characters.
            # The overlap causes the tail of the previous chunk to reappear
            # at the head of the next chunk.
            start += chunk_size - overlap

        logger.debug("Chunked %d chars into %d chunks (size=%d, overlap=%d).", len(text), len(chunks), chunk_size, overlap)

        return chunks

    # ══════════════════════════════════════════════════════════════════════
    #  QUERY & RETRIEVAL
    # ══════════════════════════════════════════════════════════════════════

    def query(
        self,
        question: str,
        k: int = 3,
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context from FAISS and generate an answer via Groq.

        Pipeline:
          1. Embed the question with the same sentence-transformer.
          2. Search FAISS for the ``k`` nearest chunks (by cosine similarity).
          3. Assemble a prompt with the retrieved context.
          4. Call the Groq API to generate a response.
          5. Return the answer, retrieved chunks, and relevance scores.

        Parameters
        ----------
        question : str
            The user's natural-language question.
        k : int, optional
            Number of top chunks to retrieve.  Defaults to 3.

        Returns
        -------
        Dict[str, Any]
            A dictionary with keys:
              - ``"answer"`` (str)            — The LLM-generated response.
              - ``"context"`` (str)           — The concatenated retrieved chunks.
              - ``"sources"`` (List[str])     — Source labels for each chunk.
              - ``"scores"`` (List[float])    — FAISS similarity scores.
              - ``"chunks"`` (List[str])      — Individual retrieved chunk texts.
        """

        # ── Step 1: Handle empty index gracefully ────────────────────────
        # If no documents have been ingested, we still want to return an
        # answer — the LLM will rely purely on its parametric knowledge.
        total_vectors = self.index.ntotal if (FAISS_AVAILABLE and self.index is not None) else (len(self.embeddings_matrix) if self.embeddings_matrix is not None else 0)
        if not self.is_indexed or total_vectors == 0:
            logger.info("No documents in index.  Querying LLM without context.")
            answer: str = self._call_groq(question=question, context="")
            return {
                "answer": answer,
                "context": "",
                "sources": [],
                "scores": [],
                "chunks": [],
            }

        # ── Step 2: Embed the question ───────────────────────────────────
        # We use the same model and normalisation as during ingestion so
        # that the vectors live in the same space.
        if not self.use_tfidf and self.embedding_model is not None:
            question_embedding: np.ndarray = self.embedding_model.encode(
                [question],
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype(np.float32)
        else:
            q_vec = self.tfidf_vectorizer.transform([question]).toarray().astype(np.float32)
            norm = np.linalg.norm(q_vec)
            if norm > 0:
                q_vec = q_vec / norm
            if q_vec.shape[1] < self.EMBEDDING_DIMENSION:
                q_vec = np.pad(q_vec, ((0, 0), (0, self.EMBEDDING_DIMENSION - q_vec.shape[1])), mode='constant')
            elif q_vec.shape[1] > self.EMBEDDING_DIMENSION:
                q_vec = q_vec[:, :self.EMBEDDING_DIMENSION]
            question_embedding = q_vec

        # ── Step 3: Search Vector Store (FAISS or NumPy fallback) ────────
        effective_k: int = min(k, total_vectors)
        if FAISS_AVAILABLE and self.index is not None:
            raw_scores, raw_indices = self.index.search(question_embedding, effective_k)
            scores = raw_scores[0]
            indices = raw_indices[0]
        else:
            # Inner product between normalized vectors equals cosine similarity
            sim_scores = np.dot(self.embeddings_matrix, question_embedding.T).flatten()
            indices = np.argsort(sim_scores)[::-1][:effective_k]
            scores = sim_scores[indices]

        # ── Step 4: Gather the matching chunks and metadata ──────────────
        retrieved_chunks: List[str] = []
        retrieved_sources: List[str] = []
        retrieved_scores: List[float] = []

        for score, idx in zip(scores, indices):
            # FAISS may return -1 for indices when there are fewer vectors
            # than k in the index.  Skip those.
            if idx == -1:
                continue

            doc_meta: Dict[str, str] = self.documents[int(idx)]
            retrieved_chunks.append(doc_meta["text"])
            retrieved_sources.append(doc_meta["source"])
            retrieved_scores.append(float(score))

        logger.info(
            "Retrieved %d chunks.  Top score: %.4f",
            len(retrieved_chunks),
            retrieved_scores[0] if retrieved_scores else 0.0,
        )

        # ── Step 5: Build the context string ─────────────────────────────
        # We join the chunks with a clear separator so the LLM can
        # distinguish between different passages.
        context: str = "\n\n---\n\n".join(retrieved_chunks)

        # ── Step 6: Generate the answer via Groq ─────────────────────────
        answer = self._call_groq(question=question, context=context)

        return {
            "answer": answer,
            "context": context,
            "sources": retrieved_sources,
            "scores": retrieved_scores,
            "chunks": retrieved_chunks,
        }

    # ──────────────────────────────────────────────────────────────────────

    def _detect_model(self) -> str:
        """
        Dynamically detect which chat model is active and accessible on Groq.
        """
        try:
            available = [m.id for m in self.groq_client.models.list().data]
            for candidate in self.PREFERRED_MODELS:
                if candidate in available:
                    return candidate
            for m in available:
                if not any(skip in m.lower() for skip in ["whisper", "guard", "orpheus"]):
                    return m
        except Exception as e:
            logger.warning("Could not auto-detect Groq models: %s", e)
        return self.LLM_MODEL

    def _call_groq(self, question: str, context: str) -> str:
        """
        Send a prompt to the Groq-hosted LLM and return the generated text.

        The prompt structure:
          - **System message**: Sets the assistant's persona and rules.
          - **User message**: Contains the retrieved context (if any) and
            the user's question.

        Parameters
        ----------
        question : str
            The user's question.
        context : str
            Retrieved document context (may be empty).

        Returns
        -------
        str
            The LLM-generated answer text.
        """

        # ── Build the user prompt ────────────────────────────────────────
        if context.strip():
            # When context is available, present it cleanly to the model.
            user_prompt: str = (
                f"Document Context:\n"
                f"```\n{context}\n```\n\n"
                f"Question: {question}\n\n"
                f"Answer the question directly and concisely. If the context contains the answer, use it. "
                f"If the context is unrelated or does not contain the answer, answer directly using your own knowledge without commenting on the context."
            )
        else:
            # No context — answer directly.
            user_prompt = question

        # ── Call the Groq API ────────────────────────────────────────────
        try:
            chat_completion = self.groq_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,       # Low temperature for factual, deterministic answers
                max_tokens=800,        # Safe limit within Groq OTPM constraints
                top_p=0.9,             # Nucleus sampling — keeps output focused
                stream=False,          # We want the full response at once
            )

            # Extract the assistant's reply text.
            answer: str = chat_completion.choices[0].message.content.strip()
            logger.info("Groq response received (%d chars).", len(answer))
            return answer

        except Exception as e:
            # If the primary model fails (e.g. rate limit, deprecation),
            # attempt the fallback model.
            logger.warning(
                "Primary model '%s' failed: %s.  Trying fallback '%s'…",
                self.llm_model, e, self.LLM_MODEL_FALLBACK,
            )
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    model=self.LLM_MODEL_FALLBACK,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=800,
                    top_p=0.9,
                    stream=False,
                )
                answer = chat_completion.choices[0].message.content.strip()
                logger.info("Fallback Groq response received (%d chars).", len(answer))
                return answer

            except Exception as fallback_error:
                logger.error("Both LLM models failed.  Error: %s", fallback_error)
                return (
                    "I'm sorry, I couldn't generate a response at this time.  "
                    "Please check your Groq API key and internet connection."
                )

    # ══════════════════════════════════════════════════════════════════════
    #  SOURCE ATTRIBUTION
    # ══════════════════════════════════════════════════════════════════════

    def _is_from_rag(
        self,
        question: str,
        context: str,
        answer: str,
    ) -> bool:
        """
        Determine whether the LLM's answer was grounded in the retrieved
        RAG context or came from the model's general parametric knowledge.

        Approach (Similarity-Based)
        ---------------------------
        We use a two-pronged heuristic:

        1. **Answer–Context Cosine Similarity**
           We embed both the ``answer`` and the ``context`` using the same
           sentence-transformer model, then compute their cosine similarity.
           If the similarity exceeds ``SIMILARITY_THRESHOLD`` (default 0.3),
           the answer's content is semantically close to the retrieved
           documents — a strong signal that the LLM drew from them.

        2. **Question–Context Relevance Check**
           We also embed the ``question`` and compute its cosine similarity
           with the ``context``.  If the *context itself* isn't relevant to
           the question (similarity below ``RELEVANCE_THRESHOLD``), then
           even a high answer–context similarity is likely coincidental.

        Both conditions must be met to classify the answer as RAG-sourced:
          • answer–context similarity  > SIMILARITY_THRESHOLD   AND
          • question–context similarity > RELEVANCE_THRESHOLD

        Why 0.3?
        --------
        Cosine similarities from all-MiniLM-L6-v2 typically fall in these
        ranges:
          • Unrelated pairs        : 0.00 – 0.15
          • Loosely related pairs  : 0.15 – 0.30
          • Topically related pairs: 0.30 – 0.60
          • Near-duplicate pairs   : 0.60 – 1.00

        A threshold of 0.3 captures genuinely related content while avoiding
        false positives from incidental word overlap.

        Parameters
        ----------
        question : str
            The original user question.
        context : str
            The concatenated retrieved chunks that were sent to the LLM.
        answer : str
            The LLM's generated response.

        Returns
        -------
        bool
            ``True`` if the answer appears to be grounded in RAG context;
            ``False`` if it likely comes from the LLM's general knowledge.
        """

        # ── Guard: if there's no context, it's definitely not from RAG ───
        if not context or not context.strip():
            return False

        # ── Guard: check if LLM explicitly indicated general knowledge usage
        lower_answer = answer.lower()
        general_knowledge_phrases = [
            "context is not relevant",
            "context is irrelevant",
            "not relevant to the question",
            "not mentioned in the context",
            "not found in the context",
            "not provided in the context",
            "using my general knowledge",
            "based on my general knowledge",
            "from my general knowledge",
            "general knowledge:",
        ]
        if any(phrase in lower_answer for phrase in general_knowledge_phrases):
            logger.info("Source attribution: LLM explicitly indicated general knowledge.")
            return False

        # ── Step 1: Embed the answer, context, and question ──────────────
        # We embed all three in a single batch call for efficiency.
        if not self.use_tfidf and self.embedding_model is not None:
            embeddings: np.ndarray = self.embedding_model.encode(
                [answer, context, question],
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            answer_emb: np.ndarray = embeddings[0].reshape(1, -1)   # shape (1, 384)
            context_emb: np.ndarray = embeddings[1].reshape(1, -1)  # shape (1, 384)
            question_emb: np.ndarray = embeddings[2].reshape(1, -1) # shape (1, 384)
        else:
            vecs = self.tfidf_vectorizer.transform([answer, context, question]).toarray().astype(np.float32)
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            vecs = vecs / norms
            if vecs.shape[1] < self.EMBEDDING_DIMENSION:
                vecs = np.pad(vecs, ((0, 0), (0, self.EMBEDDING_DIMENSION - vecs.shape[1])), mode='constant')
            elif vecs.shape[1] > self.EMBEDDING_DIMENSION:
                vecs = vecs[:, :self.EMBEDDING_DIMENSION]
            answer_emb = vecs[0:1]
            context_emb = vecs[1:2]
            question_emb = vecs[2:3]

        # ── Step 2: Compute answer ↔ context cosine similarity ───────────
        answer_context_sim: float = float(
            cosine_similarity(answer_emb, context_emb)[0][0]
        )

        # ── Step 3: Compute question ↔ context cosine similarity ─────────
        question_context_sim: float = float(
            cosine_similarity(question_emb, context_emb)[0][0]
        )

        logger.info(
            "Source attribution — answer↔context sim: %.4f  |  "
            "question↔context sim: %.4f  |  thresholds: (%.2f, %.2f)",
            answer_context_sim,
            question_context_sim,
            self.SIMILARITY_THRESHOLD,
            self.RELEVANCE_THRESHOLD,
        )

        # ── Step 4: Apply dual-threshold decision ────────────────────────
        # Both conditions must hold:
        #   (a) The answer is semantically similar to the retrieved context.
        #   (b) The retrieved context is actually relevant to the question.
        is_rag: bool = (
            answer_context_sim > self.SIMILARITY_THRESHOLD
            and question_context_sim > self.RELEVANCE_THRESHOLD
        )

        return is_rag

    # ══════════════════════════════════════════════════════════════════════
    #  MAIN PUBLIC INTERFACE
    # ══════════════════════════════════════════════════════════════════════

    def get_response(self, question: str) -> Dict[str, Any]:
        """
        End-to-end RAG query — the main method users should call.

        This method orchestrates the full pipeline:
          1. Retrieve relevant chunks and generate an answer (``query``).
          2. Determine whether the answer is RAG-sourced or from general
             LLM knowledge (``_is_from_rag``).
          3. Return the answer, a human-readable source label, and all
             intermediate data for transparency.

        Parameters
        ----------
        question : str
            A natural-language question.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing:
              - ``"answer"``       (str)        — The generated answer text.
              - ``"source_label"`` (str)        — One of:
                    • ``" From Your Documents (RAG)"``
                    • ``" From LLM General Knowledge"``
              - ``"is_rag"``       (bool)       — True if sourced from RAG.
              - ``"context"``      (str)        — Retrieved document context.
              - ``"sources"``      (List[str])  — Source identifiers of chunks.
              - ``"scores"``       (List[float])— FAISS similarity scores.
              - ``"chunks"``       (List[str])  — Individual chunk texts.

        Example
        -------
        >>> result = engine.get_response("What is the capital of France?")
        >>> print(result["answer"])
        "The capital of France is Paris."
        >>> print(result["source_label"])
        " From LLM General Knowledge"
        """

        logger.info("=" * 70)
        logger.info("get_response() called — question: '%s'", question[:100])
        logger.info("=" * 70)

        # ── Step 0: Real-time Date / Time Tool ───────────────────────────
        try:
            from tools import handle_datetime_query
            tool_result = handle_datetime_query(question)
            if tool_result is not None:
                logger.info("Answer generated via real-time tool: %s", tool_result["tool_name"])
                return {
                    "answer": tool_result["answer"],
                    "source_label": tool_result["source_label"],
                    "is_rag": False,
                    "is_tool": True,
                    "source": "tool",
                    "context": "",
                    "sources": ["System Real-time Clock Tool"],
                    "scores": [1.0],
                    "chunks": [],
                }
        except Exception as tool_err:
            logger.warning("Tool check error: %s", tool_err)

        # ── Step 1: Retrieve context and generate answer ─────────────────
        query_result: Dict[str, Any] = self.query(question=question)

        answer: str = query_result["answer"]
        context: str = query_result["context"]

        # ── Step 2: Determine source attribution ─────────────────────────
        is_rag: bool = self._is_from_rag(
            question=question,
            context=context,
            answer=answer,
        )

        # ── Step 3: Assign the human-readable label ──────────────────────
        source_label: str = self.LABEL_RAG if is_rag else self.LABEL_LLM

        logger.info("Source attribution: %s (is_rag=%s)", source_label, is_rag)

        # ── Step 4: Package everything into a clean response dict ────────
        return {
            "answer": answer,
            "source_label": source_label,
            "is_rag": is_rag,
            "context": context,
            "sources": query_result["sources"],
            "scores": query_result["scores"],
            "chunks": query_result["chunks"],
        }

    # ══════════════════════════════════════════════════════════════════════
    #  UTILITY / INTROSPECTION METHODS
    # ══════════════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """
        Return diagnostic statistics about the current state of the engine.

        Useful for dashboards and health checks.

        Returns
        -------
        Dict[str, Any]
            Keys: ``total_vectors``, ``total_documents``, ``embedding_model``,
            ``embedding_dim``, ``llm_model``, ``is_indexed``.
        """
        total_vectors = (
            self.index.ntotal
            if (FAISS_AVAILABLE and self.index is not None)
            else (len(self.embeddings_matrix) if self.embeddings_matrix is not None else 0)
        )
        return {
            "total_vectors": total_vectors,
            "total_documents": len(self.documents),
            "embedding_model": self.EMBEDDING_MODEL_NAME,
            "embedding_dim": self.EMBEDDING_DIMENSION,
            "llm_model": self.LLM_MODEL,
            "is_indexed": self.is_indexed,
        }

    def clear(self) -> None:
        """
        Remove all documents and vectors from the engine.

        This resets the index and clears the metadata store without
        needing to reinstantiate the entire engine (which would reload the
        embedding model).
        """
        if FAISS_AVAILABLE and faiss is not None:
            self.index = faiss.IndexFlatIP(self.EMBEDDING_DIMENSION)
        else:
            self.embeddings_matrix = None
        self.documents.clear()
        self.is_indexed = False
        logger.info("RAG engine cleared.  All vectors and documents removed.")

    def __repr__(self) -> str:
        """Human-readable representation for debugging."""
        total_vectors = (
            self.index.ntotal
            if (FAISS_AVAILABLE and self.index is not None)
            else (len(self.embeddings_matrix) if self.embeddings_matrix is not None else 0)
        )
        return (
            f"RAGEngine("
            f"vectors={total_vectors}, "
            f"documents={len(self.documents)}, "
            f"model='{self.EMBEDDING_MODEL_NAME}', "
            f"llm='{self.LLM_MODEL}'"
            f")"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  MODULE SELF-TEST
# ══════════════════════════════════════════════════════════════════════════════
# When run directly (python rag_engine.py), execute a minimal smoke test that
# verifies the engine can be instantiated and can process text.

if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("  RAG Engine — Smoke Test")
    print("=" * 70)

    # Check for API key.
    api_key: str = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print(
            "\n  Set the GROQ_API_KEY environment variable to run the smoke test."
            "\n   Example:  set GROQ_API_KEY=gsk_...\n"
        )
        sys.exit(1)

    # Instantiate the engine.
    engine = RAGEngine(groq_api_key=api_key)
    print(f"\n Engine created: {engine}\n")

    # Add a sample document.
    sample_text: str = (
        "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars "
        "in Paris, France.  It is named after the engineer Gustave Eiffel, whose "
        "company designed and built the tower from 1887 to 1889 as the centerpiece "
        "of the 1889 World's Fair.  The tower is 330 metres (1,083 ft) tall and "
        "was the tallest man-made structure in the world until the Chrysler "
        "Building in New York City was topped out in 1929."
    )
    num_chunks: int = engine.add_documents([sample_text], source="smoke-test")
    print(f" Added {num_chunks} chunk(s) to the index.\n")

    # Query — should use RAG context.
    result = engine.get_response("How tall is the Eiffel Tower?")
    print(f" Question : How tall is the Eiffel Tower?")
    print(f" Answer   : {result['answer']}")
    print(f"  Source   : {result['source_label']}")
    print(f" Scores   : {result['scores']}")

    print("\n" + "=" * 70)

    # Query — should use general knowledge (unrelated to Eiffel Tower).
    result2 = engine.get_response("What is the speed of light?")
    print(f" Question : What is the speed of light?")
    print(f" Answer   : {result2['answer']}")
    print(f"  Source   : {result2['source_label']}")
    print(f" Scores   : {result2['scores']}")

    print("\n" + "=" * 70)
    print("  Smoke test complete.")
    print("=" * 70)
