# Local LLM Serving Frameworks

| Name | Language | Apple Silicon support | Quantization formats supported | Tool calling? | Repo URL |
| --- | --- | --- | --- | --- | --- |
| llama.cpp | C/C++ | Yes | GGUF; 1.5-bit, 2-bit, 3-bit, 4-bit, 5-bit, 6-bit, 8-bit integer quantization | Yes | https://github.com/ggml-org/llama.cpp |
| Ollama | Go | Yes | `q8_0`, `q4_K_S`, `q4_K_M` | Yes | https://github.com/ollama/ollama |
| LocalAI | Go | Yes | Backend-dependent; README examples include GGUF `q4_k_m` and `Q8_0` | Yes | https://github.com/mudler/LocalAI |
| MLC LLM | Python/C++ | Yes | `q0f16`, `q0f32`, `q3f16_1`, `q4f16_1`, `q4f32_1`, `q4f16_awq`, `e4m3_e4m3_f16`, `e5m2_e5m2_f16` | Yes | https://github.com/mlc-ai/mlc-llm |
| mistral.rs | Rust | Yes | UQFF, GGUF (2-8 bit), GPTQ, AWQ, HQQ, FP8, BNB, ISQ | Yes | https://github.com/EricLBuehler/mistral.rs |
| MLX-LM | Python | Yes | MLX quantized checkpoints; 4-bit is explicitly documented | ? | https://github.com/ml-explore/mlx-lm |
