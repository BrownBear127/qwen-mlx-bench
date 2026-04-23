# OpenTelemetry SDK vs Collector — Minimal POC

## Quick Start

```bash
uv run --no-project --with opentelemetry-api --with opentelemetry-sdk python poc.py
```

This prints a single trace span (as JSON) to stdout. No network calls, no
Collector process, no external dependencies beyond the two SDK packages.

---

## Collector vs SDK — What's the Difference?

### OpenTelemetry SDK

The **OpenTelemetry SDK** is a library that you embed directly into your
application code. It provides the concrete implementations of the OpenTelemetry
API — things like `TracerProvider`, `Span`, and `Meter` — so your application
can actually generate telemetry data (traces, metrics, logs) at runtime. The SDK
also includes exporters that determine where that data goes: to the console, over
the network via OTLP, or to a file. When you use the SDK, your application is
responsible for creating spans, setting attributes, and shipping the data
somewhere. The SDK runs in the same process as your application and is the
primary way developers instrument their code.

### OpenTelemetry Collector

The **OpenTelemetry Collector** is a standalone, vendor-agnostic proxy service
that runs *outside* your application. It receives telemetry data from one or more
sources (typically via OTLP), processes it (filtering, sampling, transforming,
enriching), and then exports it to one or more backends (Jaeger, Prometheus,
Datadog, etc.). The Collector acts as a central aggregation point, so individual
services don't need to know about or depend on any specific observability
backend. It also handles concerns like batching, retries, and backpressure,
which makes it especially valuable in production environments where reliability
and scalability matter.

### Key Distinction

| Aspect | SDK | Collector |
|---|---|---|
| **Runs where?** | Inside your app process | Separate process / sidecar / daemon |
| **Purpose** | Generate & export telemetry | Receive, process, forward telemetry |
| **Network?** | May or may not use network | Always a network endpoint |
| **Required?** | Yes, to produce data | No — you can export directly |
| **This POC uses** | ✅ SDK only | ❌ Not involved |

In this POC, the SDK's `ConsoleSpanExporter` writes directly to stdout. There is
no Collector, no network, and no external backend — just the SDK doing its job
in-process.
