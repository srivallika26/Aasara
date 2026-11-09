"""Scheme data, eligibility rules and the tax calculator for Aasara.

Informational only: the relevant government department makes the final decision.
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "schemes.json"), encoding="utf-8") as f:
    SCHEMES = {s["id"]: s for s in json.load(f)}

# Order in which follow-up questions are asked
FIELDS = ["age", "gender", "owns_land", "income_tax_payer", "white_ration_card", "small_business", "has_lpg", "daughter_under_10"]
BOOL_FIELDS = ["owns_land", "income_tax_payer", "white_ration_card", "small_business", "has_lpg", "daughter_under_10"]

STATUS_LABEL = {
    "likely": "✅ May qualify",
    "check": "❓ Needs checking",
    "not_eligible": "❌ Does not seem eligible",
}


def clean_profile(raw):
    """Keep only valid values from what the language model extracted."""
    out = {}
    if not isinstance(raw, dict):
        return out
    try:
        age = int(raw.get("age"))
        if 0 < age < 120:
            out["age"] = age
    except (TypeError, ValueError):
        pass
    if raw.get("gender") in ("male", "female"):
        out["gender"] = raw["gender"]
    for k in BOOL_FIELDS:
        if isinstance(raw.get(k), bool):
            out[k] = raw[k]
    return out


def missing_fields(p):
    """Questions still worth asking, in order."""
    out = []
    for f in FIELDS:
        if p.get(f) is None:
            if f == "has_lpg" and p.get("gender") != "female":
                continue  # only relevant for women (PM Ujjwala)
            out.append(f)
    return out


def check(sid, p):
    """Return (status, reason) for one scheme. Status: likely / check / not_eligible."""
    age, gender = p.get("age"), p.get("gender")
    land, taxpayer = p.get("owns_land"), p.get("income_tax_payer")
    lpg, daughter = p.get("has_lpg"), p.get("daughter_under_10")

    if sid == "pm_kisan":
        if land is False:
            return "not_eligible", "PM-KISAN is for landholding farmer families, and you said no agricultural land is in your name."
        if land is True and taxpayer is True:
            return "check", "You have land, but income-tax payers can fall under the higher-income exclusions. Check the official exclusion list."
        if land is True:
            return "likely", "You have agricultural land in your name. State officials make the final decision after checking the exclusion categories."
        return "check", "Your land details are needed."

    if sid == "pmjay":
        if age is not None and age >= 70:
            return "likely", "Citizens aged 70 and above are covered irrespective of income."
        return "check", "Below 70, eligibility depends on being listed in the official SECC 2011-based database. Use 'Am I Eligible' on pmjay.gov.in or call 14555."

    if sid == "pmuy":
        if lpg is True:
            return "not_eligible", "Your household already has an LPG connection."
        if gender == "male":
            return "check", "The connection is issued in an adult woman's name. A woman of your household may apply if the household has no LPG connection and qualifies."
        if gender == "female":
            if age is not None and age < 18:
                return "not_eligible", "The applicant must be an adult woman (18 or above)."
            if lpg is False:
                return "likely", "You meet the age, gender and no-LPG conditions. The household must also be poor or in an eligible category, so confirm with an LPG distributor."
        return "check", "More details are needed."

    if sid == "ssy":
        if daughter is True:
            return "likely", "A parent or guardian can open the account for a girl child below 10 years."
        if daughter is False:
            return "not_eligible", "The account is only for a girl child below 10 years."
        return "check", "Needs to know if you have a daughter below 10."

    if sid == "apy":
        if age is not None and (age < 18 or age > 40):
            return "not_eligible", "APY is open only to people aged 18 to 40."
        if taxpayer is True:
            return "not_eligible", "Since 1 October 2022, income-tax payers cannot join APY."
        if age is not None and taxpayer is False:
            return "likely", "You are in the 18-40 age range and not an income-tax payer. You also need a savings bank or post office account."
        return "check", "Needs your age and income-tax status."

    white, biz = p.get("white_ration_card"), p.get("small_business")
    if sid == "mudra":
        if biz is True:
            return "likely", "You run or plan a small business. The bank or lender decides approval, interest and fees."
        if biz is False:
            return "not_eligible", "MUDRA loans are for people running or starting a small non-farm business."
        return "check", "Needs to know if you run or plan a small business."

    if sid == "aarogyasri":
        if white is True:
            return "likely", "White ration card families in Telangana are covered, up to Rs 10 lakh per family per year for covered treatments."
        return "check", "It is mainly for Telangana white ration card families. Rules may be extended, so check with the Aarogyasri Trust."

    if sid == "gruha_jyothi":
        if white is False:
            return "not_eligible", "A white ration card linked with Aadhaar is required."
        if white is True:
            return "likely", "If you live in Telangana, have a domestic connection linked to the card and use up to 200 units a month. Above 200 units the full bill applies."
        return "check", "Needs your ration card details."

    if sid == "aasara_pension":
        if age is not None and age >= 57:
            return "likely", "Old-age pension starts at age 57 for eligible poor Telangana residents. Confirm the current amount at your local office."
        if age is not None:
            return "check", "Below 57 you may still qualify under another category (widow, single woman, disability, weaver and so on)."
        return "check", "Needs your age."

    return "check", "No rule available."


def discover(p):
    results = []
    for sid, s in SCHEMES.items():
        status, reason = check(sid, p)
        results.append({"id": sid, "name": s["name"], "name_te": s["name_te"],
                        "status": status, "reason": reason})
    order = {"likely": 0, "check": 1, "not_eligible": 2}
    results.sort(key=lambda r: order[r["status"]])
    return results


def discover_facts(results):
    groups = {"likely": [], "check": [], "not_eligible": []}
    for r in results:
        groups[r["status"]].append(f"{r['name_te']} ({r['name']}): {r['reason']}")
    lines = []
    if groups["likely"]:
        lines.append("May qualify: " + " | ".join(groups["likely"]))
    if groups["check"]:
        lines.append("Needs checking: " + " | ".join(groups["check"]))
    if groups["not_eligible"]:
        lines.append("Does not seem eligible: " + " | ".join(groups["not_eligible"]))
    lines.append("The final decision is made by the government department.")
    return "\n".join(lines)


def scheme_facts(sid):
    s = SCHEMES[sid]
    return f"{s['name_te']} ({s['name']}). Benefit: {s['benefit']} Eligibility: " + " ".join(s["eligibility"])


# ---------- Income tax (simplified demo) ----------
# REPLACE with your hackathon tax calculator if you prefer.
# Simplified new-regime slabs (FY 2025-26), salaried, standard deduction 75,000,
# no tax up to 12 lakh taxable income, 4% cess. No marginal relief.
def new_regime_tax(income):
    taxable = max(income - 75000, 0)
    slabs = [
        (400000, 0.00), (800000, 0.05), (1200000, 0.10), (1600000, 0.15),
        (2000000, 0.20), (2400000, 0.25), (float("inf"), 0.30),
    ]
    tax, prev = 0.0, 0
    for limit, rate in slabs:
        if taxable > prev:
            tax += (min(taxable, limit) - prev) * rate
        prev = limit
    if taxable <= 1200000:
        tax = 0
    return round(tax * 1.04)