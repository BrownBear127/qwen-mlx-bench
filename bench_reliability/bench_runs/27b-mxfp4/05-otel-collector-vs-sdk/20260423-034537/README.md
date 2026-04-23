# OpenTelemetry SDK vs Collector — Minimal POC

## What is the OpenTelemetry SDK?

The OpenTelemetry SDK is a library you embed directly into your application code. It provides the concrete implementation of the OpenTelemetry API, allowing you to create spans, record metrics, and emit logs from within your own processes. The SDK handles everything from generating trace IDs and timestamps to collecting telemetry data in memory and sending it to an exporter of your choice (such as a console, an OTLP endpoint, or a file). Because it lives inside your application, the SDK gives you full programmatic control over what data is generated and how it is exported, without requiring any external infrastructure.

## What is the OpenTelemetry Collector?

The OpenTelemetry Collector is a standalone, vendor-agnostic service that runs outside your application. It acts as a middleman proxy that receives telemetry data from many sources (via OTLP, Jaeger, Prometheus, or other protocols), processes and transforms it (for example, filtering, sampling, or enriching with metadata), and then forwards it to one or more backends like Jaeger, Prometheus, or a commercial observability platform. The Collector is especially useful in production environments because it decouples your application from the final destination of its telemetry, provides a single point for data transformation, and can aggregate data from many services without requiring each service to know about the backend.

## Key Distinction

| Aspect | SDK | Collector |
|---|---|---|
| **Where it runs** | Inside your application process | As a separate service (e.g., Docker, Kubernetes) |
| **Purpose** | Generate and export telemetry from code | Receive, process, and forward telemetry from many sources |
| **Network calls** | Optional (depends on exporter) | Always (receives and sends over the network) |
| **Required for this POC?** | Yes | No |

## Running the POC

This proof-of-concept uses **only the SDK** — no Collector is needed, and no network calls are made.

```bash
uv run --no-project \
  --with opentelemetry-api \
  --with opentelemetry-sdk \
  --with opentelemetry-semantic-conventions \
  python poc.py
```

The script creates a single span named `hello-span` with one attribute (`http.method: "GET"`), exports it via `ConsoleSpanExporter`, and prints the resulting JSON to stdout.
