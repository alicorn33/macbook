import json
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import neo4j_service as db

st.set_page_config(page_title="MacBook Recommender", page_icon="💻", layout="wide")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&display=swap');
html, body, .stApp, [class*="st-"] {font-family:'Prompt',sans-serif;}
.stApp{background:radial-gradient(1100px 560px at 8% -8%,rgba(56,189,248,.20),transparent 60%),
radial-gradient(900px 500px at 100% 0%,rgba(167,139,250,.18),transparent 55%),#0a0f1c;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1180px;padding-top:2rem;}
.eyebrow{letter-spacing:.25em;font-size:.72rem;color:#38bdf8;font-weight:600;}
.hero h1{font-size:3.6rem;font-weight:700;margin:.2rem 0 .3rem;line-height:1.1;}
.grad{background:linear-gradient(90deg,#38bdf8,#a78bfa,#f472b6);-webkit-background-clip:text;background-clip:text;color:transparent;}
.sub{color:#94a3b8;max-width:640px;}
.tag{display:inline-block;margin:.6rem .4rem 0 0;padding:.25rem .8rem;border:1px solid rgba(255,255,255,.14);
border-radius:999px;font-family:monospace;font-size:.78rem;color:#cbd5e1;background:rgba(255,255,255,.03);}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
border-radius:16px;padding:6px;backdrop-filter:blur(12px);}
.stTabs [data-baseweb="tab"]{border-radius:10px;padding:8px 14px;height:auto;}
.stTabs [aria-selected="true"]{background:rgba(56,189,248,.18);}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none;}
.card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:18px;padding:14px;
backdrop-filter:blur(14px);margin-bottom:14px;}
.thumb{background:rgba(15,23,42,.65);border-radius:12px;padding:8px;margin-bottom:10px;}
.ttl{font-weight:600;font-size:1.02rem;}
.meta{color:#94a3b8;font-size:.85rem;}
.price{color:#38bdf8;font-weight:600;margin:.2rem 0;}
.reason{font-size:.82rem;color:#cbd5e1;margin-top:.15rem;}
.rank{display:inline-block;background:linear-gradient(90deg,#38bdf8,#a78bfa);color:#0a0f1c;font-weight:700;
border-radius:8px;padding:0 .55rem;margin-bottom:.4rem;font-size:.85rem;}
[data-testid="stMetric"]{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);
border-radius:16px;padding:14px 18px;}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ---------- เชื่อมต่อฐานข้อมูล ----------
try:
    db.get_driver()
except Exception as e:
    st.error(f"เชื่อมต่อ Neo4j ไม่สำเร็จ ({type(e).__name__}) ตรวจ secrets [neo4j] แล้วลองใหม่ "
             "ถ้าใช้ Aura Free ให้เปิด instance ที่ถูก pause ก่อน")
    st.code('[neo4j]\nuri = "neo4j+s://xxxx.databases.neo4j.io"\nusername = "neo4j"\n'
            'password = "YOUR_PASSWORD"\ndatabase = "neo4j"', language="toml")
    st.stop()

st.markdown(
    '<div class="hero"><div class="eyebrow">GRAPH-POWERED RECOMMENDATION · NEO4J</div>'
    '<h1>MacBook <span class="grad">Recommender</span></h1>'
    '<div class="sub">ระบบแนะนำ MacBook ด้วย Graph Database ดูว่าเพื่อนร่วมสาขาและชั้นปีเดียวกับคุณใช้รุ่นไหน '
    'แล้วแนะนำรุ่นที่คุณยังไม่มี</div>'
    '<span class="tag">(Student)-[:OWNS]-&gt;(MacBook)</span>'
    '<span class="tag">(Student)-[:PEER_OF]-(Student)</span><span class="tag">Neo4j Aura</span></div>',
    unsafe_allow_html=True)
st.write("")

# ---------- ข้อมูลหลัก ----------
students = db.read("MATCH (s:Student) RETURN s.student_id AS id, s.name AS name, s.major AS major, s.year AS year ORDER BY id")
macbooks = db.read("""
MATCH (m:MacBook) OPTIONAL MATCH (s:Student)-[:OWNS]->(m)
RETURN m.macbook_id AS macbook_id, m.model AS model, m.chip AS chip, m.ram_gb AS ram_gb,
       m.storage_gb AS storage_gb, m.price_thb AS price_thb, m.suited_for AS suited_for, count(s) AS owners
ORDER BY owners DESC, price_thb""")


def laptop_svg(model, chip):
    c = "#6b7280" if "Pro" in model and "Max" not in chip else "#cbd5e1"
    if "Max" in chip:
        c = "#3b4252"
    return (f'<svg viewBox="0 0 200 120" width="100%" height="105">'
            f'<rect x="32" y="10" width="136" height="88" rx="8" fill="{c}" stroke="#94a3b8"/>'
            f'<rect x="38" y="16" width="124" height="76" rx="4" fill="#0f172a"/>'
            f'<text x="100" y="62" text-anchor="middle" fill="#38bdf8" font-size="19" font-weight="700" '
            f'font-family="sans-serif">{chip}</text>'
            f'<path d="M8 102h184l-10 10H18z" fill="{c}" stroke="#94a3b8"/></svg>')


def mac_card(m, extra=""):
    return (f'<div class="card"><div class="thumb">{laptop_svg(m["model"], m["chip"])}</div>'
            f'<div class="ttl">{m["model"]}</div>'
            f'<div class="meta">{m["chip"]} · RAM {m["ram_gb"]}GB · {m["storage_gb"]}GB</div>'
            f'<div class="price">฿{m["price_thb"]:,}</div><div class="meta">{m["suited_for"]}</div>{extra}</div>')


def grid(cards, n=4):
    for i in range(0, len(cards), n):
        for col, html in zip(st.columns(n), cards[i:i + n]):
            col.markdown(html, unsafe_allow_html=True)


tabs = st.tabs(["📊 ภาพรวม", "✨ แนะนำ MacBook", "🔎 ค้นหา", "🧊 3D Showroom",
                "🛠️ จัดการข้อมูล", "🕸️ กราฟ", "⚙️ ตั้งค่า"])
t_over, t_rec, t_search, t_3d, t_data, t_graph, t_set = tabs

# ---------- ภาพรวม ----------
with t_over:
    st.subheader("ภาพรวมระบบ")
    cnt = db.read("""
    CALL { MATCH (s:Student) RETURN count(s) AS students }
    CALL { MATCH (m:MacBook) RETURN count(m) AS macbooks }
    CALL { MATCH ()-[o:OWNS]->() RETURN count(o) AS owns }
    CALL { MATCH ()-[p:PEER_OF]->() RETURN count(p) AS peers }
    RETURN students, macbooks, owns, peers""")[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Students", cnt["students"])
    c2.metric("MacBooks", cnt["macbooks"])
    c3.metric("OWNS", cnt["owns"])
    c4.metric("PEER_OF (คู่)", cnt["peers"] // 2)
    if not macbooks:
        st.info("ยังไม่มีข้อมูลในฐานข้อมูล ไปที่แท็บ จัดการข้อมูล แล้วกด สร้าง Constraint + Demo Data")
    else:
        st.subheader("🏆 MacBook ยอดนิยม")
        grid([mac_card(m, f'<div class="meta">👥 {m["owners"]} คนใช้</div>') for m in macbooks[:4]])
        st.subheader("รุ่นที่ใช้ในแต่ละสาขา")
        rows = db.read("""
        MATCH (s:Student)-[:OWNS]->(m:MacBook)
        RETURN s.major AS major, m.model AS macbook, count(*) AS user_count
        ORDER BY major, user_count DESC, macbook""")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ---------- แนะนำ ----------
RECO_Q = """
MATCH (me:Student {student_id:$sid}), (m:MacBook)
WHERE NOT (me)-[:OWNS]->(m) AND m.price_thb <= $max_price
OPTIONAL MATCH (me)-[:PEER_OF]-(p:Student)-[:OWNS]->(m)
WITH me, m, count(DISTINCT p) AS peer
OPTIONAL MATCH (s:Student)-[:OWNS]->(m)
WHERE s.major = me.major AND s.student_id <> me.student_id
WITH me, m, peer, count(DISTINCT s) AS major_cnt
OPTIONAL MATCH (a:Student)-[:OWNS]->(m)
WHERE a.student_id <> me.student_id
RETURN m.macbook_id AS macbook_id, m.model AS model, m.chip AS chip, m.ram_gb AS ram_gb,
       m.storage_gb AS storage_gb, m.price_thb AS price_thb, m.suited_for AS suited_for,
       peer, major_cnt, count(DISTINCT a) AS pop
"""

with t_rec:
    if not students or not macbooks:
        st.info("ยังไม่มีข้อมูล ไปที่แท็บ จัดการข้อมูล เพื่อสร้างข้อมูลตัวอย่างก่อน")
    else:
        opts = {f'{s["id"]} — {s["name"]} ({s["major"]} ปี {s["year"]})': s for s in students}
        a, b, c = st.columns([2.2, 2.6, 1])
        me = opts[a.selectbox("เลือกนักศึกษา", list(opts))]
        mode = b.radio("วิธีแนะนำ", ["Hybrid", "เพื่อนร่วมสาขา+ชั้นปี", "ทั้งสาขา"], horizontal=True)
        k = c.slider("จำนวน", 1, 10, 4)
        budget = st.slider("งบสูงสุด (บาท)", 20000, 120000, 120000, 1000)

        owned = [m["model"] for m in db.read(
            "MATCH (:Student {student_id:$sid})-[:OWNS]->(m:MacBook) RETURN m.model AS model ORDER BY model",
            sid=me["id"])]
        st.caption(f'{me["name"]} ใช้อยู่: ' + (", ".join(owned) if owned else "ยังไม่มี"))

        rows = db.read(RECO_Q, sid=me["id"], max_price=budget)
        for r in rows:
            r["score"] = {"Hybrid": r["peer"] * 3 + r["major_cnt"] * 2 + r["pop"] * 0.5,
                          "เพื่อนร่วมสาขา+ชั้นปี": r["peer"], "ทั้งสาขา": r["major_cnt"]}[mode]
        rows = sorted([r for r in rows if r["score"] > 0], key=lambda r: (-r["score"], r["model"]))[:k]

        if not rows:
            st.warning("ไม่พบรุ่นที่แนะนำด้วยวิธีนี้ (อาจไม่มีเพื่อนร่วมสาขา+ชั้นปีในระบบ หรืองบต่ำเกินไป) "
                       "ลองเปลี่ยนเป็น Hybrid หรือ ทั้งสาขา")
        cards = []
        for i, r in enumerate(rows, 1):
            why = []
            if r["peer"]:
                why.append(f'👫 เพื่อนร่วมสาขา+ชั้นปี {r["peer"]} คนใช้รุ่นนี้')
            if r["major_cnt"]:
                why.append(f'🎓 คนสาขาเดียวกัน {r["major_cnt"]} คนใช้')
            if r["pop"]:
                why.append(f'🔥 ทั้งระบบมี {r["pop"]} คนใช้')
            extra = f'<div class="rank">#{i} · คะแนน {r["score"]:g}</div>'.replace('class="rank">', 'class="rank">', 1)
            body = "".join(f'<div class="reason">{w}</div>' for w in why)
            cards.append(mac_card(r, extra=body).replace('<div class="thumb">', extra + '<div class="thumb">', 1))
        grid(cards)
        st.caption("Hybrid score = peer×3 + คนสาขาเดียวกัน×2 + ความนิยมทั้งระบบ×0.5 "
                   "(heuristic เพื่อการเรียนการสอน ไม่ใช่โมเดล ML)")
        with st.expander("ดู Cypher ที่ใช้"):
            st.code(RECO_Q, language="cypher")

# ---------- ค้นหา ----------
with t_search:
    q = st.text_input("ค้นหารุ่น / ชิป / งานที่เหมาะ", placeholder="เช่น Max, ตัดต่อวิดีโอ, เขียนโปรแกรม")
    f1, f2 = st.columns(2)
    max_p = f1.slider("ราคาไม่เกิน (บาท)", 20000, 120000, 120000, 1000, key="sp")
    min_ram = f2.select_slider("RAM อย่างน้อย (GB)", [8, 16, 18, 32, 36], value=8)
    found = db.read("""
    MATCH (m:MacBook)
    WHERE ($q = '' OR toLower(m.model) CONTAINS toLower($q) OR toLower(m.chip) CONTAINS toLower($q)
           OR toLower(m.suited_for) CONTAINS toLower($q))
      AND m.price_thb <= $max_price AND m.ram_gb >= $min_ram
    OPTIONAL MATCH (s:Student)-[:OWNS]->(m)
    RETURN m.macbook_id AS macbook_id, m.model AS model, m.chip AS chip, m.ram_gb AS ram_gb,
           m.storage_gb AS storage_gb, m.price_thb AS price_thb, m.suited_for AS suited_for, count(s) AS owners
    ORDER BY owners DESC, price_thb""", q=q.strip(), max_price=max_p, min_ram=min_ram)
    st.caption(f"พบ {len(found)} รุ่น")
    grid([mac_card(m, f'<div class="meta">👥 {m["owners"]} คนใช้</div>') for m in found])

# ---------- 3D Showroom ----------
SHOWROOM = """
<div id="c" style="width:100%;height:420px"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const el=document.getElementById('c'),W=el.clientWidth||900,H=420;
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(40,W/H,0.1,100);cam.position.set(0,2.6,7.5);cam.lookAt(0,0.7,0);
const r=new THREE.WebGLRenderer({antialias:true,alpha:true});r.setSize(W,H);el.appendChild(r.domElement);
scene.add(new THREE.AmbientLight(0xffffff,0.75));
const d=new THREE.DirectionalLight(0xffffff,0.9);d.position.set(3,6,5);scene.add(d);
const mat=new THREE.MeshStandardMaterial({color:__COLOR__,metalness:0.8,roughness:0.35});
const g=new THREE.Group();
g.add(new THREE.Mesh(new THREE.BoxGeometry(3,0.12,2.1),mat));
const piv=new THREE.Group();piv.position.set(0,0.06,-1.05);piv.rotation.x=-0.28;g.add(piv);
const lid=new THREE.Mesh(new THREE.BoxGeometry(3,2,0.08),mat);lid.position.set(0,1,0);piv.add(lid);
const cv=document.createElement('canvas');cv.width=512;cv.height=330;const x=cv.getContext('2d');
const gr=x.createLinearGradient(0,0,512,330);gr.addColorStop(0,'#1e3a8a');gr.addColorStop(1,'#7c3aed');
x.fillStyle=gr;x.fillRect(0,0,512,330);x.fillStyle='#fff';x.font='bold 64px sans-serif';x.textAlign='center';
x.fillText(__CHIP__,256,190);
const scr=new THREE.Mesh(new THREE.PlaneGeometry(2.8,1.8),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(cv)}));
scr.position.set(0,1,0.045);piv.add(scr);
const kb=new THREE.Mesh(new THREE.PlaneGeometry(2.6,1.2),new THREE.MeshBasicMaterial({color:0x111827}));
kb.rotation.x=-Math.PI/2;kb.position.set(0,0.062,0.15);g.add(kb);
g.position.y=-0.3;scene.add(g);
(function a(){g.rotation.y+=0.008;r.render(scene,cam);requestAnimationFrame(a)})();
</script>"""

with t_3d:
    if not macbooks:
        st.info("ยังไม่มีข้อมูล MacBook")
    else:
        names = {m["model"]: m for m in macbooks}
        pick = names[st.selectbox("เลือกรุ่น", list(names))]
        color = "0x3b4252" if "Max" in pick["chip"] else "0x6b7280" if "Pro" in pick["model"] else "0xcbd5e1"
        components.html(SHOWROOM.replace("__COLOR__", color).replace("__CHIP__", json.dumps(pick["chip"])), height=430)
        st.markdown(mac_card(pick), unsafe_allow_html=True)

# ---------- จัดการข้อมูล (เพิ่ม / แก้ไข / ลบ) ----------
TH = timezone(timedelta(hours=7))


def K(name):
    """key ของ widget ที่เปลี่ยนทุกครั้งหลังทำรายการสำเร็จ -> ฟอร์มรีเซ็ตและดึงค่าล่าสุดจากฐานข้อมูล"""
    return f"{name}_{st.session_state.get('dm_n', 0)}"


def done(text, ok=True, focus=None):
    """บันทึกผลลัพธ์ แล้ว rerun เพื่อให้ตารางด้านบนอ่านข้อมูลสดจากฐานข้อมูลและแสดงผล"""
    st.session_state["dm_result"] = {"text": text, "ok": ok}
    st.session_state["dm_focus"] = focus
    log = st.session_state.setdefault("dm_log", [])
    log.insert(0, f"{datetime.now(TH):%H:%M:%S} · {'✅' if ok else '⚠️'} {text}")
    del log[15:]
    st.session_state["dm_n"] = st.session_state.get("dm_n", 0) + 1
    st.rerun()


def show_table(df, key_cols, focus):
    """แสดงตาราง และไฮไลต์แถวที่เพิ่งเพิ่ม/แก้ไข"""
    if df.empty:
        st.info("ยังไม่มีข้อมูลในตารางนี้")
        return

    def hl(row):
        hit = focus is not None and tuple(row[c] for c in key_cols) == tuple(focus)
        return ["background-color: rgba(56,189,248,.30)"] * len(row) if hit else [""] * len(row)

    st.dataframe(df.style.apply(hl, axis=1), use_container_width=True, hide_index=True)


# ข้อมูลสดสำหรับตารางในหน้านี้ (cache ถูกล้างทุกครั้งที่เขียน จึงตรงกับฐานข้อมูลเสมอ)
stu_rows = db.read("""MATCH (s:Student) OPTIONAL MATCH (s)-[:OWNS]->(m:MacBook)
RETURN s.student_id AS id, s.name AS name, s.major AS major, s.year AS year, collect(m.model) AS models
ORDER BY id""")
owns = db.read("""MATCH (s:Student)-[:OWNS]->(m:MacBook)
RETURN s.student_id AS sid, s.name AS sname, m.macbook_id AS mid, m.model AS model ORDER BY sid, mid""")
df_stu = pd.DataFrame([{"รหัส": r["id"], "ชื่อ": r["name"], "สาขา": r["major"], "ชั้นปี": r["year"],
                        "รุ่นที่ใช้": ", ".join(sorted(r["models"])) or "-"} for r in stu_rows],
                      columns=["รหัส", "ชื่อ", "สาขา", "ชั้นปี", "รุ่นที่ใช้"])
df_mac = pd.DataFrame([{"รหัสรุ่น": m["macbook_id"], "รุ่น": m["model"], "ชิป": m["chip"], "RAM (GB)": m["ram_gb"],
                        "Storage (GB)": m["storage_gb"], "ราคา (บาท)": m["price_thb"],
                        "เหมาะกับงาน": m["suited_for"], "จำนวนคนใช้": m["owners"]} for m in macbooks],
                      columns=["รหัสรุ่น", "รุ่น", "ชิป", "RAM (GB)", "Storage (GB)", "ราคา (บาท)",
                               "เหมาะกับงาน", "จำนวนคนใช้"]).sort_values("รหัสรุ่น")
df_own = pd.DataFrame([{"รหัสนักศึกษา": o["sid"], "ชื่อ": o["sname"], "รหัสรุ่น": o["mid"], "รุ่น": o["model"]}
                       for o in owns], columns=["รหัสนักศึกษา", "ชื่อ", "รหัสรุ่น", "รุ่น"])

with t_data:
    # ----- ผลลัพธ์ของการกระทำล่าสุด (อยู่บนสุดของหน้านี้) -----
    res = st.session_state.pop("dm_result", None)
    if res:
        (st.success if res["ok"] else st.warning)(res["text"])
        st.toast(res["text"], icon="✅" if res["ok"] else "⚠️")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Students", cnt["students"])
    m2.metric("MacBooks", cnt["macbooks"])
    m3.metric("OWNS", cnt["owns"])
    m4.metric("PEER_OF (คู่)", cnt["peers"] // 2)

    with st.expander("🌱 ข้อมูลตัวอย่าง / ล้างข้อมูลทั้งหมด"):
        if st.button("สร้าง Constraint + Demo Data", type="primary"):
            db.seed_demo()
            done("สร้าง Constraint และข้อมูลตัวอย่างเรียบร้อย (กดซ้ำได้ ไม่สร้างข้อมูลซ้ำ)")
        if st.checkbox("ยืนยันว่าต้องการลบ Student / MacBook ทั้งหมด", key=K("clr_ok")):
            if st.button("🗑️ ลบข้อมูลทั้งหมด", key=K("clr_btn")):
                db.clear_all()
                done("ลบข้อมูล Student / MacBook ทั้งหมดแล้ว")

    # ----- เลือกว่าจะจัดการอะไร -----
    ENT = {"👤 นักศึกษา": "student", "💻 MacBook": "macbook", "🔗 OWNS (รุ่นที่ใช้)": "owns"}
    ACT = {"➕ เพิ่ม": "add", "✏️ แก้ไข": "edit", "🗑️ ลบ": "delete"}
    entity = ENT[st.radio("เลือกข้อมูลที่จะจัดการ", list(ENT), horizontal=True, key="dm_entity")]
    action = ACT[st.radio("การทำงาน", list(ACT), horizontal=True, key="dm_action")]

    # ----- ตารางข้อมูลปัจจุบัน (เห็นผลจริงทุกครั้งที่เพิ่ม/แก้/ลบ) -----
    focus = st.session_state.get("dm_focus")
    focus = focus[1:] if focus and focus[0] == entity else None
    st.markdown("##### 📋 ข้อมูลปัจจุบันในฐานข้อมูล" + (" · แถวสีฟ้า = เพิ่ง เพิ่ม/แก้ไข" if focus else ""))
    if entity == "student":
        show_table(df_stu, ["รหัส"], focus)
    elif entity == "macbook":
        show_table(df_mac, ["รหัสรุ่น"], focus)
    else:
        show_table(df_own, ["รหัสนักศึกษา", "รหัสรุ่น"], focus)
    st.divider()

    # ================= นักศึกษา =================
    if entity == "student" and action == "add":
        st.markdown("##### ➕ เพิ่มนักศึกษา")
        with st.form(K("f_add_stu")):
            c1, c2, c3, c4 = st.columns([1, 1.5, 2, 1])
            sid = c1.text_input("รหัส", placeholder="U011", key=K("as_id"))
            sname = c2.text_input("ชื่อ", key=K("as_name"))
            smajor = c3.text_input("สาขา", key=K("as_major"))
            syear = c4.number_input("ชั้นปี", 1, 8, 1, key=K("as_year"))
            go = st.form_submit_button("➕ เพิ่มนักศึกษา", type="primary")
        if go:
            sid, sname, smajor = sid.strip(), sname.strip(), smajor.strip()
            if not (sid and sname and smajor):
                st.error("กรุณากรอกให้ครบ: รหัส ชื่อ และสาขา")
            elif db.exists("Student", "student_id", sid):
                st.error(f"รหัส {sid} มีอยู่แล้ว ถ้าต้องการเปลี่ยนข้อมูลให้เลือก ✏️ แก้ไข")
            else:
                c = db.add_student(sid, sname, smajor, int(syear))
                if c["nodes_created"] == 0:
                    done(f"เพิ่ม {sid} ไม่สำเร็จ (ฐานข้อมูลไม่ได้สร้างข้อมูลใหม่)", ok=False)
                done(f"เพิ่มนักศึกษา {sid} — {sname} แล้ว · PEER_OF ทั้งระบบตอนนี้ {c['peer_pairs']} คู่",
                     focus=("student", sid))

    elif entity == "student" and action == "edit":
        st.markdown("##### ✏️ แก้ไขนักศึกษา")
        if not students:
            st.info("ยังไม่มีนักศึกษาให้แก้ไข")
        else:
            by_id = {s["id"]: s for s in students}
            pid = st.selectbox("เลือกนักศึกษา", list(by_id), key="es_pick",
                               format_func=lambda i: f'{i} — {by_id[i]["name"]}')
            cur = by_id[pid]
            with st.form(K(f"f_edit_stu_{pid}")):
                st.caption(f"รหัส {pid} (แก้ไม่ได้)")
                c1, c2, c3 = st.columns([1.5, 2, 1])
                n_name = c1.text_input("ชื่อ", cur["name"] or "", key=K(f"es_name_{pid}"))
                n_major = c2.text_input("สาขา", cur["major"] or "", key=K(f"es_major_{pid}"))
                n_year = c3.number_input("ชั้นปี", 1, 8, int(cur["year"] or 1), key=K(f"es_year_{pid}"))
                go = st.form_submit_button("💾 บันทึกการแก้ไข", type="primary")
            if go:
                n_name, n_major, n_year = n_name.strip(), n_major.strip(), int(n_year)
                changes = [f"{lbl}: {a} → {b}" for lbl, a, b in
                           [("ชื่อ", cur["name"], n_name), ("สาขา", cur["major"], n_major),
                            ("ชั้นปี", cur["year"], n_year)] if a != b]
                if not (n_name and n_major):
                    st.error("กรุณากรอกชื่อและสาขา")
                elif not changes:
                    st.warning("ไม่มีการเปลี่ยนแปลง จึงไม่ได้บันทึก")
                else:
                    c = db.update_student(pid, n_name, n_major, n_year)
                    if c["props_set"] == 0:
                        done(f"ไม่พบนักศึกษา {pid} ในฐานข้อมูล (อาจถูกลบไปแล้ว)", ok=False)
                    done(f"แก้ไขนักศึกษา {pid} แล้ว · " + " · ".join(changes) +
                         f" · PEER_OF ตอนนี้ {c['peer_pairs']} คู่", focus=("student", pid))

    elif entity == "student" and action == "delete":
        st.markdown("##### 🗑️ ลบนักศึกษา")
        if not students:
            st.info("ยังไม่มีนักศึกษาให้ลบ")
        else:
            by_id = {s["id"]: s for s in students}
            pid = st.selectbox("เลือกนักศึกษา", list(by_id), key="ds_pick",
                               format_func=lambda i: f'{i} — {by_id[i]["name"]}')
            cur = by_id[pid]
            n_own = sum(1 for o in owns if o["sid"] == pid)
            st.warning(f'จะลบ **{pid} — {cur["name"]}** ({cur["major"]} ปี {cur["year"]}) '
                       f'พร้อมความสัมพันธ์ OWNS {n_own} รายการ และ PEER_OF ที่เกี่ยวข้อง')
            ok = st.checkbox("ยืนยันการลบ", key=K(f"ds_ok_{pid}"))
            if st.button("🗑️ ลบนักศึกษา", disabled=not ok, key=K(f"ds_btn_{pid}")):
                c = db.delete_student(pid)
                if c["nodes_deleted"] == 0:
                    done(f"ไม่พบนักศึกษา {pid} ในฐานข้อมูล (อาจถูกลบไปแล้ว)", ok=False)
                peer_pairs = max(c["rels_deleted"] - n_own, 0) // 2  # PEER_OF เก็บ 2 ทิศ = 1 คู่
                done(f'ลบนักศึกษา {pid} — {cur["name"]} แล้ว · ลบโหนด {c["nodes_deleted"]} · '
                     f'ลบ OWNS {n_own} รายการ · ลบ PEER_OF {peer_pairs} คู่')

    # ================= MacBook =================
    elif entity == "macbook" and action == "add":
        st.markdown("##### ➕ เพิ่ม MacBook")
        with st.form(K("f_add_mac")):
            c1, c2, c3 = st.columns(3)
            mid = c1.text_input("รหัสรุ่น", placeholder="M011", key=K("am_id"))
            model = c2.text_input("ชื่อรุ่น", placeholder="MacBook Air M4", key=K("am_model"))
            chip = c3.text_input("ชิป", placeholder="M4", key=K("am_chip"))
            c4, c5, c6 = st.columns(3)
            ram = c4.number_input("RAM (GB)", 1, 512, 16, key=K("am_ram"))
            sto = c5.number_input("Storage (GB)", 64, 16384, 512, step=64, key=K("am_sto"))
            price = c6.number_input("ราคา (บาท)", 0, 1000000, 40000, step=1000, key=K("am_price"))
            suited = st.text_input("เหมาะกับงาน", placeholder="เขียนโปรแกรม / ตัดต่อวิดีโอ", key=K("am_suit"))
            go = st.form_submit_button("➕ เพิ่ม MacBook", type="primary")
        if go:
            mid, model, chip = mid.strip(), model.strip(), chip.strip()
            if not (mid and model and chip):
                st.error("กรุณากรอกให้ครบ: รหัสรุ่น ชื่อรุ่น และชิป")
            elif db.exists("MacBook", "macbook_id", mid):
                st.error(f"รหัสรุ่น {mid} มีอยู่แล้ว ถ้าต้องการเปลี่ยนข้อมูลให้เลือก ✏️ แก้ไข")
            else:
                c = db.add_macbook({"macbook_id": mid, "model": model, "chip": chip, "ram_gb": int(ram),
                                    "storage_gb": int(sto), "price_thb": int(price),
                                    "suited_for": suited.strip() or "-"})
                if c["nodes_created"] == 0:
                    done(f"เพิ่ม {mid} ไม่สำเร็จ (ฐานข้อมูลไม่ได้สร้างข้อมูลใหม่)", ok=False)
                done(f"เพิ่ม MacBook {mid} — {model} แล้ว (ราคา ฿{int(price):,})", focus=("macbook", mid))

    elif entity == "macbook" and action == "edit":
        st.markdown("##### ✏️ แก้ไข MacBook")
        if not macbooks:
            st.info("ยังไม่มี MacBook ให้แก้ไข")
        else:
            by_mid = {m["macbook_id"]: m for m in macbooks}
            mpid = st.selectbox("เลือก MacBook", sorted(by_mid), key="em_pick",
                                format_func=lambda i: f'{i} — {by_mid[i]["model"]}')
            cm = by_mid[mpid]
            with st.form(K(f"f_edit_mac_{mpid}")):
                st.caption(f"รหัสรุ่น {mpid} (แก้ไม่ได้)")
                c1, c2 = st.columns(2)
                m_model = c1.text_input("ชื่อรุ่น", cm["model"] or "", key=K(f"em_model_{mpid}"))
                m_chip = c2.text_input("ชิป", cm["chip"] or "", key=K(f"em_chip_{mpid}"))
                c3, c4, c5 = st.columns(3)
                m_ram = c3.number_input("RAM (GB)", 1, 512, int(cm["ram_gb"] or 8), key=K(f"em_ram_{mpid}"))
                m_sto = c4.number_input("Storage (GB)", 64, 16384, int(cm["storage_gb"] or 256), step=64,
                                        key=K(f"em_sto_{mpid}"))
                m_price = c5.number_input("ราคา (บาท)", 0, 1000000, int(cm["price_thb"] or 0), step=1000,
                                          key=K(f"em_price_{mpid}"))
                m_suit = st.text_input("เหมาะกับงาน", cm["suited_for"] or "", key=K(f"em_suit_{mpid}"))
                go = st.form_submit_button("💾 บันทึกการแก้ไข", type="primary")
            if go:
                m_model, m_chip, m_suit = m_model.strip(), m_chip.strip(), m_suit.strip() or "-"
                changes = [f"{lbl}: {a} → {b}" for lbl, a, b in
                           [("ชื่อรุ่น", cm["model"], m_model), ("ชิป", cm["chip"], m_chip),
                            ("RAM", cm["ram_gb"], int(m_ram)), ("Storage", cm["storage_gb"], int(m_sto)),
                            ("ราคา", cm["price_thb"], int(m_price)), ("เหมาะกับ", cm["suited_for"], m_suit)]
                           if a != b]
                if not (m_model and m_chip):
                    st.error("กรุณากรอกชื่อรุ่นและชิป")
                elif not changes:
                    st.warning("ไม่มีการเปลี่ยนแปลง จึงไม่ได้บันทึก")
                else:
                    c = db.update_macbook({"macbook_id": mpid, "model": m_model, "chip": m_chip,
                                           "ram_gb": int(m_ram), "storage_gb": int(m_sto),
                                           "price_thb": int(m_price), "suited_for": m_suit})
                    if c["props_set"] == 0:
                        done(f"ไม่พบ MacBook {mpid} ในฐานข้อมูล (อาจถูกลบไปแล้ว)", ok=False)
                    done(f"แก้ไข MacBook {mpid} แล้ว · " + " · ".join(changes), focus=("macbook", mpid))

    elif entity == "macbook" and action == "delete":
        st.markdown("##### 🗑️ ลบ MacBook")
        if not macbooks:
            st.info("ยังไม่มี MacBook ให้ลบ")
        else:
            by_mid = {m["macbook_id"]: m for m in macbooks}
            mpid = st.selectbox("เลือก MacBook", sorted(by_mid), key="dm_pick",
                                format_func=lambda i: f'{i} — {by_mid[i]["model"]}')
            cm = by_mid[mpid]
            st.warning(f'จะลบ **{mpid} — {cm["model"]}** พร้อมความสัมพันธ์ OWNS ของรุ่นนี้ ({cm["owners"]} คนใช้)')
            ok = st.checkbox("ยืนยันการลบ", key=K(f"dm_ok_{mpid}"))
            if st.button("🗑️ ลบ MacBook", disabled=not ok, key=K(f"dm_btn_{mpid}")):
                c = db.delete_macbook(mpid)
                if c["nodes_deleted"] == 0:
                    done(f"ไม่พบ MacBook {mpid} ในฐานข้อมูล (อาจถูกลบไปแล้ว)", ok=False)
                done(f'ลบ MacBook {mpid} — {cm["model"]} แล้ว · ลบโหนด {c["nodes_deleted"]} · '
                     f'ลบความสัมพันธ์ {c["rels_deleted"]} รายการ')

    # ================= OWNS =================
    elif entity == "owns" and action == "add":
        st.markdown("##### ➕ บันทึกว่านักศึกษาใช้ MacBook รุ่นไหน")
        if not (students and macbooks):
            st.info("ต้องมีทั้งนักศึกษาและ MacBook ก่อน")
        else:
            s_ids = [s["id"] for s in students]
            s_name = {s["id"]: s["name"] for s in students}
            m_ids = sorted(m["macbook_id"] for m in macbooks)
            m_name = {m["macbook_id"]: m["model"] for m in macbooks}
            with st.form(K("f_add_own")):
                c1, c2 = st.columns(2)
                s_sel = c1.selectbox("นักศึกษา", s_ids, format_func=lambda i: f"{i} — {s_name[i]}",
                                     key=K("ao_s"))
                m_sel = c2.selectbox("MacBook", m_ids, format_func=lambda i: f"{i} — {m_name[i]}",
                                     key=K("ao_m"))
                go = st.form_submit_button("➕ บันทึก OWNS", type="primary")
            if go:
                if any(o["sid"] == s_sel and o["mid"] == m_sel for o in owns):
                    st.warning(f"{s_sel} ใช้ {m_sel} อยู่แล้ว ไม่ได้เพิ่มซ้ำ")
                else:
                    c = db.add_owns(s_sel, m_sel)
                    if c["rels_created"] == 0:
                        done(f"บันทึก OWNS ไม่สำเร็จ ({s_sel} → {m_sel})", ok=False)
                    done(f"บันทึกแล้ว: {s_sel} {s_name[s_sel]} ใช้ {m_sel} {m_name[m_sel]}",
                         focus=("owns", s_sel, m_sel))

    elif entity == "owns" and action == "edit":
        st.markdown("##### ✏️ เปลี่ยนรุ่นที่นักศึกษาใช้")
        if not owns:
            st.info("ยังไม่มีข้อมูล OWNS ให้แก้ไข")
        else:
            pairs = {f'{o["sid"]}|{o["mid"]}': o for o in owns}
            pk = st.selectbox("เลือกรายการ OWNS", list(pairs), key="eo_pick",
                              format_func=lambda k: f'{pairs[k]["sid"]} {pairs[k]["sname"]}  →  '
                                                    f'{pairs[k]["mid"]} {pairs[k]["model"]}')
            po = pairs[pk]
            m_ids = sorted(m["macbook_id"] for m in macbooks)
            m_name = {m["macbook_id"]: m["model"] for m in macbooks}
            with st.form(K(f"f_edit_own_{pk}")):
                new_mid = st.selectbox("เปลี่ยนเป็นรุ่น", m_ids, index=m_ids.index(po["mid"]),
                                       format_func=lambda i: f"{i} — {m_name[i]}", key=K(f"eo_new_{pk}"))
                go = st.form_submit_button("💾 บันทึกการเปลี่ยนแปลง", type="primary")
            if go:
                if new_mid == po["mid"]:
                    st.warning("เลือกรุ่นเดิม ไม่มีการเปลี่ยนแปลง")
                elif any(o["sid"] == po["sid"] and o["mid"] == new_mid for o in owns):
                    st.warning(f'{po["sid"]} ใช้ {new_mid} อยู่แล้ว ให้ลบรายการเก่าแทน')
                else:
                    c = db.change_owns(po["sid"], po["mid"], new_mid)
                    if c["rels_created"] == 0:
                        done("ไม่พบรายการ OWNS เดิม (อาจถูกลบไปแล้ว)", ok=False)
                    done(f'เปลี่ยนรุ่นของ {po["sid"]} {po["sname"]}: {po["mid"]} {po["model"]} → '
                         f'{new_mid} {m_name[new_mid]}', focus=("owns", po["sid"], new_mid))

    elif entity == "owns" and action == "delete":
        st.markdown("##### 🗑️ ลบรายการ OWNS")
        if not owns:
            st.info("ยังไม่มีข้อมูล OWNS ให้ลบ")
        else:
            pairs = {f'{o["sid"]}|{o["mid"]}': o for o in owns}
            pk = st.selectbox("เลือกรายการ OWNS", list(pairs), key="do_pick",
                              format_func=lambda k: f'{pairs[k]["sid"]} {pairs[k]["sname"]}  →  '
                                                    f'{pairs[k]["mid"]} {pairs[k]["model"]}')
            po = pairs[pk]
            st.warning(f'จะลบความสัมพันธ์ **{po["sid"]} {po["sname"]} → {po["mid"]} {po["model"]}** '
                       "(ตัวนักศึกษาและตัว MacBook ยังอยู่)")
            ok = st.checkbox("ยืนยันการลบ", key=K(f"do_ok_{pk}"))
            if st.button("🗑️ ลบ OWNS", disabled=not ok, key=K(f"do_btn_{pk}")):
                c = db.delete_owns(po["sid"], po["mid"])
                if c["rels_deleted"] == 0:
                    done("ไม่พบรายการ OWNS นี้ (อาจถูกลบไปแล้ว)", ok=False)
                done(f'ลบ OWNS แล้ว: {po["sid"]} {po["sname"]} → {po["mid"]} {po["model"]}')

    # ----- ประวัติการเปลี่ยนแปลงในเซสชันนี้ -----
    if st.session_state.get("dm_log"):
        with st.expander("📜 ประวัติการเปลี่ยนแปลงในเซสชันนี้"):
            for line in st.session_state["dm_log"]:
                st.write(line)


# ---------- กราฟ ----------
with t_graph:
    show_peer = st.checkbox("แสดง PEER_OF (เส้นประสีส้ม)", True)
    own = db.read("MATCH (s:Student)-[:OWNS]->(m:MacBook) RETURN s.student_id AS sid, m.macbook_id AS mid")
    if not own:
        st.info("ยังไม่มีความสัมพันธ์ OWNS ให้แสดง")
    else:
        esc = lambda t: str(t).replace('"', '\\"')
        dot = ['graph G {', 'graph [bgcolor="transparent", overlap=false, splines=true];',
               'node [style=filled, fontname="Helvetica", fontsize=10, fontcolor="#0b1220", color="#ffffff"];',
               'edge [color="#64748b"];']
        for s in students:
            dot.append(f'"{esc(s["id"])}" [label="{esc(s["name"])}", shape=ellipse, fillcolor="#ffb3ba"];')
        for m in macbooks:
            dot.append(f'"{esc(m["macbook_id"])}" [label="{esc(m["model"])}", shape=box, fillcolor="#bae1ff"];')
        dot += [f'"{esc(o["sid"])}" -- "{esc(o["mid"])}";' for o in own]
        if show_peer:
            peers = db.read("MATCH (a:Student)-[:PEER_OF]->(b:Student) WHERE a.student_id < b.student_id "
                            "RETURN a.student_id AS a, b.student_id AS b")
            dot += [f'"{esc(p["a"])}" -- "{esc(p["b"])}" [style=dashed, color="#f59e0b", penwidth=2];' for p in peers]
        dot.append("}")
        st.graphviz_chart("\n".join(dot), use_container_width=True)
        st.caption("วงรีสีชมพู = นักศึกษา · กล่องสีฟ้า = MacBook")

# ---------- ตั้งค่า ----------
with t_set:
    cfg = st.secrets["neo4j"]
    st.write(f'**URI:** `{cfg["uri"]}`')
    st.write(f'**Database:** `{cfg.get("database") or "(home database)"}`')
    if st.button("ทดสอบการเชื่อมต่อ"):
        try:
            db.get_driver().verify_connectivity()
            st.success("เชื่อมต่อสำเร็จ")
        except Exception as e:
            st.error(f"เชื่อมต่อไม่สำเร็จ: {type(e).__name__}")
    if st.button("รีเฟรชข้อมูล (ล้างแคช)"):
        st.cache_data.clear()
        st.rerun()
