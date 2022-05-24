# create a python app that will send spans to the OpenTelemetry dynatraace
# app.py
import json
from opentelemetry import trace as OpenTelemetry
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

merged = dict()

merged.update({
    "service.name": "python-quickstart", #TODO Replace with the name of your application
    "service.version": "1.0.1", #TODO Replace with the version of your application
})
print(merged)
resource = Resource.create(merged)

tracer_provider = TracerProvider(sampler=sampling.ALWAYS_ON, resource=resource)
OpenTelemetry.set_tracer_provider(tracer_provider)

tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(
        endpoint="https://yxp44313.live.dynatrace.com/otlp/v1/traces",
        headers={
            'Authorization': 'Api-Token dt0c01.GVSTBQ233TLHNEZQKHVNNVBB.KNHS4VZZDCOHW2TDRI7SYVXNGOVI6LAKT2HAMX4ZV3464NGGIFLCUYYVWURD7EUP',
        }
    )))
print('Tracer provider created')

def main():
    """
    This is the main function to send spans to dynatrace
    """
    tracer = OpenTelemetry.get_tracer(__name__)
    with tracer.start_as_current_span("main"):
        tracer.get_current_span().set_attribute("key", "value")
        
    
