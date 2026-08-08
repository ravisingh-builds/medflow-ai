MISSING_FIELDS_PROMPT = """
You are a healthcare intake assistant.

The ONLY fields that exist in this workflow are:

- Patient Name
- Date of Birth
- Diagnosis
- Referring Physician
- Phone Number
- Insurance Provider

Do NOT invent any additional fields.

Referral:

{referral}

Known information:

{extracted}

Return ONLY the fields from the above list that are still missing.

JSON only.

{{
    "missing_fields":[]
}}
"""