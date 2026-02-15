"""
Quick manual test for the AI pipeline.
Usage: python -m backend.test_ai (from the project root)
   or: cd /path/to/dermalens && venv/bin/python -m backend.test_ai
"""
import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_pipeline import run_ai


def main():
    # Load a test image (use face.jpg at project root if it exists)
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "face.jpg")
    if not os.path.exists(image_path):
        # Try from cwd
        image_path = "face.jpg"

    if not os.path.exists(image_path):
        print("ERROR: No test image found. Place a face.jpg in the project root.")
        sys.exit(1)

    print(f"Loading test image: {image_path}")
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    print(f"Image size: {len(img_bytes)} bytes")

    quiz = {
        "sensitivity": False,
        "tight_after_wash": "no",
        "breakout_frequency": "sometimes",
    }
    priority = "acne"

    print("\nRunning AI pipeline...")
    print(f"  Model: {os.getenv('GEMINI_VISION_MODEL', 'gemini-2.5-flash')}")
    print(f"  API key set: {bool(os.getenv('GEMINI_API_KEY'))}")
    print()

    result = run_ai(
        front_bytes=img_bytes,
        left_bytes=None,
        right_bytes=None,
        quiz=quiz,
        priority=priority,
    )

    print("=== RESULT ===")
    if result.get("retake_required"):
        print("RETAKE REQUIRED")
        print(f"  Metrics: {result.get('metrics')}")
    else:
        print(f"Retake required: {result['retake_required']}")
        print(f"\nMetrics: {result['metrics']}")
        print(f"\nAnalysis (legacy format):")
        analysis = result["analysis"]
        for score in analysis["scores"]:
            print(f"  {score['name']}: {score['score']} ({score['color']})")
        print(f"  Overall Score: {analysis['overallScore']}")
        print(f"  Summary: {analysis['summary']}")
        print(f"\nPlan locked: {result.get('plan_locked')}")
        print(f"Lock reason: {result.get('lock_reason', '')}")
        print(f"\nRoutine (legacy format):")
        routine = result.get("routine", {})
        print(f"  Morning steps: {len(routine.get('morningSteps', []))}")
        for s in routine.get("morningSteps", []):
            print(f"    {s['order']}. {s['name']} — {s['productSuggestion']}")
        print(f"  Evening steps: {len(routine.get('eveningSteps', []))}")
        for s in routine.get("eveningSteps", []):
            print(f"    {s['order']}. {s['name']} — {s['productSuggestion']}")


if __name__ == "__main__":
    main()
