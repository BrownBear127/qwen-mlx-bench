"""
Minimal OpenTelemetry SDK proof-of-concept.

Uses the OpenTelemetry Python SDK (NOT the Collector) to create a single
trace span with one attribute and export it to the console.
No network calls, no Collector process required.

Run with:
    uv run --no-project --with opentelemetry-api --with opentelemetry-sdk python poc.py
"""

import json

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExportResult,
)


class JSONConsoleExporter:
    """Exports finished spans as a single JSON object to stdout."""

    def export(self, spans):
        for span in spans:
            data = {
                "name": span.name,
                "context": {
                    "trace_id": f"0x{span.get_span_context().trace_id:032x}",
                    "span_id": f"0x{span.get_span_context().span_id:016x}",
                },
                "kind": span.kind.name,
                "status": {
                    "status_code": span.status.status_code.name,
                    "description": span.status.description or None,
                },
                "attributes": dict(span.attributes) if span.attributes else {},
                "start_time": span.start_time,
                "end_time": span.end_time,
                "resource": dict(span.resource.attributes) if span.resource else {},
            }
            print(json.dumps(data, indent=2))
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


def main():
    # 1. Create a resource that identifies the service.
    resource = Resource.create(attributes={SERVICE_NAME: "otel-sdk-poc"})

    # 2. Build a TracerProvider backed by the SDK (not the Collector).
    provider = TracerProvider(resource=resource)

    # 3. Attach a SimpleSpanProcessor that sends finished spans to our
    #    JSON console exporter immediately (no batching, no network).
    provider.add_span_processor(SimpleSpanProcessor(JSONConsoleExporter()))

    # 4. Register the provider globally.
    trace.set_tracer_provider(provider)

    # 5. Obtain a tracer and create a single span with one attribute.
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("hello-span") as span:
        span.set_attribute("http.method", "GET")

    # The span is automatically ended and exported when the context manager
    # exits.  The JSON output above is the exported span.


if __name__ == "__main__":
    main()
