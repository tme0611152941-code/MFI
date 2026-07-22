import streamlit as st
import random
import time

# 1. ตั้งค่าหน้าจอ
st.set_page_config(
    page_title="Werewolf Moderator AI",
    page_icon="🐺",
    layout="centered"
)

# Custom CSS ตกแต่งสไตล์ดาร์กแฟนตาซี
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .card-box { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 15px; }
    .night-title { color: #818cf8; font-weight: bold; }
    .day-title { color: #f59e0b; font-weight: bold; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🐺 Werewolf Moderator AI")
st.caption("ระบบผู้ดำเนินรายการคุมเกมแวร์วูฟอัตโนมัติ สำหรับเล่นล้อมวงกับเพื่อน! 🎭")

st.divider()

# Initialization States
if 'game_stage' not in st.session_state:
    st.session_state.game_stage = 'SETUP' # SETUP, ASSIGN, NIGHT, DAY, VOTE, GAMEOVER
if 'players' not in st.session_state:
    st.session_state.players = []
if 'player_roles' not in st.session_state:
    st.session_state.player_roles = {}
if 'alive_players' not in st.session_state:
    st.session_state.alive_players = []
if 'night_actions' not in st.session_state:
    st.session_state.night_actions = {}
if 'current_assign_idx' not in st.session_state:
    st.session_state.current_assign_idx = 0
if 'show_role' not in st.session_state:
    st.session_state.show_role = False
if 'day_count' not in st.session_state:
    st.session_state.day_count = 1

# ==========================================
# STAGE 1: SETUP (ตั้งค่าผู้เล่นและตัวละคร)
# ==========================================
if st.session_state.game_stage == 'SETUP':
    st.subheader("⚙️ 1. ตั้งค่าจำนวนผู้เล่นและบทบาท")
    
    player_names_input = st.text_area(
        "ใส่ชื่อผู้เล่น (บรรทัดละ 1 คน - แนะนำ 5-10 คน):",
        "แต้ม\nบอม\nนนท์\nตั๊ก\nเอ็ม\nเกรท"
    )
    
    player_list = [name.strip() for name in player_names_input.split('\n') if name.strip()]
    num_players = len(player_list)
    
    st.info(f"👥 จำนวนผู้เล่นปัจจุบัน: **{num_players} คน**")
    
    st.write("🎭 **เลือกบทบาทที่จะใส่ในเกม:**")
    c1, c2 = st.columns(2)
    with c1:
        num_wolves = st.number_input("🐺 มนุษย์หมาป่า (Werewolf)", min_value=1, max_value=max(1, num_players//2), value=max(1, num_players//3))
        use_seer = st.checkbox("🔮 ผู้หยั่งรู้ (Seer)", value=True)
        use_doctor = st.checkbox("🛡️ หมอ (Doctor)", value=True)
    with c2:
        use_hunter = st.checkbox("🏹 พรานล่าสัตว์ (Hunter)", value=False)
        use_witch = st.checkbox("🧪 แม่มด (Witch)", value=False)
    
    # คำนวณชาวบ้านที่เหลือ
    special_roles_count = num_wolves + int(use_seer) + int(use_doctor) + int(use_hunter) + int(use_witch)
    num_villagers = num_players - special_roles_count
    
    if num_villagers < 0:
        st.error("❌ จำนวนบทบาทพิเศษรวมกันเกินจำนวนผู้เล่น! กรุณาลดบทบาทพิเศษหรือเพิ่มผู้เล่น")
    else:
        st.success(f"🏡 ชาวบ้านธรรมดา (Villager): **{num_villagers} คน**")
        
        if st.button("🚀 สุ่มสลับการ์ดและเริ่มแจกบทบาท!", type="primary", use_container_width=True):
            # สร้าง List บทบาท
            deck = ["🐺 หมาป่า"] * num_wolves
            if use_seer: deck.append("🔮 ผู้หยั่งรู้")
            if use_doctor: deck.append("🛡️ หมอ")
            if use_hunter: deck.append("🏹 พราน")
            if use_witch: deck.append("🧪 แม่มด")
            deck.extend(["🏡 ชาวบ้าน"] * num_villagers)
            
            random.shuffle(deck)
            
            st.session_state.players = player_list
            st.session_state.alive_players = player_list.copy()
            st.session_state.player_roles = {player_list[i]: deck[i] for i in range(num_players)}
            st.session_state.game_stage = 'ASSIGN'
            st.session_state.current_assign_idx = 0
            st.session_state.show_role = False
            st.rerun()

# ==========================================
# STAGE 2: ASSIGN (สลับกันดูการ์ดบทบาท)
# ==========================================
elif st.session_state.game_stage == 'ASSIGN':
    idx = st.session_state.current_assign_idx
    total = len(st.session_state.players)
    
    if idx < total:
        current_player = st.session_state.players[idx]
        
        st.subheader(f"📲 ส่งแท็บเล็ต/มือถือให้: **{current_player}** ({idx+1}/{total})")
        st.caption("เตือนเพื่อนคนอื่นให้หลับตาหรือหันไปทางอื่นก่อนกดดูบทบาท!")
        
        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
        if not st.session_state.show_role:
            if st.button(f"👁️ กดเพื่อเปิดดูบทบาทของ {current_player}", type="primary", use_container_width=True):
                st.session_state.show_role = True
                st.rerun()
        else:
            role = st.session_state.player_roles[current_player]
            st.markdown(f"<h2 style='text-align: center; color: #f59e0b;'>{role}</h2>", unsafe_allow_html=True)
            
            if "หมาป่า" in role:
                st.write("🎯 **เป้าหมาย:** สังหารชาวบ้านเนียนๆ ร่วมกับหมาป่าตัวอื่น")
            elif "ผู้หยั่งรู้" in role:
                st.write("🎯 **เป้าหมาย:** ส่องดูความจริงในตอนกลางคืนเพื่อหาหมาป่า")
            elif "หมอ" in role:
                st.write("🎯 **เป้าหมาย:** เลือกปกป้องคนที่คาดว่าจะโดนหมาป่าฆ่า")
            else:
                st.write("🎯 **เป้าหมาย:** จับผิดและโหวตประหารหมาป่าให้หมด")
                
            if st.button("🔒 จำได้แล้ว! ซ่อนบทบาทและส่งให้คนถัดไป", use_container_width=True):
                st.session_state.show_role = False
                st.session_state.current_assign_idx += 1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("✅ ทุกคนรับรู้บทบาทของตัวเองเรียบร้อยแล้ว!")
        if st.button("🌙 เริ่มเข้าสู่คืนแรก (Start Night 1)", type="primary", use_container_width=True):
            st.session_state.game_stage = 'NIGHT'
            st.session_state.night_actions = {}
            st.rerun()

# ==========================================
# STAGE 3: NIGHT PHASE (ช่วงกลางคืน)
# ==========================================
elif st.session_state.game_stage == 'NIGHT':
    st.markdown(f"<h2 class='night-title'>🌙 คืนที่ {st.session_state.day_count} - ทุกคนหลับตา!</h2>", unsafe_allow_html=True)
    st.warning("⚠️ ให้ผู้ถือเครื่องคุมเกมอ่านเสียงดังๆ ตามลำดับด้านล่างนี้:")
    
    # 1. หมาป่า
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.write("🔊 **พูดออกเสียง:** *'หมาป่าทุกคน... ลืมตาขึ้นมาและชี้เป้าคนที่ต้องการฆ่าคืนนี้'*")
    wolves_alive = [p for p in st.session_state.alive_players if "หมาป่า" in st.session_state.player_roles[p]]
    st.caption(f"(หมาป่าที่ยังรอดอยู่: {', '.join(wolves_alive)})")
    
    target_kill = st.selectbox("เลือกเป้าหมายที่หมาป่าตัดสินใจฆ่า:", ["-- เลือกเป้าหมาย --"] + st.session_state.alive_players)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. หมอ (ถ้ามี)
    target_heal = None
    has_doctor = any("หมอ" in st.session_state.player_roles[p] for p in st.session_state.alive_players)
    if has_doctor:
        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
        st.write("🔊 **พูดออกเสียง:** *'หมอ... ลืมตาขึ้นมาและเลือกคนที่ต้องการคุ้มกันคืนนี้'*")
        target_heal = st.selectbox("เลือกคนที่หมอต้องการคุ้มกัน:", ["-- เลือกคนที่คุ้มกัน --"] + st.session_state.alive_players)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # 3. ผู้หยั่งรู้ (ถ้ามี)
    has_seer = any("ผู้หยั่งรู้" in st.session_state.player_roles[p] for p in st.session_state.alive_players)
    if has_seer:
        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
        st.write("🔊 **พูดออกเสียง:** *'ผู้หยั่งรู้... ลืมตาขึ้นมาและชี้คนที่ต้องการส่องดูบทบาท'*")
        seer_target = st.selectbox("ผู้หยั่งรู้เลือกส่องดูบทบาทของ:", ["-- เลือกคนที่ต้องการส่อง --"] + st.session_state.alive_players, key="seer_s")
        if seer_target != "-- เลือกคนที่ต้องการส่อง --":
            is_wolf = "หมาป่า" in st.session_state.player_roles[seer_target]
            if is_wolf:
                st.error(f"🔮 คำตอบสำหรับผู้หยั่งรู้: **{seer_target} คือ หมาป่า! 🐺** (ให้ Moderator ชูนิ้วโป้งลง)")
            else:
                st.success(f"🔮 คำตอบสำหรับผู้หยั่งรู้: **{seer_target} คือ ฝ่ายดี/ชาวบ้าน 🟢** (ให้ Moderator ชูนิ้วโป้งขึ้น)")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("☀️ จบช่วงกลางคืน -> รุ่งเช้า!", type="primary", use_container_width=True):
        if target_kill == "-- เลือกเป้าหมาย --":
            st.error("กรุณาเลือกเป้าหมายที่หมาป่าฆ่าก่อนครับ!")
        else:
            # ประมวลผลการฆ่า
            killed_player = target_kill
            if target_heal and target_heal == target_kill:
                killed_player = None # หมอช่วยทัน
                
            st.session_state.last_night_killed = killed_player
            if killed_player:
                st.session_state.alive_players.remove(killed_player)
                
            st.session_state.game_stage = 'DAY'
            st.rerun()

# ==========================================
# STAGE 4: DAY PHASE (ช่วงกลางวัน & ถกเถียง)
# ==========================================
elif st.session_state.game_stage == 'DAY':
    st.markdown(f"<h2 class='day-title'>☀️ เช้าวันที่ {st.session_state.day_count} - ทุกคนลืมตา!</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    killed = st.session_state.last_night_killed
    if killed:
        st.error(f"💀 เมื่อคืนนี้เกิดเหตุร้าย! **{killed}** ถูกหมาป่าสังหารเสียชีวิต!")
    else:
        st.success("🕊️ เป็นคืนที่เงียบสงบ! เมื่อคืนนี้ **ไม่มีใครเสียชีวิต** (หมอช่วยไว้ทัน)")
    st.markdown("</div>", unsafe_allow_html=True)

    # ตรวจสอบเงื่อนไขจบเกม
    wolves_left = [p for p in st.session_state.alive_players if "หมาป่า" in st.session_state.player_roles[p]]
    villagers_left = [p for p in st.session_state.alive_players if "หมาป่า" not in st.session_state.player_roles[p]]
    
    if len(wolves_left) == 0:
        st.balloons()
        st.success("🎉 ฝ่ายชาวบ้านเป็นฝ่ายชนะ! มนุษย์หมาป่าถูกกำจัดหมดแล้ว!")
        st.session_state.game_stage = 'GAMEOVER'
    elif len(wolves_left) >= len(villagers_left):
        st.error("🐺 ฝ่ายมนุษย์หมาป่าเป็นฝ่ายชนะ! จำนวนหมาป่าเท่ากับหรือมากกว่าชาวบ้านแล้ว!")
        st.session_state.game_stage = 'GAMEOVER'
    else:
        st.subheader("🗣️ ช่วงอภิปรายและจับผิด (Discussion)")
        st.write(f"ผู้เล่นที่เหลืออยู่ ({len(st.session_state.alive_players)} คน): **{', '.join(st.session_state.alive_players)}**")
        
        # ตัวจับเวลาถอยหลัง
        if st.button("⏱️ เริ่มจับเวลาคุย 3 นาที"):
            with st.spinner("กำลังจับเวลา... คุยจับผิดกันได้เลย!"):
                time.sleep(3) # จำลอง
                st.warning("⏰ หมดเวลาถกเถียง! เตรียมตัวเข้าสู่การโหวตประหาร")

        if st.button("🗳️ เข้าสู่ช่วงลงมติโหวตประหาร (Voting)", type="primary", use_container_width=True):
            st.session_state.game_stage = 'VOTE'
            st.rerun()

# ==========================================
# STAGE 5: VOTE (โหวตประหาร)
# ==========================================
elif st.session_state.game_stage == 'VOTE':
    st.subheader("🗳️ ลงมติประหารชีวิต")
    st.write("ชี้เป้าคนที่สงสัยที่สุดพร้อมกัน แล้วเลือกว่าใครได้คะแนนโหวตสูงสุด:")
    
    executed_player = st.selectbox("เลือกคนที่ถูกโหวตประหารออก:", ["-- เสมอ / ไม่ประหารใคร --"] + st.session_state.alive_players)
    
    if st.button("⚖️ ยืนยันผลการประหาร", type="primary", use_container_width=True):
        if executed_player != "-- เสมอ / ไม่ประหารใคร --":
            st.session_state.alive_players.remove(executed_player)
            role = st.session_state.player_roles[executed_player]
            st.warning(f"⚰️ **{executed_player}** โดนประหารชีวิต! (บทบาทจริงคือ: **{role}**)")
        else:
            st.info("🕊️ วันนี้ไม่มีใครถูกประหารชีวิต")
            
        st.session_state.day_count += 1
        st.session_state.game_stage = 'NIGHT'
        st.rerun()

# ==========================================
# STAGE 6: GAMEOVER
# ==========================================
elif st.session_state.game_stage == 'GAMEOVER':
    st.subheader("🏆 จบเกม! เฉลยบทบาทของทุกคน")
    
    results = [{"ชื่อ": p, "บทบาท": st.session_state.player_roles[p], "สถานะ": "รอดชีวิต" if p in st.session_state.alive_players else "เสียชีวิต"} for p in st.session_state.players]
    st.table(results)
    
    if st.button("🔄 เริ่มเล่นใหม่อีกรอบ", type="primary", use_container_width=True):
        st.session_state.game_stage = 'SETUP'
        st.session_state.day_count = 1
        st.rerun()
