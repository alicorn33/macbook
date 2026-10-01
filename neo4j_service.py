"""ชั้นเชื่อมต่อ Neo4j แยกจาก UI (อ่าน credential จาก st.secrets เท่านั้น)"""
import streamlit as st
from neo4j import GraphDatabase

from seed_data import MACBOOKS, OWNS, STUDENTS


@st.cache_resource(show_spinner=False)
def get_driver():
    cfg = st.secrets["neo4j"]
    driver = GraphDatabase.driver(cfg["uri"], auth=(cfg["username"], cfg["password"]))
    driver.verify_connectivity()
    return driver


def _database():
    return st.secrets["neo4j"].get("database") or None


@st.cache_data(ttl=60, show_spinner=False)
def _read(query, params):
    res = get_driver().execute_query(query, parameters_=dict(params), database_=_database())
    return [r.data() for r in res.records]


def read(query, **params):
    return _read(query, tuple(sorted(params.items())))


def write(query, **params):
    get_driver().execute_query(query, parameters_=params, database_=_database())
    st.cache_data.clear()


def setup_schema():
    write("CREATE CONSTRAINT student_id_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE")
    write("CREATE CONSTRAINT macbook_id_unique IF NOT EXISTS FOR (m:MacBook) REQUIRE m.macbook_id IS UNIQUE")


def refresh_peers():
    """สร้าง PEER_OF ใหม่ทั้งหมด (ลบของเก่าก่อน เพื่อให้ถูกต้องหลังแก้ไข/ลบนักศึกษา)"""
    write("MATCH ()-[p:PEER_OF]->() DELETE p")
    write("""
    MATCH (a:Student), (b:Student)
    WHERE a.student_id <> b.student_id AND a.major = b.major AND a.year = b.year
    MERGE (a)-[:PEER_OF]->(b)
    """)


def add_student(student_id, name, major, year):
    write("MERGE (s:Student {student_id:$id}) SET s.name=$name, s.major=$major, s.year=$year",
          id=student_id, name=name, major=major, year=year)
    refresh_peers()


def add_macbook(m):
    write("""
    MERGE (m:MacBook {macbook_id:$macbook_id})
    SET m.model=$model, m.chip=$chip, m.ram_gb=$ram_gb, m.storage_gb=$storage_gb,
        m.price_thb=$price_thb, m.suited_for=$suited_for
    """, **m)


def add_owns(student_id, macbook_id):
    write("""
    MATCH (s:Student {student_id:$sid}), (m:MacBook {macbook_id:$mid})
    MERGE (s)-[:OWNS]->(m)
    """, sid=student_id, mid=macbook_id)


# ---------- แก้ไข ----------
def update_student(student_id, name, major, year):
    write("MATCH (s:Student {student_id:$id}) SET s.name=$name, s.major=$major, s.year=$year",
          id=student_id, name=name, major=major, year=year)
    refresh_peers()  # สาขา/ชั้นปีอาจเปลี่ยน -> คำนวณ PEER_OF ใหม่


def update_macbook(m):
    write("""
    MATCH (m:MacBook {macbook_id:$macbook_id})
    SET m.model=$model, m.chip=$chip, m.ram_gb=$ram_gb, m.storage_gb=$storage_gb,
        m.price_thb=$price_thb, m.suited_for=$suited_for
    """, **m)


def change_owns(student_id, old_macbook_id, new_macbook_id):
    """เปลี่ยนรุ่นที่นักศึกษาใช้ (ย้าย OWNS จากรุ่นเก่าไปรุ่นใหม่)"""
    if old_macbook_id == new_macbook_id:
        return
    write("""
    MATCH (s:Student {student_id:$sid})-[o:OWNS]->(:MacBook {macbook_id:$old})
    MATCH (n:MacBook {macbook_id:$new})
    DELETE o
    MERGE (s)-[:OWNS]->(n)
    """, sid=student_id, old=old_macbook_id, new=new_macbook_id)


# ---------- ลบ ----------
def delete_student(student_id):
    write("MATCH (s:Student {student_id:$id}) DETACH DELETE s", id=student_id)
    # PEER_OF ของคนนี้ถูกลบไปกับ DETACH DELETE แล้ว ไม่ต้องคำนวณใหม่


def delete_macbook(macbook_id):
    write("MATCH (m:MacBook {macbook_id:$id}) DETACH DELETE m", id=macbook_id)


def delete_owns(student_id, macbook_id):
    write("MATCH (:Student {student_id:$sid})-[o:OWNS]->(:MacBook {macbook_id:$mid}) DELETE o",
          sid=student_id, mid=macbook_id)


def seed_demo():
    setup_schema()
    write("""
    UNWIND $rows AS r MERGE (s:Student {student_id:r.student_id})
    SET s.name=r.name, s.major=r.major, s.year=r.year
    """, rows=STUDENTS)
    write("""
    UNWIND $rows AS r MERGE (m:MacBook {macbook_id:r.macbook_id})
    SET m.model=r.model, m.chip=r.chip, m.ram_gb=r.ram_gb, m.storage_gb=r.storage_gb,
        m.price_thb=r.price_thb, m.suited_for=r.suited_for
    """, rows=MACBOOKS)
    write("""
    UNWIND $rows AS r
    MATCH (s:Student {student_id:r.s}), (m:MacBook {macbook_id:r.m})
    MERGE (s)-[:OWNS]->(m)
    """, rows=[{"s": s, "m": m} for s, m in OWNS])
    refresh_peers()


def clear_all():
    write("MATCH (n) WHERE n:Student OR n:MacBook DETACH DELETE n")
