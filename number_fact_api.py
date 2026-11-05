"""
Number Fact API Module
-----------------------
Numbers API (http://numbersapi.com) REST API를 호출하여
게임에서 활용된 숫자의 흥미로운 수학적 사실(Math Trivia/Fact)을 조회합니다.

- .env 파일 및 환경 변수(NUMBERS_API_BASE_URL, NUMBERS_API_KEY, API_TIMEOUT_SECONDS)를 지원합니다.
- 네트워크 단절, 응답 지연(Timeout), 404/500 에러 발생 시
  자체 내장된 수학 상식 아카이브 및 동적 수론 분석 엔진(Local Fallback DB)으로 자동 전환되어
  무중단으로 신뢰할 수 있는 교육적 정보를 제공합니다.
"""

import os
import json
import random
import urllib.request
import urllib.error

# .env 로드 시도 (python-dotenv가 설치되어 있는 경우)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# 환경 설정 기본값
DEFAULT_BASE_URL = os.environ.get("NUMBERS_API_BASE_URL", "http://numbersapi.com").rstrip("/")
API_KEY = os.environ.get("NUMBERS_API_KEY", "").strip()
DEFAULT_TIMEOUT = float(os.environ.get("API_TIMEOUT_SECONDS", "3.0"))

# 사전 정의된 주요 수학적 수 아카이브 (Fallback Knowledge Base)
CURATED_FACTS = {
    1: {
        "fact_en": "1 is the multiplicative identity and the first natural number.",
        "fact_ko": "1은 곱셈에 대한 항등원이자 가장 작은 자연수입니다.",
        "quiz": {
            "question": "1은 소수일까요, 합성수일까요?",
            "options": ["소수이다", "합성수이다", "소수도 합성수도 아니다"],
            "answer_idx": 2,
            "explanation": "1은 약수가 1개뿐이므로 정의상 소수(약수 2개)도 합성수(약수 3개 이상)도 아닙니다."
        }
    },
    2: {
        "fact_en": "2 is the smallest prime number and the only even prime.",
        "fact_ko": "2는 가장 작은 소수이자 유일한 짝수 소수(Even Prime)입니다.",
        "quiz": {
            "question": "소수 중에서 유일하게 짝수인 숫자는 무엇일까요?",
            "options": ["2", "4", "없음"],
            "answer_idx": 0,
            "explanation": "2를 제외한 모든 짝수는 2로 나누어떨어지므로 합성수입니다."
        }
    },
    3: {
        "fact_en": "3 is the first odd prime and a Fermat prime (2^1 + 1).",
        "fact_ko": "3은 최초의 홀수 소수이며 페르마 소수(2^1 + 1)입니다.",
        "quiz": {
            "question": "평면에서 면을 이루는 가장 작은 다각형(삼각형)의 변의 수는?",
            "options": ["2개", "3개", "4개"],
            "answer_idx": 1,
            "explanation": "평면에서 닫힌 도형을 만들 수 있는 최소 변의 수는 3개(삼각형)입니다."
        }
    },
    4: {
        "fact_en": "4 is the smallest composite number and the square of 2.",
        "fact_ko": "4는 가장 작은 합성수(약수: 1, 2, 4)이자 2의 제곱(2²)입니다.",
        "quiz": {
            "question": "4는 가장 작은 (   )이다. 빈칸에 알맞은 말은?",
            "options": ["소수", "합성수", "홀수"],
            "answer_idx": 1,
            "explanation": "4는 1과 자기 자신 외에 2를 약수로 가지므로 가장 작은 합성수입니다."
        }
    },
    5: {
        "fact_en": "5 is the hypotenuse of the smallest Pythagorean triple (3, 4, 5).",
        "fact_ko": "5는 가장 작은 피타고라스 세 수(3, 4, 5)의 빗변 길이이자 소수입니다.",
        "quiz": {
            "question": "직각삼각형의 두 변의 길이가 3, 4일 때 빗변의 길이는?",
            "options": ["5", "6", "7"],
            "answer_idx": 0,
            "explanation": "3² + 4² = 9 + 16 = 25 = 5² 입니다."
        }
    },
    6: {
        "fact_en": "6 is the smallest perfect number, equal to the sum of its proper divisors (1 + 2 + 3).",
        "fact_ko": "6은 자신을 제외한 약수들의 합(1 + 2 + 3 = 6)과 같은 최초의 완전수(Perfect Number)입니다.",
        "quiz": {
            "question": "자신을 제외한 양의 약수들의 합이 자기 자신이 되는 수를 무엇이라 부를까요?",
            "options": ["완전수", "친화수", "카프리카수"],
            "answer_idx": 0,
            "explanation": "자신을 제외한 약수의 합이 자기 자신과 같은 수를 '완전수'라고 합니다."
        }
    },
    7: {
        "fact_en": "7 is the fourth prime number and opposite sides of standard dice always sum to 7.",
        "fact_ko": "7은 4번째 소수이며, 표준 주사위의 마주 보는 두 면의 눈의 합은 항상 7입니다.",
        "quiz": {
            "question": "표준 정육면체 주사위에서 2의 반대편 면에 적힌 숫자는?",
            "options": ["4", "5", "6"],
            "answer_idx": 1,
            "explanation": "주사위의 마주 보는 두 면의 합은 항상 7이므로 7 - 2 = 5 입니다."
        }
    },
    8: {
        "fact_en": "8 is the cube of 2 (2^3) and the number of vertices in a cube.",
        "fact_ko": "8은 2의 세제곱(2³)이자 정육면체의 꼭짓점 개수입니다.",
        "quiz": {
            "question": "정육면체의 꼭짓점의 개수는 몇 개일까요?",
            "options": ["6개", "8개", "12개"],
            "answer_idx": 1,
            "explanation": "정육면체는 면 6개, 모서리 12개, 꼭짓점 8개로 이루어져 있습니다."
        }
    },
    9: {
        "fact_en": "9 is the smallest odd composite number and the square of 3.",
        "fact_ko": "9는 가장 작은 홀수 합성수이자 3의 제곱(3²)입니다.",
        "quiz": {
            "question": "가장 작은 홀수 합성수는 무엇일까요?",
            "options": ["3", "7", "9"],
            "answer_idx": 2,
            "explanation": "홀수 중 1은 둘 다 아니고, 3, 5, 7은 소수이므로 9가 첫 번째 홀수 합성수입니다."
        }
    },
    10: {
        "fact_en": "10 is the base of the standard decimal numeral system and the sum of the first four integers (1+2+3+4).",
        "fact_ko": "10은 우리가 일상에서 쓰는 10진법의 밑(Base)이자 처음 4개 자연수의 합(1+2+3+4)입니다.",
        "quiz": {
            "question": "1부터 4까지의 자연수를 모두 더한 값은 얼마일까요?",
            "options": ["8", "10", "12"],
            "answer_idx": 1,
            "explanation": "1 + 2 + 3 + 4 = 10 입니다."
        }
    },
    12: {
        "fact_en": "12 is a sublime number with 6 divisors (1, 2, 3, 4, 6, 12) widely used in time and calendars.",
        "fact_ko": "12는 약수가 6개나 되어 시계(12시간), 1년(12달), 1다스(12개) 등 일상에서 널리 쓰이는 수입니다.",
        "quiz": {
            "question": "12의 약수의 개수는 모두 몇 개일까요?",
            "options": ["4개", "6개", "8개"],
            "answer_idx": 1,
            "explanation": "12의 약수는 1, 2, 3, 4, 6, 12 로 총 6개입니다."
        }
    },
    28: {
        "fact_en": "28 is the second perfect number (1 + 2 + 4 + 7 + 14 = 28) and the 7th triangular number.",
        "fact_ko": "28은 6에 이은 두 번째 완전수(1 + 2 + 4 + 7 + 14 = 28)이자 1부터 7까지의 합입니다.",
        "quiz": {
            "question": "6 다음으로 나타나는 두 번째 완전수는 무엇일까요?",
            "options": ["18", "24", "28"],
            "answer_idx": 2,
            "explanation": "28의 진약수 합은 1 + 2 + 4 + 7 + 14 = 28 로 완전수입니다."
        }
    },
    42: {
        "fact_en": "42 is the product of the first three terms of Sylvester's sequence and famous as the Answer to Ultimate Question of Life, the Universe, and Everything.",
        "fact_ko": "42는 소설 '은하수를 여행하는 히치하이커를 위한 안내서'에서 '삶, 우주, 그리고 모든 것에 대한 궁극적인 해답'으로 등장하는 유명한 수입니다.",
        "quiz": {
            "question": "SF 소설 '은하수를 여행하는 히치하이커를 위한 안내서'에서 우주의 궁극적인 해답으로 제시된 숫자는?",
            "options": ["7", "42", "99"],
            "answer_idx": 1,
            "explanation": "슈퍼컴퓨터 '깊은 생각'이 750만 년간 계산하여 도출한 답이 바로 42입니다."
        }
    },
    100: {
        "fact_en": "100 is the square of 10 and the basis of percentage (per cent = per hundred).",
        "fact_ko": "100은 10의 제곱(10²)이자 비율을 나타내는 백분율(Percentage, %)의 기준이 되는 수입니다.",
        "quiz": {
            "question": "백분율(%)에서 0.25를 퍼센트로 환산하면 얼마일까요?",
            "options": ["2.5%", "25%", "250%"],
            "answer_idx": 1,
            "explanation": "0.25 × 100 = 25% 입니다."
        }
    },
    496: {
        "fact_en": "496 is the third perfect number and a harmonic divisor number.",
        "fact_ko": "496은 세 번째 완전수(1+2+4+8+16+31+62+124+248 = 496)이자 31번째 삼각수입니다.",
        "quiz": {
            "question": "완전수 496은 어떤 연속된 자연수들의 합(삼각수)일까요?",
            "options": ["1부터 10까지", "1부터 31까지", "1부터 50까지"],
            "answer_idx": 1,
            "explanation": "31 × 32 / 2 = 496 으로, 1부터 31까지의 합입니다."
        }
    },
    1729: {
        "fact_en": "1729 is the Ramanujan-Hardy Taxicab number: the smallest number expressible as the sum of two cubes in two different ways (1^3 + 12^3 = 9^3 + 10^3).",
        "fact_ko": "1729는 유명한 '택시수(Taxicab Number)'로, 서로 다른 두 양의 정수의 세제곱의 합으로 2가지 방법으로 나타낼 수 있는 가장 작은 수(1³ + 12³ = 9³ + 10³)입니다.",
        "quiz": {
            "question": "1729 = 1³ + 12³ = 9³ + (? )³ 일 때, 물음표에 들어갈 숫자는?",
            "options": ["8", "10", "11"],
            "answer_idx": 1,
            "explanation": "9³(729) + 10³(1000) = 1729 입니다."
        }
    },
    6174: {
        "fact_en": "6174 is Kaprekar's constant: any 4-digit number with at least two distinct digits reaches 6174 in at most 7 routine steps.",
        "fact_ko": "6174는 '카프리카 상수'입니다. 서로 다른 2개 이상의 숫자로 이루어진 4자리 수의 자릿수를 정렬하여 최대수에서 최소수를 빼는 과정을 반복하면 최대 7단계 안에 반드시 6174에 도달합니다.",
        "quiz": {
            "question": "4자리 수에 자릿수 정렬 뺄셈을 반복하면 도달하는 카프리카 상수는?",
            "options": ["6174", "1729", "3141"],
            "answer_idx": 0,
            "explanation": "인도의 수학자 D. R. 카프리카가 발견한 4자리 카프리카 상수는 6174입니다."
        }
    }
}

def is_prime(n: int) -> bool:
    """소수 판별 헬퍼 함수"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def get_divisors(n: int) -> list[int]:
    """약수 목록 반환"""
    divs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i*i != n:
                divs.append(n // i)
    return sorted(divs)

def generate_dynamic_fact(n: int) -> dict:
    """
    사전 정의되지 않은 임의의 정수 n에 대해
    수론적 특성(소수, 제곱수, 세제곱수, 약수 개수 등)을 분석하여
    상식과 보너스 퀴즈를 동적으로 생성합니다.
    """
    divs = get_divisors(n)
    num_divs = len(divs)
    
    # 1. 소수 검사
    prime_check = is_prime(n)
    
    # 2. 완전제곱수 검사
    root = int(round(n ** 0.5))
    is_square = (root * root == n and n > 1)
    
    # 3. 2의 거듭제곱 검사
    is_pow2 = (n > 0 and (n & (n - 1)) == 0 and n > 2)
    power = n.bit_length() - 1 if is_pow2 else 0

    if prime_check:
        fact_en = f"{n} is a prime number, divisible only by 1 and itself."
        fact_ko = f"{n}은(는) 1과 자기 자신만을 약수로 가지는 '소수(Prime Number)'입니다."
        quiz = {
            "question": f"숫자 {n}의 양의 약수의 개수는 모두 몇 개일까요?",
            "options": ["1개", "2개", "3개 이상"],
            "answer_idx": 1,
            "explanation": f"{n}은 소수이므로 약수가 1과 {n} 총 2개뿐입니다."
        }
    elif is_square and is_pow2:
        fact_en = f"{n} is both a perfect square ({root}^2) and an exact power of 2 (2^{power})."
        fact_ko = f"{n}은(는) {root}의 제곱({root}²)이자 2의 {power}제곱(2^{power})인 특별한 수입니다."
        quiz = {
            "question": f"숫자 {n}은 2의 몇 제곱일까요?",
            "options": [f"{power - 1}제곱", f"{power}제곱", f"{power + 1}제곱"],
            "answer_idx": 1,
            "explanation": f"2를 {power}번 곱하면 {n}이 됩니다 (2^{power} = {n})."
        }
    elif is_square:
        fact_en = f"{n} is a perfect square, equal to {root} squared ({root}^2)."
        fact_ko = f"{n}은(는) 정수 {root}의 제곱({root}²)으로 이루어진 '완전제곱수'입니다."
        quiz = {
            "question": f"숫자 {n}은 어떤 자연수의 제곱일까요?",
            "options": [str(root - 1), str(root), str(root + 1)],
            "answer_idx": 1,
            "explanation": f"{root} × {root} = {n} 입니다."
        }
    elif is_pow2:
        fact_en = f"{n} is an exact power of 2 (2^{power}), fundamental in binary computing."
        fact_ko = f"{n}은(는) 2의 {power}제곱(2^{power})으로, 컴퓨터 2진법 시스템에서 핵심적인 수입니다."
        quiz = {
            "question": f"{n}을 2진수로 변환했을 때 1의 개수는 몇 개일까요?",
            "options": ["1개", "2개", f"{power}개"],
            "answer_idx": 0,
            "explanation": f"2의 거듭제곱수는 2진수로 1 뒤에 0이 붙는 형태(1{'0'*power})이므로 1이 정확히 1개입니다."
        }
    else:
        # 일반 합성수
        parity = "짝수" if n % 2 == 0 else "홀수"
        fact_en = f"{n} is an {parity.lower()} composite number with {num_divs} divisors."
        fact_ko = f"{n}은(는) {num_divs}개의 약수를 가지는 {parity} 합성수입니다 (약수: {', '.join(map(str, divs[:6]))}{'...' if len(divs) > 6 else ''})."
        
        # 퀴즈: 약수 개수 또는 짝수/홀수
        quiz = {
            "question": f"숫자 {n}은(는) 소수입니까, 합성수입니까?",
            "options": ["소수", "합성수", "어느 것도 아님"],
            "answer_idx": 1,
            "explanation": f"{n}의 약수는 {num_divs}개(1, {divs[1]}, ..., {n})이므로 합성수입니다."
        }
        
    return {
        "fact_en": fact_en,
        "fact_ko": fact_ko,
        "quiz": quiz
    }

def fetch_number_fact(number: int, timeout: float = None) -> dict:
    """
    선정된 숫자에 대해 Numbers API (REST API)를 호출하여 정보를 조회합니다.
    API 호출에 실패(네트워크 단절, 404, 응답 지연 등)할 경우 로컬 폴백 아카이브로 안전하게 전환됩니다.
    
    Returns:
        dict: {
            "number": int,
            "fact_en": str,
            "fact_ko": str,
            "source": str,
            "is_api": bool,
            "quiz": dict
        }
    """
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
        
    base_url = DEFAULT_BASE_URL
    url = f"{base_url}/{number}/math?json"
    
    api_success = False
    fact_en = ""
    
    # 1. 외부 REST API 호출 시도
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MathGameBattle/1.0"})
        if API_KEY:
            req.add_header("X-Api-Key", API_KEY)
            req.add_header("Authorization", f"Bearer {API_KEY}")
            
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if isinstance(data, dict) and data.get("found", True):
                    fact_en = data.get("text", "").strip()
                    if fact_en:
                        api_success = True
    except Exception:
        # HTTPError (404, 500 등), URLError, Timeout, JSON 에러 모두 포획
        api_success = False

    # 2. 로컬 아카이브 또는 동적 수론 분석 엔진에서 한글 설명 및 퀴즈 생성
    if number in CURATED_FACTS:
        local_data = CURATED_FACTS[number]
        fact_ko = local_data["fact_ko"]
        quiz = local_data["quiz"]
        if not api_success:
            fact_en = local_data["fact_en"]
    else:
        dynamic_data = generate_dynamic_fact(number)
        fact_ko = dynamic_data["fact_ko"]
        quiz = dynamic_data["quiz"]
        if not api_success:
            fact_en = dynamic_data["fact_en"]

    source_label = "REST API (Numbers API)" if api_success else "수학 상식 아카이브 (로컬 Fallback)"

    return {
        "number": number,
        "fact_en": fact_en,
        "fact_ko": fact_ko,
        "source": source_label,
        "is_api": api_success,
        "quiz": quiz
    }

def get_random_interesting_fact() -> dict:
    """새로운 임의의 흥미로운 숫자 상식을 가져옵니다."""
    candidates = list(CURATED_FACTS.keys())
    # 추가로 3자리 또는 4자리 난수 포함
    candidates.extend([random.randint(11, 99), random.randint(101, 999)])
    chosen = random.choice(candidates)
    return fetch_number_fact(chosen)
