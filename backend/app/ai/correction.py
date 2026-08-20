import re

# Longer/more specific aliases first so "date of birth" wins over a bare "birth"
# type of match when both would otherwise apply.
FIELD_ALIASES: dict[str, list[str]] = {
    "Date of Birth": ["date of birth", "birth date", "birthdate", "dob", "birthday"],
    "Referring Physician": [
        "referring physician",
        "referring doctor",
        "referrer",
        "physician",
    ],
    "Insurance Provider": ["insurance provider", "insurance", "insurer"],
    "Phone Number": [
        "phone number",
        "contact number",
        "mobile number",
        "phone",
        "mobile",
    ],
    "Diagnosis": ["diagnosis", "condition"],
    "Patient Name": ["patient name", "full name", "name"],
}

_VALUE_PATTERNS = [
    re.compile(r"\bto\s+(.+)$", re.IGNORECASE),
    re.compile(r"\bis\s+(?:actually\s+)?(.+)$", re.IGNORECASE),
    re.compile(r"\bshould\s+be\s+(.+)$", re.IGNORECASE),
    re.compile(r":\s*(.+)$"),
]


def parse_correction(text: str) -> tuple[str | None, str | None]:
    """Best-effort keyword match of free text to a known field + new value.

    Handles phrasing like "please correct my DOB to 1990-01-01",
    "change my phone number to 555-1234", or "my insurance is actually Aetna".
    Returns (field, value); either may be None if it couldn't be determined.
    """
    lowered = text.lower()

    field = None
    best_alias_len = -1
    for candidate, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in lowered and len(alias) > best_alias_len:
                field = candidate
                best_alias_len = len(alias)

    if field is None:
        return None, None

    value = None
    for pattern in _VALUE_PATTERNS:
        match = pattern.search(text)
        if match:
            value = match.group(1).strip().strip(".!? ")
            break

    return field, (value or None)
