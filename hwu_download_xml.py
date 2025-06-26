#pip install pyodbc
import pyodbc
import os

#export SQL_USERNAME='your_username'
#export SQL_PASSWORD='your_password'
username = os.environ.get('SQL_USERNAME')
password = os.environ.get('SQL_PASSWORD')

if not username or not password:
    raise ValueError("SQL_USERNAME and SQL_PASSWORD environment variables must be set.")

server = 'db.epic.netapp.com'
database = 'DHWU2.0'
platform_ids = [2032, 5265148, 13684325, 30310846, 31745792, 32834061] #ADD your platform IDs here
#    2032': 'fas','5265148': 'aff-a-series','13684325': 'asa-aff-a-series', '30310846': 'aff-c-series','31745792': 'asa-a-series','32834061': 'asa-c-series'

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
)

with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    for platform_id in platform_ids:
        cursor.execute("""
            DECLARE @techSpecXML xml;
            EXEC hwu_getTechSpecs @platformTypeId=?, @techSpecXML=@techSpecXML OUTPUT;
            SELECT @techSpecXML AS techSpecXML;
        """, platform_id)
        # Skip result sets until we find one with XML (should be the second result set)
        xml_data = None
        while True:
            if cursor.description:
                row = cursor.fetchone()
                if row and row[0] and str(row[0]).strip().startswith('<'):
                    xml_data = row[0]
                    break
            if not cursor.nextset():
                break
        if xml_data:
            print(f"Returned XML for platform {platform_id}:\n{xml_data}\n---")
            with open(f"techspec_{platform_id}.xml", "w", encoding="utf-8") as f:
                f.write(str(xml_data))
            print(f"Saved XML for platform {platform_id}")
        else:
            print(f"No XML returned for platform {platform_id}")