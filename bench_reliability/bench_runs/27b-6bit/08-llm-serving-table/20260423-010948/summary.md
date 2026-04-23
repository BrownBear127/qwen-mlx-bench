# Local LLM Serving Frameworks — OSS Landscape

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
|------|----------|----------------------|-------------------------------|---------------|----------|
| llama.cpp | C/C++ | ✅ Yes (first-class, Metal/NEON/Accelerate) | GGUF (Q2–Q8, IQ2–IQ4, MXFP4), fp16, fp32 | ✅ Yes (via `llama-server` function-calling API) | https://github.com/ggml-org/llama.cpp |
| Ollama | Go (wraps llama.cpp) | ✅ Yes (Metal via llama.cpp backend) | GGUF (inherits all llama.cpp formats) | ✅ Yes (tool calls via Modelfile `TOOLS` parameter) | https://github.com/ollama/ollama |
| MLX / MLX-LM | Python / C++ | ✅ Yes (Apple Silicon only — native Metal) | 4-bit, 6-bit, 8-bit quantization (Safetensors → MLX format) | ❌ No (no built-in tool-calling API) | https://github.com/ml-explore/mlx |
| vLLM | Python / CUDA C++ | ✅ Yes (Apple Silicon plugin available) | FP8, INT4, INT8, GPTQ, AWQ, GGUF, MXFP4, NVFP4, compressed-tensors, TorchAO | ✅ Yes (tool calling + reasoning parsers) | https://github.com/vllm-project/vllm |
| SGLang | Python / CUDA C++ | ❌ No (NVIDIA/AMD/TPU/CPU only) | FP4, FP8, INT4, AWQ, GPTQ | ✅ Yes (structured outputs, tool calling) | https://github.com/sgl-project/sglang |
| llama-cpp-python | Python (bindings to llama.cpp) | ✅ Yes (Metal via `GGML_METAL=on`) | GGUF (inherits all llama.cpp formats) | ✅ Yes (function calling support) | https://github.com/abetlen/llama-cpp-python |
