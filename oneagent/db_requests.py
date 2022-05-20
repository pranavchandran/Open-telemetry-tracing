"""
Create a common structure for database requests
sdk = oneagent.get_sdk() helps to get the SDK instance
"""
import oneagent
import pyodbc as pd

# Connect database with ip
# cnxn = pd.connect('DRIVER={SQL Server};SERVER=192.168.43.216,1433;DATABASE=Sample;UID=User1;PWD=Neepspranav12')

sdk = oneagent.get_sdk()

# Call for create a Database Request
# dbinfo = sdk.create_database_info(
#     'Sample', oneagent.sdk.DatabaseVendor.SQLSERVER,
#     oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, '169.254.149.39')
# )

# with sdk.trace_sql_database_request(dbinfo, 'select * from [dbo].Employees;') as tracer:
#     # Do actual DB request
    
#     tracer.set_rows_returned(42) # Optional
#     tracer.set_round_trip_count(3) # Optional
dbinfo = sdk.create_database_info(
    'Northwind', oneagent.sdk.DatabaseVendor.SQLSERVER,
    oneagent.sdk.Channel(oneagent.sdk.ChannelType.TCP_IP, '10.0.0.42:6666'))

def traced_db_operation(dbinfo, sql):
    print('+db', dbinfo, sql)
    with sdk.trace_sql_database_request(dbinfo, sql) as tracer:
        tracer.set_round_trip_count(3)
    


# This with-block will automatically free the database info handle
# at the end. Note that the handle is used for multiple tracers. In
# general, it is recommended to reuse database (and web application)
# info handles as often as possible (for efficiency reasons).
with dbinfo:
    traced_db_operation(
        dbinfo, "BEGIN TRAN;")
    traced_db_operation(
        dbinfo,
        "SELECT TOP 1 qux FROM baz ORDER BY quux;")
    traced_db_operation(
        dbinfo,
        "SELECT foo, bar FROM baz WHERE qux = 23")
    traced_db_operation(
        dbinfo,
        "UPDATE baz SET foo = foo + 1 WHERE qux = 23;")
    traced_db_operation(dbinfo, "COMMIT;")