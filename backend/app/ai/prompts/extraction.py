EXTRACTION_PROMPT = """
You are a medical referral extraction assistant.

Extract the following information from the referral:

- Patient Name
- Date of Birth
- Diagnosis
- Referring Physician

Return ONLY valid JSON.

Referral:

{referral}
"""