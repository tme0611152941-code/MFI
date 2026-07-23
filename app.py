import streamlit as st
import random
import time

# ==================================================
# 1. ตั้งค่าหน้าเว็บ
# ==================================================
st.set_page_config(
    page_title="Ultimate Werewolf Web App",
    page_icon="🐺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================================================
# 2. ระบบ Custom Dynamic CSS (ปรับธีมตามช่วงเวลา)
# ==================================================
def apply_theme(phase):
    if "NIGHT" in phase:
        # ธีมกลางคืน (Dark Gothic Mood)
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(180deg, #090A0F 0%, #171B26 100%);
                color: #E2E8F0;
            }
            .stButton>button {
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: bold;
                box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4);
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6);
            }
            .role-card {
                background: rgba(30, 41, 59, 0.7);
                border: 2px solid #6366F1;
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    elif phase == "DAY":
        # ธีมกลางวัน (Warm Sunlight Mood)
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(180deg, #FEF3C7 0%, #FDE68A 100%);
                color: #1E293B;
            }
            .stButton>button {
                background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-weight: bold;
                box-shadow: 0 4px 14px rgba(217, 119, 6, 0.4);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        # ธีมปกติ (Setup / Voting)
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
                color: #F8FAFC;
            }
            .stButton>button {
                background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-weight: bold;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# ==================================================
# 3. ระบบ Sound Effects (รองรับ Safari & iPad)
# ==================================================
def play_sound(sound_type):
    sounds = {
        "wake_up": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_bb630cc098.mp3",
        "action_done": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3",
        "gameover": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_c6f2a32194.mp3"
    }
    sound_url = sounds.get(sound_type, "")
    if sound_url:
        st.components.v1.html(
            f"""
            <script>
            function playAudio() {{
                var audio = new Audio('{sound_url}');
                audio.play().catch(function(error) {{
                    console.log("Autoplay blocked: ", error);
                }});
            }}
            playAudio();
            </script>
            """,
            height=0,
        )

# ==================================================
# 4. ระบบ Session State
# ==================================================
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.phase = "SETUP"
    st.session_state.players = []
    st.session_state.roles = []
    st.session_state.status = []
    st.session_state.current_peek_idx = 0
    st.session_state.card_revealed = False
    st.session_state.lovers = []
    st.session_state.witch_heal = True
    st.session_state.witch_poison = True
    st.session_state.target_wolf = None
    st.session_state.protected_player = None
    st.session_state.witch_kill_target = None
    st.session_state.witch_saved = False
    st.session_state.seer_checked = False
    st.session_state.seer_result_name = ""
    st.session_state.seer_result_is_wolf = False
    st.session_state.winner = ""

# อัปเดตธีมตามเฟสปัจจุบัน
apply_theme(st.session_state.phase)

# ==================================================
# 1. หน้าตั้งค่าและสุ่มบทบาท (SETUP)
# ==================================================
if st.session_state.phase == "SETUP":
    st.title("🐺 Ultimate Werewolf")
    st.caption("✨ ระบบเกมหมาป่าเล่นบน iPad เครื่องเดียว แบบไร้คนคุมเกม")
    
    st.subheader("📝 1. ตั้งชื่อผู้เล่นทุกคน")
    num_players = st.number_input("จำนวนผู้เล่นทั้งหมด (คน):", min_value=4, max_value=20, value=6)
    
    player_names = []
    cols = st.columns(2)
    for i in range(num_players):
        col = cols[i % 2]
        name = col.text_input(f"คนที่ {i+1}:", value=f"ผู้เล่น_{i+1}", key=f"p_{i}")
        player_names.append(name.strip())

    st.write("---")
    st.subheader("🎭 2. เลือกการ์ดตัวละครที่จะใส่ในกองสุ่ม")
    
    col1, col2 = st.columns(2)
    with col1:
        num_wolves = st.slider("🐺 หมาป่า (Werewolf):", 1, 4, 1 if num_players < 8 else 2)
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
        st.error(f"❌ บทบาทพิเศษเกินจำนวนผู้เล่น! (ผู้เล่น {num_players} คน แต่เลือกไป {special_count} บท)")
    else:
        st.info(f"📊 สรุปการ์ด: หมาป่า {num_wolves} | บทพิเศษ {special_count - num_wolves} | ชาวบ้านธรรมดา {villagers_count}")
        
        if st.button("🎲 สุ่มแจกการ์ดบทบาทลับ"):
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
            st.session_state.current_peek_idx = 0
            st.session_state.card_revealed = False
            st.session_state.game_started = True
            st.session_state.phase = "CHECK_ROLES"
            st.rerun()

# ==================================================
# 2. หน้าเปิดดูการ์ดลับทีละคน (PASS & PEEK)
# ==================================================
elif st.session_state.phase == "CHECK_ROLES":
    idx = st.session_state.current_peek_idx
    current_player = st.session_state.players[idx]

    st.title("🎴 การ์ดบทบาทลับ")
    st.subheader(f"📲 คิวของ: **{current_player}**")

    role_database = {
        'Werewolf': {
            'title': '🐺 WEREWOLF (หมาป่า)',
            'desc': 'ตื่นมาตอนกลางคืนเพื่อเลือกสังหารชาวบ้าน 1 คนร่วมกับหมาป่าตัวอื่น!',
            'img': 'https://images.unsplash.com/photo-1550948537-130a168373e4?w=500&q=80'
        },
        'Seer': {
            'title': '🔮 SEER (หมอดู)',
            'desc': 'ตื่นมาตอนกลางคืนเพื่อเลือกส่องดูบทบาทของผู้เล่นอื่น 1 คนว่าเป็นหมาป่าหรือไม่',
            'img': 'https://images.unsplash.com/photo-1514533450685-4493e01d1fdc?w=500&q=80'
        },
        'Bodyguard': {
            'title': '🛡️ BODYGUARD (บอดี้การ์ด)',
            'desc': 'เลือกปกป้องผู้เล่น 1 คนให้รอดพ้นจากการโดนหมาป่าสังหารในคืนนั้น',
            'img': 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&q=80'
        },
        'Witch': {
            'title': '🧙‍♀️ WITCH (แม่มด)',
            'desc': 'มียาชุบชีวิต 1 ขวด และยาพิษ 1 ขวด (ใช้ได้ขวดละ 1 ครั้งต่อเกม)',
            'img': 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&q=80'
        },
        'Hunter': {
            'title': '🏹 HUNTER (นายพราน)',
            'desc': 'หากคุณเสียชีวิต ไม่ว่าจะโดนฆ่าหรือโดนโหวตออก คุณจะสามารถยิงคนอื่นตายตามได้ 1 คน',
            'img': 'https://images.unsplash.com/photo-1511216335778-7cb8f49fa7a3?w=500&q=80'
        },
        'Cupid': {
            'title': '💘 CUPID (คิวปิด)',
            'desc': 'ผูกดวงคู่รัก 2 คนในคืนแรก หากคนใดคนหนึ่งตาย อีกคนจะตรอมใจตายตามทันที',
            'img': 'https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=500&q=80'
        },
        'Fool': {
            'title': '🤡 FOOL (ตัวตลก)',
            'desc': 'เป้าหมายชนะพิเศษ: ต้องปั่นให้ผู้เล่นคนอื่นโหวตประหารชีวิตคุณในตอนกลางวัน!',
            'img': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&q=80'
        },
        'Little Girl': {
            'title': '👶 LITTLE GIRL (เด็กน้อย)',
            'desc': 'สามารถแอบลืมตาดูหมาป่าในตอนกลางคืนได้ แต่ถ้าหมาป่าจับได้ว่าแอบดูจะตายทันที',
            'img': 'https://images.unsplash.com/photo-1502086223501-7ea6ecd79368?w=500&q=80'
        },
        'Villager': {
            'title': '🧑 VILLAGER (ชาวบ้าน)',
            'desc': 'ไม่มีพลังพิเศษ ใช้ไหวพริบและการสังเกตจับผิดหมาป่า แล้วโหวตออกในตอนกลางวัน',
            'img': 'https://images.unsplash.com/photo-1542224566-6e85f2e6772f?w=500&q=80'
        }
    }

    if not st.session_state.card_revealed:
        st.warning(f"👉 กรุณายื่น iPad เครื่องนี้ให้ **{current_player}** แล้วกดเปิดการ์ด")
        if st.button(f"👁️ เปิดดูบทบาทของ {current_player}"):
            st.session_state.card_revealed = True
            st.rerun()
    else:
        role = st.session_state.roles[idx]
        data = role_database.get(role, role_database['Villager'])
        
        st.markdown(
            f"""
            <div class="role-card">
                <img src="{data['img']}" style="width:100%; max-height:220px; object-fit:cover; border-radius:12px; margin-bottom:15px;">
                <h2>{data['title']}</h2>
                <p style="font-size:16px;">{data['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("---")
        if st.button("🙈 จำบทบาทแล้ว! (ซ่อนการ์ด & ส่งต่อ)"):
            st.session_state.card_revealed = False
            if st.session_state.current_peek_idx + 1 < len(st.session_state.players):
                st.session_state.current_peek_idx += 1
            else:
                st.session_state.phase = "NIGHT_CUPID" if 'Cupid' in st.session_state.roles else "NIGHT_WOLF"
            st.rerun()

# ==================================================
# 3. ช่วงกลางคืน (NIGHT PHASES)
# ==================================================
else:
    # --- 💘 คิวปิด ---
    if st.session_state.phase == "NIGHT_CUPID":
        st.title("🌙 คืนอันเงียบสงบ")
        st.subheader("🙈 [ทุกคนหลับตา] -> 💘 คิวปิด ตื่นขึ้นมา!")
        st.caption("คิวปิดหยิบ iPad ไปเลือกคู่รัก 2 คนแล้วกดส่งสัญญาณ")
        
        lover1 = st.selectbox("เลือกคู่รักคนที่ 1:", st.session_state.players, index=0)
        lover2 = st.selectbox("เลือกคู่รักคนที่ 2:", st.session_state.players, index=1)
        
        if st.button("✅ ยืนยันคู่รัก (ส่งสัญญาณเสียง)"):
            st.session_state.lovers = [lover1, lover2]
            play_sound("action_done")
            st.success("🔔 ส่งสัญญาณเสียงเรียบร้อย! ให้คิวปิดหลับตาลง")
            time.sleep(2)
            st.session_state.phase = "NIGHT_WOLF"
            st.rerun()

    # --- 🐺 หมาป่า ---
    elif st.session_state.phase == "NIGHT_WOLF":
        st.title("🌙 คืนอันเงียบสงบ")
        st.subheader("🙈 [ทุกคนหลับตา] -> 🐺 หมาป่า ตื่นขึ้นมา!")
        st.caption("หมาป่าแอบลืมตามาเลือกสังหารเหยื่อ 1 คน")
        
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        target = st.radio("เลือกเหยื่อที่จะสังหาร:", alive_players, key="wolf_choice")
        
        if st.button("✅ ยืนยันการสังหาร (ส่งสัญญาณเสียง)"):
            st.session_state.target_wolf = target
            play_sound("action_done")
            st.success("🔔 ส่งสัญญาณเสียงเรียบร้อย! ให้หมาป่าหลับตาลง")
            time.sleep(2)
            st.session_state.phase = "NIGHT_SEER" if 'Seer' in st.session_state.roles else "NIGHT_GUARD"
            st.rerun()

    # --- 🔮 หมอดู (ล็อกส่องได้คืนละ 1 คน) ---
    elif st.session_state.phase == "NIGHT_SEER":
        st.title("🌙 คืนอันเงียบสงบ")
        st.subheader("🙈 [ทุกคนหลับตา] -> 🔮 หมอดู ตื่นขึ้นมา!")
        
        seer_alive = any(st.session_state.roles[i] == 'Seer' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if seer_alive:
            if not st.session_state.seer_checked:
                check_target = st.selectbox("เลือกคนที่ต้องการส่องดูบทบาท (ส่องได้แค่ 1 คน):", st.session_state.players, key="seer_choice")
                
                if st.button("🔍 ตรวจสอบบทบาท"):
                    st.session_state.seer_checked = True # ล็อกทันที!
                    t_idx = st.session_state.players.index(check_target)
                    st.session_state.seer_result_name = check_target
                    st.session_state.seer_result_is_wolf = (st.session_state.roles[t_idx] == 'Werewolf')
                    st.rerun()
            else:
                target_name = st.session_state.seer_result_name
                if st.session_state.seer_result_is_wolf:
                    st.error(f"🔍 ผลการตรวจ: **{target_name}** เป็น 🐺 หมาป่า!")
                else:
                    st.success(f"🔍 ผลการตรวจ: **{target_name}** เป็น 🧑 คนธรรมดา (ไม่ใช่หมาป่า)")
                
                st.caption("🔒 ล็อกการส่องเรียบร้อยแล้ว คุณไม่สามารถส่องคนอื่นเพิ่มได้ในคืนนี้")

            st.write("---")
            if st.button("✅ ตรวจเสร็จแล้ว (ส่งสัญญาณเสียง)"):
                st.session_state.seer_checked = False # รีเซ็ตสำหรับคืนถัดไป
                play_sound("action_done")
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()
        else:
            if st.button("ข้ามช่วงหมอดู (เนียนส่งสัญญาณเสียง)"):
                st.session_state.seer_checked = False
                play_sound("action_done")
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()

    # --- 🛡️ บอดี้การ์ด ---
    elif st.session_state.phase == "NIGHT_GUARD":
        st.title("🌙 คืนอันเงียบสงบ")
        st.subheader("🙈 [ทุกคนหลับตา] -> 🛡️ บอดี้การ์ด ตื่นขึ้นมา!")
        guard_alive = any(st.session_state.roles[i] == 'Bodyguard' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if guard_alive:
            alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
            guard_target = st.selectbox("เลือกคนที่ต้องการปกป้อง:", alive_players, key="guard_choice")
            if st.button("✅ ยืนยันการปกป้อง (ส่งสัญญาณเสียง)"):
                st.session_state.protected_player = guard_target
                play_sound("action_done")
                st.session_state.phase = "NIGHT_WITCH" if 'Witch' in st.session_state.roles else "DAY"
                st.rerun()
        else:
            if st.button("ข้ามช่วงบอดี้การ์ด (เนียนส่งสัญญาณเสียง)"):
                play_sound("action_done")
                st.session_state.phase = "NIGHT_WITCH" if 'Witch' in st.session_state.roles else "DAY"
                st.rerun()

    # --- 🧙‍♀️ แม่มด ---
    elif st.session_state.phase == "NIGHT_WITCH":
        st.title("🌙 คืนอันเงียบสงบ")
        st.subheader("🙈 [ทุกคนหลับตา] -> 🧙‍♀️ แม่มด ตื่นขึ้นมา!")
        witch_alive = any(st.session_state.roles[i] == 'Witch' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if witch_alive:
            st.info(f"💡 เหยื่อที่โดนหมาป่าสังหารคืนนี้คือ: **{st.session_state.target_wolf}**")
            
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
                
                play_sound("action_done")
                st.session_state.phase = "DAY"
                st.rerun()
        else:
            if st.button("ข้ามช่วงแม่มด (เนียนส่งสัญญาณเสียง)"):
                play_sound("action_done")
                st.session_state.phase = "DAY"
                st.rerun()

    # ==================================================
    # 4. ช่วงเช้าวันใหม่ (DAY PHASE)
    # ==================================================
    elif st.session_state.phase == "DAY":
        play_sound("wake_up") # ⏰ เสียงนาฬิกาปลุก
        st.title("☀️ เช้าวันใหม่ - ทุกคนตื่นนอน!")
        
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

        # เช็คคู่รัก
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
            st.success("🎉 เป็นข่าวดี! คืนที่ผ่านมาไม่มีใครเสียชีวิตเลย")
        else:
            st.error(f"💀 ข่าวร้าย... ผู้เสียชีวิตในคืนนี้ได้แก่: {', '.join(dead_tonight)}")

        st.session_state.target_wolf = None
        st.session_state.protected_player = None
        st.session_state.witch_kill_target = None
        st.session_state.witch_saved = False

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
    # 5. ช่วงโหวตประหารชีวิต (VOTING PHASE)
    # ==================================================
    elif st.session_state.phase == "VOTING":
        st.title("🗳️ ช่วงการพูดคุยและโหวตประหาร")
        alive_players = [st.session_state.players[i] for i in range(len(st.session_state.players)) if st.session_state.status[i]]
        
        vote_target = st.selectbox("เลือกผู้ต้องสงสัยที่ถูกโหวตประหารชีวิต:", alive_players)
        
        if st.button("⚖️ ยืนยันผลการประหารชีวิต"):
            vote_idx = st.session_state.players.index(vote_target)
            st.session_state.status[vote_idx] = False
            play_sound("action_done")
            
            role_voted = st.session_state.roles[vote_idx]
            st.warning(f"⚖️ **{vote_target}** ถูกโหวตประหารชีวิต! (เฉลยบทบาทจริง: {role_voted})")
            
            if role_voted == 'Fool':
                st.session_state.winner = f"🤡 **{vote_target} (ตัวตลก)** ชนะเกม! เพราะปั่นจนโดนโหวตออกสำเร็จ!"
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
    # 6. หน้าจบเกม (GAME OVER)
    # ==================================================
    elif st.session_state.phase == "GAMEOVER":
        play_sound("gameover")
        st.balloons()
        st.snow()
        st.title("🏆 GAME OVER")
        st.header(st.session_state.winner)
        
        st.write("---")
        st.subheader("📜 สรุปบทบาทของผู้เล่นทั้งหมด:")
        for i in range(len(st.session_state.players)):
            st_text = "🟢 รอดชีวิต" if st.session_state.status[i] else "💀 เสียชีวิต"
            st.write(f"- **{st.session_state.players[i]}**: {st.session_state.roles[i]} ({st_text})")

        if st.button("🔄 เล่นใหม่อีกตา"):
            st.session_state.phase = "SETUP"
            st.session_state.game_started = False
            st.rerun()
