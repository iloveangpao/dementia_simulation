import json
from pathlib import Path
from src.dementia_simulation.evaluator.empathy_evaluator import evaluate_transcript


def test_quick_metrics_dump(tmp_path: Path):
    samples = [
        "I understand. It's okay. You are safe.",
        "No, you're wrong. Don't you remember?",
        "Let's try this together. I'm here.",
    ]
    scores = [evaluate_transcript(t)["overall_score"] for t in samples]
    report = {"n": len(samples), "avg_overall": sum(scores) / len(scores)}
    outdir = Path("reports")
    outdir.mkdir(exist_ok=True)
    (outdir / "quick_metrics.json").write_text(json.dumps(report), encoding="utf-8")
    assert (outdir / "quick_metrics.json").exists()
