import streamlit as st
import random
import time

# --------------------------------------------------
# ตั้งค่าหน้าเว็บ
# --------------------------------------------------
st.set_page_config(page_title="Werewolf Game", page_icon="🐺", layout="centered")

st.title("🐺 Werewolf Game (เกมหมาป่า)")
st.write("เกมล่าหมาป่าระบบ Web App เล่นผ่านเว็บ/iPad/มือถือ")

# --------------------------------------------------
# ฟังก์ชันเล่นเสียงเตือน (HTML5 Audio เล่นผ่านเบราว์เซอร์)
# --------------------------------------------------
def play_sound(sound_type):
    if sound_type == "morning":
        # เสียงนาฬิกาปลุกตอนเช้า
        sound_url = "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg"
    elif sound_type == "action":
        # เสียงเตือนเมื่อทำภารกิจเสร็จ
        sound_url = "https://actions.google.com/sounds/v1/beeps/short_beep_high.ogg"
    elif sound_type == "gameover":
        # เสียงจบเกม
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
# ระบบ Session State (เก็บสถานะเกมบน Streamlit)
# --------------------------------------------------
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.phase = "NIGHT_WOLF" # NIGHT_WOLF, NIGHT_SEER, NIGHT_GUARD, NIGHT_WITCH, DAY, VOTING, GAMEOVER
    st.session_state.players = []
    st.session_state.roles = []
    st.session_state.status = [] # True = รอด, False = ตาย
    st.session_state.witch_heal = True
    st.session_state.witch_poison = True
    st.session_state.night_logs = []
    st.session_state.target_wolf = None
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_saved = False

# --------------------------------------------------
# 1. หน้าเริ่มเกม / ตั้งค่าจำนวนผู้เล่น
# --------------------------------------------------
if not st.session_state.game_started:
    st.subheader("⚙️ ตั้งค่าเกม")
    num_players = st.number_input("จำนวนผู้เล่น (6-10 คน):", min_value=6, max_value=10, value=6)
    
    if st.button("🚀 เริ่มเกม (Start Game)"):
        players = [f"Player_{i+1}" for i in range(num_players)]
        roles_pool = ['Werewolf', 'Seer', 'Bodyguard', 'Witch', 'Hunter']
        
        if num_players >= 8:
            roles_pool.append('Werewolf')
            
        while len(roles_pool) < num_players:
            roles_pool.append('Villager')
            
        random.shuffle(roles_pool)
        
        st.session_state.players = players
        st.session_state.roles = roles_pool
        st.session_state.status = [True] * num_players
        st.session_state.game_started = True
        st.session_state.phase = "NIGHT_WOLF"
        st.rerun()

else:
    # แสดงรายชื่อผู้เล่นและบทบาท (เปิด-ปิดดูได้)
    with st.expander("👁️ ดูรายชื่อผู้เล่นและบทบาททั้งหมด (ลับ)"):
        for i in range(len(st.session_state.players)):
            status_text = "🟢 มีชีวิต" if st.session_state.status[i] else "💀 ตายแล้ว"
            st.write(f"**{st.session_state.players[i]}**: {st.session_state.roles[i]} ({status_text})")

    st.divider()

    # --------------------------------------------------
    # 2. ช่วงกลางคืน (NIGHT PHASES)
    # --------------------------------------------------
    
    # --- 🐺 หมาป่าเลือกเหยื่อ ---
    if st.session_state.phase == "NIGHT_WOLF":
        st.subheader("🌙 กลางคืน: [🐺 หมาป่า ตื่นขึ้นมา]")
        st.write("เลือกผู้เล่น 1 คนที่ต้องการสังหาร:")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        target = st.radio("เลือกเหยื่อ:", alive_players, key="wolf_choice")
        
        if st.button("ยืนยันการเลือกของหมาป่า"):
            st.session_state.target_wolf = target
            play_sound("action")
            st.session_state.phase = "NIGHT_SEER"
            st.rerun()

    # --- 🔮 หมอดูส่องบทบาท ---
    elif st.session_state.phase == "NIGHT_SEER":
        st.subheader("🌙 กลางคืน: [🔮 หมอดู ตื่นขึ้นมา]")
        
        seer_alive = any(st.session_state.roles[i] == 'Seer' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if seer_alive:
            check_target = st.selectbox("เลือกผู้เล่นที่ต้องการตรวจสอบ:", st.session_state.players, key="seer_choice")
            if st.button("ตรวจสอบบทบาท"):
                target_index = st.session_state.players.index(check_target)
                is_wolf = st.session_state.roles[target_index] == 'Werewolf'
                if is_wolf:
                    st.error(f"🔍 ผลการตรวจ: **{check_target}** เป็น 🐺 WEREWOLF!")
                else:
                    st.success(f"🔍 ผลการตรวจ: **{check_target}** เป็น 🧑 คนธรรมดา (ไม่ใช่หมาป่า)")
                play_sound("action")
                time.sleep(2)
                st.session_state.phase = "NIGHT_GUARD"
                st.rerun()
        else:
            st.info("(หมอดูเสียชีวิตแล้ว หรือไม่มีในเกม)")
            if st.button("ข้ามไปยังบทบาทถัดไป"):
                st.session_state.phase = "NIGHT_GUARD"
                st.rerun()

    # --- 🛡️ บอดี้การ์ดปกป้อง ---
    elif st.session_state.phase == "NIGHT_GUARD":
        st.subheader("🌙 กลางคืน: [🛡️ บอดี้การ์ด ตื่นขึ้นมา]")
        
        guard_alive = any(st.session_state.roles[i] == 'Bodyguard' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if guard_alive:
            alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
            guard_target = st.selectbox("เลือกผู้เล่นที่ต้องการปกป้องคืนนี้:", alive_players, key="guard_choice")
            if st.button("ยืนยันการปกป้อง"):
                st.session_state.protected_player = guard_target
                play_sound("action")
                st.session_state.phase = "NIGHT_WITCH"
                st.rerun()
        else:
            st.info("(บอดี้การ์ดเสียชีวิตแล้ว หรือไม่มีในเกม)")
            if st.button("ข้ามไปยังบทบาทถัดไป"):
                st.session_state.phase = "NIGHT_WITCH"
                st.rerun()

    # --- 🧙‍♀️ แม่มดยาพิษ/ยาช่วย ---
    elif st.session_state.phase == "NIGHT_WITCH":
        st.subheader("🌙 กลางคืน: [🧙‍♀️ แม่มด ตื่นขึ้นมา]")
        
        witch_alive = any(st.session_state.roles[i] == 'Witch' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if witch_alive:
            st.write(f"คืนนี้หมาป่าจ้องจะเล่นงาน: **{st.session_state.target_wolf}**")
            
            # ใช้ยาช่วย
            if st.session_state.witch_heal:
                use_heal = st.checkbox("🧪 ใช้ยาชุบชีวิต (Heal Potion)")
                if use_heal:
                    st.session_state.witch_saved = True
            
            # ใช้ยาพิษ
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

    # --------------------------------------------------
    # 3. ช่วงกลางวัน (DAY PHASE & ALARM)
    # --------------------------------------------------
    elif st.session_state.phase == "DAY":
        play_sound("morning") # 🔥 เปิดเสียงปลุกตอนเช้าผ่านเบราว์เซอร์
        st.subheader("⏰ ALARM!! ☀️ เช้าวันใหม่ - ทุกคนตื่นนอน!")
        
        # ประมวลผลคนตายตอนกลางคืน
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
            
            # เช็คสกิล Hunter
            for d in dead_tonight:
                d_idx = st.session_state.players.index(d)
                if st.session_state.roles[d_idx] == 'Hunter':
                    st.warning(f"🏹 {d} เป็นนายพราน (Hunter) ได้ยิงสวนก่อนตาย!")

        # รีเซ็ตค่ากลางคืน
        st.session_state.target_wolf = None
        st.session_state.protected_player = None
        st.session_state.witch_kill_target = None
        st.session_state.witch_saved = False

        # เช็คผลการชนะ
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

    # --------------------------------------------------
    # 4. ช่วงโหวตจับหมาป่า (VOTING PHASE)
    # --------------------------------------------------
    elif st.session_state.phase == "VOTING":
        st.subheader("🗳️ ช่วงการพูดคุยและโหวตประหารชีวิต")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        vote_target = st.selectbox("เลือกผู้ต้องสงสัยที่ต้องการประหารชีวิต:", alive_players)
        
        if st.button("ยืนยันผลการโหวต"):
            vote_idx = st.session_state.players.index(vote_target)
            st.session_state.status[vote_idx] = False
            play_sound("action")
            
            st.warning(f"⚖️ {vote_target} ถูกโหวตประหารชีวิต! (บทบาทจริงคือ: {st.session_state.roles[vote_idx]})")
            
            # เช็คผลชนะหลังโหวต
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

    # --------------------------------------------------
    # 5. จบเกม (GAMEOVER PHASE)
    # --------------------------------------------------
    elif st.session_state.phase == "GAMEOVER":
        play_sound("gameover")
        st.balloons()
        st.title("🏆 จบเกม! (GAME OVER)")
        st.header(st.session_state.winner)
        
        if st.button("🔄 เล่นใหม่อีกครั้ง"):
            st.session_state.game_started = False
            st.rerun()
