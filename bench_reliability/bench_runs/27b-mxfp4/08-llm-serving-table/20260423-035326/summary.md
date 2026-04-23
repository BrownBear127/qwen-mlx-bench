# Local LLM Serving Frameworks — OSS Landscape

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
|------|----------|-----------------------|-------------------------------|---------------|----------|
| llama.cpp | C/C++ | Yes (first-class: Metal, ARM NEON, Accelerate) | GGUF (1.5-bit, 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, 8-bit integer; also MXFP4) | Yes (OpenAI-compatible tool calling via `llama-server`) | https://github.com/ggml-org/llama.cpp |
| Ollama | Go (backend: llama.cpp) | Yes (native macOS, now also MLX-powered on Apple Silicon) | GGUF (via llama.cpp backend); also supports native model formats | Yes (tool calling with streaming support, added July 2024) | https://github.com/ollama/ollama |
| MLX (Apple) | Python / C++ / Swift | Yes (Apple Silicon only — designed exclusively for it) | 4-bit, 8-bit; QAT (quantization-aware training) models; native FP16/BF16 | No (framework-level; tool calling depends on model/chat layer, not built-in) | https://github.com/ml-explore/mlx |
| llamafile | C/C++ (llama.cpp + Cosmopolitan Libc) | Yes (inherits llama.cpp Metal/NEON support) | GGUF (same as llama.cpp: 1.5-bit through 8-bit) | Yes (inherits llama.cpp tool calling via bundled `llama-server`) | https://github.com/mozilla-ai/llamafile |
| llama-cpp-python | Python (bindings to llama.cpp) | Yes (Metal backend via `GGML_METAL=on`) | GGUF (same as llama.cpp: 1.5-bit through 8-bit) | Yes (structured function calling via JSON schema, OpenAI-compatible) | https://github.com/abetlen/llama-cpp-python |
