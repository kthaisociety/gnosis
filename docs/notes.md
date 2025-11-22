# Gnosis

## Models To Test
- Open-Source
  - Tesseract
  - ViT
  - PaddleOCR
  - Kraken
  - OCRopus
  - docTR
  - EasyOCR
  - Camelot ? github.com/atlanhq/camelot
  - Microsoft table transformer
  - PlotDigitizer (graphs, charts, scatter graphs)
  - graph2table
  - fine tune Microsoft's E5 model
  - Stella-en-1.5B, Voyage-3-large, BGE-large embedding models

- Proprietary
  - Grooper???
  - Amazon Textract
  - ABBYY FineReader + ABBYY Vantage
  - Google Cloud Vision
  - Azure AI Document Intelligence (Form Recognizer)
  - Adobe Scan ?
  - Mistral OCR
  - Gemini
  - ChatGPT
  - Claude
  - IBM ?
  - Hyperscience -> looks good but very proprietary
  - UI Path (proprietary)
  - Nanonets
  - Rossum
  - Tungsten Capture

## Ideas
- Use several models and merge results => better overall results
- Post processing with LLMs *probably* a good idea
- Equinor just used Azure services for digitization it seems
- Weviate = excellent VDB
- LangChain???

## Concepts
- **Preprocessing**
  - Deskew (rotation)
  - Denoise (lighting, spots, stains)
    - Simple filters work for light noise
    - Convolutional Autoencoder (CAE) for complex noise
  - Thresholding
    - There is dynamic thresholding (i.e. Otsu's method or Sauvola's method) to handle lighting variations in the same image
  - AI upscaling for sharpness ???

- **Layout analysis**
  - Examples:
    - DiT: ViT, transformer based, can be fine-tuned!!!
    - LayoutLM (Microsoft)

- **OCR**
  - CRNN with Attention mechanism
  - Decoder (post processing that predicts words based on what is given out by the OCR)

- **Table Recognition**
  - grid structure, rows, columns
  - i.e. TableNet
  - Finally apply **OCR** on this too

- **Chart/Graph Recognition**
  - Fine-tune DiT to identify chart components like x/y-labels etc.
  - **OCR** on detected labels etc.

- **Multimodal Document Embedding**
  - i.e. LayoutLMv3
  - Tokenise and prepare input to feed into model
