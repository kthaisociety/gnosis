# Gnosis CLI

### Features
1. Beautiful CLI TUI
2. Authentication with API key
3. PDF + image support
4. PDF text and table/graph embeddings/annotations

### Pipeline
1. User calls CLI with PDF or image
2. PDF/image is sent to Gnosis cloud service for processing
    - image: returns metadata
    - PDF: returns text, graph/table metadata, and PDF coordinates
3. Client embeds PDF with text and metadata based with returned coordinates
4. Output
    - image: metadata is simply returned as csv
    - PDF: embedded PDF is returned
