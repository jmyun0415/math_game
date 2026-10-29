import random
import tkinter as tk

class VictoryScreen:
    def __init__(self, root, winner):
        self.root = root
        self.canvas = tk.Canvas(root, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(360, 140, text="🎉 축하합니다! 🎉", font=("Arial", 28, "bold"), fill="#FFD369")
        self.canvas.create_text(360, 210, text=f"최종 승리자: {winner}", font=("Arial", 32, "bold"), fill="#00ADB5")
        tk.Button(root, text="종료", font=("Arial", 14, "bold"), bg="#FF5722", fg="white",
                  width=12, command=root.destroy).place(x=300, y=420)
        self.sparks = []
        self.animate()

    def animate(self):
        if not self.root.winfo_exists():
            return
        colors = ["#FF5722", "#FFD369", "#00ADB5", "#EEEEEE", "#E91E63", "#4CAF50", "#9C27B0"]
        if random.random() < 0.4 and len(self.sparks) < 70:
            cx, cy = random.randint(120, 600), random.randint(80, 340)
            col = random.choice(colors)
            for _ in range(16):
                spd = random.uniform(2, 6)
                vx = spd * 1.5 * random.choice([-1, 1]) * random.random()
                vy = spd * 1.5 * random.choice([-1, 1]) * random.random()
                self.sparks.append([cx, cy, vx, vy, col, 22])
        self.canvas.delete("spark")
        alive = []
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[5] -= 1
            if s[5] > 0:
                self.canvas.create_oval(s[0]-3, s[1]-3, s[0]+3, s[1]+3, fill=s[4], outline="", tags="spark")
                alive.append(s)
        self.sparks = alive
        self.root.after(50, self.animate)
