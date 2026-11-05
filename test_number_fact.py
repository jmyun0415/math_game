import unittest
from game_logic import GameLogic, is_prime
from number_fact_api import (
    fetch_number_fact,
    generate_dynamic_fact,
    get_divisors,
    get_random_interesting_fact,
    CURATED_FACTS
)

class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.logic = GameLogic("Alice", "Bob")

    def test_prime_function(self):
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertFalse(is_prime(4))
        self.assertTrue(is_prime(997))

    def test_question_numbers_recording(self):
        # 1. 암산 게임 (game_idx = 0)
        self.logic.start_game()
        q0 = self.logic.next_question()
        self.assertIn("x", q0)
        self.assertGreater(len(self.logic.question_numbers), 0)

        # 2. 암기 게임 (game_idx = 1)
        self.logic.game_idx = 1
        self.logic.start_game()
        self.assertEqual(len(self.logic.memory_numbers), 10)
        q1 = self.logic.next_question()
        self.assertIn("번째", q1)

        # 3. 소수 찾기 게임 (game_idx = 2)
        self.logic.game_idx = 2
        self.logic.start_game()
        q2 = self.logic.next_question()
        self.assertIn("소수", q2)

        # 代表 숫자 선정 테스트
        num, context = self.logic.get_featured_number()
        self.assertIsInstance(num, int)
        self.assertGreater(num, 0)
        self.assertIsInstance(context, str)

class TestNumberFactAPI(unittest.TestCase):
    def test_curated_facts(self):
        for num in [1, 2, 6, 42, 1729, 6174]:
            self.assertIn(num, CURATED_FACTS)
            res = fetch_number_fact(num, timeout=1.0)
            self.assertEqual(res["number"], num)
            self.assertTrue(len(res["fact_ko"]) > 0)
            self.assertIn("quiz", res)
            self.assertIn("question", res["quiz"])
            self.assertEqual(len(res["quiz"]["options"]), 3)
            self.assertIn(res["quiz"]["answer_idx"], [0, 1, 2])

    def test_dynamic_fact_generation(self):
        # 완전제곱수
        res_sq = generate_dynamic_fact(144)
        self.assertIn("완전제곱수", res_sq["fact_ko"])
        self.assertEqual(res_sq["quiz"]["answer_idx"], 1)

        # 2의 거듭제곱
        res_pow = generate_dynamic_fact(256)
        self.assertIn("2의", res_pow["fact_ko"])

        # 소수
        res_prime = generate_dynamic_fact(101)
        self.assertIn("소수", res_prime["fact_ko"])

        # 합성수
        res_comp = generate_dynamic_fact(15)
        self.assertIn("합성수", res_comp["fact_ko"])

    def test_random_fact_generation(self):
        res = get_random_interesting_fact()
        self.assertIsInstance(res["number"], int)
        self.assertTrue(len(res["fact_ko"]) > 0)
        self.assertIn("quiz", res)

if __name__ == "__main__":
    unittest.main()
