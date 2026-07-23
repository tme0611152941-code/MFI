import random
import time
import winsound  # ไลบรารีสำหรับทำเสียงเตือนปลุกบน Windows / Python

# --------------------------------------------------
# ฟังก์ชันทำเสียงปลุก (Alarm Sounds)
# --------------------------------------------------
def play_morning_alarm():
    # เสียงปลุกตอนเช้า (ดังสลับความถี่แบบนาฬิกาปลุก iOS)
    for _ in range(3):
        winsound.Beep(1000, 150)  # ความถี่ 1000Hz ยาว 0.15 วิ
        winsound.Beep(1500, 150)  # ความถี่ 1500Hz ยาว 0.15 วิ
        time.sleep(0.1)

def play_action_sound():
    # เสียงเตือนเมื่อทำภารกิจ/โหวตเสร็จ
    winsound.Beep(800, 200)

def play_gameover_alarm():
    # เสียงปลุกรัวๆ เมื่อจบเกม
    for i in range(4):
        winsound.Beep(1200 - (i * 200), 200)

# --------------------------------------------------
# 1. ตั้งค่าผู้เล่นและสุ่มบทบาท (Roles Setup)
# --------------------------------------------------
print("=== WELCOME TO WEREWOLF GAME ===")
num_players = int(input("Enter number of players (6-10): "))

players = []
for i in range(1, num_players + 1):
    players.append("Player_" + str(i))

roles_pool = ['Werewolf', 'Seer', 'Bodyguard', 'Witch', 'Hunter']

if num_players >= 8:
    roles_pool.append('Werewolf')

while len(roles_pool) < num_players:
    roles_pool.append('Villager')

random.shuffle(roles_pool)

player_roles = list(roles_pool)
player_status = [] 
for p in players:
    player_status.append(True)

witch_heal = True
witch_poison = True

print("\n--- ASSIGNING ROLES ---")
for i in range(num_players):
    print(players[i] + " is " + player_roles[i])
    
print("\nGame start in 3 seconds...")
time.sleep(3)

# --------------------------------------------------
# 2. เริ่มลูปเกม (Game Loop)
# --------------------------------------------------
game_over = False
winner = ""

while not game_over:
    
    # ----------------------------------------------
    # NIGHT PHASE (ช่วงกลางคืน)
    # ----------------------------------------------
    print("\n==========================================")
    print("🌙 NIGHT PHASE - Everyone close your eyes...")
    print("==========================================")
    
    target_wolf = ""
    protected_player = ""
    witch_kill_target = ""
    witch_saved = False
    
    # --- 1. WEREWOLF TURN ---
    print("\n[🐺 Werewolf Turn]")
    for i in range(num_players):
        if player_status[i]:
            print(str(i+1) + ". " + players[i])
            
    wolf_choice = int(input("Werewolf! Choose player index to kill: ")) - 1
    target_wolf = players[wolf_choice]
    play_action_sound()  # เสียงเตือนเมื่อหมาป่าทำภารกิจเสร็จ
    
    # --- 2. SEER TURN ---
    print("\n[🔮 Seer Turn]")
    seer_alive = False
    for i in range(num_players):
        if player_roles[i] == 'Seer' and player_status[i]:
            seer_alive = True
            
    if seer_alive:
        seer_choice = int(input("Seer! Choose player index to check: ")) - 1
        if player_roles[seer_choice] == 'Werewolf':
            print(">>> Result: This player is a WEREWOLF! 🐺")
        else:
            print(">>> Result: This player is NOT a werewolf. 🧑")
        play_action_sound()  # เสียงเตือนเมื่อหมอดูส่องเสร็จ
    else:
        print("(Seer is not in game or dead)")

    # --- 3. BODYGUARD TURN ---
    print("\n[🛡️ Bodyguard Turn]")
    guard_alive = False
    for i in range(num_players):
        if player_roles[i] == 'Bodyguard' and player_status[i]:
            guard_alive = True
            
    if guard_alive:
        guard_choice = int(input("Bodyguard! Choose player index to protect: ")) - 1
        protected_player = players[guard_choice]
        play_action_sound()  # เสียงเตือนเมื่อบอดี้การ์ดเลือกเสร็จ
    else:
        print("(Bodyguard is not in game or dead)")

    # --- 4. WITCH TURN ---
    print("\n[🧙‍♀️ Witch Turn]")
    witch_alive = False
    for i in range(num_players):
        if player_roles[i] == 'Witch' and player_status[i]:
            witch_alive = True
            
    if witch_alive:
        print("Tonight, " + target_wolf + " was targeted by wolves.")
        if witch_heal:
            use_heal = input("Do you want to use HEAL potion? (y/n): ")
            if use_heal == 'y':
                witch_saved = True
                witch_heal = False
                
        if witch_poison:
            use_poison = input("Do you want to use POISON potion? (y/n): ")
            if use_poison == 'y':
                poison_choice = int(input("Choose player index to poison: ")) - 1
                witch_kill_target = players[poison_choice]
                witch_poison = False
        play_action_sound()  # เสียงเตือนเมื่อแม่มดเลือกเสร็จ
    else:
        print("(Witch is not in game or dead)")

    # ----------------------------------------------
    # PROCESS NIGHT DEATHS
    # ----------------------------------------------
    dead_tonight = []
    
    if target_wolf != protected_player and not witch_saved:
        for i in range(num_players):
            if players[i] == target_wolf and player_status[i]:
                player_status[i] = False
                dead_tonight.append(players[i])

    if witch_kill_target != "":
        for i in range(num_players):
            if players[i] == witch_kill_target and player_status[i]:
                player_status[i] = False
                dead_tonight.append(players[i])

    # ----------------------------------------------
    # DAY PHASE (ช่วงกลางวัน)
    # ----------------------------------------------
    print("\n==========================================")
    print("⏰ ALARM! ⏰")
    play_morning_alarm()  # 🔥 เสียงปลุกตอนเช้าปลุกทุกคนตื่น!
    print("☀️ DAY PHASE - Everyone wake up!")
    print("==========================================")
    
    if len(dead_tonight) == 0:
        print("Good news! No one died last night.")
    else:
        print("Bad news... Players who died last night:")
        for d in dead_tonight:
            print("- " + d)
            
            if player_roles[players.index(d)] == 'Hunter':
                print("🏹 HUNTER SKILL ACTIVATED!")
                hunter_shoot = int(input("Hunter! Choose player index to shoot before dying: ")) - 1
                player_status[hunter_shoot] = False
                print(players[hunter_shoot] + " was shot by the Hunter!")
                play_action_sound()

    # ----------------------------------------------
    # WIN CHECK 1
    # ----------------------------------------------
    wolves_alive = 0
    villagers_alive = 0
    for i in range(num_players):
        if player_status[i]:
            if player_roles[i] == 'Werewolf':
                wolves_alive += 1
            else:
                villagers_alive += 1

    if wolves_alive == 0:
        game_over = True
        winner = "VILLAGERS WIN! All werewolves are dead."
        break
    elif wolves_alive >= villagers_alive:
        game_over = True
        winner = "WEREWOLVES WIN! They outnumber the villagers."
        break

    # ----------------------------------------------
    # VOTING PHASE
    # ----------------------------------------------
    print("\n--- VOTING TIME ---")
    print("Discuss and vote for a suspect.")
    for i in range(num_players):
        if player_status[i]:
            print(str(i+1) + ". " + players[i])
            
    voted_choice = int(input("\nEnter player index to ELIMINATE: ")) - 1
    player_status[voted_choice] = False
    play_action_sound()
    
    print("\n" + players[voted_choice] + " was voted out and executed!")
    print("Role was: " + player_roles[voted_choice])
    
    if player_roles[voted_choice] == 'Hunter':
        print("🏹 HUNTER SKILL ACTIVATED!")
        hunter_shoot = int(input("Hunter! Choose player index to shoot before dying: ")) - 1
        player_status[hunter_shoot] = False
        print(players[hunter_shoot] + " was shot by the Hunter!")
        play_action_sound()

    # ----------------------------------------------
    # WIN CHECK 2
    # ----------------------------------------------
    wolves_alive = 0
    villagers_alive = 0
    for i in range(num_players):
        if player_status[i]:
            if player_roles[i] == 'Werewolf':
                wolves_alive += 1
            else:
                villagers_alive += 1

    if wolves_alive == 0:
        game_over = True
        winner = "VILLAGERS WIN! All werewolves are dead."
    elif wolves_alive >= villagers_alive:
        game_over = True
        winner = "WEREWOLVES WIN! They outnumber the villagers."

# --------------------------------------------------
# 3. สรุปผลเกม (End Game)
# --------------------------------------------------
print("\n==========================================")
play_gameover_alarm()  # 🔥 เสียงปลุกจบเกม
print("🎉 GAME OVER 🎉")
print(winner)
print("==========================================")
