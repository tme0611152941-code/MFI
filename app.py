import streamlit as st
import random
import time

# --------------------------------------------------
# ตั้งค่าหน้าเว็บ
# --------------------------------------------------
st.set_page_config(page_title="Ultimate Werewolf", page_icon="🐺", layout="centered")

st.title("🐺 Ultimate Werewolf Game")
st.write("ระบบจัดการเกมหมาป่า: กรอกชื่อเพื่อน + สุ่มบทบาทครบชุด!")

# --------------------------------------------------
# ฟังก์ชันเล่นเสียงเตือนผ่านเบราว์เซอร์
# --------------------------------------------------
def play_sound(sound_type):
    if sound_type == "morning":
        sound_url = "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg"
    elif sound_type == "action":
        sound_url = "https://actions.google.com/sounds/v1/beeps/short_beep_high.ogg"
    elif sound_type == "gameover":
        sound_url = "https://actions.google.com/sounds/v1/cartoon/clapping.ogg"
    
    st.components.v1.html(
        f"""
        <audio autoplay style="display:none;">
          <source src="{sound_url}" type="audio/ogg">
        </audio>
        """,
        height=0,
    )

# --------------------------------------------------
# ระบบ Session State
# --------------------------------------------------
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.phase = "SETUP"
    st.session_state.players = []
    st.session_state.roles = []
    st.session_state.status = []
    st.session_state.lovers = [] # คู่รักจาก Cupid
    st.session_state.witch_heal = True
    st.session_state.witch_poison = True
    st.session_state.target_wolf = None
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_saved = False
    st.session_state.winner = ""

# ==================================================
# 1. หน้าตั้งชื่อผู้เล่นและเลือกบทบาท (SETUP)
# ==================================================
if st.session_state.phase == "SETUP":
    st.subheader("📝 1. กรอกชื่อผู้เล่น")
    
    num_players = st.number_input("จำนวนผู้เล่นทั้งหมด (คน):", min_value=4, max_value=20, value=6)
    
    st.write("---")
    st.write("👤 **ใส่ชื่อเพื่อนแต่ละคน:**")
    
    player_names = []
    cols = st.columns(2)
    for i in range(num_players):
        col = cols[i % 2]
        default_name = f"เพื่อน_{i+1}"
        name = col.text_input(f"คนที่ {i+1}:", value=default_name, key=f"p_{i}")
        player_names.append(name.strip())

    st.write("---")
    st.subheader("🎭 2. เลือกบทบาทที่จะให้มีในเกม")
    
    col1, col2 = st.columns(2)
    with col1:
        num_wolves = st.slider("🐺 จำนวนหมาป่า:", 1, 4, 1 if num_players < 8 else 2)
        has_seer = st.checkbox("🔮 หมอดู (Seer)", value=True)
        has_guard = st.checkbox("🛡️ บอดี้การ์ด (Bodyguard)", value=True)
        has_witch = st.checkbox("🧙‍♀️ แม่มด (Witch)", value=True)
    
    with col2:
        has_hunter = st.checkbox("🏹 นายพราน (Hunter)", value=True)
        has_cupid = st.checkbox("💘 คิวปิด (Cupid)", value=num_players >= 7)
        has_fool = st.checkbox("🤡 ตัวตลก (Fool / Jester)", value=num_players >= 7)
        has_girl = st.checkbox("👶 เด็กน้อย (Little Girl)", value=False)

    # คำนวณจำนวนบทบาทพิเศษ
    special_count = num_wolves
    if has_seer: special_count += 1
    if has_guard: special_count += 1
    if has_witch: special_count += 1
    if has_hunter: special_count += 1
    if has_cupid: special_count += 1
    if has_fool: special_count += 1
    if has_girl: special_count += 1

    villagers_count = num_players - special_count

    if villagers_count < 0:
        st.error(f"❌ บทบาทที่เลือกเกินจำนวนคนเล่น! (ผู้เล่น {num_players} คน แต่เลือกไป {special_count} บทบาท)")
    else:
        st.info(f"💡 สรุป: หมาป่า {num_wolves} คน | บทพิเศษ {special_count - num_wolves} คน | ชาวบ้าน {villagers_count} คน")
        
        if st.button("🎲 สุ่มแจกบทบาทและเริ่มเกม!"):
            # สร้าง List รวมบทบาททั้งหมด
            roles_pool = ['Werewolf'] * num_wolves
            if has_seer: roles_pool.append('Seer')
            if has_guard: roles_pool.append('Bodyguard')
            if has_witch: roles_pool.append('Witch')
            if has_hunter: roles_pool.append('Hunter')
            if has_cupid: roles_pool.append('Cupid')
            if has_fool: roles_pool.append('Fool')
            if has_girl: roles_pool.append('Little Girl')
            roles_pool.extend(['Villager'] * villagers_count)

            # สุ่มบทบาท
            random.shuffle(roles_pool)

            # บันทึกข้อมูล
            st.session_state.players = player_names
            st.session_state.roles = roles_pool
            st.session_state.status = [True] * num_players
            st.session_state.game_started = True
            st.session_state.phase = "CHECK_ROLES"
            st.rerun()

# ==================================================
# 2. หน้าวนกันแอบดูบทบาทตัวเอง (CHECK ROLES)
# ==================================================
elif st.session_state.phase == "CHECK_ROLES":
    st.subheader("🔍 แอบดูบทบาทตัวเอง (วนเปิดทีละคน)")
    st.warning("⚠️ แนะนำให้ยื่นหน้าจอให้เพื่อนเปิดดูทีละคน แล้วกดซ่อนก่อนส่งต่อ!")

    selected_player = st.selectbox("เลือกชื่อของคุณ:", st.session_state.players)
    idx = st.session_state.players.index(selected_player)

    with st.expander(f"👉 คลิกที่นี่เพื่อเปิดดูบทบาทของคุณ ({selected_player})"):
        role = st.session_state.roles[idx]
        
        role_descriptions = {
            'Werewolf': ("🐺 WEREWOLF (หมาป่า)", "ตื่นมาตอนกลางคืนเพื่อเลือกฆ่าชาวบ้าน!"),
            'Seer': ("🔮 SEER (หมอดู)", "ตื่นมาส่องดูผู้เล่นอื่นในตอนกลางคืนว่าเป็นหมาป่าหรือไม่"),
            'Bodyguard': ("🛡️ BODYGUARD (บอดี้การ์ด)", "เลือกปกป้องผู้เล่น 1 คนในตอนกลางคืนไม่ให้โดนหมาป่ากัด"),
            'Witch': ("🧙‍♀️ WITCH (แม่มด)", "มียาชุบชีวิต 1 ขวด และยาพิษ 1 ขวด ใช้ได้ขวดละครั้ง"),
            'Hunter': ("🏹 HUNTER (นายพราน)", "ถ้าคุณตาย คุณสามารถยิงสังหารคนอื่นตายตามได้ 1 คน"),
            'Cupid': ("💘 CUPID (คิวปิด)", "ผูกดวงคู่รัก 2 คนในคืนแรก ถ้าคนหนึ่งตาย อีกคนจะตายตามทันที!"),
            'Fool': ("🤡 FOOL / JESTER (ตัวตลก)", "เงื่อนไขชนะพิเศษ: ต้องปั่นให้คนอื่นโหวตประหารชีวิตคุณ!"),
            'Little Girl': ("👶 LITTLE GIRL (เด็กน้อย)", "แอบลืมตาดูหมาป่าได้ แต่ถ้าหมาป่าจับได้จะตายทันที"),
            'Villager': ("🧑 VILLAGER (ชาวบ้าน)", "ไม่มีพลังพิเศษ ใช้การสังเกตและโหวตจับหมาป่าในตอนกลางวัน")
        }
        
        title, desc = role_descriptions.get(role, ("🧑 VILLAGER", "ชาวบ้านธรรมดา"))
        st.markdown(f"### **{title}**")
        st.write(f"**ภารกิจ:** {desc}")

    st.write("---")
    if st.button("🌙 เมื่อทุกคนดูบทบาทครบแล้ว -> เริ่มกลางคืนแรก"):
        # ถ้ามี Cupid ให้เข้าเฟส Cupid ก่อน
        if 'Cupid' in st.session_state.roles:
            st.session_state.phase = "NIGHT_CUPID"
        else:
            st.session_state.phase = "NIGHT_WOLF"
        st.rerun()

# ==================================================
# 3. ช่วงกลางคืน (NIGHT PHASES)
# ==================================================
else:
    # เมนูเฉลยสำหรับคนคุมเกม
    with st.expander("👁️ เฉลยบทบาททั้งหมด (สำหรับคนคุมเกมดู)"):
        for i in range(len(st.session_state.players)):
            st_text = "🟢 รอด" if st.session_state.status[i] else "💀 ตายแล้ว"
            st.write(f"**{st.session_state.players[i]}**: {st.session_state.roles[i]} ({st_text})")
        if st.session_state.lovers:
            st.write(f"💘 **คู่รัก:** {st.session_state.lovers[0]} ❤️ {st.session_state.lovers[1]}")

    st.divider()

    # --- 💘 คิวปิดจับคู่รัก (คืนแรกคืนเดียว) ---
    if st.session_state.phase == "NIGHT_CUPID":
        st.subheader("🌙 กลางคืน: [💘 คิวปิด ตื่นขึ้นมา]")
        st.write("เลือกผู้เล่น 2 คนให้กลายเป็นคู่รักกัน:")
        
        lover1 = st.selectbox("คู่รักคนที่ 1:", st.session_state.players, index=0)
        lover2 = st.selectbox("คู่รักคนที่ 2:", st.session_state.players, index=1)
        
        if st.button("ผูกดวงคู่รัก"):
            st.session_state.lovers = [lover1, lover2]
            play_sound("action")
            st.session_state.phase = "NIGHT_WOLF"
            st.rerun()

    # --- 🐺 หมาป่าเลือกเหยื่อ ---
    elif st.session_state.phase == "NIGHT_WOLF":
        st.subheader("🌙 กลางคืน: [🐺 หมาป่า ตื่นขึ้นมา]")
        st.write("เลือกคนที่หมาป่าต้องการสังหารคืนนี้:")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        target = st.radio("เลือกเหยื่อ:", alive_players, key="wolf_choice")
        
        if st.button("ยืนยันการฆ่าของหมาป่า"):
            st.session_state.target_wolf = target
            play_sound("action")
            st.session_state.phase = "NIGHT_SEER" if 'Seer' in st.session_state.roles else "NIGHT_GUARD"
            st.rerun()

    # --- 🔮 หมอดูส่องบทบาท ---
    elif st.session_state.phase == "NIGHT_SEER":
        st.subheader("🌙 กลางคืน: [🔮 หมอดู ตื่นขึ้นมา]")
        seer_alive = any(st.session_state.roles[i] == 'Seer' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if seer_alive:
            check_target = st.selectbox("เลือกผู้เล่นที่ต้องการตรวจสอบ:", st.session_state.players, key="seer_choice")
            if st.button("ตรวจสอบบทบาท"):
                t_idx = st.session_state.players.index(check_target)
                if st.session_state.roles[t_idx] == 'Werewolf':
                    st.error(f"🔍 ผลการตรวจ: **{check_target}** เป็น 🐺 WEREWOLF!")
                else:
                    st.success(f"🔍 ผลการตรวจ: **{check_target}** เป็น 🧑 คนธรรมดา")
                play_sound("action")
                time.sleep(2)
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()
        else:
            st.info("(หมอดูเสียชีวิตแล้ว หรือไม่มีในเกม)")
            if st.button("ข้ามไปบทบาทถัดไป"):
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()

    # --- 🛡️ บอดี้การ์ดปกป้อง ---
    elif st.session_state.phase == "NIGHT_GUARD":
        st.subheader("🌙 กลางคืน: [🛡️ บอดี้การ์ด ตื่นขึ้นมา]")
        guard_alive = any(st.session_state.roles[i] == 'Bodyguard' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if guard_alive:
            alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
            guard_target = st.selectbox("เลือกคนที่ต้องการปกป้องคืนนี้:", alive_players, key="guard_choice")
            if st.button("ยืนยันการปกป้อง"):
                st.session_state.protected_player = guard_target
                play_sound("action")
                st.session_state.phase = "NIGHT_WITCH" if 'Witch' in st.session_state.roles else "DAY"
                st.rerun()
        else:
            st.info("(บอดี้การ์ดเสียชีวิตแล้ว หรือไม่มีในเกม)")
            if st.button("ข้ามไปบทบาทถัดไป"):
                st.session_state.phase = "NIGHT_WITCH" if 'Witch' in st.session_state.roles else "DAY"
                st.rerun()

    # --- 🧙‍♀️ แม่มดยาพิษ/ยาช่วย ---
    elif st.session_state.phase == "NIGHT_WITCH":
        st.subheader("🌙 กลางคืน: [🧙‍♀️ แม่มด ตื่นขึ้นมา]")
        witch_alive = any(st.session_state.roles[i] == 'Witch' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if witch_alive:
            st.write(f"คืนนี้หมาป่าจ้องจะเล่นงาน: **{st.session_state.target_wolf}**")
            
            if st.session_state.witch_heal:
                use_heal = st.checkbox("🧪 ใช้ยาชุบชีวิต (Heal Potion)")
                if use_heal:
                    st.session_state.witch_saved = True
            
            poison_target = None
            if st.session_state.witch_poison:
                use_poison = st.checkbox("☠️ ใช้ยาพิษ (Poison Potion)")
                if use_poison:
                    alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
                    poison_target = st.selectbox("เลือกคนที่ต้องการวางยาพิษ:", alive_players)
            
            if st.button("จบขั้นตอนแม่มด"):
                if st.session_state.witch_saved:
                    st.session_state.witch_heal = False
                if poison_target:
                    st.session_state.witch_kill_target = poison_target
                    st.session_state.witch_poison = False
                
                play_sound("action")
                st.session_state.phase = "DAY"
                st.rerun()
        else:
            st.info("(แม่มดเสียชีวิตแล้ว หรือไม่มีในเกม)")
            if st.button("เข้าสู่ช่วงเช้า"):
                st.session_state.phase = "DAY"
                st.rerun()

    # ==================================================
    # 4. ช่วงกลางวัน (DAY PHASE & ALARM)
    # ==================================================
    elif st.session_state.phase == "DAY":
        play_sound("morning") # 🔥 เสียงปลุกตอนเช้า
        st.subheader("⏰ ALARM!! ☀️ เช้าวันใหม่ - ทุกคนตื่นนอน!")
        
        dead_tonight = []
        if st.session_state.target_wolf != st.session_state.protected_player and not st.session_state.witch_saved:
            target_idx = st.session_state.players.index(st.session_state.target_wolf)
            if st.session_state.status[target_idx]:
                st.session_state.status[target_idx] = False
                dead_tonight.append(st.session_state.target_wolf)
                
        if st.session_state.witch_kill_target:
            poison_idx = st.session_state.players.index(st.session_state.witch_kill_target)
            if st.session_state.status[poison_idx]:
                st.session_state.status[poison_idx] = False
                dead_tonight.append(st.session_state.witch_kill_target)

        # เช็คการตายของคู่รัก (Cupid Link)
        if st.session_state.lovers:
            l1, l2 = st.session_state.lovers
            l1_dead = not st.session_state.status[st.session_state.players.index(l1)]
            l2_dead = not st.session_state.status[st.session_state.players.index(l2)]
            
            if l1_dead and not l2_dead:
                st.session_state.status[st.session_state.players.index(l2)] = False
                dead_tonight.append(f"{l2} (ตรอมใจตายตามคู่รัก {l1})")
            elif l2_dead and not l1_dead:
                st.session_state.status[st.session_state.players.index(l1)] = False
                dead_tonight.append(f"{l1} (ตรอมใจตายตามคู่รัก {l2})")

        if len(dead_tonight) == 0:
            st.success("🎉 เป็นโชคดีของหมู่บ้าน! คืนที่ผ่านมาไม่มีใครเสียชีวิต")
        else:
            st.error(f"💀 ข่าวร้าย... ผู้เสียชีวิตได้แก่: {', '.join(dead_tonight)}")

        # รีเซ็ตค่ากลางคืน
        st.session_state.target_wolf = None
        st.session_state.protected_player = None
        st.session_state.witch_kill_target = None
        st.session_state.witch_saved = False

        # เช็คผลชนะ
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

        if st.button("🗳️ ไปยังช่วงโหวตประหารชีวิต"):
            st.session_state.phase = "VOTING"
            st.rerun()

    # ==================================================
    # 5. ช่วงโหวตจับหมาป่า (VOTING PHASE)
    # ==================================================
    elif st.session_state.phase == "VOTING":
        st.subheader("🗳️ ช่วงพูดคุยและโหวตประหารชีวิต")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        vote_target = st.selectbox("เลือกคนที่ถูกเสียงส่วนใหญ่โหวตออก:", alive_players)
        
        if st.button("ยืนยันการประหารชีวิต"):
            vote_idx = st.session_state.players.index(vote_target)
            st.session_state.status[vote_idx] = False
            play_sound("action")
            
            role_voted = st.session_state.roles[vote_idx]
            st.warning(f"⚖️ {vote_target} ถูกโหวตประหารชีวิต! (บทบาทจริงคือ: {role_voted})")
            
            # เช็คเงื่อนไขชนะของ Fool (ตัวตลก)
            if role_voted == 'Fool':
                st.session_state.winner = f"🤡 {vote_target} (ตัวตลก) ชนะเกม! เพราะปั่นจนโดนโหวตประหารสำเร็จ!"
                st.session_state.phase = "GAMEOVER"
                st.rerun()

            wolves = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] == 'Werewolf')
            villagers = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] != 'Werewolf')

            if wolves == 0:
                st.session_state.winner = "🎉 ฝ่ายชาวบ้านชนะ! (Villagers Win)"
                st.session_state.phase = "GAMEOVER"
            elif wolves >= villagers:
                st.session_state.winner = "🐺 ฝ่ายหมาป่าชนะ! (Werewolves Win)"
                st.session_state.phase = "GAMEOVER"
            else:
                st.session_state.phase = "NIGHT_WOLF"
            
            time.sleep(3)
            st.rerun()

    # ==================================================
    # 6. จบเกม (GAMEOVER PHASE)
    # ==================================================
    elif st.session_state.phase == "GAMEOVER":
        play_sound("gameover")
        st.balloons()
        st.title("🏆 จบเกม! (GAME OVER)")
        st.header(st.session_state.winner)
        
        if st.button("🔄 เริ่มเกมใหม่"):
            st.session_state.phase = "SETUP"
            st.session_state.game_started = False
            st.rerun()
