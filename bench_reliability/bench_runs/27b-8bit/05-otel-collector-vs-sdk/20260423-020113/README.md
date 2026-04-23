# OpenTelemetry SDK vs Collector — Minimal POC

## Collector vs SDK: What's the difference?

### OpenTelemetry SDK

The OpenTelemetry SDK is a library that you embed directly into your application code. It provides the concrete implementation of the OpenTelemetry API — things like tracers, meters, and loggers — and is responsible for creating, managing, and exporting telemetry data (traces, metrics, logs) from within your process. The SDK handles span lifecycle, context propagation, sampling decisions, and ships the data to whatever exporter you configure (console, OTLP over HTTP/gRPC, etc.). In short, the SDK is the client-side component that lives inside your application and turns your instrumentation calls into real telemetry signals.

### OpenTelemetry Collector

The OpenTelemetry Collector is a standalone, vendor-agnostic daemon (a separate process or service) that receives telemetry data from many sources, processes it, and forwards it to one or more backends. It acts as a middleman between instrumented applications and observability backends like Jaeger, Prometheus, or commercial APM platforms. The Collector can transform, filter, sample, batch, and enrich telemetry data in-flight, and it supports receiving data in multiple formats (OTLP, Jaeger, Zipkin, Prometheus, etc.) while exporting to any combination of destinations. In short, the Collector is a server-side proxy that sits between your apps and your observability backends, giving you a single, flexible pipeline for all telemetry.

### Key distinction

| Aspect | SDK | Collector |
|---|---|---|
| Where it runs | Inside your application process | As a separate service/daemon |
| Role | Creates and exports telemetry | Receives, processes, and forwards telemetry |
| Required for this POC? | **Yes** | **No** |
| Network calls? | Only if you use a network exporter | Always (it's a network service) |

## Running this POC

This proof-of-concept uses **only the SDK** — no Collector is running, and no network calls are made. The span is exported directly to stdout via `ConsoleSpanExporter`.

```bash
uv run --no-project --with opentelemetry-api --with opentelemetry-sdk python poc.py
```

### Expected output

A JSON object representing the exported span, similar to:

```json
{
  "name": "hello-span",
  "context": {
    "trace_id": "0x...",
    "span_id": "0x..."
  },
  "kind": "INTERNAL",
  "status": {
    "status_code": "UNSET",
    "description": null
  },
  "attributes": {
    "http.method": "GET"
  },
  "start_time": 1719000000000000000,
  "end_time": 1719000000000000000,
  "resource": {
    "service.name": "otel-sdk-poc",
    ...
  }
}
```

## Dependencies

| Package | Purpose |
|---|---|
| `opentelemetry-api` | The OpenTelemetry API (interfaces) |
| `opentelemetry-sdk` | The OpenTelemetry SDK (implementation + ConsoleSpanExporter) |
