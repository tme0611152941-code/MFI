import streamlit as st
import random
import time

# 1. ตั้งค่าหน้าจอ
st.set_page_config(
    page_title="AI Werewolf Master - No Moderator Needed",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS ตกแต่งบรรยากาศดาร์กแฟนตาซี
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: white; }
    .secret-box { background-color: #1e293b; padding: 25px; border-radius: 15px; border: 2px solid #3b82f6; text-align: center; }
    .night-card { background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #4f46e5; margin-bottom: 15px; }
    .stButton>button { border-radius: 10px; font-weight: bold; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI Werewolf Master")
st.caption("ระบบดำเนินรายการอัตโนมัติ 100% — ทุกคนเล่นด้วยกันได้ทั้งหมด ไม่ต้องมีคนคุมเกม!")

st.divider()

# Session State Initializations
if 'game_phase' not in st.session_state:
    st.session_state.game_phase = 'SETUP'
if 'players' not in st.session_state:
    st.session_state.players = []
if 'player_roles' not in st.session_state:
    st.session_state.player_roles = {}
if 'alive_players' not in st.session_state:
    st.session_state.alive_players = []
if 'day_count' not in st.session_state:
    st.session_state.day_count = 1
if 'night_step' not in st.session_state:
    st.session_state.night_step = 0
if 'night_kills' not in st.session_state:
    st.session_state.night_kills = None
if 'night_heals' not in st.session_state:
    st.session_state.night_heals = None

# ==========================================
# PHASE 1: SETUP (ใส่ชื่อผู้เล่นทุกคน)
# ==========================================
if st.session_state.game_phase == 'SETUP':
    st.subheader("⚙️ 1. ตั้งค่าผู้เล่น (ทุกคนเข้าร่วมเล่นได้หมด!)")
    
    player_input = st.text_area(
        "ใส่ชื่อผู้เล่นทุกคน (บรรทัดละ 1 คน):",
        "แต้ม\nบอม\nนนท์\nตั๊ก\nเอ็ม\nเกรท"
    )
    
    p_list = [name.strip() for name in player_input.split('\n') if name.strip()]
    n_players = len(p_list)
    
    st.info(f"👥 จำนวนผู้เล่นทั้งหมด: **{n_players} คน**")
    
    col1, col2 = st.columns(2)
    with col1:
        n_wolves = st.number_input("🐺 มนุษย์หมาป่า (Werewolf)", min_value=1, max_value=max(1, n_players//2), value=max(1, n_players//3))
        has_seer = st.checkbox("🔮 ผู้หยั่งรู้ (Seer)", value=True)
    with col2:
        has_doctor = st.checkbox("🛡️ หมอ (Doctor)", value=True)
    
    n_villagers = n_players - (n_wolves + int(has_seer) + int(has_doctor))
    
    if n_villagers < 0:
        st.error("❌ บทบาทพิเศษมากกว่าจำนวนผู้เล่น! กรุณาเพิ่มผู้เล่นหรือลดบทบาทลง")
    else:
        st.success(f"🏡 ชาวบ้านธรรมดา: **{n_villagers} คน**")
        
        if st.button("🎲 สุ่มแจกการ์ดบทบาทลับ!", type="primary", use_container_width=True):
            deck = ["🐺 หมาป่า"] * n_wolves
            if has_seer: deck.append("🔮 ผู้หยั่งรู้")
            if has_doctor: deck.append("🛡️ หมอ")
            deck.extend(["🏡 ชาวบ้าน"] * n_villagers)
            
            random.shuffle(deck)
            
            st.session_state.players = p_list
            st.session_state.alive_players = p_list.copy()
            st.session_state.player_roles = {p_list[i]: deck[i] for i in range(n_players)}
            st.session_state.game_phase = 'VIEW_ROLES'
            st.session_state.view_idx = 0
            st.session_state.revealed = False
            st.rerun()

# ==========================================
# PHASE 2: SECRET VIEW ROLES (สลับกันถือเครื่องไปแอบดูบทบาท)
# ==========================================
elif st.session_state.game_phase == 'VIEW_ROLES':
    idx = st.session_state.view_idx
    total = len(st.session_state.players)
    
    if idx < total:
        curr_p = st.session_state.players[idx]
        
        st.markdown("<div class='secret-box'>", unsafe_allow_html=True)
        st.subheader(f"📱 ยื่นมือถือ/ไอแพดให้: **{curr_p}**")
        st.caption("*(คนอื่นในวงห้ามแอบมองหน้าจอนะครับ!)*")
        
        if not st.session_state.revealed:
            if st.button(f"👁️ กดเพื่อแอบดูบทบาทของ {curr_p}", type="primary"):
                st.session_state.revealed = True
                st.rerun()
        else:
            role = st.session_state.player_roles[curr_p]
            st.markdown(f"<h1 style='color: #f59e0b;'>{role}</h1>", unsafe_allow_html=True)
            
            if "หมาป่า" in role:
                st.warning("🎯 เป้าหมาย: แอบกำจัดชาวบ้านในตอนกลางคืนร่วมกับหมาป่าคนอื่น")
            elif "ผู้หยั่งรู้" in role:
                st.info("🎯 เป้าหมาย: ตื่นมาส่องดูความจริงคืนละ 1 คน")
            elif "หมอ" in role:
                st.success("🎯 เป้าหมาย: ตื่นมาเลือกเซฟเพื่อนคืนละ 1 คน")
            else:
                st.write("🎯 เป้าหมาย: ช่วยกันจับผิดและโหวตประหารหมาป่าให้หมด")
                
            if st.button("🔒 จำได้แล้ว! ปิดหน้าจอและยื่นให้คนถัดไป"):
                st.session_state.revealed = False
                st.session_state.view_idx += 1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("✅ ทุกคนรู้บทบาทลับของตัวเองแล้ว! วางเครื่องไว้กลางวง")
        if st.button("🌙 เริ่มเข้าสู่ คืนแรก (Everyone Close Your Eyes!)", type="primary", use_container_width=True):
            st.session_state.game_phase = 'NIGHT_LOOP'
            st.session_state.night_step = 1
            st.rerun()

# ==========================================
# PHASE 3: AUTOMATED NIGHT PHASE (ทุกคนหลับตา สลับกันทำหน้าที่)
# ==========================================
elif st.session_state.game_phase == 'NIGHT_LOOP':
    st.subheader(f"🌙 ช่วงกลางคืน (คืนที่ {st.session_state.day_count})")
    st.error("🙈 **ทุกคนในวงต้องหลับตาแน่นๆ!** อ่านคำแนะนำแล้วยื่นเครื่องตามบทบาท")
    
    # Step 1: หมาป่าตื่นมาเลือกฆ่า
    if st.session_state.night_step == 1:
        st.markdown("<div class='night-card'>", unsafe_allow_html=True)
        st.markdown("### 🐺 1. ช่วงเวลาของมนุษย์หมาป่า")
        st.write("ให้ **หมาป่าทุกคนลืมตาขึ้นมาอย่างเงียบๆ** แอบส่งสัญญาณรับเครื่องไปกดเลือกเป้าหมายที่ต้องการฆ่า:")
        
        target_k = st.selectbox("เลือกคนที่หมาป่าต้องการฆ่า:", ["-- เลือกเป้าหมาย --"] + st.session_state.alive_players)
        
        if st.button("🔒 ยืนยันเป้าหมายสังหาร (ส่งเครื่องคืนกลางวง & หลับตาลง)"):
            if target_k != "-- เลือกเป้าหมาย --":
                st.session_state.night_kills = target_k
                st.session_state.night_step = 2
                st.rerun()
            else:
                st.error("กรุณาเลือกเป้าหมายก่อนครับ!")
        st.markdown("</div>", unsafe_allow_html=True)

    # Step 2: หมอตื่นมาเลือกเซฟ (ถ้ายังมีหมออยู่)
    elif st.session_state.night_step == 2:
        has_doc = any("หมอ" in st.session_state.player_roles[p] for p in st.session_state.alive_players)
        if has_doc:
            st.markdown("<div class='night-card'>", unsafe_allow_html=True)
            st.markdown("### 🛡️ 2. ช่วงเวลาของหมอ")
            st.write("ให้ **หมอลืมตาขึ้นมารับเครื่องอย่างเงียบๆ** กดเลือกคนที่ต้องการปกป้องคืนนี้ (เซฟตัวเองก็ได้):")
            
            target_h = st.selectbox("เลือกคนที่หมอคุ้มกัน:", ["-- ไม่คุ้มกันใคร --"] + st.session_state.alive_players)
            
            if st.button("🔒 ยืนยันการปกป้อง (ส่งเครื่องคืนกลางวง & หลับตาลง)"):
                st.session_state.night_heals = target_h
                st.session_state.night_step = 3
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.session_state.night_step = 3
            st.rerun()

    # Step 3: ผู้หยั่งรู้ตื่นมาส่อง (ถ้ายังมีผู้หยั่งรู้)
    elif st.session_state.night_step == 3:
        has_seer = any("ผู้หยั่งรู้" in st.session_state.player_roles[p] for p in st.session_state.alive_players)
        if has_seer:
            st.markdown("<div class='night-card'>", unsafe_allow_html=True)
            st.markdown("### 🔮 3. ช่วงเวลาของผู้หยั่งรู้")
            st.write("ให้ **ผู้หยั่งรู้ลืมตาขึ้นมารับเครื่องอย่างเงียบๆ** เลือกส่องดูบทบาทลับของเพื่อน 1 คน:")
            
            seer_t = st.selectbox("เลือกคนที่ต้องการส่อง:", ["-- เลือกคนที่จะส่อง --"] + st.session_state.alive_players)
            
            if seer_t != "-- เลือกคนที่จะส่อง --":
                is_wolf = "หมาป่า" in st.session_state.player_roles[seer_t]
                if is_wolf:
                    st.error(f"🔮 คำตอบลับเฉพาะคุณ: **{seer_t} คือ หมาป่า! 🐺**")
                else:
                    st.success(f"🔮 คำตอบลับเฉพาะคุณ: **{seer_t} คือ ฝ่ายดี/ชาวบ้าน 🟢**")
            
            if st.button("🔒 อ่านแล้ว! ปิดเครื่อง (ส่งคืนกลางวง & หลับตาลง)"):
                st.session_state.night_step = 4
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.session_state.night_step = 4
            st.rerun()

    # Step 4: ประมวลผลคืนนี้เข้าสู่อรุณสวัสดิ์
    elif st.session_state.night_step == 4:
        st.success("✅ กิจกรรมกลางคืนเสร็จสิ้นทั้งหมดแล้ว!")
        if st.button("☀️ ปลุกทุกคนลืมตา! (เข้าสู่รุ่งเช้า)", type="primary", use_container_width=True):
            # ประมวลผลคนตาย
            killed = st.session_state.night_kills
            healed = st.session_state.night_heals
            
            if killed and killed == healed:
                st.session_state.today_dead = None # หมอช่วยไว้ทัน
            else:
                st.session_state.today_dead = killed
                if killed in st.session_state.alive_players:
                    st.session_state.alive_players.remove(killed)
                    
            st.session_state.game_phase = 'DAY_PHASE'
            st.rerun()

# ==========================================
# PHASE 4: DAY PHASE (รุ่งเช้า & ถกเถียง)
# ==========================================
elif st.session_state.game_phase == 'DAY_PHASE':
    st.subheader(f"☀️ รุ่งเช้าวันที่ {st.session_state.day_count} — ทุกคนลืมตา!")
    
    st.markdown("<div class='secret-box'>", unsafe_allow_html=True)
    dead = st.session_state.today_dead
    if dead:
        st.error(f"💀 เมื่อคืนนี้เกิดเรื่องเศร้า... **{dead}** โดนหมาป่าสังหารเสียชีวิต!")
    else:
        st.success("🕊️ คืนที่ผ่านมาเงียบสงบ! **ไม่มีใครเสียชีวิต** (หมอช่วยไว้ทัน)")
    st.markdown("</div>", unsafe_allow_html=True)

    # ตรวจสอบเงื่อนไขจบเกม
    wolves = [p for p in st.session_state.alive_players if "หมาป่า" in st.session_state.player_roles[p]]
    villagers = [p for p in st.session_state.alive_players if "หมาป่า" not in st.session_state.player_roles[p]]
    
    if len(wolves) == 0:
        st.balloons()
        st.success("🎉 **ฝ่ายชาวบ้านชนะ!** มนุษย์หมาป่าถูกกำจัดออกจนหมดแล้ว!")
        st.session_state.game_phase = 'END'
    elif len(wolves) >= len(villagers):
        st.error("🐺 **ฝ่ายมนุษย์หมาป่าชนะ!** จำนวนหมาป่าเท่ากับหรือมากกว่าชาวบ้านแล้ว!")
        st.session_state.game_phase = 'END'
    else:
        st.write(f"👥 ผู้เล่นที่ยังรอดชีวิต ({len(st.session_state.alive_players)} คน): **{', '.join(st.session_state.alive_players)}**")
        st.caption("พูดคุย ถกเถียง และจับผิดกันในวงได้เลย!")
        
        if st.button("🗳️ เมื่ออภิปรายเสร็จแล้ว -> เข้าสู่หน้าโหวตประหาร", type="primary", use_container_width=True):
            st.session_state.game_phase = 'VOTE_PHASE'
            st.rerun()

# ==========================================
# PHASE 5: VOTE PHASE (นับโหวตประหาร)
# ==========================================
elif st.session_state.game_phase == 'VOTE_PHASE':
    st.subheader("🗳️ โหวตประหารชีวิต")
    st.write("นับ 1 2 3 แล้วทุกคนชี้เป้าคนที่สงสัยพร้อมกัน! จากนั้นเลือกคนที่ได้คะแนนโหวตสูงสุด:")
    
    voted_out = st.selectbox("คนที่โดนโหวตประหารออก:", ["-- เสมอ / ไม่ประหารใคร --"] + st.session_state.alive_players)
    
    if st.button("⚖️ ยืนยันผลการประหาร", type="primary", use_container_width=True):
        if voted_out != "-- เสมอ / ไม่ประหารใคร --":
            st.session_state.alive_players.remove(voted_out)
            r = st.session_state.player_roles[voted_out]
            st.warning(f"⚰️ **{voted_out}** โดนประหารชีวิต! (บทบาทลับคือ: **{r}**)")
        else:
            st.info("🕊️ วันนี้ไม่มีใครโดนประหารชีวิต")
            
        st.session_state.day_count += 1
        st.session_state.game_phase = 'NIGHT_LOOP'
        st.session_state.night_step = 1
        st.rerun()

# ==========================================
# PHASE 6: END GAME (เฉลยทุกคน)
# ==========================================
elif st.session_state.game_phase == 'END':
    st.subheader("🏆 จบเกม! เฉลยบทบาทลับทั้งหมด")
    
    res = [{"ชื่อ": p, "บทบาท": st.session_state.player_roles[p], "สถานะ": "รอดชีวิต" if p in st.session_state.alive_players else "เสียชีวิต"} for p in st.session_state.players]
    st.table(res)
    
    if st.button("🔄 เล่นใหม่อีกรอบ", type="primary", use_container_width=True):
        st.session_state.game_phase = 'SETUP'
        st.session_state.day_count = 1
        st.rerun()
