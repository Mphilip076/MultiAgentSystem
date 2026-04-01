from typing import List, Literal, Optional
from pydantic import BaseModel, Field


Decision = Literal["pass", "flag", "reject"]
VerificationStatus = Literal["verified", "partially_verified", "unverified"]


class ValidationResult(BaseModel):
    source_name: str
    source_type: str
    claim: str
    authority_score: int = Field(ge=1, le=5)
    evidence_strength_score: int = Field(ge=1, le=5)
    transparency_score: int = Field(ge=1, le=5)
    recency_score: int = Field(ge=1, le=5)
    bias_risk_score: int = Field(ge=1, le=5)
    credibility_score_total: int = Field(ge=5, le=25)

    verification_status: VerificationStatus
    direct_support_score: int = Field(ge=0, le=2)
    cross_verification_score: int = Field(ge=0, le=2)
    specificity_score: int = Field(ge=0, le=2)
    consistency_score: int = Field(ge=0, le=2)
    claim_verification_total: int = Field(ge=0, le=8)

    report_worthiness_score: int = Field(ge=1, le=5)
    decision: Decision
    reasoning: str
    missing_information: List[str] = []
    supporting_evidence: List[str] = []