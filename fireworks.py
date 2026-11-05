import random
import threading
import tkinter as tk
from number_fact_api import fetch_number_fact, get_random_interesting_fact

class VictoryScreen:
    def __init__(self, root, winner, featured_number=1729, number_context="오늘의 대표 숫자"):
        self.root = root
        self.winner = winner
        self.featured_number = featured_number
        self.number_context = number_context
        self.sparks = []
        self.quiz_data = None
        self.quiz_buttons = []
        
        # 윈도우 크기 조정 (상식 패널이 여유 있게 보이도록 확장)
        self.root.geometry("800x680")
        self.root.configure(bg="#111827")

        # 메인 컨테이너
        self.main_container = tk.Frame(self.root, bg="#111827")
        self.main_container.pack(fill="both", expand=True)

        # 1. 상단 축하 캔버스 (폭죽 애니메이션 구역)
        self.canvas_height = 200
        self.canvas = tk.Canvas(self.main_container, bg="#111827", height=self.canvas_height, highlightthickness=0)
        self.canvas.pack(fill="x", side="top")

        self.canvas.create_text(400, 50, text="🎉 축하합니다! 🎉", font=("Arial", 24, "bold"), fill="#FFD369")
        self.canvas.create_text(400, 110, text=f"🏆 최종 승리자: {winner} 🏆", font=("Arial", 28, "bold"), fill="#00ADB5")
        self.canvas.create_text(400, 160, text="3판 2선승제 배틀에서 승리하였습니다!", font=("Arial", 13), fill="#EEEEEE")

        # 2. 하단 '오늘의 숫자 상식' 카드 프레임
        self.card_frame = tk.Frame(self.main_container, bg="#1F2937", bd=2, relief="groove")
        self.card_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # 카드 상단 헤더 & 뱃지 행
        self.header_row = tk.Frame(self.card_frame, bg="#1F2937")
        self.header_row.pack(fill="x", padx=15, pady=(12, 6))

        tk.Label(
            self.header_row,
            text="📚 오늘의 숫자 상식 (Today's Number Fact)",
            font=("Arial", 14, "bold"),
            fg="#60A5FA",
            bg="#1F2937"
        ).pack(side="left")

        self.source_badge = tk.Label(
            self.header_row,
            text="조회 중...",
            font=("Arial", 10, "bold"),
            fg="#9CA3AF",
            bg="#374151",
            padx=8,
            pady=3
        )
        self.source_badge.pack(side="right")

        # 선정된 숫자 안내
        self.number_banner = tk.Label(
            self.card_frame,
            text=f"선정 숫자: [ {self.featured_number} ]  ({self.number_context})",
            font=("Arial", 13, "bold"),
            fg="#FCD34D",
            bg="#1F2937"
        )
        self.number_banner.pack(pady=4)

        # 상식 내용 (영어 원문 & 한글 해설)
        self.fact_en_lbl = tk.Label(
            self.card_frame,
            text="Numbers API로부터 흥미로운 수학적 사실을 가져오는 중입니다...",
            font=("Arial", 11, "italic"),
            fg="#E5E7EB",
            bg="#1F2937",
            wraplength=720,
            justify="center"
        )
        self.fact_en_lbl.pack(padx=15, pady=4)

        self.fact_ko_lbl = tk.Label(
            self.card_frame,
            text="",
            font=("Arial", 12),
            fg="#A7F3D0",
            bg="#1F2937",
            wraplength=720,
            justify="center"
        )
        self.fact_ko_lbl.pack(padx=15, pady=4)

        # 3. 보너스 퀴즈 섹션
        self.quiz_frame = tk.Frame(self.card_frame, bg="#111827", bd=1, relief="ridge")
        self.quiz_frame.pack(fill="x", padx=20, pady=8)

        self.quiz_title_lbl = tk.Label(
            self.quiz_frame,
            text="💡 보너스 수학 퀴즈",
            font=("Arial", 11, "bold"),
            fg="#F59E0B",
            bg="#111827"
        )
        self.quiz_title_lbl.pack(anchor="w", padx=10, pady=(6, 2))

        self.quiz_q_lbl = tk.Label(
            self.quiz_frame,
            text="문제를 불러오는 중...",
            font=("Arial", 11),
            fg="#F3F4F6",
            bg="#111827"
        )
        self.quiz_q_lbl.pack(padx=10, pady=2)

        # 퀴즈 보기 버튼 컨테이너
        self.quiz_btn_frame = tk.Frame(self.quiz_frame, bg="#111827")
        self.quiz_btn_frame.pack(pady=6)

        # 퀴즈 결과 메시지
        self.quiz_result_lbl = tk.Label(
            self.quiz_frame,
            text="",
            font=("Arial", 11, "bold"),
            fg="#10B981",
            bg="#111827"
        )
        self.quiz_result_lbl.pack(pady=(0, 6))

        # 4. 하단 버튼 영역 (상식 새로고침 & 종료)
        self.bottom_btn_frame = tk.Frame(self.card_frame, bg="#1F2937")
        self.bottom_btn_frame.pack(fill="x", pady=10)

        self.refresh_btn = tk.Button(
            self.bottom_btn_frame,
            text="🔄 다른 숫자 상식 보기",
            font=("Arial", 11, "bold"),
            bg="#3B82F6",
            fg="white",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.request_random_fact
        )
        self.refresh_btn.pack(side="left", padx=30)

        self.close_btn = tk.Button(
            self.bottom_btn_frame,
            text="게임 종료",
            font=("Arial", 11, "bold"),
            bg="#EF4444",
            fg="white",
            padx=20,
            pady=4,
            cursor="hand2",
            command=self.root.destroy
        )
        self.close_btn.pack(side="right", padx=30)

        # 비동기로 첫 번째 상식 데이터 가져오기 (GUI 멈춤 방지)
        self.load_fact_async(self.featured_number)

        # 폭죽 애니메이션 시작
        self.animate()

    def load_fact_async(self, number: int):
        """백그라운드 스레드에서 REST API를 비동기 호출합니다."""
        self.source_badge.config(text="API 연결 중...", fg="#9CA3AF", bg="#374151")
        self.fact_en_lbl.config(text=f"숫자 {number}의 수학적 사실을 Numbers API에 요청하고 있습니다...")
        self.fact_ko_lbl.config(text="")
        self.quiz_q_lbl.config(text="보너스 퀴즈를 준비 중입니다...")
        self.quiz_result_lbl.config(text="")

        def task():
            fact_data = fetch_number_fact(number)
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.render_fact(fact_data))

        threading.Thread(target=task, daemon=True).start()

    def request_random_fact(self):
        """'다른 숫자 상식 보기' 버튼 클릭 시 무작위 흥미로운 상식을 비동기로 요청합니다."""
        self.refresh_btn.config(state="disabled")
        self.source_badge.config(text="데이터 요청 중...", fg="#9CA3AF", bg="#374151")

        def task():
            fact_data = get_random_interesting_fact()
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.on_random_fact_loaded(fact_data))

        threading.Thread(target=task, daemon=True).start()

    def on_random_fact_loaded(self, fact_data: dict):
        self.refresh_btn.config(state="normal")
        self.featured_number = fact_data["number"]
        self.number_context = "새로 탐색한 숫자"
        self.render_fact(fact_data)

    def render_fact(self, fact_data: dict):
        """API 또는 폴백에서 가져온 상식 데이터를 GUI 컴포넌트에 반영합니다."""
        num = fact_data["number"]
        self.number_banner.config(text=f"선정 숫자: [ {num} ]  ({self.number_context})")
        
        # 뱃지 스타일링
        if fact_data.get("is_api", False):
            self.source_badge.config(text="🟢 REST API (Numbers API)", fg="#10B981", bg="#064E3B")
        else:
            self.source_badge.config(text="🟡 수학 상식 아카이브 (로컬)", fg="#F59E0B", bg="#78350F")

        self.fact_en_lbl.config(text=f'"{fact_data["fact_en"]}"')
        self.fact_ko_lbl.config(text=fact_data["fact_ko"])

        # 퀴즈 렌더링
        self.render_quiz(fact_data.get("quiz"))

    def render_quiz(self, quiz: dict):
        # 기존 버튼 제거
        for btn in self.quiz_buttons:
            btn.destroy()
        self.quiz_buttons = []
        self.quiz_result_lbl.config(text="")

        if not quiz:
            self.quiz_q_lbl.config(text="이 숫자에 대한 퀴즈가 준비되지 않았습니다.")
            return

        self.quiz_data = quiz
        self.quiz_q_lbl.config(text=f"Q. {quiz['question']}")

        for idx, option_text in enumerate(quiz.get("options", [])):
            btn = tk.Button(
                self.quiz_btn_frame,
                text=f"({idx + 1}) {option_text}",
                font=("Arial", 10),
                bg="#374151",
                fg="#F3F4F6",
                activebackground="#4B5563",
                activeforeground="#FFFFFF",
                padx=10,
                pady=3,
                cursor="hand2",
                command=lambda i=idx: self.check_quiz_answer(i)
            )
            btn.pack(side="left", padx=6)
            self.quiz_buttons.append(btn)

    def check_quiz_answer(self, chosen_idx: int):
        if not self.quiz_data:
            return
        correct_idx = self.quiz_data.get("answer_idx", 0)
        explanation = self.quiz_data.get("explanation", "")

        for btn in self.quiz_buttons:
            btn.config(state="disabled")

        if chosen_idx == correct_idx:
            self.quiz_result_lbl.config(
                text=f"🎉 정답입니다! {explanation}",
                fg="#10B981"
            )
        else:
            correct_opt = self.quiz_data["options"][correct_idx]
            self.quiz_result_lbl.config(
                text=f"❌ 아쉽네요! 정답은 '({correct_idx + 1}) {correct_opt}' 입니다. ({explanation})",
                fg="#EF4444"
            )

    def animate(self):
        """폭죽 파티클 애니메이션"""
        if not self.root.winfo_exists():
            return
        colors = ["#FF5722", "#FFD369", "#00ADB5", "#EEEEEE", "#E91E63", "#4CAF50", "#9C27B0", "#60A5FA"]
        
        # 새로운 폭죽 생성
        if random.random() < 0.4 and len(self.sparks) < 60:
            cx = random.randint(100, 700)
            cy = random.randint(40, self.canvas_height - 30)
            col = random.choice(colors)
            for _ in range(14):
                spd = random.uniform(1.8, 5.0)
                vx = spd * random.choice([-1, 1]) * random.random()
                vy = spd * random.choice([-1, 1]) * random.random()
                self.sparks.append([cx, cy, vx, vy, col, 20])

        self.canvas.delete("spark")
        alive = []
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[5] -= 1
            if s[5] > 0:
                self.canvas.create_oval(
                    s[0] - 2.5, s[1] - 2.5, s[0] + 2.5, s[1] + 2.5,
                    fill=s[4], outline="", tags="spark"
                )
                alive.append(s)
        self.sparks = alive
        self.root.after(50, self.animate)
