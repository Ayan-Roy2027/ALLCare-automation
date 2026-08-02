import sqlite3
from pathlib import Path
from app.models.schemas import Lead,LeadStatus,OptInRecord,OptInStatus
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent/"allcare.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads(
        phone TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        requirement TEXT,
        location Text,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opt_in_status(
        phone TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        last_updated TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def insert_lead(lead: Lead):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads(phone,name,category,requirement,location,status,created_at)
        VALUES(?,?,?,?,?,?,?)""",
        (lead.phone,lead.name,lead.category,lead.requirement,lead.location,lead.status.value,lead.created_at.isoformat()
        ))

    conn.commit()
    conn.close()


def get_lead_by_phone(phone:str) -> Lead | None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM leads WHERE phone = ?""",(phone,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None
    
    return Lead(
        phone = row['phone'],
        name = row['name'],
        category = row['category'],
        requirement = row['requirement'],
        location = row['location'],
        status = row['status'],
        created_at =datetime.fromisoformat(row['created_at'])
        )

def update_lead_status(phone:str,new_status :LeadStatus):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""UPDATE leads SET STATUS = ? WHERE PHONE = ?""",(new_status.value,phone))
    conn.commit()
    conn.close()

def insert_opt_in_record(record : OptInRecord):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO opt_in_status(phone,status,last_updated)
    VALUES(?,?,?)
    """,(record.phone,record.status.value,record.last_updated.isoformat()))
    conn.commit()
    conn.close()

def get_opt_in_status(phone:str) -> OptInRecord | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM opt_in_status WHERE phone = ?""",(phone,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None
    
    return OptInRecord(
        phone = row['phone'],
        status = row['status'],
        last_updated = datetime.fromisoformat(row['last_updated'])
    )

def update_opt_in_status(phone:str,new_status: OptInStatus):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE opt_in_status SET status = ? WHERE phone = ?""",(new_status.value,phone)
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":

    create_tables()

    print("--- Test 1: insert and read a lead ---")
    test_lead = Lead(
        phone="919876543210",
        name="Amit",
        category="CCTV & Security Systems",
        requirement="4-camera setup",
        location="Garia",
    )
    insert_lead(test_lead)
    print('Lead inserted')
    fetched_lead = get_lead_by_phone("919876543210")
    print(fetched_lead)
    print(fetched_lead.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    assert fetched_lead is not None
    assert fetched_lead.name == "Amit"
    assert fetched_lead.status == LeadStatus.NEW
    print("PASSED\n")

    print("--- Test 2: update lead status ---")
    update_lead_status("919876543210", LeadStatus.BOT_ENGAGED)
    updated_lead = get_lead_by_phone("919876543210")
    print(updated_lead)
    assert updated_lead.status == LeadStatus.BOT_ENGAGED
    print("PASSED\n")

    print("--- Test 3: insert and read an opt-in record ---")
    test_record = OptInRecord(phone="919876543210")
    insert_opt_in_record(test_record)
    fetched_record = get_opt_in_status("919876543210")
    print(fetched_record)
    assert fetched_record is not None
    assert fetched_record.status == OptInStatus.NOT_CONTACTED
    print("PASSED\n")

    print("--- Test 4: update opt-in status ---")
    update_opt_in_status("919876543210", OptInStatus.OPTED_IN)
    updated_record = get_opt_in_status("919876543210")
    print(updated_record)
    assert updated_record.status == OptInStatus.OPTED_IN
    print("PASSED\n")

    print("All local_store tests passed.")