import spacy


# Load spaCy English model
nlp = spacy.load("en_core_web_sm")


# Skill vocabulary
COMMON_SKILLS = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "excel",
    "power bi",
    "tableau",
    "aws",
    "azure",
    "docker",
    "kubernetes",
    "fastapi",
    "flask",
    "django",
    "javascript",
    "react",
    "node.js",
    "mongodb",
    "postgresql",
    "git",
    "github"
]


def extract_skills(text):
    """
    Extract skills from text using spaCy
    """

    doc = nlp(text.lower())

    extracted_skills = []

    # Check full text for multi-word skills
    for skill in COMMON_SKILLS:
        if skill in text.lower():
            extracted_skills.append(skill)

    # Check token-level skills
    for token in doc:
        if token.text in COMMON_SKILLS:
            extracted_skills.append(token.text)

    # Remove duplicates
    extracted_skills = list(set(extracted_skills))

    return extracted_skills