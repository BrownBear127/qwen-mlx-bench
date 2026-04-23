"""
Minimal OpenTelemetry SDK proof-of-concept.

Uses the OpenTelemetry SDK (NOT the Collector) to create a single trace span
with one attribute and export it to the console. No network calls, no Collector
running — everything happens in-process.
"""

import json
import sys

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExportResult,
)
from opentelemetry.trace import Span as TraceSpan


class JSONSpanExporter:
    """Exports finished spans as compact JSON to stdout (no network, no Collector)."""

    def export(self, spans):
        for span in spans:
            ctx = span.get_span_context()
            span_dict = {
                "name": span.name,
                "context": {
                    "trace_id": f"0x{ctx.trace_id:032x}",
                    "span_id": f"0x{ctx.span_id:016x}",
                },
                "kind": span.kind.name,
                "attributes": dict(span.attributes) if span.attributes else {},
                "start_time": span.start_time,
                "end_time": span.end_time,
                "status": {
                    "status_code": span.status.status_code.name,
                    "description": span.status.description or None,
                },
                "events": [
                    {
                        "name": event.name,
                        "timestamp": event.timestamp,
                        "attributes": dict(event.attributes) if event.attributes else {},
                    }
                    for event in span.events
                ],
            }
            print(json.dumps(span_dict, indent=2))
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return SpanExportResult.SUCCESS


def main():
    # 1. Create a Resource identifying this service.
    resource = Resource.create(attributes={SERVICE_NAME: "otel-sdk-poc"})

    # 2. Build a TracerProvider backed by the SDK (not the Collector).
    tracer_provider = TracerProvider(resource=resource)

    # 3. Attach a SimpleSpanProcessor that sends finished spans to our
    #    JSONSpanExporter (which writes to stdout).
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(JSONSpanExporter())
    )

    # 4. Register the provider globally so `trace.get_tracer()` finds it.
    trace.set_tracer_provider(tracer_provider)

    # 5. Obtain a tracer and create a single span with one attribute.
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("hello-span") as span:
        span.set_attribute("http.method", "GET")

    # The span is automatically ended and exported when the `with` block exits.


if __name__ == "__main__":
    main()
