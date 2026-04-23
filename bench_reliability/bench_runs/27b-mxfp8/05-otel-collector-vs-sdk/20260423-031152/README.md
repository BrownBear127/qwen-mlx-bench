# OpenTelemetry SDK vs Collector — Proof of Concept

## What is the OpenTelemetry SDK?

The OpenTelemetry SDK is a library that you embed directly into your application code. It provides the concrete implementation of the OpenTelemetry API, allowing you to create, manage, and export telemetry data (traces, metrics, and logs) from within your application process. The SDK handles span creation, context propagation, and ships built-in exporters that can send data to various destinations — including the console, OTLP endpoints, or other backends. In this POC, the SDK runs entirely in-process with no external services required.

## What is the OpenTelemetry Collector?

The OpenTelemetry Collector is a standalone, vendor-agnostic proxy service that receives, processes, and exports telemetry data from multiple sources. It runs as a separate process (or agent) outside your application and acts as a central aggregation point: applications send their telemetry to the Collector, which can then batch, filter, transform, or route the data to one or more backends (e.g., Jaeger, Prometheus, Datadog). The Collector is useful in production environments where you want to decouple your application from backend-specific exporters, add retry/batching logic, or apply uniform data processing across many services.

## Key Distinction

| Aspect | SDK | Collector |
|---|---|---|
| **Where it runs** | Inside your application process | As a separate service/agent |
| **Purpose** | Generate and export telemetry from code | Receive, process, and forward telemetry from many sources |
| **Network calls** | Optional (depends on exporter) | Always involved (receives from apps, sends to backends) |
| **Required for this POC?** | Yes | No |

## Running this POC

This proof-of-concept uses only the OpenTelemetry SDK with a `ConsoleSpanExporter`. No Collector is running, and no network calls are made.

```bash
uv run --no-project --with opentelemetry-api --with opentelemetry-sdk python poc.py
```

### Expected output

You will see a JSON object representing the exported span, containing fields such as `name`, `context` (with `trace_id` and `span_id`), `attributes` (with `"greeting": "Hello, OpenTelemetry!"`), and `resource` metadata.
