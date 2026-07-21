import time

start = time.time()

answer = generate_answer(
    "What is phishing?",
    "Phishing is..."
)

end = time.time()

print(
    f"Response Time: {end - start:.2f} seconds"
)