from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

span_exporter = OTLPSpanExporter(
    endpoint="https://yxp44313.live.dynatrace.com/otlp/v1/traces"
    # insecure=True,
    headers=({
        'Authorization': 'Api-Token dt0c01.GVSTBQ233TLHNEZQKHVNNVBB.KNHS4VZZDCOHW2TDRI7SYVXNGOVI6LAKT2HAMX4ZV3464NGGIFLCUYYVWURD7EUP',
    }
    )
)
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
span_processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)

# Configure the tracer to use the collector exporter
tracer = trace.get_tracer_provider().get_tracer(__name__)

with tracer.start_as_current_span("foo"):
    print("Hello world!")