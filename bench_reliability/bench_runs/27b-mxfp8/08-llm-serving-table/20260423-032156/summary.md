# Local LLM Serving Frameworks — OSS Landscape

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
|------|----------|----------------------|-------------------------------|---------------|----------|
| llama.cpp | C/C++ | ✅ Yes (first-class, Metal/NEON/Accelerate) | Q2, Q3, Q4, Q5, Q6, Q8, IQ2, IQ3, IQ4, IQ5, IQ6, IQ8, MXFP4, GGUF | ✅ Yes (via `llama-server` function-calling API) | https://github.com/ggml-org/llama.cpp |
| Ollama | Go (wraps llama.cpp) | ✅ Yes (native macOS/Metal support) | Q4, Q5, Q8 (via GGUF backend) | ✅ Yes (tool calling via Modelfile `TOOLS` parameter) | https://github.com/ollama/ollama |
| MLX / mlx-lm | Python/C++ (Apple MLX framework) | ✅ Yes (Apple silicon only — designed for it) | 4-bit, 8-bit, FP16 (MLX native quantization) | ❌ No (no built-in tool calling; requires custom integration) | https://github.com/ml-explore/mlx-lm |
| llamafile | C/C++ (llama.cpp + Cosmopolitan libc) | ✅ Yes (inherits llama.cpp Metal backend) | Q2–Q8, GGUF (same as llama.cpp) | ✅ Yes (inherits llama.cpp function-calling support) | https://github.com/mozilla-ai/llamafile |
| vLLM | Python/C++/CUDA | ✅ Yes (Apple Silicon via Metal plugin) | FP8, INT4, INT8, GPTQ, AWQ, GGUF, MXFP4, NVFP4, compressed-tensors | ✅ Yes (tool calling and reasoning parsers built in) | https://github.com/vllm-project/vllm |
| SGLang | Python/C++/CUDA | ❌ No (NVIDIA/AMD/TPU/CPU only) | FP4, FP8, INT4, AWQ, GPTQ | ✅ Yes (structured outputs, tool calling via OpenAI-compatible API) | https://github.com/sgl-project/sglang |
