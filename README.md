# CLIP Semantic Search

An end-to-end multimodal semantic image-search demo for finding ABO product images using natural-language queries.

The project uses CLIP to place product images and text in the same 512-dimensional embedding space. FastAPI converts text queries to embeddings, Qdrant performs cosine-similarity retrieval, and a React frontend presents the top matching images.

## Demo

Local Docker services:

| Service | Address |
|---|---|
| React UI | `http://localhost:3000` |
| FastAPI | `http://localhost:8000` |
| API documentation | `http://localhost:8000/docs` |
| Streamlit fallback | `http://localhost:8501` |
| Qdrant dashboard | `http://localhost:6333/dashboard` |

Example queries:

- `black handbag`
- `blue phone case`
- `comfortable running shoes`
- `cozy bedroom vibe`
- `modern office setup`

## Architecture

```text
React
  -> Nginx
  -> FastAPI
  -> CLIP text encoder
  -> 512-dimensional query vector
  -> Qdrant
  -> top-5 product images
```

Image data:

```text
4,500 ABO images
  -> CLIP image encoder
  -> normalized 512-dimensional vectors
  -> Qdrant collection
```

## Benchmark

The final 40-query evaluation used separate visual relevance judgments for CLIP and BM25.

| System | Overall Precision@5 |
|---|---:|
| CLIP + Qdrant | `0.970` |
| BM25 over title, product type, brand, and color | `0.605` |

Category breakdown:

| Query category | CLIP | BM25 |
|---|---:|---:|
| Literal | `0.98` | `0.62` |
| Attribute | `0.98` | `0.70` |
| Functional | `0.96` | `0.60` |
| Abstract | `0.96` | `0.50` |

Warm Docker benchmark over 100 search requests:

| Metric | Latency |
|---|---:|
| Mean | `11.82 ms` |
| p50 | `9.36 ms` |
| p95 | `23.13 ms` |
| p99 | `30.35 ms` |

The latency value is end-to-end HTTP latency from outside Docker and does not include model-loading or container cold-start time.

## Technology

- Python 3.13
- PyTorch
- Hugging Face Transformers
- OpenAI CLIP `openai/clip-vit-base-patch32`
- NumPy and pandas
- FastAPI and Uvicorn
- Qdrant
- React, TypeScript, Vite, Nginx
- Streamlit
- Docker Compose
- pytest

## Project Structure

```text
.
├── src/
│   ├── main.py
│   ├── config.py
│   ├── embedder.py
│   └── vector_store.py
├── frontend-react/
├── frontend/
├── scripts/
│   ├── index_qdrant.py
│   └── benchmark_latency.py
├── notebooks/
├── tests/
├── data/
│   ├── metadata/
│   ├── embeddings/
│   └── evaluation/
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.frontend
└── DEPLOYMENT_GUIDE.md
```

## Quick Start

Clone and enter the repository:

```bash
git clone <repository-url>
cd clip-semantic-search
```

Download and extract the ABO small-image archive:

```bash
mkdir -p data/ABO
curl --fail --location --retry 3 \
  --output data/ABO/abo-images-small.tar \
  https://amazon-berkeley-objects.s3.us-east-1.amazonaws.com/archives/abo-images-small.tar

tar -xf data/ABO/abo-images-small.tar -C data/ABO
```

Start the complete Docker stack:

```bash
docker compose up --build -d
```

Open the React interface:

```text
http://localhost:3000
```

Stop the stack:

```bash
docker compose down
```

For all cloning, image-download, public deployment, HTTPS, DNS, backup, update, and troubleshooting commands, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Python Development

Install project dependencies:

```bash
uv sync
```

Run the API locally:

```bash
uv run uvicorn src.main:app --reload
```

Run the Streamlit frontend locally:

```bash
uv run streamlit run frontend/app.py
```

Run API tests:

```bash
uv run pytest
```

Run the React frontend locally:

```bash
cd frontend-react
npm install
npm run dev
```

## Dataset

The project uses the Amazon Berkeley Objects public dataset.

The repository includes:

- the 4,500-record subset manifest
- precomputed `(4500, 512)` image embeddings
- embedding metadata
- evaluation CSV files

It does not include the raw ABO image archive or local Qdrant storage. Those must be downloaded or rebuilt as documented in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## Known Limitations

- Search quality depends on the limited 4,500-image category subset.
- Queries outside the dataset domain may return unrelated nearest matches.
- Dataset and product metadata may contain inaccurate or inconsistent labels.
- CLIP cosine similarity is a visual/semantic approximation, not a confidence score.
- The local BM25 baseline searches titles and metadata, not image pixels.
- The public demo should not be presented as a production recommendation engine.

## License and Attribution

The Amazon Berkeley Objects dataset is licensed under Creative Commons Attribution 4.0 International (`CC BY 4.0`).

Credit Amazon.com and the ABO dataset authors listed in `ABO_README.md`. The license text is included in `LICENSE-CC-BY-4.0.txt`.

Project code is for educational and portfolio use.