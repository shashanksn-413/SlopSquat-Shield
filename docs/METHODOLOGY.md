# Research Methodology

## Objective
Quantify the risk of LLM-powered supply chain attacks by measuring hallucination rates in AI-generated code recommendations across multiple coding domains.

## Approach

### Phase 1: Prompt Design
- Designed 60 prompts across 10 security-relevant categories:
  - Web Development (Flask, Express, middleware)
  - API Integration (GitHub, AWS S3, OAuth2)
  - Authentication (JWT, hashing, 2FA)
  - Database (PostgreSQL, ORM, migrations)
  - Data Science (NumPy, Pandas, ML)
  - DevOps (Docker, CI/CD, Lambda)
  - Security (Input validation, XSS, CSRF)
  - File Handling (CSV, XML, JSON)
  - Testing (Unit tests, mocking, fixtures)
  - Networking (HTTP, URL parsing, SSL)

### Phase 2: LLM Querying
- Model: OpenAI GPT-4o-mini
- Total prompts sent: 20 (2 per category for cost efficiency)
- Response collection: Package names extracted from code suggestions using regex patterns
- Rate limiting: 1 request/second to manage API budget

### Phase 3: Registry Validation
- Checked all extracted package names against:
  - PyPI JSON API (https://pypi.org/pypi/{package}/json)
  - npm Registry API (https://registry.npmjs.org/{package})
- Classification:
  - Real packages: exist on one or both registries
  - Hallucinated packages: exist nowhere, available for registration

### Phase 4: Analysis
- Calculated hallucination rates by category
- Identified exploitable (registrable) packages
- Generated attack surface metrics for CLI scanner database

## Data Sources
- 55 total package recommendations across 20 LLM queries
- 43 unique package names extracted
- 100% coverage of PyPI and npm registries validated

## Limitations
- Single model tested (GPT-4o-mini)
- Limited prompt set (20 prompts, 2 per category) for budget constraints
- No temporal tracking of package registration availability