import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='opd_admin',
        password='krithi_raj07',
        database='hospital_opd'
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")