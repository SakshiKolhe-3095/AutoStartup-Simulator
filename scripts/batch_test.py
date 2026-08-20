"""Run the pipeline against diverse sample ideas, log failures/anomalies for review.
Not a pytest suite — this is exploratory hardening, output is for manual review."""
import json
import time
from backend.orchestration.graph import build_graph
from backend.utils.logger import get_logger

logger = get_logger(__name__)

SAMPLE_IDEAS = [
    "AI-powered plant disease detector for farmers",
    "Marketplace connecting local artisans with buyers",
    "Mobile app for tracking daily water intake with reminders",
    "Subscription box for eco-friendly cleaning products",
    "B2B SaaS dashboard for restaurant inventory management",
    "AI resume reviewer for job seekers",
    "Peer-to-peer tool rental platform for neighborhoods",
    "Personal finance app for freelancers to track irregular income",
    "AI-powered code review bot for GitHub",
    "Telehealth booking platform for rural clinics",
]

def run_batch():
    app = build_graph()
    results = []

    for idea in SAMPLE_IDEAS:
        logger.info(f"=== Running: {idea} ===")
        start = time.time()
        try:
            result = app.invoke({"idea": idea})
            elapsed = time.time() - start
            results.append({
                "idea": idea,
                "status": result.get("status"),
                "errors": result.get("errors", []),
                "elapsed_seconds": round(elapsed, 1),
                "cmo_empty": not bool(result.get("cmo_output", {}).get("market")),
                "cto_empty": not bool(result.get("cto_output", {}).get("mvp_features")),
                "cfo_empty": not bool(result.get("cfo_output", {}).get("cost_projection")),
                "investor_score": result.get("investor_score"),
            })
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"CRASHED on idea '{idea}': {e}", exc_info=True)
            results.append({
                "idea": idea, "status": "CRASHED", "errors": [str(e)],
                "elapsed_seconds": round(elapsed, 1),
            })

    with open("data/batch_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # summary
    print("\n=== BATCH SUMMARY ===")
    for r in results:
        flag = "❌" if r["status"] != "done" or r.get("errors") else "✅"
        print(f"{flag} [{r['elapsed_seconds']}s] {r['idea'][:50]} — status={r['status']}, errors={r.get('errors', [])}")


if __name__ == "__main__":
    run_batch()