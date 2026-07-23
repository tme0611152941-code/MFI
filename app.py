import streamlit as st
import random
import time

# --------------------------------------------------
# 1. ตั้งค่าหน้าเว็บ
# --------------------------------------------------
st.set_page_config(
    page_title="Extruder Overload: Polymer Master",
    page_icon="🔬",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #A855F7 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
        width: 100%;
    }
    .order-box {
        background-color: #1E293B;
        border-left: 6px solid #8B5CF6;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .badge {
        background-color: #334155;
        color: #38BDF8;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. ฐานข้อมูลพอลิเมอร์ครบทุกหมวด ทุกเกรด และผู้ผลิต
# --------------------------------------------------
POLYMER_DATABASE = [
    # --- หมวด 1: Biopolymers & Bio-composites ---
    {
        "id": 1,
        "category": "🌱 Biopolymers & Composites",
        "material": "PLA (Polylactic Acid)",
        "grade": "Ingeo™ Biopolymer 4032D (Film Grade)",
        "producer": "NatureWorks LLC / GC International",
        "desc": "เป่าฟิล์มย่อยสลายได้สำหรับถุงใส่อาหาร ห้ามใช้อุณหภูมิสูงเกินไปเพราะเสี่ยง Thermal Degradation และ MFI เปลี่ยน!",
        "target_temp": (180, 200),
        "target_rpm": (40, 60),
        "target_additive": (5, 10),
        "target_cooling": (6, 10)
    },
    {
        "id": 2,
        "category": "🌱 Biopolymers & Composites",
        "material": "PLA/PBAT/Biochar Composite",
        "grade": "Custom Senior Research Grade (Bio-composite)",
        "producer": "SUT Laboratory / In-house Compound",
        "desc": "คอมพาวนด์ฟิล์มเกษตรผสมไบโอชา ห้ามใช้ Shear force สูงเกินไป เพราะไบโอชาจะแตกละเอียดส่งผลเสียต่อ Tensile Strength!",
        "target_temp": (160, 180),
        "target_rpm": (30, 50),
        "target_additive": (10, 20),
        "target_cooling": (8, 12)
    },
    
    # --- หมวด 2: Commodity Plastics ---
    {
        "id": 3,
        "category": "📦 Commodity Plastics",
        "material": "HDPE (High-Density Polyethylene)",
        "grade": "InnoPlus HD5000S (Injection Grade)",
        "producer": "PTT Global Chemical (GC)",
        "desc": "งานฉีดขึ้นรูปลังพลาสติกบรรจุสินค้า ต้องการ Flowability ดี แต่ห้ามเกิด Sink Mark (รอยบุ๋ม) จากการเย็นตัวไม่เท่ากัน!",
        "target_temp": (210, 240),
        "target_rpm": (70, 90),
        "target_additive": (0, 5),
        "target_cooling": (15, 25)
    },
    {
        "id": 4,
        "category": "📦 Commodity Plastics",
        "material": "PP (Polypropylene Random Copolymer)",
        "grade": "SCG PP P700J (Injection Grade)",
        "producer": "SCG Chemicals (SCGC)",
        "desc": "กล่องบรรจุอาหารใสทนความร้อน ไมโครเวฟได้ ห้ามเกิด Warpage (ชิ้นงานบิดโก่ง) เด็ดขาด!",
        "target_temp": (200, 230),
        "target_rpm": (60, 80),
        "target_additive": (2, 8),
        "target_cooling": (10, 18)
    },

    # --- หมวด 3: Engineering Plastics ---
    {
        "id": 5,
        "category": "⚙️ Engineering Plastics",
        "material": "PA66 (Polyamide 66 / Nylon 66)",
        "grade": "Ultramid® A3K (Unreinforced)",
        "producer": "BASF",
        "desc": "ฉีดเฟืองเกียร์พลาสติกในเครื่องจักรอุตสาหกรรม ต้องระวัง Hydrolysis Degradation ถ้าความชื้นสูง และห้ามใช้อุณหภูมิต่ำเกินไปจนพลาสติกไม่หลอม!",
        "target_temp": (270, 295),
        "target_rpm": (50, 75),
        "target_additive": (1, 5),
        "target_cooling": (12, 20)
    },
    {
        "id": 6,
        "category": "⚙️ Engineering Plastics",
        "material": "PC (Polycarbonate)",
        "grade": "Makrolon® 2407 (Light Guide Grade)",
        "producer": "Covestro",
        "desc": "ฉีดเลนส์โคมไฟหน้ารถยนต์ โปร่งใสไร้รอยคราบ ห้ามเกิด Yellowing Index (ชิ้นงานเหลือง) จากการไหม้ในบาร์เรล!",
        "target_temp": (280, 310),
        "target_rpm": (40, 60),
        "target_additive": (0, 3),
        "target_cooling": (15, 25)
    },

    # --- หมวด 4: High-Performance Plastics ---
    {
        "id": 7,
        "category": "🚀 High-Performance Plastics",
        "material": "PEEK (Polyether Ether Ketone)",
        "grade": "VICTREX™ PEEK 450G",
        "producer": "Victrex plc",
        "desc": "ชิ้นส่วนการแพทย์/การบินและอวกาศ ทนอุณหภูมิสูงและเคมีรุนแรง ต้องใช้อุณหภูมิหลอมสูงมาก ห้ามหล่อเย็นเร็วเกินไปจน Crystallinity ตก!",
        "target_temp": (360, 390),
        "target_rpm": (30, 50),
        "target_additive": (0, 2),
        "target_cooling": (25, 40)
    }
]

# --------------------------------------------------
# 3. ระบบจัดการสถานะเกม (Session State)
# --------------------------------------------------
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_order_idx' not in st.session_state:
    st.session_state.current_order_idx = random.randint(0, len(POLYMER_DATABASE) - 1)

# Function สำหรับสุ่มออเดอร์ใหม่
def next_order():
    st.session_state.current_order_idx = random.randint(0, len(POLYMER_DATABASE) - 1)

# --------------------------------------------------
# 4. หน้าตา UI
# --------------------------------------------------
st.title("🔬 Extruder Overload: Polymer Master")
st.caption("🤖 เกมจำลองกระบวนการแปรรูปพอลิเมอร์สมจริง แข่งกับ AI ลูกค้าสุดเฮี้ยบ")

# โหมดเลือกเกรดด้วยตัวเอง หรือสุ่ม
st.sidebar.header("🎯 ตัวเลือกโหมดเล่น")
mode = st.sidebar.radio("โหมดการสุ่มออเดอร์:", ["🎲 สุ่มเกรดพลาสติกไปเรื่อยๆ", "📌 เลือกเกรดที่อยากทดลองเอง"])

if mode == "📌 เลือกเกรดที่อยากทดลองเอง":
    selected_name = st.sidebar.selectbox(
        "เลือกเกรดพลาสติก:",
        [f"{p['material']} - {p['grade']}" for p in POLYMER_DATABASE]
    )
    for idx, p in enumerate(POLYMER_DATABASE):
        if f"{p['material']} - {p['grade']}" == selected_name:
            st.session_state.current_order_idx = idx

order = POLYMER_DATABASE[st.session_state.current_order_idx]

st.metric("🏆 คะแนนเกียรตินิยมวิศวกร", f"{st.session_state.score} EXP")

st.markdown(f"""
<div class="order-box">
    <span class="badge">{order['category']}</span>
    <h3 style="margin-top:10px; color:#F43F5E;">{order['material']}</h3>
    <p><b>เกรดพลาสติก:</b> <code style="color:#A855F7;">{order['grade']}</code></p>
    <p><b>บริษัทผู้ผลิต:</b> 🏢 {order['producer']}</p>
    <hr style="border-color:#334155;">
    <p><b>ข้อกำหนดลูกค้า (Requirement):</b><br><i>"{order['desc']}"</i></p>
</div>
""", unsafe_allow_html=True)

st.subheader("🎛️ ตั้งค่ากระบวนการแปรรูป (Processing Parameters)")

col1, col2 = st.columns(2)

with col1:
    temp = st.slider("🌡️ Barrel Temp (°C)", 140, 420, 200, step=5)
    rpm = st.slider("🔄 Screw Speed (RPM)", 10, 120, 50, step=5)

with col2:
    additive = st.slider("🧪 Additive / Plasticizer (%)", 0, 30, 5, step=1)
    cooling = st.slider("❄️ Cooling Time (s)", 2, 45, 10, step=1)

st.write("---")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    run_btn = st.button("🚀 สั่งรันเครื่อง (Run Process)")

with col_btn2:
    st.button("🔄 เปลี่ยนไปเกรดถัดไป (Random Next)", on_click=next_order)

if run_btn:
    with st.spinner("⚙️ พอลิเมอร์กำลังเคลื่อนผ่าน Feed Zone -> Compression Zone -> Metering Zone..."):
        time.sleep(1.2)
        
        defects = []
        deductions = 0
        
        # 1. เช็ก Barrel Temp
        if temp < order['target_temp'][0]:
            defects.append(f"🥶 Temp ต่ำกว่า Processing Window ({order['target_temp'][0]}°C): พอลิเมอร์ไม่หลอมสมบูรณ์ เกิด Unmelted Pellets อุดตัน Die!")
            deductions += 30
        elif temp > order['target_temp'][1]:
            defects.append(f"🔥 Temp สูงเกินเกณฑ์ ({order['target_temp'][1]}°C): เกิด Thermal Degradation สายโซ่ขาด ชิ้นงานไหม้ดำและเกิดก๊าซพิษ!")
            deductions += 35

        # 2. เช็ก Screw Speed (RPM)
        if rpm > order['target_rpm'][1]:
            defects.append("🌀 RPM สูงเกินไป: เกิด Shear Heating สะสมสูงเกินไป สายโซ่พอลิเมอร์ถูกตัดขาด (Shear Degradation) และเกิดฟองอากาศ")
            deductions += 25
        elif rpm < order['target_rpm'][0]:
            defects.append("🐢 RPM ช้าเกินไป: Residence Time ในบาร์เรลนานเกินไป พลาสติกเสื่อมสภาพ และได้ Output ต่ำกว่าเป้าหมาย")
            deductions += 15

        # 3. เช็ก Additive
        if additive > order['target_additive'][1]:
            defects.append("💧 ใส่ Additive/Plasticizer มากเกินไป: เกิด Phase Separation (เยิ้มออกมาหน้าชิ้นงาน) และค่า Tensile Strength ตกอย่างรุนแรง")
            deductions += 20
        elif additive < order['target_additive'][0]:
            defects.append("🧱 ใส่ Additive น้อยเกินไป: ชิ้นงานเปราะแตกง่าย ไม่ได้สมบัติทางกลตามสเปกของเกรดนี้")
            deductions += 20

        # 4. เช็ก Cooling Time
        if cooling < order['target_cooling'][0]:
            defects.append("⏱️ Cooling Time น้อยเกินไป: ชิ้นงานยังไม่เซ็ตตัว เกิด Warpage (บิดโก่ง) หรือ Sink Mark (รอยบุ๋ม)")
            deductions += 20

        # แสดงผลลัพธ์
        if len(defects) == 0:
            st.balloons()
            st.success("🎉 PERFECT! ขึ้นรูปชิ้นงานได้ตรงตามสเปก โครงสร้างผลึก (Crystallinity) และสมบัติทางกลสมบูรณ์แบบ!")
            st.session_state.score += 150
            st.info("🤖 **AI QC Inspector:** 'ผ่าน QC 100%! เกรดนี้แปรรูปยากมาก แต่คุณทำได้เนียนจริงๆ!'")
        else:
            st.error("💥 QC Reject! ชิ้นงานเสียสภาพ พบข้อผิดพลาดทางเทคนิคดังนี้:")
            for d in defects:
                st.write(f"- {d}")
            
            gained_score = max(0, 100 - deductions)
            st.session_state.score += gained_score
            st.warning(f"📉 ได้รับคะแนนรอบนี้: {gained_score} / 100 คะแนน")
            st.info("🤖 **AI QC Inspector:** 'ชิ้นงานเกรดนี้ราคาแพงมากนะ! ปรับค่า Parameter ใหม่ แล้วลองดูอีกที!'")
