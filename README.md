# MacBook Recommender

ระบบแนะนำ MacBook ให้นักศึกษาด้วย **Neo4j Aura + Streamlit** แปลงมาจากโน้ตบุ๊ก *ระบบแนะนำ Macbook*

```
(Student)-[:OWNS]->(MacBook)
(Student)-[:PEER_OF]-(Student)   -- สาขาเดียวกัน + ชั้นปีเดียวกัน
```

## แท็บในแอป
ภาพรวม · แนะนำ MacBook (Hybrid / เพื่อนร่วมสาขา+ชั้นปี / ทั้งสาขา + กรองงบ) · ค้นหา · 3D Showroom · จัดการข้อมูล (เพิ่ม / แก้ไข / ลบ) · กราฟ · ตั้งค่า

### จัดการข้อมูล (CRUD)
- **เพิ่ม**: นักศึกษา, MacBook, OWNS
- **แก้ไข**: ชื่อ/สาขา/ชั้นปีของนักศึกษา, สเปก/ราคาของ MacBook, เปลี่ยนรุ่นที่นักศึกษาใช้ (รหัสแก้ไม่ได้)
- **ลบ**: นักศึกษา, MacBook, OWNS รายการเดียว (ต้องติ๊กยืนยันก่อน) การลบนักศึกษา/MacBook จะลบความสัมพันธ์ที่เกี่ยวข้องด้วย
- แก้สาขา/ชั้นปีแล้วระบบคำนวณ `PEER_OF` ใหม่ให้อัตโนมัติ

Hybrid score = `peer×3 + คนสาขาเดียวกัน×2 + ความนิยมทั้งระบบ×0.5` (heuristic เพื่อการเรียนการสอน)

## โครงสร้างไฟล์
```
app.py              UI (Streamlit)
neo4j_service.py    ชั้นเชื่อมต่อ/คิวรีฐานข้อมูล
seed_data.py        ข้อมูลตัวอย่างจากโน้ตบุ๊ก
cypher/schema.cypher
requirements.txt
.streamlit/config.toml            ธีมมืด
.streamlit/secrets.toml.example   ตัวอย่าง secrets (ไฟล์จริงห้าม commit)
```

## รันในเครื่อง
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # แล้วใส่รหัสผ่านจริง
streamlit run app.py
```

## อัปขึ้น GitHub
1. สร้าง repository ใหม่ที่ github.com (เช่น `macbook-recommender`) ไม่ต้องติ๊กสร้าง README
2. ในโฟลเดอร์โปรเจกต์:
```bash
git init
git add .
git commit -m "MacBook Recommender"
git branch -M main
git remote add origin https://github.com/<USERNAME>/macbook-recommender.git
git push -u origin main
```
`.gitignore` กันไฟล์ `secrets.toml` ไว้แล้ว ตรวจให้แน่ใจว่าไม่มีรหัสผ่านใน repo

## Deploy บน Streamlit Community Cloud
1. เข้า https://share.streamlit.io แล้วล็อกอินด้วย GitHub
2. กด **Create app** → เลือก repo `macbook-recommender`, branch `main`, Main file path = `app.py`
3. เปิด **Advanced settings → Secrets** แล้ววาง
```toml
[neo4j]
uri = "neo4j+s://477ddcbe.databases.neo4j.io"
username = "477ddcbe"
password = "รหัสผ่าน Aura ของคุณ"
database = "477ddcbe"
```
4. กด **Deploy** แล้วเปิดแอป ไปแท็บ **จัดการข้อมูล** → กด **สร้าง Constraint + Demo Data** ครั้งแรก

## หมายเหตุ
- Aura Free จะถูก pause เมื่อไม่ได้ใช้งานนาน ให้เข้า console.neo4j.io กด Resume ก่อน
- ในโน้ตบุ๊กเดิม การแนะนำแบบ peer ได้ผลลัพธ์ว่างกับนักศึกษาส่วนใหญ่ เพราะมีแค่ 2 คู่ที่สาขา+ชั้นปีตรงกัน
  (U003/U004 และ U009/U010) แอปนี้จึงเพิ่มโหมด Hybrid และ ทั้งสาขา เป็นทางเลือก
