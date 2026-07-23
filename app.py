import streamlit as st
import random
import time

# --------------------------------------------------
# ตั้งค่าหน้าเว็บ
# --------------------------------------------------
st.set_page_config(page_title="Werewolf Game for Friends", page_icon="🐺", layout="centered")

st.title("🐺 Werewolf Game (ระบบจัดการสำหรับเล่นกับเพื่อน)")
st.write("ตั้งค่าบทบาท สุ่มแจก และรันเกมผ่านเว็บได้เลย!")

# --------------------------------------------------
# ฟังก์ชันเล่นเสียงเตือนผ่านเบราว์เซอร์ (iOS / PC / Android)
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
    st.session_state.phase = "SETUP" # SETUP, CHECK_ROLES, NIGHT_WOLF, NIGHT_SEER, NIGHT_GUARD, NIGHT_WITCH, DAY, VOTING, GAMEOVER
    st.session_state.players = []
    st.session_state.roles = []
    st.session_state.status = []
    st.session_state.witch_heal = True
    st.session_state.witch_poison = True
    st.session_state.target_wolf = None
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_saved = False

# ==================================================
# 1. หน้าตั้งค่าบทบาทและจำนวนผู้เล่น (SETUP PHASE)
# ==================================================
if st.session_state.phase == "SETUP":
    st.subheader("⚙️ 1. เลือกจำนวนคนและตั้งค่าบทบาท")
    
    num_players = st.number_input("จำนวนผู้เล่นทั้งหมด (คน):", min_value=4, max_value=15, value=6)
    
    st.write("---")
    st.write("🎯 **เลือกบทบาทพิเศษที่จะให้มีในเกม:**")
    
    num_wolves = st.slider("จำนวนหมาป่า (Werewolves):", min_value=1, max_value=3, value=1 if num_players < 8 else 2)
    has_seer = st.checkbox("🔮 หมอดู (Seer - ส่องดูหมาป่า)", value=True)
    has_guard = st.checkbox("🛡️ บอดี้การ์ด (Bodyguard - ปกป้องคน)", value=True)
    has_witch = st.checkbox("🧙‍♀️ แม่มด (Witch - ยาช่วย / ยาพิษ)", value=True)
    has_hunter = st.checkbox("🏹 นายพราน (Hunter - ยิงสวนก่อนตาย)", value=True)

    # คำนวณจำนวนบทบาทพิเศษ
    special_roles_count = num_wolves
    if has_seer: special_roles_count += 1
    if has_guard: special_roles_count += 1
    if has_witch: special_roles_count += 1
    if has_hunter: special_roles_count += 1

    villagers_count = num_players - special_roles_count

    if villagers_count < 0:
        st.error(f"❌ เลือกบทบาทพิเศษเกินจำนวนคน! (คนเล่น {num_players} คน แต่เลือกบทบาทไป {special_roles_count} บท)")
    else:
        st.info(f"💡 สรุปบทบาท: หมาป่า {num_wolves} คน | บทบาทพิเศษ {special_roles_count - num_wolves} คน | ชาวบ้านธรรมดา {villagers_count} คน")
        
        if st.button("🎲 สุ่มบทบาทและเริ่มเกม (Start Game)"):
            # สร้าง List บทบาททั้งหมด
            roles_pool = ['Werewolf'] * num_wolves
            if has_seer: roles_pool.append('Seer')
            if has_guard: roles_pool.append('Bodyguard')
            if has_witch: roles_pool.append('Witch')
            if has_hunter: roles_pool.append('Hunter')
            roles_pool.extend(['Villager'] * villagers_count)

            # สุ่มลำดับบทบาท
            random.shuffle(roles_pool)

            # บันทึกลงระบบ
            st.session_state.players = [f"Player_{i+1}" for i in range(num_players)]
            st.session_state.roles = roles_pool
            st.session_state.status = [True] * num_players
            st.session_state.game_started = True
            st.session_state.phase = "CHECK_ROLES"
            st.rerun()

# ==================================================
# 2. หน้าแอบดูบทบาทตัวเองทีละคน (CHECK ROLES PHASE)
# ==================================================
elif st.session_state.phase == "CHECK_ROLES":
    st.subheader("🔍 2. แจกจ่ายบทบาท (วนเปิดทีละคน)")
    st.warning("⚠️ ส่งเครื่องให้อ่านทีละคน และห้ามให้เพื่อนข้างๆ แอบดูหน้าจอ!")

    selected_player = st.selectbox("เลือกชื่อของคุณเพื่อดูบทบาท:", st.session_state.players)
    idx = st.session_state.players.index(selected_player)

    with st.expander(f"👉 คลิกที่นี่เพื่อเปิดดูบทบาทของ {selected_player}"):
        role = st.session_state.roles[idx]
        if role == 'Werewolf':
            st.error("🐺 คุณได้บทบาท: WEREWOLF (หมาป่า)\n\nภารกิจ: ลอบฆ่าชาวบ้านในตอนกลางคืน!")
        elif role == 'Seer':
            st.info("🔮 คุณได้บทบาท: SEER (หมอดู)\n\nภารกิจ: ส่องดูผู้เล่นในตอนกลางคืนว่าเป็นหมาป่าหรือไม่")
        elif role == 'Bodyguard':
            st.success("🛡️ คุณได้บทบาท: BODYGUARD (บอดี้การ์ด)\n\nภารกิจ: ปกป้องผู้เล่น 1 คนในทุกๆ คืน")
        elif role == 'Witch':
            st.warning("🧙‍♀️ คุณได้บทบาท: WITCH (แม่มด)\n\nภารกิจ: มียาช่วย 1 ขวด และยาพิษ 1 ขวด")
        elif role == 'Hunter':
            st.warning("🏹 คุณได้บทบาท: HUNTER (นายพราน)\n\nภารกิจ: ถ้าคุณตาย คุณสามารถลากคนอื่นตายตามได้ 1 คน")
        else:
            st.write("🧑 คุณได้บทบาท: VILLAGER (ชาวบ้านธรรมดา)\n\nภารกิจ: ช่วยกันพูดคุยและโหวตจับหมาป่าในตอนกลางวัน!")

    st.write("---")
    if st.button("🌙 เมื่อทุกคนดูบทบาทครบแล้ว -> เริ่มช่วงกลางคืนแรก"):
        st.session_state.phase = "NIGHT_WOLF"
        st.rerun()

# ==================================================
# 3. ช่วงกลางคืน (NIGHT PHASES)
# ==================================================
else:
    # เมนูซ่อน/เปิด ดูบทบาททั้งหมดสำหรับผู้ดำเนินเกม (Moderator)
    with st.expander("👁️ เฉลยบทบาททั้งหมด (สำหรับคนคุมเกมดูเท่านั้น)"):
        for i in range(len(st.session_state.players)):
            status_text = "🟢 รอด" if st.session_state.status[i] else "💀 ตายแล้ว"
            st.write(f"**{st.session_state.players[i]}**: {st.session_state.roles[i]} ({status_text})")

    st.divider()

    # --- 🐺 หมาป่าเลือกเหยื่อ ---
    if st.session_state.phase == "NIGHT_WOLF":
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
                target_index = st.session_state.players.index(check_target)
                if st.session_state.roles[target_index] == 'Werewolf':
                    st.error(f"🔍 ผลการตรวจ: **{check_target}** เป็น 🐺 WEREWOLF!")
                else:
                    st.success(f"🔍 ผลการตรวจ: **{check_target}** เป็น 🧑 คนธรรมดา")
                play_sound("action")
                time.sleep(2)
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()
        else:
            st.info("(หมอดูเสียชีวิตแล้ว หรือไม่มีในเกม)")
            if st.button("ข้ามไปยังบทบาทถัดไป"):
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
            if st.button("ข้ามไปยังบทบาทถัดไป"):
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
        play_sound("morning") # 🔥 เสียงปลุกตอนเช้าดังผ่านเบราว์เซอร์
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

        if len(dead_tonight) == 0:
            st.success("🎉 เป็นโชคดีของหมู่บ้าน! คืนที่ผ่านมาไม่มีใครเสียชีวิต")
        else:
            st.error(f"💀 ข่าวร้าย... ผู้เสียชีวิตในคืนนี้ได้แก่: {', '.join(dead_tonight)}")
            
            for d in dead_tonight:
                d_idx = st.session_state.players.index(d)
                if st.session_state.roles[d_idx] == 'Hunter':
                    st.warning(f"🏹 {d} เป็นนายพราน (Hunter) ได้ยิงสวนก่อนตาย!")

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
        st.subheader("🗳️ ช่วงพูดคุยจับผิด และโหวตประหารชีวิต")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        vote_target = st.selectbox("เลือกคนที่ถูกเสียงส่วนใหญ่โหวตออก:", alive_players)
        
        if st.button("ยืนยันการประหารชีวิต"):
            vote_idx = st.session_state.players.index(vote_target)
            st.session_state.status[vote_idx] = False
            play_sound("action")
            
            st.warning(f"⚖️ {vote_target} ถูกโหวตประหารชีวิต! (บทบาทจริงคือ: {st.session_state.roles[vote_idx]})")
            
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
