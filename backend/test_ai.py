from services.test import run_ai

# Load a local image (put any selfie jpg inside backend/)
with open("face.jpg", "rb") as f:
    front = f.read()

# Minimal quiz data for now
quiz = {
    "sensitivity": False,
    "tight_after_wash": "no",
    "breakout_frequency": "sometimes"
}

result = run_ai(
    front_bytes=front,
    left_bytes=None,
    right_bytes=None,
    quiz=quiz,
    priority="acne",
    weeks_on_plan=3
)

print(result)
