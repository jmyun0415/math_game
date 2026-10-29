import random
import time

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

class GameLogic:
    def __init__(self, p1, p2):
        self.p1, self.p2 = p1, p2
        self.match_wins = {1: 0, 2: 0}
        self.game_idx = 0
        self.game_names = ["암산 게임", "암기 게임", "소수 찾기 게임"]
        self.scores = {1: 0, 2: 0}
        self.lockouts = {1: 0.0, 2: 0.0}
        self.memory_numbers = []
        self.memory_positions = []
        self.target_answer = ""
        self.question_text = ""

    def start_game(self):
        self.scores = {1: 0, 2: 0}
        self.lockouts = {1: 0.0, 2: 0.0}
        if self.game_idx == 1:
            self.memory_numbers = [random.randint(0, 9) for _ in range(10)]
            self.memory_positions = list(range(1, 11))
            random.shuffle(self.memory_positions)

    def next_question(self):
        if self.game_idx == 0:
            a, b = random.randint(100, 999), random.randint(100, 999)
            self.target_answer = str(a * b)
            self.question_text = f"{a}  x  {b}  =  ?"
        elif self.game_idx == 1:
            if not self.memory_positions:
                self.memory_positions = list(range(1, 11))
                random.shuffle(self.memory_positions)
            pos = self.memory_positions.pop()
            self.target_answer = str(self.memory_numbers[pos - 1])
            self.question_text = f"{pos}번째 숫자는 무엇이었습니까? (1~10번째)"
        elif self.game_idx == 2:
            primes = [n for n in range(100, 1000) if is_prime(n)]
            composites = [n for n in range(100, 1000) if not is_prime(n)]
            if random.random() < 0.5:
                num, ans = random.choice(primes), "1"
            else:
                num, ans = random.choice(composites), "2"
            self.target_answer = ans
            self.question_text = f"{num}은(는) 소수입니까, 합성수입니까?\n(1: 소수,  2: 합성수)"
        return self.question_text

    def check_answer(self, ans):
        return ans.strip() == self.target_answer

    def record_correct(self, player):
        self.scores[player] += 1
        if self.scores[player] >= 2:
            self.match_wins[player] += 1
            return True
        return False

    def record_wrong(self, player):
        self.lockouts[player] = time.time() + 10

    def is_locked(self, player):
        return time.time() < self.lockouts[player]

    def remaining_lockout(self, player):
        return max(0.0, self.lockouts[player] - time.time())

    def match_winner(self):
        if self.match_wins[1] >= 2:
            return 1
        if self.match_wins[2] >= 2:
            return 2
        return None
