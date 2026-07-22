import streamlit as st
import time

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="GÖTTFERT mi40 Simulator", layout="centered")

st.title("🎛️ GÖTTFERT mi40 - Melt Index Tester")
st.caption("โปรแกรมจำลองหน้าจอทดสอบ MFI / MFR / MVR")

st.divider()

# แถบตั้งค่าด้านข้าง
st.sidebar.header("⚙️ การตั้งค่าพารามิเตอร์")
sample_id = st.sidebar.text_input("รหัสตัวอย่าง (Sample ID)", "HDPE-LOT-01")
material = st.sidebar.selectbox("ชนิดพลาสติก", ["HDPE", "PP", "LDPE", "PET", "Custom"])

if material == "HDPE":
    default_temp, default_load, default_density = 190.0, 2.16, 0.766
elif material == "PP":
    default_temp, default_load, default_density = 230.0, 2.16, 0.738
else:
    default_temp, default_load, default_density = 190.0, 2.16, 0.766

temp = st.sidebar.number_input("อุณหภูมิทดสอบ (°C)", value=default_temp)
load = st.sidebar.selectbox("น้ำหนักกด (kg)", [1.2, 2.16, 5.0, 10.0, 21.6], index=1)
melt_density = st.sidebar.number_input("ความหนาแน่นขณะหลอม (g/cm³)", value=default_density)

# แสดงสถานะหน้าจอ
col1, col2, col3 = st.columns(3)
col1.metric("Target Temp", f"{temp} °C")
col2.metric("Test Load", f"{load} kg")
col3.metric("Status", "READY")

st.divider()

# ขั้นตอนทำแลปแบบกดติ๊กเช็ก
st.subheader("📋 ขั้นตอนการเตรียมเครื่อง")
chk1 = st.checkbox("1. ใส่ Die ด้านล่างของ Barrel เรียบร้อย")
chk2 = st.checkbox("2. ชั่งเม็ดพลาสติก 3-5 กรัม เทลง Barrel")
chk3 = st.checkbox("3. กระทุ้งไล่ฟองอากาศ และใส่ Piston ค้างไว้")

# ปุ่มเริ่มทดสอบ
if chk1 and chk2 and chk3:
    if st.button("🚀 เริ่มการทดสอบ (START TEST)", type="primary"):
        st.info("🔥 กำลัง Pre-heat พลาสติก และรอตำแหน่ง Piston...")
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.04)
            progress_bar.progress(i + 1)
        
        st.success("📍 ตรวจพบ Lower Mark -> กำลังบันทึกการไหล...")
        time.sleep(1)
        st.success("📍 ตรวจพบ Upper Mark -> การทดสอบเสร็จสมบูรณ์!")
        
        # ผลการทดสอบ
        st.balloons()
        st.subheader("📊 ผลการทดสอบ (Test Results)")
        simulated_mvr = 3.08
        simulated_mfr = simulated_mvr * melt_density
        
        res1, res2 = st.columns(2)
        res1.metric("MVR (ปริมาตร)", f"{simulated_mvr:.3f} cm³/10min")
        res2.metric("MFR (มวลสาร)", f"{simulated_mfr:.3f} g/10min")
else:
    st.warning("⚠️ กรุณาติ๊กเช็กขั้นตอนการเตรียมเครื่องให้ครบก่อนเริ่มกดทดสอบ")
