    # --- 🔮 หมอดู ---
    elif st.session_state.phase == "NIGHT_SEER":
        st.title("🌙 คืนอันเงียบสงบ")
        st.subheader("🙈 [ทุกคนหลับตา] -> 🔮 หมอดู ตื่นขึ้นมา!")
        
        # สร้างตัวแปรเช็กว่าส่องไปแล้วหรือยังใน session_state
        if 'seer_checked' not in st.session_state:
            st.session_state.seer_checked = False

        seer_alive = any(st.session_state.roles[i] == 'Seer' and st.session_state.status[i] for i in range(len(st.session_state.players)))
        
        if seer_alive:
            # ถ้ายังไม่ได้ส่อง ให้เลือกคนแล้วกดส่องได้
            if not st.session_state.seer_checked:
                check_target = st.selectbox("เลือกคนที่ต้องการส่องดูบทบาท (ส่องได้แค่ 1 คน):", st.session_state.players, key="seer_choice")
                
                if st.button("🔍 ตรวจสอบบทบาท"):
                    st.session_state.seer_checked = True # ล็อกทันทีหลังกด!
                    t_idx = st.session_state.players.index(check_target)
                    st.session_state.seer_result_name = check_target
                    st.session_state.seer_result_is_wolf = (st.session_state.roles[t_idx] == 'Werewolf')
                    st.rerun()
            
            # ถ้าส่องไปแล้ว ให้แสดงผลตรวจเพียงอย่างเดียว และล็อกไม่ให้ส่องคนอื่นเพิ่ม
            else:
                target_name = st.session_state.seer_result_name
                if st.session_state.seer_result_is_wolf:
                    st.error(f"🔍 ผลการตรวจ: **{target_name}** เป็น 🐺 หมาป่า!")
                else:
                    st.success(f"🔍 ผลการตรวจ: **{target_name}** เป็น 🧑 คนธรรมดา (ไม่ใช่หมาป่า)")
                
                st.caption("🔒 ล็อกการส่องเรียบร้อยแล้ว คุณไม่สามารถส่องคนอื่นเพิ่มได้ในคืนนี้")

            st.write("---")
            if st.button("✅ ตรวจเสร็จแล้ว (ส่งสัญญาณเสียง)"):
                st.session_state.seer_checked = False # รีเซ็ตค่าสำหรับคืนถัดไป
                play_sound("action_done")
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()
        else:
            if st.button("ข้ามช่วงหมอดู (เนียนส่งสัญญาณเสียง)"):
                st.session_state.seer_checked = False
                play_sound("action_done")
                st.session_state.phase = "NIGHT_GUARD" if 'Bodyguard' in st.session_state.roles else "NIGHT_WITCH"
                st.rerun()
