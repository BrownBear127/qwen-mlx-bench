# OpenTelemetry: Collector vs SDK

## What the SDK does

The OpenTelemetry SDK is a language-specific library (Python, Java, Go, etc.) that you embed directly inside your application process. It is responsible for creating and managing telemetry data — traces, metrics, and logs — at the point where they originate. The SDK provides the APIs you call in your code to start spans, record attributes, and register exporters that decide where the data goes. Because it runs in-process, the SDK is the only component that can instrument your application code; without it, no telemetry is generated in the first place.

## What the Collector does

The OpenTelemetry Collector is a standalone binary (or sidecar/daemon) that runs outside your application as a separate process. It receives telemetry data over the network (typically via OTLP gRPC or HTTP), and can then transform, filter, batch, and re-export that data to one or more backends such as Jaeger, Prometheus, or a cloud vendor's ingestion endpoint. The Collector is optional — your SDK can export directly to a backend — but in production it is common to route through a Collector so that concerns like retry logic, credential management, and fan-out to multiple backends are handled outside the application.

## Running the POC

```bash
uv run --no-project \
  --with opentelemetry-api \
  --with opentelemetry-sdk \
  python poc.py
```

This prints the exported span (including its trace ID, span ID, attributes, and timing) as JSON to stdout. No Collector or external service is needed.
