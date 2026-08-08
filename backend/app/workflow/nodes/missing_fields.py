from app.ai.missing_fields import detect_missing_fields


def missing_fields_node(state):

    print("========== EXTRACTED BEFORE MISSING FIELDS ==========")
    print(state["extracted"])

    """
    Determine which clinical/patient fields are still missing
    after considering both the original referral and everything
    collected so far.
    """

    missing_fields = detect_missing_fields(
        referral=state["referral"],
        extracted=state["extracted"],
    )

    print("======= State RETURNING FROM MISSING FIELDS NODE =====")
    print(missing_fields)

    return {
        "missing_fields": missing_fields
    }