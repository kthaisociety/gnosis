import sys
import os
import grpc

CURRENT_DIR = os.path.dirname(__file__)
GRPC_DIR = os.path.join(CURRENT_DIR, "..", "app", "gRPC")
sys.path.insert(0, GRPC_DIR)

from generated import vlm_pb2, vlm_pb2_grpc


def test_inference(
    image_path: str,
    model_name: str = "nanonets/Nanonets-OCR-s",
    prompt: str = "Extract all text from this image.",
    use_gpu: bool = False,
    server: str = "localhost:50051",
):
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    config_json = f'{{"model_name": "{model_name}", "use_gpu": {str(use_gpu).lower()}}}'

    channel = grpc.insecure_channel(server)
    stub = vlm_pb2_grpc.VLMServerStub(channel)

    request = vlm_pb2.InferenceRequest(
        image=img_bytes,
        config_json=config_json,
        prompt=prompt,
    )

    print(f"Sending request to {server}...")
    print(f"  Model: {model_name}")
    print(f"  GPU: {use_gpu}")
    print(f"  Image: {image_path} ({len(img_bytes)} bytes)")

    response = stub.GenerateResponse(request)

    print("\nResponse:")
    if response.json:
        print(f"  json: {response.json}")
    if response.text:
        print(f"  text: {response.text}")
    if response.html:
        print(f"  html: {response.html}")
    if response.csv:
        print(f"  csv: {response.csv}")
    if response.markdown:
        print(f"  markdown: {response.markdown}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grpc_client.py <image_path> [server:port]")
        print("Example: python grpc_client.py test.png localhost:50051")
        sys.exit(1)

    img = sys.argv[1]
    srv = sys.argv[2] if len(sys.argv) > 2 else "localhost:50051"
    test_inference(img, server=srv)
