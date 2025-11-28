import sqlite3
from datetime import datetime
import json

DB_PATH = 'candidates.db'

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            raw_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_name ON candidates(name)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_email ON candidates(email)
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def insert_candidate(data):
    """Insert a candidate into the database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO candidates (name, email, phone, skills, education, experience, raw_text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('name', 'Unknown'),
        data.get('email', ''),
        data.get('phone', ''),
        json.dumps(data.get('skills', [])),
        json.dumps(data.get('education', [])),
        json.dumps(data.get('experience', [])),
        data.get('raw_text', '')
    ))
    
    conn.commit()
    candidate_id = cursor.lastrowid
    conn.close()
    
    return candidate_id

def search_candidates(skill=None, name=None):
    """Search candidates by skill or name"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM candidates WHERE 1=1'
    params = []
    
    if skill:
        query += ' AND LOWER(skills) LIKE ?'
        params.append(f'%{skill.lower()}%')
    
    if name:
        query += ' AND LOWER(name) LIKE ?'
        params.append(f'%{name.lower()}%')
    
    query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    candidates = []
    for row in rows:
        candidates.append({
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'phone': row['phone'],
            'skills': json.loads(row['skills']) if row['skills'] else [],
            'education': json.loads(row['education']) if row['education'] else [],
            'experience': json.loads(row['experience']) if row['experience'] else [],
            'created_at': row['created_at']
        })
    
    return candidates

def get_all_candidates():
    """Get all candidates"""
    return search_candidates()

def get_candidate_by_id(candidate_id):
    """Get a specific candidate by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'phone': row['phone'],
            'skills': json.loads(row['skills']) if row['skills'] else [],
            'education': json.loads(row['education']) if row['education'] else [],
            'experience': json.loads(row['experience']) if row['experience'] else [],
            'created_at': row['created_at']
        }
    return None

def delete_candidate(candidate_id):
    """Delete a candidate by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM candidates WHERE id = ?', (candidate_id,))
    conn.commit()
    conn.close()
