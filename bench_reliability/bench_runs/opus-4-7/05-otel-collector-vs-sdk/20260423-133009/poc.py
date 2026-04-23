"""Minimal OpenTelemetry SDK trace demo — no Collector required."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("poc")

with tracer.start_as_current_span("hello-span") as span:
    span.set_attribute("greeting", "world")

provider.shutdown()
