import os, time, tkinter as tk
from game_logic import GameLogic
from fireworks import VictoryScreen

def get_digits(e):
    kc, ks = getattr(e, 'keycode', 0), getattr(e, 'keysym', '')
    if 96 <= kc <= 105: return None, str(kc - 96)
    kp_map = {"KP_0":"0","KP_1":"1","KP_2":"2","KP_3":"3","KP_4":"4","KP_5":"5","KP_6":"6","KP_7":"7","KP_8":"8","KP_9":"9",
              "KP_Insert":"0","KP_End":"1","KP_Down":"2","KP_Next":"3","KP_Left":"4","KP_Begin":"5","KP_Right":"6","KP_Home":"7","KP_Up":"8","KP_Prior":"9"}
    if ks in kp_map: return None, kp_map[ks]
    if 48 <= kc <= 57: return str(kc - 48), None
    return (ks, None) if ks in "0123456789" else (None, None)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("미니게임 배틀")
        self.root.geometry("720x540")
        self.root.configure(bg="#222831")
        self.logic, self.active_player = None, None
        self.input_buf, self.ans_start = "", 0.0
        self.mem_phase, self.mem_end = False, 0.0
        self.intermission, self.intermission_end = False, 0.0
        self.build_id_screen()
        self.root.bind("<Key>", self.on_key)
        self.root.after(100, self.tick)

    def build_id_screen(self):
        self.frame = tk.Frame(self.root, bg="#222831")
        self.frame.pack(expand=True)
        tk.Label(self.frame, text="🎮 미니게임 배틀", font=("Arial", 26, "bold"), fg="#00ADB5", bg="#222831").pack(pady=20)
        tk.Label(self.frame, text="플레이어 1 ID (상단 숫자열키):", font=("Arial", 12), fg="#EEEEEE", bg="#222831").pack()
        self.e1 = tk.Entry(self.frame, font=("Arial", 14), justify="center")
        self.e1.pack(pady=6)
        tk.Label(self.frame, text="플레이어 2 ID (우측 숫자패드):", font=("Arial", 12), fg="#EEEEEE", bg="#222831").pack()
        self.e2 = tk.Entry(self.frame, font=("Arial", 14), justify="center")
        self.e2.pack(pady=6)
        self.err_lbl = tk.Label(self.frame, text="", font=("Arial", 11), fg="#FF5722", bg="#222831")
        self.err_lbl.pack(pady=8)
        tk.Button(self.frame, text="게임 시작", font=("Arial", 13, "bold"), bg="#00ADB5", fg="white", width=15, command=self.start_game).pack(pady=10)

    def start_game(self):
        p1, p2 = self.e1.get().strip(), self.e2.get().strip()
        if not p1 or not p2:
            self.err_lbl.config(text="두 플레이어의 아이디를 모두 입력하세요.")
            return
        if p1 == p2:
            self.err_lbl.config(text="같은 플레이어 아이디를 받을 수 없습니다.")
            return
        self.logic = GameLogic(p1, p2)
        self.frame.destroy()
        self.build_game_screen()
        self.load_game()

    def build_game_screen(self):
        self.frame = tk.Frame(self.root, bg="#222831")
        self.frame.pack(fill="both", expand=True, padx=20, pady=15)
        self.top_lbl = tk.Label(self.frame, font=("Arial", 14, "bold"), fg="#EEEEEE", bg="#393E46", height=2)
        self.top_lbl.pack(fill="x")
        self.title_lbl = tk.Label(self.frame, font=("Arial", 18, "bold"), fg="#00ADB5", bg="#222831")
        self.title_lbl.pack(pady=6)
        self.score_lbl = tk.Label(self.frame, font=("Arial", 13, "bold"), fg="#FFD369", bg="#222831")
        self.score_lbl.pack()
        self.q_lbl = tk.Label(self.frame, font=("Arial", 20, "bold"), fg="#EEEEEE", bg="#222831", height=3)
        self.q_lbl.pack(pady=8)
        self.status_lbl = tk.Label(self.frame, font=("Arial", 13), fg="#EEEEEE", bg="#222831")
        self.status_lbl.pack(pady=4)
        self.input_lbl = tk.Label(self.frame, font=("Arial", 18, "bold"), fg="#00ADB5", bg="#393E46", width=30, height=2)
        self.input_lbl.pack(pady=6)
        self.timer_lbl = tk.Label(self.frame, font=("Arial", 13, "bold"), fg="#FF5722", bg="#222831")
        self.timer_lbl.pack()
        tk.Label(self.frame, text="P1: 상단 숫자열키 + Enter  |  P2: 우측 숫자패드 + Numpad Enter",
                 font=("Arial", 10), fg="#888888", bg="#222831").pack(side="bottom", pady=4)

    def load_game(self):
        self.logic.start_game()
        self.title_lbl.config(text=f"종목: {self.logic.game_names[self.logic.game_idx]} (2점 선취 승리)")
        if self.logic.game_idx == 1:
            self.mem_phase = True
            dur = 1 if os.environ.get("TEST_MODE") else 30
            self.mem_end = time.time() + dur
            self.q_lbl.config(text="  ".join(map(str, self.logic.memory_numbers)))
            self.status_lbl.config(text="10개의 숫자를 암기하세요! (30초)")
        else:
            self.mem_phase = False
            self.next_q()

    def next_q(self):
        self.active_player, self.input_buf = None, ""
        self.q_lbl.config(text=self.logic.next_question())
        self.status_lbl.config(text="숫자를 누르면 10초간 답변 기회가 주어집니다.")
        self.input_lbl.config(text="[ 대기 중 ]")
        self.update_scores()

    def update_scores(self):
        l = self.logic
        self.top_lbl.config(text=f"{l.p1}: {l.match_wins[1]}승   vs   {l.p2}: {l.match_wins[2]}승 (3판 2선승제)")
        self.score_lbl.config(text=f"현재 게임 점수  -  {l.p1}: {l.scores[1]}점   |   {l.p2}: {l.scores[2]}점")

    def on_key(self, e):
        if not self.logic or self.mem_phase or self.intermission or self.logic.match_winner():
            return
        ks = getattr(e, "keysym", "")
        p1_d, p2_d = get_digits(e)
        if self.active_player is None:
            if p1_d and not self.logic.is_locked(1):
                self.start_answer(1, p1_d)
            elif p2_d and not self.logic.is_locked(2):
                self.start_answer(2, p2_d)
            elif (p1_d and self.logic.is_locked(1)) or (p2_d and self.logic.is_locked(2)):
                p = 1 if p1_d else 2
                self.status_lbl.config(text=f"{p}번 플레이어는 10초 패널티 중! ({self.logic.remaining_lockout(p):.1f}초 남음)")
        else:
            p = self.active_player
            d = p1_d if p == 1 else p2_d
            bs = ("BackSpace",) if p == 1 else ("KP_Delete", "Delete", "BackSpace")
            ent = ("Return",) if p == 1 else ("KP_Enter", "Return")
            if d: self.input_buf += d
            elif ks in bs: self.input_buf = self.input_buf[:-1]
            elif ks in ent: self.submit_answer()
            p_name = self.logic.p1 if p == 1 else self.logic.p2
            self.input_lbl.config(text=f"{p_name}: {self.input_buf}")

    def start_answer(self, p, digit):
        self.active_player, self.input_buf, self.ans_start = p, digit, time.time()
        p_name = self.logic.p1 if p == 1 else self.logic.p2
        self.status_lbl.config(text=f"[{p_name}] 입력 중! 10초 안에 답을 제출하세요.")
        self.input_lbl.config(text=f"{p_name}: {self.input_buf}")

    def submit_answer(self):
        p, ans = self.active_player, self.input_buf
        p_name = self.logic.p1 if p == 1 else self.logic.p2
        if self.logic.check_answer(ans):
            won_game = self.logic.record_correct(p)
            self.active_player = None
            self.update_scores()
            if won_game:
                self.intermission = True
                dur = 0.5 if os.environ.get("TEST_MODE") else 5
                self.intermission_end = time.time() + dur
                l = self.logic
                self.q_lbl.config(text=f"🏆 {p_name} 게임 승리!\n현재 스코어: {l.p1} {l.match_wins[1]}승 - {l.p2} {l.match_wins[2]}승")
                self.input_lbl.config(text="[ 게임 종료 ]")
                self.timer_lbl.config(text="")
            else:
                self.next_q()
        else:
            self.logic.record_wrong(p)
            self.active_player = None
            self.update_scores()
            self.status_lbl.config(text=f"오답! {p_name} 10초간 입력 불가")
            self.input_lbl.config(text="[ 대기 중 ]")

    def tick(self):
        if self.logic and not self.logic.match_winner():
            now = time.time()
            if self.intermission:
                rem = max(0, int(self.intermission_end - now) + 1)
                self.status_lbl.config(text=f"게임 승자와 스코어 표시 중 ({rem}초 후 이동)")
                if now >= self.intermission_end:
                    self.intermission = False
                    if self.logic.match_winner():
                        w = self.logic.p1 if self.logic.match_winner() == 1 else self.logic.p2
                        self.frame.destroy()
                        VictoryScreen(self.root, w)
                    else:
                        self.logic.game_idx += 1
                        self.load_game()
                self.root.after(100, self.tick)
                return
            if self.mem_phase:
                rem = max(0, int(self.mem_end - now))
                self.status_lbl.config(text=f"숫자를 암기하세요! 남은 시간: {rem}초")
                if rem <= 0:
                    self.mem_phase = False
                    self.next_q()
            elif self.active_player:
                rem = max(0.0, 10.0 - (now - self.ans_start))
                self.timer_lbl.config(text=f"답변 제한 시간: {rem:.1f}초")
                if rem <= 0.0:
                    p = self.active_player
                    p_name = self.logic.p1 if p == 1 else self.logic.p2
                    self.logic.record_wrong(p)
                    self.active_player = None
                    self.update_scores()
                    self.status_lbl.config(text=f"시간 초과! {p_name} 10초간 입력 불가")
                    self.input_lbl.config(text="[ 대기 중 ]")
            else:
                l1, l2 = self.logic.remaining_lockout(1), self.logic.remaining_lockout(2)
                t1 = f"P1 패널티: {l1:.1f}초" if l1 > 0 else "P1 준비 완료"
                t2 = f"P2 패널티: {l2:.1f}초" if l2 > 0 else "P2 준비 완료"
                self.timer_lbl.config(text=f"{t1}   |   {t2}")
        self.root.after(100, self.tick)

if __name__ == "__main__":
    r = tk.Tk()
    app = App(r)
    r.mainloop()
