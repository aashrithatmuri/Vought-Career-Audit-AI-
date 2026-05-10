def predict_role_fit(
    match_percentage
):

    if match_percentage >= 75:
        return {
            "fit": "High",
            "verdict": "Strong alignment with target role."
        }

    elif match_percentage >= 45:
        return {
            "fit": "Medium",
            "verdict": "Moderate alignment. Upskilling recommended."
        }

    else:
        return {
            "fit": "Low",
            "verdict": "Low alignment. Significant upskilling required."
        }