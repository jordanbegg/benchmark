import urllib.parse
import pyodbc
from sqlmodel import create_engine


connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:benchmark-db-server-dev.database.windows.net,1433;Database=benchmark-database;Uid=benchmarkadmin;Pwd=GymBro95$;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
encoded_connection_string = urllib.parse.quote_plus(connection_string)
sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={encoded_connection_string}"
print(sqlalchemy_url)

engine_azure = create_engine(sqlalchemy_url,echo=True, connect_args={"check_same_thread": False})

print('connection is ok')