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
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_message_ids(
        message_id TEXT PRIMARY KEY
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
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return lead.model_copy(update={'lead_id':new_id})

def get_all_leads_by_phone(phone: str) -> list[Lead]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM leads WHERE phone = ? ORDER BY created_at DESC
    """, (phone,))
    rows = cursor.fetchall()
    conn.close()

    leads = []
    for row in rows:
        leads.append(Lead(
            lead_id=row["lead_id"],
            phone=row["phone"],
            name=row["name"],
            category=row["category"],
            requirement=row["requirement"],
            location=row["location"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        ))
    return leads

def get_active_lead(phone: str) -> Lead | None:
    all_leads = get_all_leads_by_phone(phone)
    for lead in all_leads:
        if lead.status != LeadStatus.CLOSED:
            return lead
    return None
    
def update_lead_status(lead_id:int,new_status :LeadStatus):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""UPDATE leads SET STATUS = ? WHERE lead_id = ?""",(new_status.value,lead_id))
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

def mark_message_processed(message_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO processed_message_ids(message_id)
        VALUES(?)
    
    """,(message_id,))
    conn.commit()
    conn.close()

def has_processed_message(message_id: str)->bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT message_id from processed_message_ids WHERE message_id = ?""",(message_id,))
    row = cursor.fetchone()
    conn.close()

    return row is not None


def count_opt_in_sends_today()->int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as count FROM opt_in_status
        WHERE date(last_updated) = date('now')
    """)
    row = cursor.fetchone()
    conn.close()
    return row['count']



create_tables()