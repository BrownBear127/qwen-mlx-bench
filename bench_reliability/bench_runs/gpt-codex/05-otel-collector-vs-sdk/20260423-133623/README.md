# OpenTelemetry SDK-Only Python POC

This example uses the OpenTelemetry Python SDK directly inside the application process. It creates one trace span, adds one span attribute, and sends the exported result to stdout. No Collector is required, and no network call is made.

## Collector vs SDK

### What the Collector does

The OpenTelemetry Collector is a separate service, not a library you import into your Python file. Its job is to receive telemetry from applications, optionally reshape or filter it, and then forward it to one or more backends. In other words, the Collector sits between apps and observability systems so you can centralize routing, processing, and policy outside your application code.

### What the SDK does

The OpenTelemetry SDK is the in-process library that your application uses to create and manage telemetry. It is responsible for things like creating spans, attaching attributes, applying sampling and span processing, and handing finished spans to an exporter. In this POC, the SDK never talks to a remote service because it uses `ConsoleSpanExporter`, which prints the span JSON directly to stdout.

## Why this POC uses the SDK and not the Collector

This example is intentionally local and minimal. The Python process creates the span and exports it itself, so there is no extra service running beside it. That keeps the example focused on the SDK role and avoids the common beginner mistake of thinking the Collector is required just to make a span exist.

## Run

```bash
uv run --no-project --with opentelemetry-sdk python poc.py
```

If you are in a restricted sandbox where `uv` cannot write to its default cache directory, use:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with opentelemetry-sdk python poc.py
```

## Expected output

The exact IDs and timestamps will differ, but the output will be JSON printed to stdout and will include the single span attribute:

```json
{
    "name": "demo-span",
    "attributes": {
        "demo.attribute": "hello"
    }
}
```

## Files

- `poc.py`: minimal SDK-only example
- `README.md`: explanation and run instructions

## Sources

- OpenTelemetry components: https://opentelemetry.io/docs/concepts/components/
- OpenTelemetry Collector: https://opentelemetry.io/docs/collector/
- OpenTelemetry Python exporters: https://opentelemetry.io/docs/languages/python/exporters/
- OpenTelemetry Python SDK docs: https://opentelemetry-python.readthedocs.io/en/latest/sdk/index.html
- OpenTelemetry Python trace export docs: https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html
