import json
from pathlib import Path

from src.dementia_simulation.evaluator.empathy_evaluator import evaluate_transcript


def test_quick_metrics_dump():
    samples = [
        "I understand. It's okay. You are safe.",
        "No, you're wrong. Don't you remember?",
        "Let's try this together. I'm here.",
    ]
    scores = [evaluate_transcript(t)["overall_score"] for t in samples]
    outdir = Path("reports")
    outdir.mkdir(exist_ok=True)
    (outdir / "quick_metrics.json").write_text(
        json.dumps({"n": len(samples), "avg_overall": sum(scores) / len(scores)}),
        encoding="utf-8",
    )
    assert (outdir / "quick_metrics.json").exists()
