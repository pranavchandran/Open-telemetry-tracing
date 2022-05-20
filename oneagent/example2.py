import oneagent

if not oneagent.initialize():
    print('Error initializing OneAgent SDK.')

with oneagent.get_sdk().trace_incoming_remote_call('Simpletool', 'caller',
                                                   'https://simple-tool-rental-api.glitch.me',
                                                   protocol_name='SimpleToolRental',
                                                   str_tag='strtag') as call:
    print('+remote')
    # create a log entry
    with oneagent.get_sdk().trace_log_entry('SimpleToolRental', 'caller', 'caller',
                                            'https://simple-tool-rental-api.glitch.me',
                                            protocol_name='SimpleToolRental',
                                            str_tag='strtag') as log:
        print('+log')
        # create a metric entry
        with oneagent.get_sdk().trace_metric_entry('SimpleToolRental', 'caller',
                                                   'caller', 'https://simple-tool-rental-api.glitch.me',
                                                   protocol_name='SimpleToolRental',
                                                   str_tag='strtag') as metric:
            print('+metric')
            print('+metric with value')

            

print('It may take a few moments before the path appears in the UI.')
input('Please wait...')
oneagent.shutdown()
