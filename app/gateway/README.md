### API structure

- `generated/`: generated protobuf types and gRPC stubs.
- `protos/`: Protobuf code for our comms protocols (you know, the sauce).
- `utils/`: helpers like bytes <-> image conversions.
- `server.py`: actual gRPC server entrypoint.
- `client.py`: internal client for testing (throw a random image at the server).

### Generate protos
```bash
python3 -m grpc_tools.protoc -I gRPC/protos --python_out=gRPC/generated --grpc_python_out=gRPC/generated gRPC/protos/request.proto
```

### API & Service architecture
```mermaid
graph TD
    A[User] -->|REST request| B[REST API / Client Layer]
    B -->|gRPC request of encoded| C[gRPC Server]
    C -->|decode_image| D[utils/processbytes.py]
    D -->|np.ndarray| C
    C -->|np.ndarray| E[preprocessing/main.py]
    E -->|resize & clean| F[standardize.py]
    F -->|deskew| G[rotate.py]
    G -->|encode_image| H[utils/processbytes.py]
    H -->|bytes| C
    C -->|ProcessedImage encoded - response.proto| B
    B -->|REST response| A
```