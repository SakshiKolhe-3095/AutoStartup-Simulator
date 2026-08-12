"""
CFO Agent — cost model logic, unit economics, revenue-model options.
Owner: Sakshi
"""

from dataclasses import dataclass


@dataclass
class CostEstimate:
    idea: str
    dev_cost_estimate: float = 0.0
    monthly_infra_cost: float = 0.0
    notes: str = ""


class CFOAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def estimate_costs(self, idea: str) -> CostEstimate:
        """
        Skeleton: takes startup idea text, returns rough cost model.
        TODO (Wk2): revenue-model options, unit economics calc.
        """
        # placeholder logic
        return CostEstimate(
            idea=idea,
            dev_cost_estimate=0.0,
            monthly_infra_cost=0.0,
            notes="stub — not yet implemented"
        )


if __name__ == "__main__":
    agent = CFOAgent()
    result = agent.estimate_costs("sample startup idea")
    print(result)