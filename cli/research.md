# Gnosis CLI
- CLI uploaded to PyPI (can be made available from pip, brew, yay (AUR)...)
- no local inference for now
- Pipeline
    1. send PDF or image to VLM server
    2. wait for text and coordinate response
    3. Embed PDF
- if you have bounding boxes you can embed annotations into the PDF => on click table/graph metadata is shown
    - on hover is unreliable across PDF viewers


## Plan
1. Initial CLI outline
2. Wire CLI to backend
3. Authentication
    - in CLI client
    - possibly requires new endpoints in backend to handle authentication
    - API keys
4. Add backend support for PDFs
5. CLI client embedding pipeline to output ready PDF with backend response using PyMuPDF
6. Clean CLI TUI with nice coloring etc.
