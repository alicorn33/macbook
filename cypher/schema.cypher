CREATE CONSTRAINT student_id_unique IF NOT EXISTS
FOR (s:Student) REQUIRE s.student_id IS UNIQUE;

CREATE CONSTRAINT macbook_id_unique IF NOT EXISTS
FOR (m:MacBook) REQUIRE m.macbook_id IS UNIQUE;

// เพื่อนร่วมสาขา + ชั้นปีเดียวกัน
MATCH (a:Student), (b:Student)
WHERE a.student_id <> b.student_id AND a.major = b.major AND a.year = b.year
MERGE (a)-[:PEER_OF]->(b);

// แนะนำตาม peer (ตัวอย่าง)
MATCH (me:Student {student_id:"U003"})-[:PEER_OF]-(peer:Student)-[:OWNS]->(m:MacBook)
WHERE NOT EXISTS { MATCH (me)-[:OWNS]->(m) }
RETURN m.model AS recommendation, count(DISTINCT peer) AS score
ORDER BY score DESC;
