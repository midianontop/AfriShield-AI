import time
from threat_detector import ThreatDetector
from translations import translate_message, get_translator
from language_detector import detect_language_detailed


SAMPLE_TEXTS = [
    "My GTBank account was hacked and they asked for my OTP 123456 and took ₦5,000",
    "Someone withdrew ₦20000 from my account without permission",
    "An scam ne, sun nemi BVN na da OTP",
    "How can I recover from a WhatsApp takeover?",
    "My phone was infected with a virus and I see pop-up ads everywhere.",
]


def time_function(fn, *args, iterations=20):
    start = time.perf_counter()
    for _ in range(iterations):
        fn(*args)
    end = time.perf_counter()
    return (end - start) / iterations


if __name__ == "__main__":
    print("=== Performance Benchmark ===")

    print("Warm-up: instantiating translator, detector, and language detector...")
    get_translator()
    ThreatDetector()
    detect_language_detailed(SAMPLE_TEXTS[0])

    print("Warm-up complete. Running latency measurements...")
    detector = ThreatDetector()

    for text in SAMPLE_TEXTS:
        print(f"\nSample: {text}")
        t_translate = time_function(translate_message, text, None)
        print(f"  translate_message: {t_translate * 1000:.2f} ms")
        t_detect = time_function(detector.analyze, text)
        print(f"  detector.analyze: {t_detect * 1000:.2f} ms")

    print("\nNote: startup time should be measured separately by launching the app once.")
