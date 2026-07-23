import streamlit as st
import random

# --------------------------------------------------
# 1. ตั้งค่าหน้าเว็บ
# --------------------------------------------------
st.set_page_config(
    page_title="Rubber Tech Exam Prep Game!",
    page_icon="🌳",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .stButton>button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        width: 100%;
    }
    .quiz-box {
        background-color: #1E293B;
        border-left: 6px solid #10B981;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .badge {
        background-color: #334155;
        color: #34D399;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. คลังข้อสอบวิชา Rubber Technology
# --------------------------------------------------
RUBBER_QUESTIONS = [
    # --- หมวด 1: โครงสร้างทางเคมี & พื้นฐาน ---
    {
        "category": "🧪 โครงสร้างทางเคมี & พื้นฐาน",
        "question": "ยางธรรมชาติ (Natural Rubber: NR) มีโครงสร้างทางเคมีหลักเป็นแบบใด?",
        "options": [
            "cis-1,4-polyisoprene",
            "trans-1,4-polyisoprene (Gutta-percha)",
            "Styrene-Butadiene Copolymer",
            "1,2-polybutadiene"
        ],
        "answer": "cis-1,4-polyisoprene",
        "explanation": "ยางธรรมชาติประกอบด้วย cis-1,4-polyisoprene เกือบ 100% ซึ่งทำให้ยางมีความยืดหยุ่นสูงและเกิด Crystallization induced by strain ได้ ส่วน trans-1,4 คือ Gutta-percha ที่แข็งและไม่ยืดหยุ่น"
    },
    {
        "category": "🧪 โครงสร้างทางเคมี & พื้นฐาน",
        "question": "สารชนิดใดที่เป็น Non-rubber components ในน้ำยางสดและมีส่วนช่วยให้ยางธรรมชาติมีสมบัติเฉพาะตัว เช่น Green Strength สูง?",
        "options": [
            "โปรตีนและลิพิด (Proteins & Lipids)",
            "ซิลิกาและแคลเซียม (Silica & Calcium)",
            "เซลลูโลสและลิกนิน (Cellulose & Lignin)",
            "ฟีนอลและแทนนิน (Phenol & Tannin)"
        ],
        "answer": "โปรตีนและลิพิด (Proteins & Lipids)",
        "explanation": "Non-rubber components ในน้ำยางสด เช่น โปรตีนและลิพิด ทำหน้าที่เป็น Natural antioxidants และช่วยเกาะเกี่ยวโครงสร้าง (Branching) ทำให้ยาง NR มี Green Strength สูง"
    },

    # --- หมวด 2: ยางสังเคราะห์ (Synthetic Rubbers) ---
    {
        "category": "🏭 ยางสังเคราะห์ (Synthetic Rubbers)",
        "question": "ยางสังเคราะห์ชนิดใดที่นิยมนำมาผลิต 'ยางรถยนต์' ร่วมกับยางธรรมชาติมากที่สุด เนื่องจากทนต่อการขัดถู (Abrasion Resistance) ได้ดีเยี่ยม?",
        "options": [
            "SBR (Styrene-Butadiene Rubber)",
            "NBR (Nitrile Butadiene Rubber)",
            "EPDM (Ethylene Propylene Diene Monomer)",
            "CR (Chloroprene Rubber)"
        ],
        "answer": "SBR (Styrene-Butadiene Rubber)",
        "explanation": "SBR เป็นยางสังเคราะห์ที่ใช้งานมากที่สุดในอุตสาหกรรมยางรถยนต์เพราะทนการขัดถูดีและราคาถูก ส่วน NBR เด่นเรื่องทนน้ํามัน, EPDM เด่นเรื่องทนสภาพอากาศ/Ozone, CR (Neoprene) เด่นเรื่องทนไฟและน้ำมัน"
    },
    {
        "category": "🏭 ยางสังเคราะห์ (Synthetic Rubbers)",
        "question": "หากต้องการผลิต 'ท่อยางส่งน้ำมันเชื้อเพลิง' ควรเลือกใช้ยางสังเคราะห์ชนิดใด?",
        "options": [
            "NBR (Nitrile Rubber)",
            "NR (Natural Rubber)",
            "SBR (Styrene Rubber)",
            "BR (Polybutadiene Rubber)"
        ],
        "answer": "NBR (Nitrile Rubber)",
        "explanation": "NBR มีหมู่ Nitrile (-CN) ซึ่งเป็นขั้วสูง ทำให้ทนต่อสารละลายไม่มีขั้วอย่างน้ำมันเชื้อเพลิงปิโตรเลียมได้ดีเยี่ยม ยิ่งมี % Acrylonitrile (ACN) สูง ยิ่งทนน้ำมันได้ดี"
    },

    # --- หมวด 3: กระบวนการแปรรูป & เกรดมาตรฐาน ---
    {
        "category": "⚙️ กระบวนการแปรรูป & เกรดมาตรฐาน",
        "question": "กระบวนการ Mastication มีวัตถุประสงค์หลักเพื่ออะไร?",
        "options": [
            "ลดโมเลกุล (Molecular Weight) และความหนืด (Viscosity) ของยาง",
            "เร่งปฏิกิริยาการคงรูปด้วยกำมะถัน",
            "เพิ่มความหนาแน่นและค่า Tensile Strength",
            "กำจัดน้ำและโปรตีนออกจากน้ำยาง"
        ],
        "answer": "ลดโมเลกุล (Molecular Weight) และความหนืด (Viscosity) ของยาง",
        "explanation": "Mastication คือการตัดสายโซ่โมเลกุลยางด้วยแรงตัดเฉือน (Shear) และความร้อน เพื่อลดความหนืด ทำให้ผสมสารเคมีเติมแต่ง (Compounding Ingredients) เข้ากันได้ง่ายขึ้น"
    },
    {
        "category": "⚙️ กระบวนการแปรรูป & เกรดมาตรฐาน",
        "question": "ยางแท่งมาตรฐานไทย (Standard Thai Rubber: STR) เกรดใดที่มีความบริสุทธิ์สูงที่สุด และมีค่า Dirt Content ต่ำที่สุด?",
        "options": [
            "STR XL / STR 5",
            "STR 10",
            "STR 20",
            "STR 50"
        ],
        "answer": "STR XL / STR 5",
        "explanation": "STR XL และ STR 5 เป็นยางแท่งเกรดพรีเมียม ทำจากน้ำยางสด (Latex) มีสิ่งสกปรก (Dirt) น้อยมาก ไม่เกิน 0.03-0.05% ส่วน STR 10/20 ทำจากยางก้อนคัพลัมพ์ (Cup lump) สิ่งสกปรกจะเยอะกว่า"
    },

    # --- หมวด 4: การคงรูป (Vulcanization) & สารเคมี ---
    {
        "category": "🔥 Vulcanization & Compounding",
        "question": "ปฏิกิริยา Vulcanization แบบดั้งเดิมที่ใช้ Sulphur จะเกิดพันธะข้ามสายโซ่ (Crosslink) แบบใดระหว่างสายโซ่ยาง?",
        "options": [
            "Sulfide Crosslinks (-S- / -S-S- / -Sn-)",
            "Carbon-Carbon Direct Crosslinks",
            "Ester Linkages",
            "Hydrogen Bonds"
        ],
        "answer": "Sulfide Crosslinks (-S- / -S-S- / -Sn-)",
        "explanation": "การคงรูปด้วยกำมะถันทำให้เกิดพันธะ Mono-, Di-, หรือ Poly-sulfidic crosslinks ยึดสายโซ่เข้าด้วยกัน ทำให้ยางเปลี่ยนจาก Viscoelastic fluid กลายเป็น Rubber elastic solid ที่ไม่ละลาย"
    },
    {
        "category": "🔥 Vulcanization & Compounding",
        "question": "สารใดทำหน้าที่เป็น 'Activator System' หลักที่ช่วยเสริมประสิทธิภาพของสารเร่งการคงรูป (Accelerators) ในสูตรยาง?",
        "options": [
            "ZnO + Stearic acid",
            "Carbon Black + Silica",
            "Parrafin wax + DOP",
            "CBS + TMTD"
        ],
        "answer": "ZnO + Stearic acid",
        "explanation": "ZnO (Zinc Oxide) ทำหน้าที่เป็น Activator ร่วมกับ Stearic Acid เกิดเป็น Zinc Stearate ซึ่งช่วยให้สารเร่งคงรูป (Accelerator) ทำงานได้อย่างมีประสิทธิภาพสูงสุด"
    }
]

# --------------------------------------------------
# 3. Session State Management
# --------------------------------------------------
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False

def next_question():
    st.session_state.q_idx = (st.session_state.q_idx + 1) % len(RUBBER_QUESTIONS)
    st.session_state.answered = False

# --------------------------------------------------
# 4. หน้าตา UI
# --------------------------------------------------
st.title("🌳 Rubber Tech Exam Prep Master")
st.caption("🎯 เกมตะลุยโจทย์ทบทวนวิชา Rubber Technology เตรียมพร้อมสอบวันเสาร์นี้!")

q = RUBBER_QUESTIONS[st.session_state.q_idx]

col_score, col_progress = st.columns(2)
with col_score:
    st.metric("🏆 คะแนนที่ได้", f"{st.session_state.score} คะแนน")
with col_progress:
    st.caption(f"ข้อที่ {st.session_state.q_idx + 1} / {len(RUBBER_QUESTIONS)}")

st.markdown(f"""
<div class="quiz-box">
    <span class="badge">{q['category']}</span>
    <h3 style="margin-top:10px; color:#F8FAFC;">{q['question']}</h3>
</div>
""", unsafe_allow_html=True)

# ตัวเลือก
user_choice = st.radio("เลือกคำตอบที่ถูกต้อง:", q['options'], disabled=st.session_state.answered)

st.write("---")

if not st.session_state.answered:
    if st.button("ส่งคำตอบ (Submit)"):
        st.session_state.answered = True
        if user_choice == q['answer']:
            st.balloons()
            st.success("🎉 ถูกต้องครับ! เก่งมากแต้ม!")
            st.session_state.score += 10
        else:
            st.error(f"❌ ยังไม่ถูกครับ! คำตอบที่ถูกต้องคือ: {q['answer']}")
        st.rerun()

else:
    # เฉลยและคำอธิบายอย่างละเอียด
    st.info(f"💡 **คำอธิบายสำหรับข้อสอบ:** {q['explanation']}")
    st.button("ข้อถัดไป ➡️", on_click=next_question)
