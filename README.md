# CLIP Semantic Search

A multimodal semantic search engine for finding relevant images using natural-language queries.

This project uses OpenAI's CLIP model to map images and text into a shared embedding space. Users can search for images using descriptions such as:

- `a stylish fashion item`
- `a cozy vintage outfit`
- `comfortable running shoes`
- `a minimalist black handbag`

The system ranks images according to their semantic similarity to the user's query instead of relying only on filenames, tags, or exact keyword matches.

## Project Goals

- Generate image embeddings using CLIP.
- Convert natural-language queries into text embeddings.
- Search image embeddings using cosine similarity.
- Store and retrieve embeddings with Qdrant.
- Provide a FastAPI backend for search.
- Build a simple Streamlit frontend.
- Evaluate retrieval quality using precision@5.
- Containerize and deploy the application.

## Architecture

```text
User query
    ↓
Streamlit frontend
    ↓
FastAPI backend
    ↓
CLIP text encoder
    ↓
Text embedding
    ↓
Qdrant vector search
    ↓
Ranked image results
```

The image ingestion pipeline is:

```text
Dataset images
    ↓
CLIP image encoder
    ↓
Image embeddings
    ↓
Qdrant collection
```

## Technology Stack

- Python
- PyTorch
- Hugging Face Transformers
- OpenAI CLIP
- NumPy
- Pillow
- Qdrant
- FastAPI
- Streamlit
- Docker

## Project Structure

```text
clip-semantic-search/
├── data/
│   └── images/
├── frontend/
│   └── app.py
├── notebooks/
│   └── 01_explore_clip.ipynb
├── src/
│   ├── embedder.py
│   ├── main.py
│   └── vector_store.py
├── .gitignore
├── main.py
├── pyproject.toml
└── README.md
```

## Status

This project is under development.

## Planned Features

- [ ] Create an image dataset pipeline
- [ ] Generate and persist image embeddings
- [ ] Implement brute-force similarity search
- [ ] Integrate Qdrant
- [ ] Build FastAPI search endpoints
- [ ] Build the Streamlit interface
- [ ] Add retrieval evaluation
- [ ] Dockerize the application
- [ ] Deploy the application

## Installation

Install the project dependencies with `uv`:

```bash
uv sync
```

Activate the virtual environment if needed:

```bash
source .venv/bin/activate
```

## Running the Project

The application components will be added as development progresses.

The planned services are:

```bash
# Start the FastAPI backend
uvicorn src.main:app --reload

# Start the Streamlit frontend
streamlit run frontend/app.py
```

## Dataset

The project is intended to use a real product-image dataset. The initial dataset will be a manageable subset suitable for experimentation and local development.

Generated embeddings and local vector database storage should not be committed to the repository.

## Limitations

CLIP's results may be affected by:

- Ambiguous or subjective queries
- Image quality and composition
- Dataset domain and diversity
- Details that are not clearly visible in an image
- Differences between product images and real-world photographs

The system is intended as a semantic retrieval demonstration rather than a replacement for a carefully labeled production search system.

## License

This project is for educational and portfolio purposes. Dataset usage must comply with the license and terms of the selected dataset.