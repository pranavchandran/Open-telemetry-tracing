import oneagent

if not oneagent.initialize():
    print('Error initializing OneAgent SDK.')

with oneagent.get_sdk().trace_incoming_remote_call('SimpleToolRental', 'example3',
                                                   'https://simple-tool-rental-api.glitch.me',
                                                   protocol_name='SimpleToolRental',
                                                   str_tag='strtag') as call:
    print('+remote')


            

print('It may take a few moments before the path appears in the UI.')
input('Please wait...')
oneagent.shutdown()
