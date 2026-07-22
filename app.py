import streamlit as st
import random
import time

# 1. ตั้งค่าหน้าจอ
st.set_page_config(
    page_title="AI Werewolf Master",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: white; }
    .secret-box { background-color: #1e293b; padding: 25px; border-radius: 15px; border: 2px solid #3b82f6; text-align: center; }
    .night-card { background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #4f46e5; margin-bottom: 15px; }
    .stButton>button { border-radius: 10px; font-weight: bold; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

# ลิงก์ไฟล์เสียงมาตรฐาน MP3
SOUND_BEEP = "https://www.soundjay.com/buttons/sounds/button-16a.mp3"
SOUND_ALARM = "https://www.soundjay.com/clock/sounds/alarm-clock-01.mp3"

st.title("🤖 AI Werewolf Master")
st.caption("ระบบคุมเกมอัตโนมัติ 100% (แก้ไขระบบเสียงเรียบร้อยแล้ว) 🔊")

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
if 'play_sound_type' not in st.session_state:
    st.session_state.play_sound_type = None

# ==========================================
# PHASE 1: SETUP
# ==========================================
if st.session_state.game_phase == 'SETUP':
    st.subheader("⚙️ 1. ตั้งค่าผู้เล่น")
    
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
        st.error("❌ บทบาทพิเศษมากกว่าจำนวนผู้เล่น!")
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
# PHASE 2: SECRET VIEW ROLES
# ==========================================
elif st.session_state.game_phase == 'VIEW_ROLES':
    idx = st.session_state.view_idx
    total = len(st.session_state.players)
    
    if idx < total:
        curr_p = st.session_state.players[idx]
        
        st.markdown("<div class='secret-box'>", unsafe_allow_html=True)
        st.subheader(f"📱 ยื่นมือถือ/ไอแพดให้: **{curr_p}**")
        
        if not st.session_state.revealed:
            if st.button(f"👁️ กดเพื่อแอบดูบทบาทของ {curr_p}", type="primary"):
                st.session_state.revealed = True
                st.rerun()
        else:
            role = st.session_state.player_roles[curr_p]
            st.markdown(f"<h1 style='color: #f59e0b;'>{role}</h1>", unsafe_allow_html=True)
            
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
# PHASE 3: AUTOMATED NIGHT PHASE
# ==========================================
elif st.session_state.game_phase == 'NIGHT_LOOP':
    st.subheader(f"🌙 ช่วงกลางคืน (คืนที่ {st.session_state.day_count})")
    st.error("🙈 **ทุกคนในวงหลับตาแน่นๆ!**")
    
    # Step 1: หมาป่า
    if st.session_state.night_step == 1:
        st.markdown("<div class='night-card'>", unsafe_allow_html=True)
        st.markdown("### 🐺 1. ช่วงเวลาของมนุษย์หมาป่า")
        
        target_k = st.selectbox("เลือกคนที่หมาป่าต้องการฆ่า:", ["-- เลือกเป้าหมาย --"] + st.session_state.alive_players)
        
        if st.button("🔔 ยืนยัน (เล่นเสียงเตือนเสร็จให้ส่งเครื่องคืนกลางวง)", type="primary"):
            if target_k != "-- เลือกเป้าหมาย --":
                st.session_state.night_kills = target_k
                st.session_state.play_sound_type = "beep"
            else:
                st.error("กรุณาเลือกเป้าหมายก่อนครับ!")
        
        # แสดงเครื่องเล่นเสียงหลังกด
        if st.session_state.play_sound_type == "beep":
            st.audio(SOUND_BEEP, autoplay=True)
            if st.button("➡️ ส่งเครื่องคืนกลางวงแล้ว -> เข้าสู่บทบาทถัดไป"):
                st.session_state.play_sound_type = None
                st.session_state.night_step = 2
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Step 2: หมอ
    elif st.session_state.night_step == 2:
        has_doc = any("หมอ" in st.session_state.player_roles[p] for p in st.session_state.alive_players)
        if has_doc:
            st.markdown("<div class='night-card'>", unsafe_allow_html=True)
            st.markdown("### 🛡️ 2. ช่วงเวลาของหมอ")
            
            target_h = st.selectbox("เลือกคนที่หมอคุ้มกัน:", ["-- ไม่คุ้มกันใคร --"] + st.session_state.alive_players)
            
            if st.button("🔔 ยืนยัน (เล่นเสียงเตือนเสร็จให้ส่งเครื่องคืนกลางวง)", type="primary"):
                st.session_state.night_heals = target_h
                st.session_state.play_sound_type = "beep"
            
            if st.session_state.play_sound_type == "beep":
                st.audio(SOUND_BEEP, autoplay=True)
                if st.button("➡️ ส่งเครื่องคืนกลางวงแล้ว -> เข้าสู่บทบาทถัดไป"):
                    st.session_state.play_sound_type = None
                    st.session_state.night_step = 3
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.session_state.night_step = 3
            st.rerun()

    # Step 3: ผู้หยั่งรู้
    elif st.session_state.night_step == 3:
        has_seer = any("ผู้หยั่งรู้" in st.session_state.player_roles[p] for p in st.session_state.alive_players)
        if has_seer:
            st.markdown("<div class='night-card'>", unsafe_allow_html=True)
            st.markdown("### 🔮 3. ช่วงเวลาของผู้หยั่งรู้")
            
            seer_t = st.selectbox("เลือกคนที่ต้องการส่อง:", ["-- เลือกคนที่จะส่อง --"] + st.session_state.alive_players)
            
            if seer_t != "-- เลือกคนที่จะส่อง --":
                is_wolf = "หมาป่า" in st.session_state.player_roles[seer_t]
                if is_wolf:
                    st.error(f"🔮 คำตอบลับ: **{seer_t} คือ หมาป่า! 🐺**")
                else:
                    st.success(f"🔮 คำตอบลับ: **{seer_t} คือ ฝ่ายดี/ชาวบ้าน 🟢**")
            
            if st.button("🔔 อ่านแล้วกดฟังเสียงเตือน (แล้วส่งเครื่องคืนกลางวง)", type="primary"):
                st.session_state.play_sound_type = "beep"
            
            if st.session_state.play_sound_type == "beep":
                st.audio(SOUND_BEEP, autoplay=True)
                if st.button("➡️ ส่งเครื่องคืนกลางวงแล้ว -> ปลุกทุกคน"):
                    st.session_state.play_sound_type = None
                    st.session_state.night_step = 4
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.session_state.night_step = 4
            st.rerun()

    # Step 4: ปลุกทุกคนด้วยเสียงปลุก
    elif st.session_state.night_step == 4:
        st.success("✅ กิจกรรมกลางคืนเสร็จสิ้นทั้งหมดแล้ว!")
        
        st.markdown("### ⏰ กดปุ่มด้านล่างเพื่อส่งเสียงปลุกทุกคนในวง:")
        st.audio(SOUND_ALARM, autoplay=True)
        
        if st.button("☀️ เข้าสู่ช่วงสรุปผลรุ่งเช้า (ทุกคนลืมตาได้!)", type="primary", use_container_width=True):
            killed = st.session_state.night_kills
            healed = st.session_state.night_heals
            
            if killed and killed == healed:
                st.session_state.today_dead = None
            else:
                st.session_state.today_dead = killed
                if killed in st.session_state.alive_players:
                    st.session_state.alive_players.remove(killed)
                    
            st.session_state.game_phase = 'DAY_PHASE'
            st.rerun()

# ==========================================
# PHASE 4: DAY PHASE
# ==========================================
elif st.session_state.game_phase == 'DAY_PHASE':
    st.subheader(f"☀️ รุ่งเช้าวันที่ {st.session_state.day_count} — ทุกคนลืมตา!")
    
    st.markdown("<div class='secret-box'>", unsafe_allow_html=True)
    dead = st.session_state.today_dead
    if dead:
        st.error(f"💀 เมื่อคืนนี้... **{dead}** โดนหมาป่าสังหารเสียชีวิต!")
    else:
        st.success("🕊️ คืนที่ผ่านมาเงียบสงบ! **ไม่มีใครเสียชีวิต**")
    st.markdown("</div>", unsafe_allow_html=True)

    wolves = [p for p in st.session_state.alive_players if "หมาป่า" in st.session_state.player_roles[p]]
    villagers = [p for p in st.session_state.alive_players if "หมาป่า" not in st.session_state.player_roles[p]]
    
    if len(wolves) == 0:
        st.balloons()
        st.success("🎉 **ฝ่ายชาวบ้านชนะ!** มนุษย์หมาป่าถูกกำจัดหมดแล้ว!")
        st.session_state.game_phase = 'END'
    elif len(wolves) >= len(villagers):
        st.error("🐺 **ฝ่ายมนุษย์หมาป่าชนะ!** จำนวนหมาป่าเท่ากับหรือมากกว่าชาวบ้านแล้ว!")
        st.session_state.game_phase = 'END'
    else:
        st.write(f"👥 ผู้เล่นที่เหลืออยู่ ({len(st.session_state.alive_players)} คน): **{', '.join(st.session_state.alive_players)}**")
        
        if st.button("🗳️ เข้าสู่หน้าโหวตประหาร", type="primary", use_container_width=True):
            st.session_state.game_phase = 'VOTE_PHASE'
            st.rerun()

# ==========================================
# PHASE 5: VOTE PHASE
# ==========================================
elif st.session_state.game_phase == 'VOTE_PHASE':
    st.subheader("🗳️ โหวตประหารชีวิต")
    
    voted_out = st.selectbox("คนที่โดนโหวตประหารออก:", ["-- เสมอ / ไม่ประหารใคร --"] + st.session_state.alive_players)
    
    if st.button("⚖️ ยืนยันผลการประหาร", type="primary", use_container_width=True):
        if voted_out != "-- เสมอ / ไม่ประหารใคร --":
            st.session_state.alive_players.remove(voted_out)
            r = st.session_state.player_roles[voted_out]
            st.warning(f"⚰️ **{voted_out}** โดนประหาร! (บทบาทลับคือ: **{r}**)")
        else:
            st.info("🕊️ วันนี้ไม่มีใครโดนประหารชีวิต")
            
        st.session_state.day_count += 1
        st.session_state.game_phase = 'NIGHT_LOOP'
        st.session_state.night_step = 1
        st.rerun()

# ==========================================
# PHASE 6: END GAME
# ==========================================
elif st.session_state.game_phase == 'END':
    st.subheader("🏆 จบเกม! เฉลยบทบาทลับทั้งหมด")
    
    res = [{"ชื่อ": p, "บทบาท": st.session_state.player_roles[p], "สถานะ": "รอดชีวิต" if p in st.session_state.alive_players else "เสียชีวิต"} for p in st.session_state.players]
    st.table(res)
    
    if st.button("🔄 เล่นใหม่อีกรอบ", type="primary", use_container_width=True):
        st.session_state.game_phase = 'SETUP'
        st.session_state.day_count = 1
        st.rerun()
