"""
A curated list of common tech-industry skills, used for keyword-based
skill extraction. This is intentionally broad but not exhaustive — for a
final-year project this kind of curated-list approach is standard and
explainable (much easier to defend in a viva than a black-box NER model).

Feel free to extend SKILLS_DB with skills relevant to the job domains
you plan to demo (e.g. add "figma", "photoshop" for design roles).
"""

SKILLS_DB = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "dart",

    # Web frontend
    "html", "css", "sass", "react", "reactjs", "angular", "vue", "vuejs",
    "next.js", "nextjs", "svelte", "tailwind", "bootstrap", "jquery",
    "redux", "webpack",

    # Backend / frameworks
    "node.js", "nodejs", "express", "django", "flask", "fastapi",
    "spring", "spring boot", "ruby on rails", "laravel", "asp.net",
    "graphql", "rest api", "grpc", "microservices",

    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis",
    "sqlite", "oracle", "cassandra", "dynamodb", "elasticsearch",
    "firebase", "mariadb",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "terraform", "ansible", "jenkins", "ci/cd", "git", "github",
    "gitlab", "linux", "bash", "nginx", "cloudformation",

    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "data analysis", "data science", "data engineering",
    "spark", "hadoop", "tableau", "power bi", "airflow", "opencv",
    "hugging face", "llm", "generative ai",

    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",

    # Testing / QA
    "unit testing", "selenium", "jest", "pytest", "junit", "cypress",
    "test automation", "tdd",

    # Soft / methodology
    "agile", "scrum", "kanban", "project management", "jira",
    "communication", "leadership", "teamwork", "problem solving",

    # Design
    "figma", "photoshop", "adobe xd", "ui/ux", "sketch",

    # Other common tools
    "excel", "powerpoint", "word", "linux administration", "api development",
]

# Normalize once for fast lookups
SKILLS_DB_LOWER = sorted(set(s.lower() for s in SKILLS_DB), key=len, reverse=True)
