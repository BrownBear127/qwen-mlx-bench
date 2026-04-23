"""
Minimal OpenTelemetry SDK proof-of-concept.

Creates a single trace span with one attribute and exports it to the console
using the OpenTelemetry Python SDK — no Collector, no network calls.
"""

import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

# 1. Create a TracerProvider (the core SDK component that manages spans).
provider = TracerProvider()

# 2. Attach a SimpleSpanProcessor with a ConsoleSpanExporter.
#    SimpleSpanProcessor exports each span synchronously as soon as it ends.
#    ConsoleSpanExporter writes the span data to stdout as JSON.
provider.add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# 3. Set the global tracer provider so trace.get_tracer() uses it.
trace.set_tracer_provider(provider)

# 4. Obtain a tracer and create a single span with one attribute.
tracer = trace.get_tracer("poc-tracer")

with tracer.start_as_current_span("hello-span") as span:
    span.set_attribute("greeting", "Hello, OpenTelemetry!")

# The span is automatically exported to stdout as JSON above when it ends.
# For clarity, we also print a confirmation message.
print("\n--- Confirmation ---")
print("Span exported to console via the OpenTelemetry SDK (no Collector used).")
