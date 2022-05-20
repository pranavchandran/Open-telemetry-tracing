# -*- coding: utf-8 -*-
#
# Copyright 2018 Dynatrace LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Checking the Traces
'''

from __future__ import print_function # Python 2 compatibility.
import threading
import oneagent # SDK initialization functions
import oneagent.sdk as onesdk # All other SDK functions.
from oneagent.common import MessagingDestinationType
import pandas as pd
import pyodbc

IN_DEV_ENVIRONMENT = True # Let's assume we are *not* in production here...
getsdk = oneagent.get_sdk # Just to make the code shorter.


def traced_db_operation(dbinfo, sql):
    print('+db', dbinfo, sql)

    # Entering the with block automatically start the tracer.
    with getsdk().trace_sql_database_request(dbinfo, sql) as tracer:
        sql = tracer.sql
        # connect to the database
        conn = pyodbc.connect('DRIVER={SQL Server};SERVER=LAPTOP-NRPENFG5\SQLEXPRESS;DATABASE=Sample;')
        cursor = conn.cursor()
        ans = cursor.execute('select * from dbo.tblEmployee')
        
         # setter available on a tracer (as opposed to an optional parameter to a
        # trace_* function), it may be called anytime between creating and
        # ending the tracer (i.e. also after starting it).
        if ans:
            tracer.exit_message = 'Success'
            tracer.exit_status = onesdk.ExitStatus.SUCCESS
        else:
            tracer.exit_message = 'Failure'
            tracer.exit_status = onesdk.ExitStatus.FAILURE
    print('-db', dbinfo, sql)


# def mock_custom_service():
#     sdk = getsdk()

#     with sdk.trace_custom_service('Pranav', 'Pranav Chandran'):
#         print('do some fancy stuff')
        
def do_remote_call(strtag, success):
    print('+remote call')
    print('strtag:', strtag)
    print('success:', success)
    print('-remote call')

def outgoing_remote_call(success):
    print('+remote')

    # We use positional arguments to specify required values and named arguments
    # to specify optional values.
    call = getsdk().trace_outgoing_remote_call(
        'Mynewmethod', 'caller', 'dupypr://localhost/dummyEndpoint',
        onesdk.Channel(onesdk.ChannelType.IN_PROCESS, 'localhost'),
        protocol_name='DUMMY_PROTOCOL')
    try:
        with call:
            # Note that this property can only be accessed after starting the
            # tracer. See the documentation on tagging for more information.
            strtag = call.outgoing_dynatrace_string_tag
            do_remote_call(strtag, success)
            
    except RuntimeError: # Swallow the exception raised above.
        pass
    print('-remote')
    
def do_remote_call_thread_func(strtag, success):
    try:
        print('+thread')
        # We use positional arguments to specify required values and named
        # arguments to specify optional values.
        incall = getsdk().trace_incoming_remote_call(
            'Mynewmethod', 'caller',
            'dupypr://localhost/dummyEndpoint',
            protocol_name='DUMMY_PROTOCOL', str_tag=strtag)
        with incall:
            if not success:
                raise RuntimeError('Remote call failed on the server side.')
            dbinfo = getsdk().create_database_info(
                'Northwind', onesdk.DatabaseVendor.SQLSERVER,
                onesdk.Channel(onesdk.ChannelType.TCP_IP, '10.0.0.42:6666'))
            print('+db')
            traced_db_operation(dbinfo, 'select * from dbo.tblEmployee')
            print('-db')
    except RuntimeError:
        # Swallow the exception raised above.
        pass

def main():
    print('+main')
    sdk_options = oneagent.sdkopts_from_commandline(remove=True)
    init_result = oneagent.initialize(sdk_options)
    try:
        if init_result.error is not None:
            print('Error during SDK initialization:', init_result.error)
        sdk = getsdk()
        print('Agent state:', sdk.agent_state)
        # The instance attribute 'agent_found' indicates whether an agent could be found or not.
        print('Agent found:', sdk.agent_found)
        # If an agent was found but it is incompatible with this version of the SDK for Python
        # then 'agent_is_compatible' would be set to false.
        print('Agent is compatible:', sdk.agent_is_compatible)
        # The agent version is a string holding both the OneAgent version and the
        # OneAgent SDK for C/C++ version separated by a '/'.
        print('Agent version:', sdk.agent_version_string)
        # with sdk.trace_incoming_remote_call('main', 'main', 'main'):
        #     link = sdk.create_in_process_link()
        traced_db_operation('Northwind', "BEGIN TRAN;")
        # mock_custom_service()
    except Exception as e:
        print('Exception during SDK initialization:', e)

if __name__ == '__main__':
    main()
