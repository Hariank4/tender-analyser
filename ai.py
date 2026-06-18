import anthropic
import os
import json
import fitz
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MERAPATH_PROFILE = {
    "company": "MeraPath Education Limited",
    "established": 2004,
    "certifications": ["ISO 9001", "ISO 14001", "ISO 45001", "ISO 21001", "ISO 22000", "MSME registered", "DPIIT", "EPF", "ESIC", "GST", "FSSAI"],
    "presence": "14+ states, 100+ districts, 500+ blocks, 3000+ panchayats",
    "total_beneficiaries": "4.2 lakh+",
    "nsdc_empanelled": True,
    "flagship_projects": [
        "PMGDISHA — 1,59,547 beneficiaries",
        "Jal Jeevan Mission — 1,34,627 trainees",
        "PMAY-G Rural Mason Training — 26,720 trainees",
        "NDLM — 41,873 beneficiaries",
        "Lakhpati Didi — 65,186 beneficiaries across 75 districts",
        "Saubhagya — 1,500 technicians trained"
    ],
    "specialisations": [
        "Skill development and vocational training",
        "Digital literacy programs",
        "Capacity building for government schemes",
        "Rural and grassroots delivery",
        "Call center and BPO training",
        "Toolkit-based livelihood solutions",
        "AI and digital training"
    ]
}

MATCH_CRITERIA = [
    {"key": "pmgdisha", "label": "PMGDISHA Experience", "detail": "1,59,547 beneficiaries"},
    {"key": "jjm", "label": "Jal Jeevan Mission", "detail": "1,34,627 trainees"},
    {"key": "lakhpati", "label": "Lakhpati Didi Experience", "detail": "65,186 beneficiaries"},
    {"key": "ndlm", "label": "NDLM Experience", "detail": "41,873 beneficiaries"},
    {"key": "pmay", "label": "PMAY-G Experience", "detail": "26,720 trainees"},
    {"key": "iso", "label": "ISO Certifications", "detail": "ISO 9001, 14001, 45001, 21001, 22000"},
    {"key": "msme", "label": "MSME Status", "detail": "MSME registered"},
    {"key": "geographic", "label": "Geographic Reach", "detail": "14+ states, 3000+ panchayats"},
    {"key": "scale", "label": "Beneficiary Scale", "detail": "4.2 lakh+ trained"},
]


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def analyse_tender(pdf_bytes: bytes) -> dict:
    raw_text = extract_text_from_pdf(pdf_bytes)

    prompt = f"""You are a senior bid analyst for MeraPath Education Limited.

MeraPath Profile:
- Established: {MERAPATH_PROFILE['established']} (20+ years)
- Certifications: {', '.join(MERAPATH_PROFILE['certifications'])}
- Pan-India presence: {MERAPATH_PROFILE['presence']}
- Total beneficiaries trained: {MERAPATH_PROFILE['total_beneficiaries']}
- NSDC empanelled: Yes
- Major projects: {', '.join(MERAPATH_PROFILE['flagship_projects'])}
- Specialisations: {', '.join(MERAPATH_PROFILE['specialisations'])}

Analyse this tender document and return ONLY valid JSON. No markdown, no explanation.

TENDER TEXT:
{raw_text[:8000]}

Return this exact JSON:
{{
  "bid_number": "tender/bid reference number or empty string",
  "ra_option": "Yes or No — whether reverse auction is mentioned",
  "start_date": "tender start date or empty string",
  "end_date": "submission deadline with time or empty string",
  "department_name": "full department name and address",
  "estimated_cost": "tender value in rupees",
  "epbg": "earnest money deposit / performance bank guarantee amount or empty string",
  "processing_fee": "processing fee amount or Not mentioned",
  "tender_fee": "tender document fee or Not mentioned",
  "appraisal_fee": "appraisal fee or Not mentioned",
  "project_name": "name of the project or scheme",
  "scope_of_work": ["point 1", "point 2", "point 3"],
  "eligibility_criteria": ["criterion 1", "criterion 2", "criterion 3"],
  "documents_required": ["document 1", "document 2", "document 3"],
  "remarks_risk": ["risk or remark 1", "risk or remark 2"],
  "jist": "One paragraph plain English summary of what this tender wants — who is issuing it, what they need, how big it is, and when it closes.",
  "state": "Indian state where work will be done",
  "region": "district or region if mentioned",
  "category": "one of: skill_development, digital_literacy, agriculture, healthcare, infrastructure, corporate_training, ai_training, other",
  "portal": "GeM or CPPP or State Portal or NSDC or other",
  "match_engine": {{
    "pmgdisha": true or false,
    "jjm": true or false,
    "lakhpati": true or false,
    "ndlm": true or false,
    "pmay": true or false,
    "iso": true,
    "msme": true,
    "geographic": true,
    "scale": true
  }},
  "bid_strength_score": number between 0 and 100,
  "win_probability": number between 0 and 100,
  "score_reasoning": "2-3 sentences explaining the score",
  "proposal_sections": ["Section 1: title", "Section 2: title", "Section 3: title", "Section 4: title", "Section 5: title"]
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


