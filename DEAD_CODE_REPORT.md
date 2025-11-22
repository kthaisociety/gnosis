# Dead Code & Inefficiency Report

## Dead Code

### 1. Unused Proto Files in Gateway
**Location**: `app/gateway/app/gRPC/generated/request_pb2.py`, `request_pb2_grpc.py`, `app/gateway/app/gRPC/protos/request.proto`

**Issue**: These files define a `PreProcessing` service but are never imported or used. Gateway only uses `vlm.proto` for VLM inference.

**Action**: Delete if preprocessing service is not needed, or document if it's for future use.

### 2. Unused VLMVLLM Class
**Location**: `app/gateway/app/services/inference/vlm/vllm.py`, exported in `__init__.py`

**Issue**: `VLMVLLM` is defined and exported but never used in `main.py` inference routing. Only `VLMTransformer` and `VLMGemini` are used.

**Action**: Remove from `__init__.py` exports if not needed, or add support in `main.py`.

## Inefficiencies

### 1. Duplicate Model Definitions
**Location**: 
- `app/gateway/app/models/vlm_models.py`
- `app/vlm_server/src/infer/vlm/vlm.py`

**Issue**: `VLMOutput`, `DataPoint`, `InferenceConfig` defined in both places. Gateway services use gateway models, but vlm_server has its own.

**Status**: Known issue, TODO in PR to consolidate.

## Recommendations

1. **Delete unused `request.proto` files** or document if for future use
2. **Remove `VLMVLLM` from exports** if not used, or add support in `main.py`
3. **Consolidate model definitions** (already in TODO)
