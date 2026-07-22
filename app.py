import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าจอ
st.set_page_config(
    page_title="eFootball 3D Penalty - Streamlit Edition",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ eFootball 3D: Ultimate Penalty Kick")
st.caption("เกมยิงจุดโทษ 3D รันสดบนเบราว์เซอร์ผ่าน Three.js Physics Engine 🎮")

# 2. ฝัง HTML/JavaScript (Three.js 3D Engine)
html_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; overflow: hidden; background-color: #1a1a1a; font-family: sans-serif; }
        #canvas-container { width: 100vw; height: 75vh; }
        #ui-panel {
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.8); padding: 15px 25px; border-radius: 12px;
            color: white; text-align: center; border: 2px solid #00ff66;
            box-shadow: 0 0 15px rgba(0,255,102,0.4);
        }
        button {
            background: #00ff66; color: black; border: none; padding: 10px 20px;
            font-size: 16px; font-weight: bold; border-radius: 6px; cursor: pointer; margin: 5px;
        }
        button:hover { background: #00cc52; }
        .slider-group { display: inline-block; margin: 0 10px; }
    </style>
    <!-- Three.js Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>

    <div id="canvas-container"></div>

    <div id="ui-panel">
        <div class="slider-group">
            <label>มุมยิง (Aim): </label>
            <input type="range" id="aimAngle" min="-0.3" max="0.3" step="0.01" value="0">
        </div>
        <div class="slider-group">
            <label>แรงยิง (Power): </label>
            <input type="range" id="shootPower" min="15" max="35" step="1" value="22">
        </div>
        <button onclick="shootBall()">⚽ SHOOT!</button>
        <button onclick="resetBall()" style="background:#ff9900;">🔄 RESET</button>
        <h3 id="result-text" style="margin: 8px 0 0 0; color: #00ff66;">เล็งมุมแล้วกด SHOOT เพื่อยิงประตู!</h3>
    </div>

<script>
    // --- 3D SCENE SETUP ---
    const container = document.getElementById('canvas-container');
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a2b3c);
    scene.fog = new THREE.FogExp2(0x1a2b3c, 0.015);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / (window.innerHeight * 0.75), 0.1, 1000);
    camera.position.set(0, 2.2, 10);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight * 0.75);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // --- LIGHTS ---
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(10, 20, 10);
    dirLight.castShadow = true;
    scene.add(dirLight);

    // --- PITCH (สนามหญ้า) ---
    const pitchGeo = new THREE.PlaneGeometry(60, 80);
    const pitchMat = new THREE.MeshStandardMaterial({ color: 0x1e88e5, roughness: 0.8 }); // Green Pitch
    const pitch = new THREE.Mesh(pitchGeo, pitchMat);
    pitch.material.color.setHex(0x2e7d32);
    pitch.rotation.x = -Math.PI / 2;
    pitch.receiveShadow = true;
    scene.add(pitch);

    // --- GOAL POST (โกลฟุตบอล 3D) ---
    const goalGroup = new THREE.Group();
    const postMat = new THREE.MeshStandardMaterial({ color: 0xffffff });
    
    // เสาซ้าย-ขวา & คาน
    const leftPost = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 3), postMat);
    leftPost.position.set(-3.6, 1.5, -15);
    const rightPost = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 3), postMat);
    rightPost.position.set(3.6, 1.5, -15);
    const crossbar = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 7.4), postMat);
    crossbar.rotation.z = Math.PI / 2;
    crossbar.position.set(0, 3, -15);

    goalGroup.add(leftPost, rightPost, crossbar);
    scene.add(goalGroup);

    // --- GOALKEEPER 3D (โกล AI) ---
    const gkGeo = new THREE.BoxGeometry(0.8, 2.2, 0.5);
    const gkMat = new THREE.MeshStandardMaterial({ color: 0xffcc00 }); // เสื้อโกลสีเหลือง
    const goalkeeper = new THREE.Mesh(gkGeo, gkMat);
    goalkeeper.position.set(0, 1.1, -14.8);
    goalkeeper.castShadow = true;
    scene.add(goalkeeper);

    // --- FOOTBALL 3D (ลูกบอล) ---
    const ballGeo = new THREE.SphereGeometry(0.35, 32, 32);
    const ballMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
    const ball = new THREE.Mesh(ballGeo, ballMat);
    ball.position.set(0, 0.35, 6);
    ball.castShadow = true;
    scene.add(ball);

    // --- PHYSICS & ANIMATION ---
    let ballVelocity = new THREE.Vector3();
    let isMoving = false;
    let gkVelocityX = 0;

    function shootBall() {
        if (isMoving) return;
        
        const aim = parseFloat(document.getElementById('aimAngle').value);
        const power = parseFloat(document.getElementById('shootPower').value);

        ballVelocity.set(aim * 15, power * 0.25, -power);
        isMoving = true;

        // AI โกลพุ่งเซฟสุ่มซ้าย/ขวา
        gkVelocityX = (Math.random() - 0.5) * 6;
    }

    function resetBall() {
        ball.position.set(0, 0.35, 6);
        ballVelocity.set(0, 0, 0);
        goalkeeper.position.set(0, 1.1, -14.8);
        gkVelocityX = 0;
        isMoving = false;
        document.getElementById('result-text').innerText = "เล็งมุมแล้วกด SHOOT เพื่อยิงประตู!";
        document.getElementById('result-text').style.color = "#00ff66";
    }

    function animate() {
        requestAnimationFrame(animate);

        if (isMoving) {
            // บอลเคลื่อนที่ตามแรง
            ball.position.addScaledVector(ballVelocity, 0.016);
            ballVelocity.y -= 9.8 * 0.016; // แรงโน้มถ่วง
            ball.rotation.x -= 0.1;

            // โกลพุ่งตัว
            if (goalkeeper.position.y > 0.5) {
                goalkeeper.position.x += gkVelocityX * 0.016;
            }

            // ชนพื้น
            if (ball.position.y <= 0.35) {
                ball.position.y = 0.35;
                ballVelocity.y *= -0.4; // เด้งพื้น
            }

            // ตรวจสอบเข้าประตู / ติดเซฟ
            if (ball.position.z <= -14.8) {
                isMoving = false;
                
                // ตรวจระยะชนโกล
                const distToGK = ball.position.distanceTo(goalkeeper.position);
                if (distToGK < 1.2) {
                    document.getElementById('result-text').innerText = "❌ SAVED! ติดเซฟผู้รักษาประตู!";
                    document.getElementById('result-text').style.color = "#ff3333";
                } else if (Math.abs(ball.position.x) < 3.5 && ball.position.y < 3.0) {
                    document.getElementById('result-text').innerText = "⚽ GOALLLLL! เข้าประตูสุดสวย!";
                    document.getElementById('result-text').style.color = "#00ff66";
                } else {
                    document.getElementById('result-text').innerText = "OUT! ยิงออกนอกกรอบ!";
                    document.getElementById('result-text').style.color = "#ffcc00";
                }
            }
        }

        renderer.render(scene, camera);
    }

    animate();
</script>
</body>
</html>
"""

# แสดงผล HTML 3D บน Streamlit
components.html(html_code, height=650)
