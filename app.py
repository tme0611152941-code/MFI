<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Werewolf Master</title>
    <style>
        body { font-family: 'Sukhumvit Set', 'Kanit', sans-serif; background-color: #0b0f19; color: white; text-align: center; padding: 20px; }
        .card { background-color: #1e293b; padding: 20px; border-radius: 15px; border: 2px solid #3b82f6; max-width: 500px; margin: 0 auto 20px; }
        button { background-color: #2563eb; color: white; border: none; padding: 15px 25px; font-size: 18px; font-weight: bold; border-radius: 10px; cursor: pointer; width: 100%; margin-top: 10px; }
        button:hover { background-color: #1d4ed8; }
        select, textarea { width: 90%; padding: 10px; font-size: 16px; border-radius: 8px; margin-bottom: 10px; }
        .night { background-color: #111827; border-color: #4f46e5; }
        .alert { color: #f59e0b; font-size: 24px; font-weight: bold; }
    </style>
</head>
<body>

    <h1>🤖 AI Werewolf Master</h1>
    <p>ระบบคุมเกมอัตโนมัติ (เวอร์ชัน HTML สำหรับ iPad เสียงชัวร์ 100%)</p>

    <!-- Phase 1: Setup -->
    <div id="setup-phase" class="card">
        <h2>⚙️ ตั้งค่าผู้เล่น</h2>
        <textarea id="player-names" rows="6">แต้ม&#10;บอม&#10;นนท์&#10;ตั๊ก&#10;เอ็ม&#10;เกรท</textarea><br>
        <button onclick="startGame()">🎲 เริ่มสุ่มบทบาท</button>
    </div>

    <!-- Phase 2: Action Phase -->
    <div id="game-phase" class="card night" style="display:none;">
        <h2 id="phase-title">🌙 กลางคืน</h2>
        <div id="phase-content"></div>
        <button id="action-btn" onclick="nextStep()">🔔 ยืนยัน</button>
    </div>

    <script>
        let players = [];
        let roles = {};
        let currentStep = 0;
        let nightKills = "";

        // เสียงไก่ขัน MP3 ชัดเจน
        const roosterAudio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');

        // ฟังก์ชันพูดภาษาไทย
        function speak(text, delay = 0) {
            setTimeout(() => {
                window.speechSynthesis.cancel();
                let msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'th-TH';
                msg.rate = 0.85;
                window.speechSynthesis.speak(msg);
            }, delay);
        }

        function startGame() {
            let input = document.getElementById("player-names").value.trim();
            players = input.split('\n').map(p => p.trim()).filter(p => p);
            if(players.length < 4) { alert("กรุณาใส่ชื่อผู้เล่นอย่างน้อย 4 คน"); return; }

            // สุ่มบทบาท
            let deck = ["🐺 หมาป่า", "🔮 ผู้หยั่งรู้", "🛡️ หมอ"];
            while(deck.length < players.length) deck.push("🏡 ชาวบ้าน");
            deck = deck.sort(() => Math.random() - 0.5);

            players.forEach((p, i) => roles[p] = deck[i]);

            document.getElementById("setup-phase").style.display = "none";
            document.getElementById("game-phase").style.display = "block";
            
            startNight();
        }

        function startNight() {
            currentStep = 1;
            showWolfStep();
        }

        function showWolfStep() {
            document.getElementById("phase-title").innerText = "🐺 ช่วงเวลาของมนุษย์หมาป่า";
            let options = players.map(p => `<option value="${p}">${p}</option>`).join('');
            document.getElementById("phase-content").innerHTML = `
                <p>เลือกคนที่หมาป่าต้องการฆ่า:</p>
                <select id="kill-target">${options}</select>
            `;
            document.getElementById("action-btn").onclick = () => {
                nightKills = document.getElementById("kill-target").value;
                document.getElementById("phase-content").innerHTML = "<p class='alert'>⏳ บันทึกข้อมูลเรียบร้อย...</p>";
                // หน่วง 2 วินาที แล้วพูดเสียงคน
                speak("ทำภารกิจเสร็จแล้ว ส่งเครื่องคืนกลางวง แล้วหลับตาลงได้ค่ะ", 2000);
                setTimeout(showDoctorStep, 4000);
            };
        }

        function showDoctorStep() {
            document.getElementById("phase-title").innerText = "🛡️ ช่วงเวลาของหมอ";
            let options = players.map(p => `<option value="${p}">${p}</option>`).join('');
            document.getElementById("phase-content").innerHTML = `
                <p>เลือกคนที่หมอต้องการคุ้มกัน:</p>
                <select id="heal-target">${options}</select>
            `;
            document.getElementById("action-btn").onclick = () => {
                let healTarget = document.getElementById("heal-target").value;
                if(healTarget === nightKills) nightKills = ""; // ช่วยทัน
                document.getElementById("phase-content").innerHTML = "<p class='alert'>⏳ บันทึกข้อมูลเรียบร้อย...</p>";
                speak("ทำภารกิจเสร็จแล้ว ส่งเครื่องคืนกลางวง แล้วหลับตาลงได้ค่ะ", 2000);
                setTimeout(showMorningStep, 4000);
            };
        }

        function showMorningStep() {
            document.getElementById("phase-title").innerText = "🐓 เช้าวันใหม่";
            document.getElementById("phase-content").innerHTML = "<p class='alert'>🔔 กำลังส่งเสียงไก่ขันปลุกทุกคน...</p>";
            document.getElementById("action-btn").style.display = "none";

            // เล่นเสียงไก่ขันทันที
            roosterAudio.play();

            // AI พูดปลุกหลังไก่ขันจบ
            speak("อรุณสวัสดิ์ค่ะทุกคน ลืมตาขึ้นมาได้แล้วค่ะ", 2500);

            setTimeout(() => {
                let resultText = nightKills ? `💀 เมื่อคืนนี้... ${nightKills} โดนหมาป่าสังหาร!` : "🕊️ คืนที่ผ่านมาเงียบสงบ ไม่มีใครเสียชีวิต!";
                document.getElementById("phase-content").innerHTML = `<h2>${resultText}</h2>`;
            }, 5000);
        }
    </script>
</body>
</html>
