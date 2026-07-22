import streamlit as st
import time
import pandas as pd
import numpy as np

# 1. ตั้งค่าคอนฟิกหน้าจอให้กว้างและใช้ธีม Dark/Industrial เหมือนซอฟต์แวร์จริง
st.set_page_config(
    page_title="GÖTTFERT miConnect - Melt Index Software",
    page_icon="🎛️",
    layout="wide"
)

# Custom CSS ตกแต่งให้เหมือนซอฟต์แวร์ควบคุมเครื่องจักร
st.markdown("""
    <style>
    .main { background-color: #1e1e1e; }
    .stMetric { background-color: #2b2b2b; padding: 10px; border-radius: 5px; border-left: 4px solid #ff6b00; }
    .status-box { background-color: #0d3b1e; color: #00ff66; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_allow_html=True)

# Header ซอฟต์แวร์จริง
st.title("🎛️ GÖTTFERT miConnect v4.2")
st.caption("Testing System for Melt Flow Rate (MFR) & Melt Volume Rate (MVR) - mi40 Series")

st.divider()

# 2. เลย์เอาต์แบ่ง 2 คอลัมน์ (ฝั่งตั้งค่า / ฝั่งหน้าจอควบคุม)
col_setup, col_display = st.columns([1, 2])

# --- ฝั่งซ้าย: TEST PARAMETERS & METHOD SETUP ---
with col_setup:
    st.subheader("🛠️ Test Parameters")
    
    sample_id = st.text_input("Sample Name / Batch ID", "HDPE-LOT-2026-01")
    operator = st.text_input("Operator Name", "Tam (SUT)")
    standard = st.selectbox("Standard Method", ["ISO 1133-1", "ASTM D1238"])
    
    st.markdown("---")
    st.markdown("**Material Profile & Conditions**")
    material = st.selectbox("Polymer Selection", ["HDPE", "PP", "LDPE", "PET", "Custom"])
    
    # Preset ค่าตามชนิดพลาสติก
    if material == "HDPE":
        def_temp, def_load, def_density = 190.0, 2.16, 0.766
    elif material == "PP":
        def_temp, def_load, def_density = 230.0, 2.16, 0.738
    elif material == "LDPE":
        def_temp, def_load, def_density = 190.0, 2.16, 0.762
    else:
        def_temp, def_load, def_density = 190.0, 2.16, 0.766

    set_temp = st.number_input("Set Temperature (°C)", value=def_temp, step=0.1)
    test_load = st.number_input("Test Load (kg)", value=def_load, step=0.01)
    melt_density = st.number_input("Melt Density (g/cm³)", value=def_density, format="%.3f")
    preheat_time = st.slider("Pre-heat Time (sec)", 60, 300, 240)

# --- ฝั่งขวา: REAL-TIME MONITORING & GRAPH ---
with col_display:
    st.subheader("🖥️ Machine Control & Live Monitor")
    
    # แสดงไฟสถานะและ Metric 3 ช่อง
    m1, m2, m3 = st.columns(3)
    m1.metric("Barrel Temp", f"{set_temp:.1f} °C", "STABLE (±0.1)")
    m2.metric("Selected Load", f"{test_load} kg", "Motorized OK")
    m3.metric("Piston Sensor", "READY", "Zone 0 mm")
    
    st.markdown("<div class='status-box'>SYSTEM STATUS: THERMAL EQUILIBRIUM REACHED</div>", unsafe_allow_html=True)
    st.write("")

    # แท็บจำลองหน้าจอทำงาน
    tab_graph, tab_data, tab_manual = st.tabs(["📈 Live Measuring Curve", "📊 Result Data Table", "📋 Operating Checklist"])
    
    with tab_manual:
        st.write("** Checkpoints Before Test Run:**")
        c1 = st.checkbox("Die inserted at Barrel bottom")
        c2 = st.checkbox("Sample resin (3-5g) loaded & tamped")
        c3 = st.checkbox("Piston positioned in Barrel")
        c4 = st.checkbox("Heat shield & Safety cover closed")

    with tab_graph:
        st.write("**Piston Position Trajectory (Start Range -> End Range)**")
        
        # ปุ่มสั่ง START TEST
        if st.button("🔴 START MEASUREMENT", type="primary", use_container_width=True):
            if not (c1 and c2 and c3):
                st.error("❌ Please complete all Operating Checklists before starting!")
            else:
                # จำลองการ Pre-heat
                with st.spinner(f"Pre-heating melt for {preheat_time}s..."):
                    p_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        p_bar.progress(i + 1)
                
                st.success("✅ Pre-heat Complete! Weight released automatically.")
                
                # จำลองสร้างข้อมูลกราฟ Real-time
                chart_place = st.empty()
                time_steps = np.linspace(0, 30, 30)
                # กราฟระยะการเคลื่อนของ Piston (mm)
                distance_data = np.cumsum(np.random.normal(0.85, 0.05, 30))
                
                chart_df = pd.DataFrame({
                    "Time (s)": time_steps,
                    "Piston Travel (mm)": distance_data,
                    "Lower Mark (Start)": 6.35,
                    "Upper Mark (End)": 25.4
                }).set_index("Time (s)")
                
                # วาดกราฟ
                st.line_chart(chart_df)
                
                # คำนวณผลลัพธ์
                sim_mvr = 2.85 + np.random.uniform(-0.05, 0.05)
                sim_mfr = sim_mvr * melt_density
                
                # บันทึกผลไว้ใน Session
                st.session_state['test_done'] = True
                st.session_state['res_mvr'] = sim_mvr
                st.session_state['res_mfr'] = sim_mfr

    with tab_data:
        if st.session_state.get('test_done', False):
            st.subheader("📋 Measured Results")
            r1, r2 = st.columns(2)
            r1.metric("MVR (Melt Volume Rate)", f"{st.session_state['res_mvr']:.3f} cm³/10min")
            r2.metric("MFR (Melt Mass Rate)", f"{st.session_state['res_mfr']:.3f} g/10min")
            
            st.divider()
            # ตาราง Data Log
            res_df = pd.DataFrame({
                "Parameter": ["Sample ID", "Operator", "Standard", "Material", "Temp (°C)", "Load (kg)", "MFR (g/10min)", "MVR (cm³/10min)"],
                "Value": [sample_id, operator, standard, material, set_temp, test_load, f"{st.session_state['res_mfr']:.3f}", f"{st.session_state['res_mvr']:.3f}"]
            })
            st.table(res_df)
            
            st.button("📥 Export Test Report (PDF/Excel)", help="Export summary report to local system")
        else:
            st.info("No test data available. Run measurement from 'Live Measuring Curve' tab.")
