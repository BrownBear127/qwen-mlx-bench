# Local LLM Serving Frameworks — OSS Landscape

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
|---|---|---|---|---|---|
| llama.cpp | C/C++ | ✅ Yes (Metal + CPU) | GGUF (Q2–Q8, IQ1–IQ4, MXFP4, and more) | ✅ Yes (via llama-server REST API) | https://github.com/ggml-org/llama.cpp |
| Ollama | Go | ✅ Yes (Metal + MLX backend preview) | GGUF (Q4_K_M, Q5_K_M, Q8_0, etc.) | ✅ Yes (OpenAI-compatible API) | https://github.com/ollama/ollama |
| vLLM | Python | ✅ Yes (vllm-metal plugin, vllm-mlx) | FP8, INT8, INT4, GPTQ, AWQ, GGUF, MXFP8/MXFP4, NVFP4 | ✅ Yes (OpenAI-compatible API) | https://github.com/vllm-project/vllm |
| MLX-LM | Python | ✅ Yes (native, Apple-only) | INT4, INT8, MXFP4 (MLX-native formats) | ✅ Yes (mlx-lm server with OpenAI-compatible API) | https://github.com/ml-explore/mlx-lm |
| TGI (Text Generation Inference) | Rust | ❌ No (CPU-only on Apple Silicon) | GPTQ, AWQ, bitsandbytes (INT8/INT4), EETQ, EXL2, FP8 | ✅ Yes (function calling / tool-use support) | https://github.com/huggingface/text-generation-inference |
