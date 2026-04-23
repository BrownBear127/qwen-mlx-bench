from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor


def main() -> None:
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    tracer = trace.get_tracer("poc")

    with tracer.start_as_current_span("demo-span") as span:
        span.set_attribute("demo.attribute", "hello")

    provider.shutdown()


if __name__ == "__main__":
    main()
