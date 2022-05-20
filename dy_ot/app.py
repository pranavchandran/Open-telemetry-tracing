import json
import requests
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
for name in ["dt_metadata_e617c525669e072eebe3d0f08212e8f2.json", "/var/lib/dynatrace/enrichment/dt_metadata.json"]:
    try:
        data = ''
        with open(name) as f:
          data = json.load(f if name.startswith("/var") else open(f.read()))
        merged.update(data)
    except:
        pass

merged.update({
    "service.name": "python-quickstart", #TODO Replace with the name of your application
    "service.version": "1.0.1", #TODO Replace with the version of your application
})
resource = Resource.create(merged)

tracer_provider = TracerProvider(sampler=sampling.ALWAYS_ON, resource=resource)
OpenTelemetry.set_tracer_provider(tracer_provider)
headers = {
    "Authorization": "Api-Token dt0c01.GVSTBQ233TLHNEZQKHVNNVBB.KNHS4VZZDCOHW2TDRI7SYVXNGOVI6LAKT2HAMX4ZV3464NGGIFLCUYYVWURD7EUP",
    "Content-Type": "application/json"
}
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(
        endpoint="http://yxp44313.live.dynatrace.com/otlp/v1/traces",
        headers=headers
    )))


# response = requests.post(
#     "http://yxp44313.live.dynatrace.com/otlp/v1/traces", headers=headers, data=json.dumps({"spans": []})
# )