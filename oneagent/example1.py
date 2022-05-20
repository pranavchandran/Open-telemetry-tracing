import oneagent

if not oneagent.initialize():
    print('Error initializing OneAgent SDK.')

with oneagent.get_sdk().trace_incoming_remote_call('Mynewmethod', 'caller',
                                                   'dupypr://localhost/dummyEndpoint',
                                                   protocol_name='DUMMY_PROTOCOL',
                                                   str_tag='strtag') as call:
    print('+remote')


print('It may take a few moments before the path appears in the UI.')
input('Please wait...')
oneagent.shutdown()
