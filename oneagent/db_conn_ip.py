import pyodbc as pd

# Connect database with ip
cnxn = pd.connect('DRIVER={SQL Server};SERVER=192.168.43.216,1433;DATABASE=Sample;UID=User1;PWD=Neepspranav12')
cursor = cnxn.cursor()
cursor.execute('SELECT * FROM [dbo].[Employees]')
row = cursor.fetchone()
while row:
    print(row)
    row = cursor.fetchone()