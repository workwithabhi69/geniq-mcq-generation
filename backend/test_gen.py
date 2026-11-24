import sys, os
sys.path.append(r"C:\Users\ag634\.gemini\antigravity\scratch\geniq\backend")
from dotenv import load_dotenv
load_dotenv(r"C:\Users\ag634\.gemini\antigravity\scratch\geniq\backend\.env")
from app.generation.gemini_generator import GeminiGenerator

gen = GeminiGenerator()
print("Is configured:", gen.is_configured())

passage = "Newton's second law of motion states that the acceleration of an object is directly proportional to the net force acting upon it and inversely proportional to its mass, represented as F = ma."
mcq, latency, err = gen.generate_single_mcq(
    passage=passage,
    strategy="structured",
    model_name="gemini-flash-lite-latest",
    topic="Physics"
)

if err:
    print("Generation Error:", err)
else:
    print("SUCCESS! Generated Question:", mcq.question)
    print("Options:", mcq.options.dict())
    print("Correct Answer:", mcq.correct_answer)
    print("Latency:", latency, "ms")
