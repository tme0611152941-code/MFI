import streamlit as st
import random
import time

# --------------------------------------------------
# ตั้งค่าหน้าเว็บ
# --------------------------------------------------
st.set_page_config(page_title="No-Moderator Werewolf", page_icon="🐺", layout="centered")

st.title("🐺 Ultimate Werewolf (แบบไม่มีคนคุมเกม)")
st.caption("เล่นได้ทุกคนบน iPad เครื่องเดียว มีเสียงสัญญาณบอกเมื่อทำภารกิจเสร็จสิ้น")

# --------------------------------------------------
# ฟังก์ชันเล่นเสียงสัญญาณต่าง ๆ ผ่าน iPad/เบราว์เซอร์
# --------------------------------------------------
def play_sound(sound_type):
    # เลือกลิงก์ไฟล์เสียงสัญญาณที่ชัดเจน
    sounds = {
        "wake_up": "https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg",          # เสียงปลุกเช้า/เปลี่ยนเฟส
        "action_done": "https://actions.google.com/sounds/v1/beeps/short_beep_high.ogg",  # เสียงปี๊บ! ทำภารกิจเสร็จ
        "gameover": "https://actions.google.com/sounds/v1/cartoon/clapping.ogg"           # เสียงจบเกม
    }
    sound_url = sounds.get(sound_type, "")
    
    if sound_url:
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
    st.session_state.lovers = []
    st.session_state.witch_heal = True
    st.session_state.witch_poison = True
    st.session_state.target_wolf = None
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_saved = False
    st.session_state.winner = ""

# ==================================================
# 1. ตั้งค่าชื่อผู้เล่นและเลือกตัวละคร (SETUP)
# ==================================================
if st.session_state.phase == "SETUP":
    st.subheader("📝 1. ตั้งชื่อผู้เล่นทุกคน")
    num_players = st.number_input("จำนวนผู้เล่นทั้งหมด (คน):", min_value=4, max_value=20, value=6)
    
    player_names = []
    cols = st.columns(2)
    for i in range(num_players):
        col = cols[i % 2]
        name = col.text_input(f"คนที่ {i+1}:", value=f"ผู้เล่น_{i+1}", key=f"p_{i}")
        player_names.append(name.strip())

    st.write("---")
    st.subheader("🎭 2. เลือกตัวละครที่จะใส่ในสุ่ม")
    
    col1, col2 = st.columns(2)
    with col1:
        num_wolves = st.slider("🐺 จำนวนหมาป่า:", 1, 4, 1 if num_players < 8 else 2)
        has_seer = st.checkbox("🔮 หมอดู (Seer)", value=True)
        has_guard = st.checkbox("🛡️ บอดี้การ์ด (Bodyguard)", value=True)
        has_witch = st.checkbox("🧙‍♀️ แม่มด (Witch)", value=True)
    with col2:
        has_hunter = st.checkbox("🏹 นายพราน (Hunter)", value=True)
        has_cupid = st.checkbox("💘 คิวปิด (Cupid)", value=num_players >= 7)
        has_fool = st.checkbox("🤡 ตัวตลก (Fool)", value=num_players >= 7)
        has_girl = st.checkbox("👶 เด็กน้อย (Little Girl)", value=False)

    special_count = num_wolves + sum([has_seer, has_guard, has_witch, has_hunter, has_cupid, has_fool, has_girl])
    villagers_count = num_players - special_count

    if villagers_count < 0:
        st.error(f"❌ บทบาทที่เลือกเกินจำนวนคนเล่น! (คนเล่น {num_players} คน แต่เลือกไป {special_count} บทบาท)")
    else:
        st.info(f"💡 สรุป: หมาป่า {num_wolves} | บทพิเศษ {special_count - num_wolves} | ชาวบ้าน {villagers_count}")
        
        if st.button("🚀 เริ่มสุ่มบทบาท"):
            roles_pool = ['Werewolf'] * num_wolves
            if has_seer: roles_pool.append('Seer')
            if has_guard: roles_pool.append('Bodyguard')
            if has_witch: roles_pool.append('Witch')
            if has_hunter: roles_pool.append('Hunter')
            if has_cupid: roles_pool.append('Cupid')
            if has_fool: roles_pool.append('Fool')
            if has_girl: roles_pool.append('Little Girl')
            roles_pool.extend(['Villager'] * villagers_count)

            random.shuffle(roles_pool)

            st.session_state.players = player_names
            st.session_state.roles = roles_pool
            st.session_state.status = [True] * num_players
            st.session_state.game_started = True
            st.session_state.phase = "CHECK_ROLES"
            st.rerun()

# ==================================================
# 2. วนแอบดูบทบาทตัวเองทีละคน (CHECK ROLES)
# ==================================================
elif st.session_state.phase == "CHECK_ROLES":
    st.subheader("🔍 ส่ง iPad วนให้เพื่อนแอบดูบทบาททีละคน")
    
    selected_player = st.selectbox("เลือกชื่อของคุณเพื่อดูบทบาท:", st.session_state.players)
    idx = st.session_state.players.index(selected_player)

    with st.expander(f"👉 คลิกเพื่อดูบทบาทของ ({selected_player})"):
        role = st.session_state.roles[idx]
        st.write(f"คุณคือ: **{role}**")
        st.caption("จำบทบาทตัวเองไว้ให้ดี แล้วปิดหน้าจอนี้ก่อนส่งต่อให้คนอื่น!")

    st.write("---")
    if st.button("🌙 เมื่อทุกคนดูครบแล้ว -> เริ่มเข้าสู่คืนแรก (หลับตาทั้งวง)"):
        st.session_state.phase = "NIGHT_CUPID" if 'Cupid' in st.session_state.roles else "NIGHT_WOLF"
        st.rerun()

# ==================================================
# 3. ช่วงกลางคืนอัตโนมัติ (NIGHT PHASES)
# ==================================================
else:
    # --- 💘 คิวปิด ---
    if st.session_state.phase == "NIGHT_CUPID":
        st.subheader("🌙 [ทุกคนหลับตา] -> 💘 คิวปิด ตื่นขึ้นมา!")
        st.write("ให้ **คิวปิด** หยิบ iPad ไปเลือกคู่รัก 2 คนแล้วกด ยืนยัน")
        
        lover1 = st.selectbox("คู่รักคนที่ 1:", st.session_state.players, index=0)
        lover2 = st.selectbox("คู่รักคนที่ 2:", st.session_state.players, index=1)
        
        if st.button("✅ ยืนยันคู่รัก (ส่งสัญญาณเสียง)"):
            st.session_state.lovers = [lover1, lover2]
            play_sound("action_done") # 🔔 เสียงสัญญาณเสร็จสิ้น!
            st.success("🔔 ส่งสัญญาณเสียงแล้ว! ให้คิวปิดหลับตาลง")
            time.sleep(2)
            st.session_state.phase = "NIGHT_WOLF"
            st.rerun()

    # --- 🐺 หมาป่า ---
    elif st.session_state.phase == "NIGHT_WOLF":
        st.subheader("🌙 [ทุกคนหลับตา] -> 🐺 หมาป่า ตื่นขึ้นมา!")
        st.write("ให้ **หมาป่า** แอบลืมตามาเลือกเหยื่อ 1 คนแล้วกด ยืนยัน")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        target = st.radio("เลือกเหยื่อที่จะสังหาร:", alive_players, key="wolf_choice")
        
        if st.button("✅ ยืนยันการเลือกของหมาป่า (ส่งสัญญาณเสียง)"):
            st.session_state.target_wolf = target
            play_sound("action_done") # 🔔 เสียงสัญญาณเสร็จสิ้น!
            st.success("🔔 ส่งสัญญาณเสียงแล้ว! ให้หมาป่าหลับตาลง")
            time.sleep(2)
            st.session_state.phase = "NIGHT_SEER" if 'Seer' in st.session_state.roles else "NIGHT_GUARD"
            st.rerun()

    # --- 🔮 หมอดู ---
    elif st.session_state.phase == "NIGHT_SEER":
        st.subheader("🌙 [ทุกคนหลับตา] -> 🔮 หมอดู ตื่นขึ้นมา!")
        seer_alive = any(st.session_state.roles[i] == 'Seer' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if seer_alive:
            st.write("ให้ **หมอดู** ลืมตามาเลือกตรวจบทบาท 1 คน:")
            check_target = st.selectbox("เลือกคนที่ต้องการตรวจ:", st.session_state.players, key="seer_choice")
            if st.button("🔍 ดูผลการตรวจ"):
                t_idx = st.session_state.players.index(check_target)
                if st.session_state.roles[t_idx] == 'Werewolf':
                    st.error(f"ผลตรวจ: **{check_target}** เป็น 🐺 หมาป่า!")
                else:
                    st.success(f"ผลตรวจ: **{check_target}** เป็น 🧑 คนธรรมดา")
            
            if st.button("✅ หมอดูตรวจเสร็จแล้ว (ส่งสัญญาณเสียง)"):
                play_sound("action_done") # 🔔 เสียงสัญญาณเสร็จสิ้น!
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()
        else:
            # ถ้าหมอดูตายแล้ว ให้หน่วงเวลาและส่งเสียงเนียนๆ เพื่อไม่ให้คนอื่นรู้
            st.caption("ระบบกำลังรอดำเนินการ...")
            if st.button("ข้ามช่วงหมอดู (เนียนส่งสัญญาณเสียง)"):
                play_sound("action_done")
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()

    # --- 🛡️ บอดี้การ์ด ---
    elif st.session_state.phase == "NIGHT_GUARD":
        st.subheader("🌙 [ทุกคนหลับตา] -> 🛡️ บอดี้การ์ด ตื่นขึ้นมา!")
        guard_alive = any(st.session_state.roles[i] == 'Bodyguard' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if guard_alive:
            alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
            guard_target = st.selectbox("เลือกคนที่ต้องการปกป้องคืนนี้:", alive_players, key="guard_choice")
            if st.button("✅ ยืนยันการปกป้อง (ส่งสัญญาณเสียง)"):
                st.session_state.protected_player = guard_target
                play_sound("action_done") # 🔔 เสียงสัญญาณเสร็จสิ้น!
                st.session_state.phase = "NIGHT_WITCH" if 'Witch' in st.session_state.roles else "DAY"
                st.rerun()
        else:
            if st.button("ข้ามช่วงบอดี้การ์ด (เนียนส่งสัญญาณเสียง)"):
                play_sound("action_done")
                st.session_state.phase = "NIGHT_WITCH" if 'Witch' in st.session_state.roles else "DAY"
                st.rerun()

    # --- 🧙‍♀️ แม่มด ---
    elif st.session_state.phase == "NIGHT_WITCH":
        st.subheader("🌙 [ทุกคนหลับตา] -> 🧙‍♀️ แม่มด ตื่นขึ้นมา!")
        witch_alive = any(st.session_state.roles[i] == 'Witch' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if witch_alive:
            st.write(f"เหยื่อที่หมาป่าจ้องฆ่าคืนนี้คือ: **{st.session_state.target_wolf}**")
            
            if st.session_state.witch_heal:
                if st.checkbox("🧪 ใช้ยาชุบชีวิต"):
                    st.session_state.witch_saved = True
            
            poison_target = None
            if st.session_state.witch_poison:
                if st.checkbox("☠️ ใช้ยาพิษ"):
                    alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
                    poison_target = st.selectbox("เลือกคนที่ต้องการวางยาพิษ:", alive_players)
            
            if st.button("✅ ยืนยันการใช้ยา (ส่งสัญญาณเสียง)"):
                if st.session_state.witch_saved:
                    st.session_state.witch_heal = False
                if poison_target:
                    st.session_state.witch_kill_target = poison_target
                    st.session_state.witch_poison = False
                
                play_sound("action_done") # 🔔 เสียงสัญญาณเสร็จสิ้น!
                st.session_state.phase = "DAY"
                st.rerun()
        else:
            if st.button("ข้ามช่วงแม่มด (เนียนส่งสัญญาณเสียง)"):
                play_sound("action_done")
                st.session_state.phase = "DAY"
                st.rerun()

    # ==================================================
    # 4. ช่วงเช้าวันใหม่ (DAY PHASE & ALARM)
    # ==================================================
    elif st.session_state.phase == "DAY":
        play_sound("wake_up") # ⏰ เสียงนาฬิกาปลุกดังลั่น iPad บอกให้ทุกคนลืมตา!
        st.subheader("☀️ ALARM!! เช้าวันใหม่ - ทุกคนลืมตาขึ้นมาได้!")
        
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

        # เช็คคู่รักตายตามกัน
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
            st.success("🎉 คืนที่ผ่านมาไม่มีใครเสียชีวิต!")
        else:
            st.error(f"💀 ผู้เสียชีวิตในคืนนี้ได้แก่: {', '.join(dead_tonight)}")

        # รีเซ็ตค่ากลางคืน
        st.session_state.target_wolf = None
        st.session_state.protected_player = None
        st.session_state.witch_kill_target = None
        st.session_state.witch_saved = False

        # เช็คผลชนะ
        wolves = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] == 'Werewolf')
        villagers = sum(1 for i in range(len(st.session_state.players)) if st.session_state.status[i] and st.session_state.roles[i] != 'Werewolf')

        if wolves == 0:
            st.session_state.winner = "🎉 ฝ่ายชาวบ้านชนะ!"
            st.session_state.phase = "GAMEOVER"
            st.rerun()
        elif wolves >= villagers:
            st.session_state.winner = "🐺 ฝ่ายหมาป่าชนะ!"
            st.session_state.phase = "GAMEOVER"
            st.rerun()

        if st.button("🗳️ พูดคุยเสร็จแล้ว -> ไปช่วงโหวตประหาร"):
            st.session_state.phase = "VOTING"
            st.rerun()

    # ==================================================
    # 5. ช่วงโหวตประหารชีวิต (VOTING PHASE)
    # ==================================================
    elif st.session_state.phase == "VOTING":
        st.subheader("🗳️ ช่วงโหวตจับหมาป่า")
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        
        vote_target = st.selectbox("เลือกคนที่ถูกโหวตออกเสียงส่วนใหญ่:", alive_players)
        
        if st.button("⚖️ ประหารชีวิต"):
            vote_idx = st.session_state.players.index(vote_target)
            st.session_state.status[vote_idx] = False
            play_sound("action_done")
            
            role_voted = st.session_state.roles[vote_idx]
            st.warning(f"⚖️ {vote_target} ถูกโ犯ประหารชีวิต! (บทบาทจริงคือ: {role_voted})")
            
            if role_voted == 'Fool':
                st.session_state.winner = f"🤡 {vote_target} (ตัวตลก) ชนะเกม!"
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
                st.session_state.phase = "NIGHT_WOLF"
            
            time.sleep(3)
            st.rerun()

    # ==================================================
    # 6. จบเกม (GAMEOVER)
    # ==================================================
    elif st.session_state.phase == "GAMEOVER":
        play_sound("gameover")
        st.balloons()
        st.title("🏆 GAME OVER")
        st.header(st.session_state.winner)
        
        if st.button("🔄 เล่นอีกตา"):
            st.session_state.phase = "SETUP"
            st.session_state.game_started = False
            st.rerun()
