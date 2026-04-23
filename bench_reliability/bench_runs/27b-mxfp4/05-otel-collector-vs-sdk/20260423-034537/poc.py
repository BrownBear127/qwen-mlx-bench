"""
Minimal OpenTelemetry SDK proof-of-concept.

Emits a single trace span with one attribute and exports it to the console
using only the SDK — no Collector, no network calls.

Run with:
    uv run --no-project --with opentelemetry-api --with opentelemetry-sdk --with opentelemetry-semantic-conventions python poc.py
"""

import io
import json
import sys

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)

# --- Configure the SDK ---

resource = Resource.create(attributes={SERVICE_NAME: "poc-service"})
provider = TracerProvider(resource=resource)

# Capture the ConsoleSpanExporter output into a string buffer
captured = io.StringIO()
exporter = ConsoleSpanExporter(out=captured)
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)

# --- Create and close a span ---

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("hello-span") as span:
    span.set_attribute("http.method", "GET")

# --- Print the exported span as JSON ---

# Flush the span so it is exported
captured.seek(0)
raw = captured.read()
span_data = json.loads(raw)

print(json.dumps(span_data, indent=4))
