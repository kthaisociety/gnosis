# Evaluation Service

VLM performance evaluation using cloud-based benchmark datasets.

## Setup

Create a `.env` file:

```env
DATABASE_URL=postgresql://...
BUCKET_NAME=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
SCHEMA_NAME=benchmark
```

## Workflow

### Run Evaluation
Execute evaluations against a dataset already registered in the Cloud (Neon DB + S3/R2):

```bash
uv run src/eval/eval.py
```

## Tree

```
.
├── src/eval/
│   ├── data/           # Database, S3, and pipeline logic
│   ├── metrics/        # Scoring algorithms (RMS, RNSS)
│   ├── eval.py         # Main evaluation runner
│   └── models.py       # Pydantic schemas
└── tests/              # Integration and unit tests
```
