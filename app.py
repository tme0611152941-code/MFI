import streamlit as st
import random
import time

# ==================================================
# 1. ตั้งค่าหน้าเว็บ & Theme
# ==================================================
st.set_page_config(
    page_title="Ultimate Werewolf - PIN Edition",
    page_icon="🐺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def apply_theme(phase):
    if "NIGHT" in phase or phase == "NIGHT_INPUT":
        st.markdown(
            """
            <style>
            .stApp { background: linear-gradient(180deg, #090A0F 0%, #171B26 100%); color: #E2E8F0; }
            .stButton>button { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); color: white; border: none; border-radius: 12px; padding: 12px 24px; font-weight: bold; }
            .role-card { background: rgba(30, 41, 59, 0.7); border: 2px solid #6366F1; border-radius: 16px; padding: 20px; text-align: center; }
            </style>
            """, unsafe_allow_html=True
        )
    elif phase == "DAY":
        st.markdown(
            """
            <style>
            .stApp { background: linear-gradient(180deg, #FEF3C7 0%, #FDE68A 100%); color: #1E293B; }
            .stButton>button { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; border: none; border-radius: 12px; padding: 12px 24px; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .stApp { background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%); color: #F8FAFC; }
            .stButton>button { background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); color: white; border: none; border-radius: 12px; padding: 10px 20px; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True
        )

# ==================================================
# 2. ระบบ Session State
# ==================================================
if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"
    st.session_state.players = []
    st.session_state.roles = []
    st.session_state.pins = {}          # เก็บ PIN แต่ละคน {player: pin}
    st.session_state.status = []        # สถานะ มีชีวิต(True) / ตาย(False)
    st.session_state.current_peek_idx = 0
    st.session_state.card_revealed = False
    
    # ข้อมูลการกระทำในคืนนั้นๆ
    st.session_state.night_current_idx = 0
    st.session_state.wolf_votes = {}    # {target: count}
    st.session_state.seer_logs = {}     # {seer_name: result_text}
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_heal_used = False
    st.session_state.witch_poison_used = False
    st.session_state.witch_saved_tonight = False
    st.session_state.winner = ""

apply_theme(st.session_state.phase)

# ==================================================
# 1. SETUP (ตั้งชื่อ + เลือกบทบาท)
# ==================================================
if st.session_state.phase == "SETUP":
    st.title("🐺 Ultimate Werewolf")
    st.caption("✨ ระบบ PIN ล็อกอินทำภารกิจส่วนตัว เนียนที่สุด ไร้คนจับได้")
    
    st.subheader("📝 1. ตั้งชื่อผู้เล่น")
    num_players = st.number_input("จำนวนผู้เล่นทั้งหมด (คน):", min_value=4, max_value=20, value=6)
    
    player_names = []
    cols = st.columns(2)
    for i in range(num_players):
        col = cols[i % 2]
        name = col.text_input(f"คนที่ {i+1}:", value=f"ผู้เล่น_{i+1}", key=f"p_{i}")
        player_names.append(name.strip())

    st.write("---")
    st.subheader("🎭 2. เลือกบทบาทในเกม")
    col1, col2 = st.columns(2)
    with col1:
        num_wolves = st.slider("🐺 หมาป่า (Werewolf):", 1, 4, 1 if num_players < 8 else 2)
        has_seer = st.checkbox("🔮 หมอดู (Seer)", value=True)
        has_guard = st.checkbox("🛡️ บอดี้การ์ด (Bodyguard)", value=True)
    with col2:
        has_witch = st.checkbox("🧙‍♀️ แม่มด (Witch)", value=True)
        has_fool = st.checkbox("🤡 ตัวตลก (Fool)", value=num_players >= 7)

    special_count = num_wolves + sum([has_seer, has_guard, has_witch, has_fool])
    villagers_count = num_players - special_count

    if villagers_count < 0:
        st.error(f"❌ บทบาทพิเศษเกินจำนวนผู้เล่น! (เลือกไว้ {special_count} บท)")
    else:
        st.info(f"📊 สรุป: หมาป่า {num_wolves} | บทพิเศษ {special_count - num_wolves} | ชาวบ้าน {villagers_count}")
        
        if st.button("🎲 เริ่มสุ่มบทบาท & ตั้งรหัส PIN"):
            roles_pool = ['Werewolf'] * num_wolves
            if has_seer: roles_pool.append('Seer')
            if has_guard: roles_pool.append('Bodyguard')
            if has_witch: roles_pool.append('Witch')
            if has_fool: roles_pool.append('Fool')
            roles_pool.extend(['Villager'] * villagers_count)

            random.shuffle(roles_pool)

            st.session_state.players = player_names
            st.session_state.roles = roles_pool
            st.session_state.status = [True] * num_players
            st.session_state.current_peek_idx = 0
            st.session_state.card_revealed = False
            st.session_state.phase = "CHECK_ROLES"
            st.rerun()

# ==================================================
# 2. CHECK ROLES & SET PIN (ดูบทบาท + ตั้ง PIN)
# ==================================================
elif st.session_state.phase == "CHECK_ROLES":
    idx = st.session_state.current_peek_idx
    current_player = st.session_state.players[idx]

    st.title("🎴 ดูบทบาทลับ & ตั้งรหัส PIN")
    st.subheader(f"📲 คิวของ: **{current_player}**")

    if not st.session_state.card_revealed:
        st.warning(f"👉 ส่ง iPad ให้ **{current_player}** แล้วกดปุ่มเพื่อเปิดการ์ด")
        if st.button(f"👁️ เปิดดูบทบาทของ {current_player}"):
            st.session_state.card_revealed = True
            st.rerun()
    else:
        role = st.session_state.roles[idx]
        st.markdown(f"""
            <div class="role-card">
                <h2>คุณได้บทบาท: {role}</h2>
                <p>จำบทบาทนี้ไว้ให้ดี และอย่าให้เพื่อนข้างๆ เห็นหน้าจอ!</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("🔑 ตั้งรหัส PIN ส่วนตัว 4 หลัก (ไว้ใช้เข้าทำภารกิจตอนกลางคืน)")
        pin_input = st.text_input("กรอกรหัส PIN (ตัวเลข 4 หลัก):", type="password", max_chars=4, key=f"pin_set_{idx}")

        if st.button("🔒 ยืนยันรหัส PIN & ส่งต่อ iPad"):
            if len(pin_input) == 4 and pin_input.isdigit():
                st.session_state.pins[current_player] = pin_input
                st.session_state.card_revealed = False
                
                if st.session_state.current_peek_idx + 1 < len(st.session_state.players):
                    st.session_state.current_peek_idx += 1
                else:
                    # ตั้ง PIN ครบทุกคนแล้ว -> เข้าสู่ช่วงกลางคืน
                    st.session_state.phase = "START_NIGHT"
                st.rerun()
            else:
                st.error("⚠️ กรุณากรอกรหัส PIN เป็นตัวเลข 4 หลักให้ถูกต้อง")

# ==================================================
# 3. START NIGHT (เตรียมวนส่ง iPad ช่วงกลางคืน)
# ==================================================
elif st.session_state.phase == "START_NIGHT":
    st.title("🌙 ราตรีคลี่คลุม... ได้เวลาทำภารกิจลับ")
    st.info("ส่ง iPad วนให้เพื่อนทีละคนตามรายชื่อ เพื่อกรอก PIN เข้าไปทำภารกิจประจำคืน")
    
    st.session_state.night_current_idx = 0
    st.session_state.wolf_votes = {}
    st.session_state.seer_logs = {}
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_saved_tonight = False
    
    if st.button("🚀 เริ่มต้นส่ง iPad ทำภารกิจ"):
        st.session_state.phase = "NIGHT_INPUT"
        st.rerun()

# ==================================================
# 4. NIGHT INPUT (กรอก PIN ทำภารกิจทีละคน)
# ==================================================
elif st.session_state.phase == "NIGHT_INPUT":
    idx = st.session_state.night_current_idx
    current_player = st.session_state.players[idx]
    is_alive = st.session_state.status[idx]

    st.title("🌙 คืนอันเงียบสงบ")
    st.subheader(f"📲 ยื่น iPad ให้: **{current_player}**")

    if not is_alive:
        st.error(f"💀 {current_player} เสียชีวิตแล้ว (ข้ามภารกิจ)")
        if st.button("ส่งต่อให้คนถัดไป ➡️"):
            if st.session_state.night_current_idx + 1 < len(st.session_state.players):
                st.session_state.night_current_idx += 1
            else:
                st.session_state.phase = "DAY"
            st.rerun()
    else:
        pin_attempt = st.text_input("🔑 กรอกรหัส PIN 4 หลักของคุณ:", type="password", max_chars=4, key=f"night_pin_{idx}")
        
        if st.button("🔓 ล็อกอินทำภารกิจ"):
            if pin_attempt == st.session_state.pins[current_player]:
                st.session_state.phase = "NIGHT_TASK"
                st.rerun()
            else:
                st.error("❌ รหัส PIN ไม่ถูกต้อง!")

# ==================================================
# 5. NIGHT TASK (หน้าภารกิจลับตามบทบาท)
# ==================================================
elif st.session_state.phase == "NIGHT_TASK":
    idx = st.session_state.night_current_idx
    current_player = st.session_state.players[idx]
    role = st.session_state.roles[idx]

    st.title(f"🎭 ภารกิจลับของ: {current_player}")
    st.caption(f"บทบาทของคุณคือ: **{role}**")
    st.write("---")

    alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]

    # --- ภารกิจหมาป่า ---
    if role == 'Werewolf':
        st.subheader("🐺 เลือกเหยื่อที่จะสังหารในคืนนี้:")
        target = st.radio("เลือกเหยื่อ:", alive_players, key="wolf_target")
        if st.button("✅ ยืนยันการฆ่า"):
            st.session_state.wolf_votes[target] = st.session_state.wolf_votes.get(target, 0) + 1
            st.success("บันทึกภารกิจเรียบร้อย!")
            time.sleep(1)
            # ถัดไป
            if st.session_state.night_current_idx + 1 < len(st.session_state.players):
                st.session_state.night_current_idx += 1
                st.session_state.phase = "NIGHT_INPUT"
            else:
                st.session_state.phase = "DAY"
            st.rerun()

    # --- ภารกิจหมอดู ---
    elif role == 'Seer':
        st.subheader("🔮 เลือกคนที่ต้องการส่องดูบทบาท (1 คน):")
        seer_target = st.selectbox("เลือกผู้เล่น:", [p for p in st.session_state.players if p != current_player])
        
        if st.button("🔍 ตรวจสอบ"):
            t_idx = st.session_state.players.index(seer_target)
            is_wolf = (st.session_state.roles[t_idx] == 'Werewolf')
            res = "🐺 เป็นหมาป่า!" if is_wolf else "🧑 เป็นคนธรรมดา"
            st.info(f"ผลการส่อง: **{seer_target}** -> {res}")
            
            if st.button("✅ รับทราบ & ปิดหน้าจอ"):
                if st.session_state.night_current_idx + 1 < len(st.session_state.players):
                    st.session_state.night_current_idx += 1
                    st.session_state.phase = "NIGHT_INPUT"
                else:
                    st.session_state.phase = "DAY"
                st.rerun()

    # --- ภารกิจบอดี้การ์ด ---
    elif role == 'Bodyguard':
        st.subheader("🛡️ เลือกคนที่ต้องการปกป้องคืนนี้:")
        guard_target = st.selectbox("เลือกผู้เล่น:", alive_players)
        if st.button("✅ ยืนยันการปกป้อง"):
            st.session_state.protected_player = guard_target
            st.success("บันทึกการปกป้องเรียบร้อย!")
            time.sleep(1)
            if st.session_state.night_current_idx + 1 < len(st.session_state.players):
                st.session_state.night_current_idx += 1
                st.session_state.phase = "NIGHT_INPUT"
            else:
                st.session_state.phase = "DAY"
            st.rerun()

    # --- ภารกิจแม่มด ---
    elif role == 'Witch':
        st.subheader("🧙‍♀️ แม่มดใช้เวทมนตร์:")
        
        # คำนวณเหยื่อหมาป่าคร่าวๆ ให้แม่มดเห็น
        top_wolf_target = max(st.session_state.wolf_votes, key=st.session_state.wolf_votes.get) if st.session_state.wolf_votes else None
        if top_wolf_target:
            st.warning(f"💡 คืนนี้หมาป่าเล็งสังหาร: **{top_wolf_target}**")
        else:
            st.info("💡 คืนนี้ยังไม่มีเหยื่อหมาป่าชัดเจน")

        use_heal = False
        if not st.session_state.witch_heal_used and top_wolf_target:
            use_heal = st.checkbox(f"🧪 ใช้ยาชุบชีวิตช่วย {top_wolf_target}")

        use_poison = False
        poison_target = None
        if not st.session_state.witch_poison_used:
            use_poison = st.checkbox("☠️ ใช้ยาพิษสังหารผู้เล่น")
            if use_poison:
                poison_target = st.selectbox("เลือกคนที่ต้องการวางยาพิษ:", alive_players)

        if st.button("✅ ยืนยันการใช้ยา"):
            if use_heal:
                st.session_state.witch_saved_tonight = True
                st.session_state.witch_heal_used = True
            if use_poison and poison_target:
                st.session_state.witch_kill_target = poison_target
                st.session_state.witch_poison_used = True

            st.success("บันทึกภารกิจแม่มดเรียบร้อย!")
            time.sleep(1)
            if st.session_state.night_current_idx + 1 < len(st.session_state.players):
                st.session_state.night_current_idx += 1
                st.session_state.phase = "NIGHT_INPUT"
            else:
                st.session_state.phase = "DAY"
            st.rerun()

    # --- ภารกิจชาวบ้าน / ตัวตลก / บทอื่นๆ (ปุ่มหลอกเนียนๆ) ---
    else:
        st.subheader("🧑 ชาวบ้านธรรมดา / บทบาททั่วไป")
        st.info("คุณไม่มีพลังพิเศษในตอนกลางคืน กดปุ่มด้านล่างเพื่อยืนยันการทำภารกิจเนียนๆ")
        if st.button("✅ ยืนยันการทำภารกิจเรียบร้อย"):
            st.success("บันทึกข้อมูลเรียบร้อย!")
            time.sleep(1)
            if st.session_state.night_current_idx + 1 < len(st.session_state.players):
                st.session_state.night_current_idx += 1
                st.session_state.phase = "NIGHT_INPUT"
            else:
                st.session_state.phase = "DAY"
            st.rerun()

# ==================================================
# 6. DAY PHASE (ประมวลผลตอนเช้า)
# ==================================================
elif st.session_state.phase == "DAY":
    st.title("☀️ เช้าวันใหม่ - สรุปผลคืนที่ผ่านมา")
    
    # คำนวณคนตายจากหมาป่า
    dead_tonight = []
    final_wolf_target = max(st.session_state.wolf_votes, key=st.session_state.wolf_votes.get) if st.session_state.wolf_votes else None

    if final_wolf_target:
        # เช็คว่าโดนการ์ดปกป้อง หรือแม่มดช่วยไหม
        if final_wolf_target != st.session_state.protected_player and not st.session_state.witch_saved_tonight:
            w_idx = st.session_state.players.index(final_wolf_target)
            if st.session_state.status[w_idx]:
                st.session_state.status[w_idx] = False
                dead_tonight.append(final_wolf_target)

    # คำนวณคนตายจากยาพิษแม่มด
    if st.session_state.witch_kill_target:
        p_idx = st.session_state.players.index(st.session_state.witch_kill_target)
        if st.session_state.status[p_idx]:
            st.session_state.status[p_idx] = False
            dead_tonight.append(st.session_state.witch_kill_target)

    if len(dead_tonight) == 0:
        st.success("🎉 เป็นข่าวดี! เมื่อคืนไม่มีใครเสียชีวิตเลย")
    else:
        st.error(f"💀 ผู้เสียชีวิตในคืนนี้ได้แก่: {', '.join(dead_tonight)}")

    # ตรวจสอบเงื่อนไขชนะ
    wolves = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] == 'Werewolf')
    villagers = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] != 'Werewolf')

    if wolves == 0:
        st.session_state.winner = "🎉 ฝ่ายชาวบ้านชนะ! (Villagers Win)"
        st.session_state.phase = "GAMEOVER"
        st.rerun()
    elif wolves >= villagers:
        st.session_state.winner = "🐺 ฝ่ายหมาป่าชนะ! (Werewolves Win)"
        st.session_state.phase = "GAMEOVER"
        st.rerun()

    if st.button("🗳️ พูดคุยเสร็จแล้ว -> ไปช่วงโหวตประหาร"):
        st.session_state.phase = "VOTING"
        st.rerun()

# ==================================================
# 7. VOTING (โหวตประหาร)
# ==================================================
elif st.session_state.phase == "VOTING":
    st.title("🗳️ ช่วงโหวตประหารชีวิต")
    alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
    
    vote_target = st.selectbox("เลือกคนถูกโหวตประหาร:", alive_players)
    
    if st.button("⚖️ ยืนยันผลประหารชีวิต"):
        v_idx = st.session_state.players.index(vote_target)
        st.session_state.status[v_idx] = False
        role_voted = st.session_state.roles[v_idx]
        
        st.warning(f"⚖️ **{vote_target}** ถูกประหารชีวิต! (บทบาทจริงคือ: {role_voted})")
        
        if role_voted == 'Fool':
            st.session_state.winner = f"🤡 **{vote_target} (ตัวตลก)** ชนะเกม! เพราะปั่นจนโดนโหวตออกสำเร็จ!"
            st.session_state.phase = "GAMEOVER"
            st.rerun()

        wolves = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] == 'Werewolf')
        villagers = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] != 'Werewolf')

        if wolves == 0:
            st.session_state.winner = "🎉 ฝ่ายชาวบ้านชนะ!"
            st.session_state.phase = "GAMEOVER"
        elif wolves >= villagers:
            st.session_state.winner = "🐺 ฝ่ายหมาป่าชนะ!"
            st.session_state.phase = "GAMEOVER"
        else:
            st.session_state.phase = "START_NIGHT"
        
        time.sleep(3)
        st.rerun()

# ==================================================
# 8. GAME OVER
# ==================================================
elif st.session_state.phase == "GAMEOVER":
    st.balloons()
    st.title("🏆 GAME OVER")
    st.header(st.session_state.winner)
    
    st.write("---")
    st.subheader("📜 เฉลยบทบาททุกคน:")
    for i in range(len(st.session_state.players)):
        st_text = "🟢 รอดชีวิต" if st.session_state.status[i] else "💀 เสียชีวิต"
        st.write(f"- **{st.session_state.players[i]}**: {st.session_state.roles[i]} ({st_text})")

    if st.button("🔄 เล่นใหม่อีกรอบ"):
        st.session_state.phase = "SETUP"
        st.rerun()
