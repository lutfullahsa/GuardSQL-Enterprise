# GuardSQL Enterprise

Enterprise-grade Multi-Tenant Text-to-SQL security and auditing platform.

## Architecture
```mermaid
graph TD
    User[User] --> FE[Streamlit Frontend]
    FE --> API[FastAPI Backend]
    API --> SQLVal[SQL Validator]
    API --> T2S[Text-to-SQL Engine]
    SQLVal --> DB[(PostgreSQL)]
```

## Quick Start
```bash
docker-compose up --build
```

## Demo
[Watch the demo video]
