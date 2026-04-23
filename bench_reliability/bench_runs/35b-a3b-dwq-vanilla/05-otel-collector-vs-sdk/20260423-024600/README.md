# OpenTelemetry Collector vs SDK — Distinction

## OpenTelemetry SDK

The **OpenTelemetry SDK** is the language-specific library you install into your
application code. It is responsible for **generating** telemetry data — creating
spans, recording metrics, and capturing log records — according to the
OpenTelemetry specification. The SDK provides the `TracerProvider`, `MeterProvider`,
and `LoggerProvider` classes that you instantiate and configure in your
application. It also defines how telemetry is processed (via span processors,
meter readers, and log processors) and exported (via exporters that send data to
a backend or, for development, to the console). In short, the SDK lives **inside
your application** and is the part of OpenTelemetry that actually produces the
observability signals from your code.

## OpenTelemetry Collector

The **OpenTelemetry Collector** is a standalone, vendor-agnostic **proxy service**
that receives, processes, and exports telemetry data from many sources. It runs
as a separate process — typically deployed as a sidecar, daemon, or central
gateway — and is **not** part of your application's code. The Collector accepts
telemetry over various protocols (OTLP, Jaeger, Prometheus, etc.), applies
transformations (filtering, enrichment, batching), and forwards the data to one
or more backends (Jaeger, Prometheus, Zipkin, commercial APM tools, and so on).
Its purpose is to decouple your instrumented applications from the specifics of
where their telemetry data ends up, giving you a single point of control for
routing, security, and scaling across your entire observability pipeline.

## Key Differences

| Aspect              | SDK                              | Collector                          |
|---------------------|----------------------------------|------------------------------------|
| **Where it runs**   | Inside your application process  | As a separate, standalone service  |
| **What it does**    | Generates telemetry from code    | Receives, processes, routes data   |
| **Language-specific**| Yes (Python, Go, Java, …)       | No — language-agnostic             |
| **Network calls**   | Can send directly or to Collector| Always receives from many sources  |
| **Configuration**   | API calls in your code           | YAML config file                   |

## This POC

This proof-of-concept uses **only the OpenTelemetry Python SDK** — no Collector
is involved. It creates a `TracerProvider`, attaches a `SimpleSpanProcessor`
with a `ConsoleSpanExporter`, and emits a single span named `greeting` with one
attribute (`greeting.target`). The span is printed as JSON to stdout.

### Run

```bash
uv run --no-project --with opentelemetry-api --with opentelemetry-sdk python poc.py
```
