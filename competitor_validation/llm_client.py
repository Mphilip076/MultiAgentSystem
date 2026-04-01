import json
import ollama
from schemas import ValidationResult


OLLAMA_MODEL = "qwen3:8b"


def build_validation_prompt(source_name: str, source_type: str, raw_text: str) -> str:
    return f"""
You are a Data Auditor specializing in clinical trial and competitor intelligence validation.

Your job:
1. Extract the single most important factual claim from the input.
2. Score the source on:
   - authority (1-5)
   - evidence_strength (1-5)
   - transparency (1-5)
   - recency (1-5)
   - bias_risk (1-5)
3. Compute credibility_score_total as the sum of the five source scores.
4. Score the claim on:
   - direct_support_score (0-2)
   - cross_verification_score (0-2)
   - specificity_score (0-2)
   - consistency_score (0-2)
5. Compute claim_verification_total as the sum of the four claim scores.
6. Assign verification_status as one of:
   - verified
   - partially_verified
   - unverified
7. Assign report_worthiness_score from 1-5.
8. Assign decision as one of:
   - pass
   - flag
   - reject

Decision rules:
- pass: credibility_score_total >= 18 AND claim_verification_total >= 6 AND report_worthiness_score >= 3
- flag: mixed evidence, missing details, or important but not fully confirmed
- reject: low credibility, weak support, or not worth reporting

Important rules:
- Never invent facts not present in the input.
- If cross-verification is not possible from the provided text alone, be conservative.
- Return ONLY valid JSON matching the schema below.

Schema fields:
{{
  "source_name": "string",
  "source_type": "string",
  "claim": "string",
  "authority_score": 1,
  "evidence_strength_score": 1,
  "transparency_score": 1,
  "recency_score": 1,
  "bias_risk_score": 1,
  "credibility_score_total": 5,
  "verification_status": "verified",
  "direct_support_score": 0,
  "cross_verification_score": 0,
  "specificity_score": 0,
  "consistency_score": 0,
  "claim_verification_total": 0,
  "report_worthiness_score": 1,
  "decision": "flag",
  "reasoning": "string",
  "missing_information": ["string"],
  "supporting_evidence": ["string"]
}}

Input metadata:
source_name: {source_name}
source_type: {source_type}

Input text:
{raw_text}
""".strip()


def validate_with_ollama(source_name: str, source_type: str, raw_text: str) -> ValidationResult:
    prompt = build_validation_prompt(source_name, source_type, raw_text)

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0}
    )

    content = response["message"]["content"].strip()

    # Remove accidental markdown fences if the model adds them
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()

    data = json.loads(content)
    return ValidationResult(**data)