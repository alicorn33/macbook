STUDENTS = [
    {"student_id": "U001", "name": "Meow",    "major": "วิทยาการคอมพิวเตอร์", "year": 1},
    {"student_id": "U002", "name": "Dum",     "major": "วิทยาการคอมพิวเตอร์", "year": 2},
    {"student_id": "U003", "name": "Frog",    "major": "วิศวกรรมซอฟต์แวร์",   "year": 3},
    {"student_id": "U004", "name": "Fish",    "major": "วิศวกรรมซอฟต์แวร์",   "year": 3},
    {"student_id": "U005", "name": "Alex",    "major": "การออกแบบกราฟิก",     "year": 4},
    {"student_id": "U006", "name": "Bob",     "major": "การออกแบบกราฟิก",     "year": 1},
    {"student_id": "U007", "name": "Charlie", "major": "บริหารธุรกิจ",        "year": 2},
    {"student_id": "U008", "name": "Daisy",   "major": "บริหารธุรกิจ",        "year": 4},
    {"student_id": "U009", "name": "Ethan",   "major": "สถาปัตยกรรมศาสตร์",   "year": 3},
    {"student_id": "U010", "name": "Fiona",   "major": "สถาปัตยกรรมศาสตร์",   "year": 3},
]

# ราคาเป็นราคาตัวอย่างเพื่อการเรียนรู้เท่านั้น
MACBOOKS = [
    {"macbook_id": "M001", "model": "MacBook Air M1",     "chip": "M1",     "ram_gb": 8,  "storage_gb": 256,  "price_thb": 29900,  "suited_for": "งานเอกสารทั่วไป / เรียนออนไลน์"},
    {"macbook_id": "M002", "model": "MacBook Air M2",     "chip": "M2",     "ram_gb": 8,  "storage_gb": 256,  "price_thb": 36900,  "suited_for": "งานเอกสารทั่วไป / เขียนโค้ดเบื้องต้น"},
    {"macbook_id": "M003", "model": "MacBook Air M3",     "chip": "M3",     "ram_gb": 8,  "storage_gb": 256,  "price_thb": 39900,  "suited_for": "งานเอกสารทั่วไป / เขียนโค้ด"},
    {"macbook_id": "M004", "model": "MacBook Pro M1 Pro", "chip": "M1 Pro", "ram_gb": 16, "storage_gb": 512,  "price_thb": 59900,  "suited_for": "ตัดต่อวิดีโอเบื้องต้น / เขียนโปรแกรม"},
    {"macbook_id": "M005", "model": "MacBook Pro M2 Pro", "chip": "M2 Pro", "ram_gb": 16, "storage_gb": 512,  "price_thb": 65900,  "suited_for": "ตัดต่อวิดีโอ / พัฒนาแอปพลิเคชัน"},
    {"macbook_id": "M006", "model": "MacBook Pro M2 Max", "chip": "M2 Max", "ram_gb": 32, "storage_gb": 1024, "price_thb": 89900,  "suited_for": "ออกแบบกราฟิก 3D / ตัดต่อวิดีโอระดับสูง"},
    {"macbook_id": "M007", "model": "MacBook Pro M3",     "chip": "M3",     "ram_gb": 8,  "storage_gb": 512,  "price_thb": 62900,  "suited_for": "เขียนโปรแกรม / งานทั่วไป"},
    {"macbook_id": "M008", "model": "MacBook Pro M3 Pro", "chip": "M3 Pro", "ram_gb": 18, "storage_gb": 512,  "price_thb": 79900,  "suited_for": "ตัดต่อวิดีโอ / งานสถาปัตยกรรม (CAD เบื้องต้น)"},
    {"macbook_id": "M009", "model": "MacBook Pro M3 Max", "chip": "M3 Max", "ram_gb": 36, "storage_gb": 1024, "price_thb": 109900, "suited_for": "ออกแบบกราฟิก 3D / CAD / Rendering"},
    {"macbook_id": "M010", "model": "MacBook Pro M4",     "chip": "M4",     "ram_gb": 16, "storage_gb": 512,  "price_thb": 72900,  "suited_for": "เขียนโปรแกรม / งาน AI เบื้องต้น"},
]

OWNS = [
    ("U001", "M001"), ("U001", "M002"), ("U002", "M003"), ("U002", "M007"),
    ("U003", "M008"), ("U003", "M009"), ("U004", "M008"), ("U004", "M010"),
    ("U005", "M006"), ("U005", "M009"), ("U006", "M002"), ("U006", "M003"),
    ("U007", "M003"), ("U007", "M007"), ("U007", "M008"), ("U008", "M009"),
    ("U008", "M010"), ("U009", "M004"), ("U009", "M005"), ("U010", "M005"),
    ("U010", "M008"),
]
