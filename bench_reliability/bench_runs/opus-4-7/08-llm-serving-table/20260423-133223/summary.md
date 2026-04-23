# Local LLM Serving Frameworks

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
|------|----------|----------------------|-------------------------------|---------------|----------|
| llama.cpp | C/C++ | Yes (Metal, ANE) | GGUF (Q2_K through Q8_0, F16, F32) | Yes (via server mode) | https://github.com/ggml-org/llama.cpp |
| Ollama | Go (wraps llama.cpp) | Yes (Metal) | GGUF (all llama.cpp quantizations) | Yes | https://github.com/ollama/ollama |
| vLLM | Python (C++/CUDA kernels) | No (CUDA/ROCm only) | GPTQ, AWQ, SqueezeLLM, FP8 | Yes | https://github.com/vllm-project/vllm |
| MLX (mlx-lm) | Python / C++ (Apple MLX) | Yes (Metal, native) | 4-bit, 8-bit (MLX format) | No | https://github.com/ml-explore/mlx-examples |
| LocalAI | Go (wraps llama.cpp + others) | Yes (Metal via llama.cpp) | GGUF, GPTQ (backend-dependent) | Yes | https://github.com/mudler/LocalAI |
| LM Studio | TypeScript/C++ (wraps llama.cpp) | Yes (Metal) | GGUF (all llama.cpp quantizations) | Yes | https://github.com/lmstudio-ai/lms |
| MLC LLM | Python / C++ (TVM) | Yes (Metal) | q4f16_1, q4f32_1, q3f16_1, q0f16, q0f32 | ? | https://github.com/mlc-ai/mlc-llm |
