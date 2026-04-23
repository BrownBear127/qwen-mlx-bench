"""
Minimal OpenTelemetry SDK POC — emits a single trace span with one attribute
and exports it to the console. No Collector, no network calls.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# 1. Create a TracerProvider (the SDK component that manages spans)
provider = TracerProvider()

# 2. Attach a SimpleSpanProcessor with a ConsoleSpanExporter
#    SimpleSpanProcessor exports spans synchronously (one-at-a-time),
#    and ConsoleSpanExporter prints them as JSON to stdout.
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# 3. Set the global default tracer provider
trace.set_tracer_provider(provider)

# 4. Get a tracer and create a single span with one attribute
tracer = trace.get_tracer("poc.tracer")

with tracer.start_as_current_span("greeting") as span:
    span.set_attribute("greeting.target", "world")
