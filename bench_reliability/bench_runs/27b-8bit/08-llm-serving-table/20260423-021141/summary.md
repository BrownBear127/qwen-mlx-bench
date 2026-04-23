# Local LLM Serving Frameworks — OSS Landscape

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
|------|----------|----------------------|-------------------------------|---------------|----------|
| llama.cpp | C/C++ | ✅ Yes (first-class, Metal/NEON/Accelerate) | GGUF (Q2, Q3, Q4, Q5, Q6, Q8, IQ1_M, etc.), MXFP4 | ✅ Yes (via `llama-server` OpenAI-compatible API) | https://github.com/ggml-org/llama.cpp |
| Ollama | Go | ✅ Yes (native, uses llama.cpp backend) | GGUF (inherited from llama.cpp) | ✅ Yes (OpenAI-compatible `/api/chat` with tools parameter) | https://github.com/ollama/ollama |
| MLX / mlx-lm | Python (C++ core) | ✅ Yes (Apple Silicon only for GPU; CPU-only Linux also available) | 4-bit, 8-bit, FP16 (MLX native safetensors) | ✅ Yes (via chat template; model-dependent) | https://github.com/ml-explore/mlx-lm |
| vLLM | Python (CUDA/C++ kernels) | ✅ Yes (Apple Silicon via Metal plugin, experimental) | FP8, INT4, INT8, GPTQ, AWQ, GGUF, MXFP4, NVFP4, compressed-tensors, TorchAO | ✅ Yes (tool calling and reasoning parsers built-in) | https://github.com/vllm-project/vllm |
| SGLang | Python (CUDA/Rust) | ❌ No (NVIDIA/AMD/TPU/Intel CPU only) | FP4, FP8, INT4, AWQ, GPTQ | ✅ Yes (structured outputs, OpenAI API compatible) | https://github.com/sgl-project/sglang |
| Hugging Face TGI | Rust (Python glue) | ❌ No (NVIDIA/AMD/Inferentia/Intel GPU only) | bitsandbytes (INT8/INT4), GPTQ, EETQ, AWQ, Marlin, FP8, Safetensors | ✅ Yes (via guidance/JSON structured outputs) | https://github.com/huggingface/text-generation-inference |
