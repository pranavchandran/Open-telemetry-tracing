'''This example demonstrates instrumenting a (mocked) application that executes
a remote call that sometimes fails and does some database operations.'''

import threading
import oneagent # SDK initialization functions
import oneagent.sdk as onesdk # All other SDK functions.
from oneagent.common import MessagingDestinationType
import pyodbc as pd

IN_DEV_ENVIRONMENT = True # Let's assume we are *not* in production here...
getsdk = oneagent.get_sdk # Just to make the code shorter.

def traced_db_operation(dbinfo, sql):
    print('+db', dbinfo, sql)

    # Entering the with block automatically start the tracer.
    with getsdk().trace_sql_database_request(dbinfo, sql) as tracer:
    # Connect database with ip
        cnxn = pd.connect('DRIVER={SQL Server};SERVER=192.168.43.216,1433;DATABASE=Sample;UID=User1;PWD=Neepspranav12')
        cursor = cnxn.cursor()
        cursor.execute('SELECT * FROM [dbo].[Employees]')
        row = cursor.fetchone()
        while row:
            print(row)
            row = cursor.fetchone()
        # In real-world code, you would do the actual database operation here,
        # i.e. call the database's API.

        # Set an optional "exit"-field on the tracer. Whenever there is a
        # setter available on a tracer (as opposed to an optional parameter to a
        # trace_* function), it may be called anytime between creating and
        # ending the tracer (i.e. also after starting it).
        # find length of the table
        cursor.execute('SELECT COUNT(*) FROM [dbo].[Employees]')
        count = cursor.fetchone()[0]
        tracer.set_rows_returned(count)
        tracer.set_round_trip_count(3)

    print('-db', dbinfo, sql)

def outgoing_remote_call(success):
    print('+remote')

    # We use positional arguments to specify required values and named arguments
    # to specify optional values.
    call = getsdk().trace_outgoing_remote_call(
        'dummyPyMethod', 'DummyPyService', 'dupypr://localhost/dummyEndpoint',
        onesdk.Channel(onesdk.ChannelType.IN_PROCESS, 'localhost'),
        protocol_name='DUMMY_PY_PROTOCOL')
    try:
        with call:

            # Note that this property can only be accessed after starting the
            # tracer. See the documentation on tagging for more information.
            strtag = call.outgoing_dynatrace_string_tag
            do_remote_call(strtag, success)
    except RuntimeError: # Swallow the exception raised above.
        pass
    print('-remote')

failed = [None]

def do_remote_call_thread_func(strtag, success):
    try:
        print('+thread')
        # We use positional arguments to specify required values and named
        # arguments to specify optional values.
        incall = getsdk().trace_incoming_remote_call(
            'dummyPyMethod', 'DummyPyService',
            'dupypr://localhost/dummyEndpoint',
            protocol_name='DUMMY_PY_PROTOCOL', str_tag=strtag)
        with incall:
            if not success:
                raise RuntimeError('Remote call failed on the server side.')
            dbinfo = getsdk().create_database_info(
                'Sample', oneagent.sdk.DatabaseVendor.SQLSERVER,
                oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, '169.254.149.39')
            )

            # This with-block will automatically free the database info handle
            # at the end. Note that the handle is used for multiple tracers. In
            # general, it is recommended to reuse database (and web application)
            # info handles as often as possible (for efficiency reasons).
            with dbinfo:
                traced_db_operation(
                    dbinfo, "select * from [dbo].Employees;")

                
 
        print('-thread')
    except Exception as e:
        failed[0] = e
        raise


def do_remote_call(strtag, success):
    # This function simulates doing a remote call by calling a function
    # do_remote_call_thread_func in another thread, passing a string tag. See
    # the documentation on tagging for more information.

    failed[0] = None
    workerthread = threading.Thread(
        target=do_remote_call_thread_func,
        args=(strtag, success))
    workerthread.start()

    # Note that we need to join the thread, as all tagging assumes synchronous
    # calls.
    workerthread.join()

    if failed[0] is not None:
        raise failed[0] #pylint:disable=raising-bad-type

def mock_incoming_web_request():
    sdk = getsdk()
    wappinfo = sdk.create_web_application_info(
        virtual_host='pranav.com', # Logical name of the host server.
        application_id='MyTestApplication', # Unique web application ID.
        context_root='/my-test-app/') # App's prefix of the path part of the URL.

    with wappinfo:
        # This with-block will automatically free web application info handle
        # at the end. Note that the handle can be used for multiple tracers. In
        # general, it is recommended to reuse web application info handles as
        # often as possible (for efficiency reasons). For example, if you use
        # WSGI, the web application info could be stored as an attribute of the
        # application object.
        #
        # Note that different ways to specify headers, response headers and
        # parameter (form fields) not shown here also exist. Consult the
        # documentation for trace_incoming_web_request and
        # IncomingWebRequestTracer.
        wreq = sdk.trace_incoming_web_request(
            wappinfo,
            'https://simple-tool-rental-api.glitch.me/tools?category=electric-generators&available=true',
            'GET',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Language': 'en-US,en;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'simple-tool-rental-api.glitch.me',
                'Cookie': '_ga=GA1.2.1278131931.1569781288; _gid=GA1.2.1023225811.1569781288; _gat=1',
            }
        )
        with wreq:
            wreq.add_parameter('category', 'electric-generators')
            wreq.add_parameter('available', 'true')
            # Process web request
            wreq.add_response_headers({
                'Content-Type': 'application/json'
            }
            )
            wreq.set_status_code(200)

            # Add 3 different custom attributes.
            # sdk.add_custom_request_attribute('custom int attribute', 42)
            # sdk.add_custom_request_attribute('custom float attribute', 1.778)
            # sdk.add_custom_request_attribute('custom string attribute', 'snow is falling')

            # # This call will trigger the diagnostic callback.
            # sdk.add_custom_request_attribute('another key', None)

            # This call simulates incoming messages.
            mock_process_incoming_message()

def _process_my_outgoing_request(_tag):
    pass

def mock_outgoing_web_request():
    sdk = getsdk()
    url = 'https://simple-tool-rental-api.glitch.me/tools?category=electric-generators&available=true'
    
    # Create tracer and and request headers.
    tracer = sdk.trace_outgoing_web_request(url, 'GET',
                                            headers={
                                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                                                'Accept-Language': 'en-US,en;q=0.9',
                                                'Upgrade-Insecure-Requests': '1',
                                                'Cache-Control': 'max-age=0',
                                                'Connection': 'keep-alive',
                                                'Host': 'simple-tool-rental-api.glitch.me',
                                                'Cookie': '_ga=GA1.2.1278131931.1569781288; _gid=GA1.2.1023225811.1569781288; _gat=1',
                                            }
                                            )
    with tracer:
        # Process request
        tracer.add_response_headers({
            'Content-Type': 'application/json'
        }
        )
        tracer.set_status_code(200)
        # Add 3 different custom attributes.
        # sdk.add_custom_request_attribute('custom int attribute', 42)
        # sdk.add_custom_request_attribute('custom float attribute', 1.778)
        # sdk.add_custom_request_attribute('custom string attribute', 'snow is falling')

        # # This call will trigger the diagnostic callback.
        # sdk.add_custom_request_attribute('another key', None)

        # This call simulates incoming messages.
        # mock_process_incoming_message()

    with tracer:
        # Now get the outgoing dynatrace tag. You have to add this tag as request header to your
        # request if you want that the path is continued on the receiving site. Use the constant
        # oneagent.common.DYNATRACE_HTTP_HEADER_NAME as request header name.
        tag = tracer.outgoing_dynatrace_string_tag

        # Here you process and send your web request.
        # _process_my_outgoing_request(tag)
        response = sdk.trace_outgoing_web_request(url, 'GET',
                                        headers={
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                                            'Accept-Language': 'en-US,en;q=0.9',
                                            'Upgrade-Insecure-Requests': '1',
                                            'DYNATRACE_HTTP_HEADER_NAME': tag,
                                            'Cache-Control': 'max-age=0',
                                            'Connection': 'keep-alive',
                                            'Host': 'simple-tool-rental-api.glitch.me',
                                            'Cookie': '_ga=GA1.2.1278131931.1569781288; _gid=GA1.2.1023225811.1569781288; _gat=1',
                                        }
                                        )

        # As soon as the response is received, you can add the response headers to the
        # tracer and you shouldn't forget to set the status code, too.
        tracer.add_response_headers({
            'Content-Type': 'application/json',
            'X-Dynatrace-Tag': tag,
        }
        )
        tracer.set_status_code(response.get_status_code())

        # This call will trigger the diagnostic callback.
        # sdk.add_custom_request_attribute('another key', None)

        # This call simulates incoming messages.
        mock_process_incoming_message()

def mock_process_incoming_message():
    sdk = getsdk()

    # Create the messaging system info object.
    msi_handle = sdk.create_messaging_system_info(
        'MyPythonSenderVendor', 'MyPythonDestination', MessagingDestinationType.QUEUE,
        onesdk.Channel(onesdk.ChannelType.UNIX_DOMAIN_SOCKET, 'MyPythonChannelEndpoint'))

    with msi_handle:
        # Create the receive tracer for incoming messages.
        with sdk.trace_incoming_message_receive(msi_handle):
            print('here we wait for incoming messages ...')

            # Create the tracer for processing incoming messages.
            tracer = sdk.trace_incoming_message_process(msi_handle)

            # Now we can set the vendor message and correlation IDs. It's possible to set them
            # either before the tracer is started or afterwards. But they have to be set before
            # the tracer ends.
            tracer.set_vendor_message_id('message_id')
            with tracer:
                print('handle incoming message')
                tracer.set_correlation_id('correlation_id')

def mock_outgoing_message():
    sdk = getsdk()

    # Create the messaging system info object.
    msi_handle = sdk.create_messaging_system_info(
        'MyPythonReceiverVendor', 'MyPythonDestination', MessagingDestinationType.TOPIC,
        onesdk.Channel(onesdk.ChannelType.TCP_IP, '10.11.12.13:1415'))

    with msi_handle:
        # Create the outgoing message tracer;
        with sdk.trace_outgoing_message(msi_handle) as tracer:
            # Set the message and correlation IDs.
            tracer.set_vendor_message_id('msgId')
            tracer.set_correlation_id('corrId')

            print('handle outgoing message')

def mock_custom_service():
    sdk = getsdk()

    with sdk.trace_custom_service('my_fancy_transaction', 'MyFancyService'):
        print('do some fancy stuff')

def _diag_callback(text):
    print(text)

def main():
    print('+main')

    # This gathers arguments prefixed with '--dt_' from sys.argv into the
    # returned list. See initialize below.
    sdk_options = oneagent.sdkopts_from_commandline(remove=True)

    # Before using the SDK you have to initialize the OneAgent. You can call oneagent.initialize()
    # as often as you want, but you also have to call oneagent.shutdown() for every call to
    # initialize() as well.
    #
    # Passing in the sdk_options is entirely optional and usually not required
    # as all settings will be automatically provided by the Dynatrace OneAgent
    # that is installed on the host.
    init_result = oneagent.initialize(sdk_options)
    try:
        if init_result.error is not None:
            print('Error during SDK initialization:', init_result.error)

        # While not by much, it is a bit faster to cache the result of
        # oneagent.get_sdk() instead of calling the function multiple times.
        sdk = getsdk()

        # Set the diagnostic callback. Strongly recommended.
        sdk.set_diagnostic_callback(_diag_callback)

        # Set the verbose callback.
        # Not recommended in production as lots of messages can be emitted.
        if IN_DEV_ENVIRONMENT:
            sdk.set_verbose_callback(_diag_callback)

        # The agent state is one of the integers in oneagent.sdk.AgentState.
        print('Agent state:', sdk.agent_state)

        # The instance attribute 'agent_found' indicates whether an agent could be found or not.
        print('Agent found:', sdk.agent_found)

        # If an agent was found but it is incompatible with this version of the SDK for Python
        # then 'agent_is_compatible' would be set to false.
        print('Agent is compatible:', sdk.agent_is_compatible)

        # The agent version is a string holding both the OneAgent version and the
        # OneAgent SDK for C/C++ version separated by a '/'.
        print('Agent version:', sdk.agent_version_string)

        mock_incoming_web_request()

        mock_outgoing_web_request()

        mock_outgoing_message()

        mock_custom_service()

        # We use trace_incoming_remote_call here, because it is one of the few
        # calls that create a new path if none is running yet.
        with sdk.trace_incoming_remote_call('main', 'main', 'main'):
            # We want to start an asynchronous execution at this time, so we create an
            # in-process link which we will use afterwards (or in a different thread).
            link = sdk.create_in_process_link()

            # Simulate some remote calls
            outgoing_remote_call(success=True)
            outgoing_remote_call(success=True)
            outgoing_remote_call(success=False)

        # Now the asynchronous execution starts. So we create an in-process tracer. We're using
        # the in-process link which we've created above. This link specifies where the traced
        # actions below will show up in the path.
        with sdk.trace_in_process_link(link):
            outgoing_remote_call(success=True)

        print('-main')
        input('Now wait until the path appears in the UI...')
    finally:
        shutdown_error = oneagent.shutdown()
        if shutdown_error:
            print('Error shutting down SDK:', shutdown_error)

if __name__ == '__main__':
    main()