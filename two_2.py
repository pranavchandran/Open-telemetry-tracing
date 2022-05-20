'''This example demonstrates instrumenting a (mocked) application that executes
a remote call that sometimes fails and does some database operations.'''

from __future__ import print_function # Python 2 compatibility.

import threading

import oneagent # SDK initialization functions
import oneagent.sdk as onesdk # All other SDK functions.

from oneagent.common import MessagingDestinationType

IN_DEV_ENVIRONMENT = True # Let's assume we are *not* in production here...
getsdk = oneagent.get_sdk # Just to make the code shorter.


def mock_incoming_web_request():
    sdk = getsdk()
    wappinfo = sdk.create_web_application_info(
        virtual_host='example.com', # Logical name of the host server.
        application_id='MyPythonapplication', # Unique web application ID.
        context_root='/my-web-app/') # App's prefix of the path part of the URL.

    with wappinfo:
        wreq = sdk.trace_incoming_web_request(
            wappinfo,
            'http://example.com/my-web-app/foo?bar=baz',
            'GET',
            headers={'Host': 'example.com', 'X-foo': 'bar'},
            remote_address='127.0.0.1:12345')
        with wreq:
            print('+web request')
            wreq.add_parameter('my_form_field', '1234')
            # Process web request
            wreq.add_response_headers({'Content-Length': '1234'})
            wreq.set_status_code(200) # OK
            sdk.add_custom_request_attribute('custom int attribute', 42)
            sdk.add_custom_request_attribute('custom float attribute', 1.778)
            sdk.add_custom_request_attribute('custom string attribute', 'snow is falling')
            sdk.add_custom_request_attribute('another key', None)

mock_incoming_web_request()