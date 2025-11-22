# Whiteboard Architecture

see [Image](systemArchitecture_v0.1.jpg) for full image
```mermaid
flowchart TD
    A[Client] -->|Send img| B[Middleware]
    B -->|Forward img| C[Processing Node]

    C -->|Run Classification| D[Model]
    C -->|Extract Text| E[OCR]
    C -->|Store/Retrieve| F[(S3 Bucket)]

    D -->|Results| C
    E -->|Text Data| C
    F -->|Image Data| C
```
