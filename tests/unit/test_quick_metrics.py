import json
from pathlib import Path

from src.dementia_simulation.evaluator.empathy_evaluator import EmpathyEvaluator


async def test_quick_metrics_dump():
    """
    Tests that a quick metrics report can be generated from sample caregiver responses.
    """
    samples = [
        "I understand. It's okay. You are safe.",
        "No, you're wrong. Don't you remember?",
        "Let's try this together. I'm here.",
    ]
    evaluator = EmpathyEvaluator()

    # evaluate_conversation takes a list of responses and returns a single dict
    result = await evaluator.evaluate_conversation(
        conversation_history=[], caregiver_responses=samples
    )
    score = result["overall_score"]

    outdir = Path("reports")
    outdir.mkdir(exist_ok=True)
    (outdir / "quick_metrics.json").write_text(
        json.dumps({"n": len(samples), "avg_overall": score}),
        encoding="utf-8",
    )
    assert (outdir / "quick_metrics.json").exists()

    # Verify content
    with open(outdir / "quick_metrics.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["n"] == 3
    assert "avg_overall" in data
    assert isinstance(data["avg_overall"], float)
