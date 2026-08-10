"""
CTO-agent and CFO-agent structured output contracts.
Owner: Lakshit

Consumed by: the deck-builder step (Sakshi) and CEO-agent synthesis (Yeshita) via
AgentState["cto_output"] / AgentState["cfo_output"]. CTOAgent.run() / CFOAgent.run()
return a dict matching these schemas' shape (model_dump()) rather than the model
instance itself, so it drops cleanly into the LangGraph state without a pydantic
dependency leaking into consumers that don't want it.
"""
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class MVPFeature(BaseModel):
    name: str
    description: str
    priority: Literal["must_have", "nice_to_have"]


class TechStackRecommendation(BaseModel):
    frontend: str
    backend: str
    database: str
    hosting: str
    rationale: str


class LandingPageValidation(BaseModel):
    valid: bool
    attempts: int
    errors: List[str] = Field(default_factory=list)
    fallback: bool = False


class CTOOutput(BaseModel):
    category: str
    mvp_features: List[MVPFeature]
    tech_stack: TechStackRecommendation
    architecture_summary: str
    landing_page_html: str
    landing_page_path: Optional[str] = None
    landing_page_validation: LandingPageValidation
    code_repo: Optional[str] = None


class CostProjection(BaseModel):
    development_cost: str
    operational_cost: str
    reasoning: str


class RevenueModelOption(BaseModel):
    model: str
    description: str


class UnitEconomics(BaseModel):
    cac: str
    ltv: str
    gross_margin: str
    reasoning: str


class FundingAsk(BaseModel):
    amount: str
    use_of_funds: str
    reasoning: str


class CFOOutput(BaseModel):
    category: str
    cost_projection: CostProjection
    revenue_model_options: List[RevenueModelOption]
    unit_economics: UnitEconomics
    funding_ask: FundingAsk
