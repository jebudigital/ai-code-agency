# Functional Requirements

## Goal

To achieve an autonomous AI-Coding Agency which can taken user-requirements and delegate to multiple AI-agents to complete the work with production-quality.
This app should be able to intercept a problem-statement (interms of well-defined functional-requirements.md - like this and develop a package/project as a zip with code,test, proof-of-work/demo, documentation)

Some of the agents envisioned are
- Planner Agent
    - Main role to analyze the requirements, breakdown to individual stories, assign to the right AI-agent using MCP
- Coder Agent
    - Can be a full-stack/polyglot-developer agent or separate as frontend, backend developer agents
    - Implements the request with quality code, good unit-test/integration-test coverage, completes task with proof of the work
- Reviewer Agent
    - Used to review PRs - should be more qualitative, analyze the PR based on functiona-requirements, production-quality, how it fits overall architecture
    - runs linters (ruff), bandit (if installed) and pytest via subprocess and returns structured reports.

- Documentation Agent
    - Updates documentation based on updates - should include developer-guide,architecture-documents (with sufficient mermaid-diagrams),constant updates based on evolving requirements, bug-fixes, remove static/stale documentation, and also runbook - to handle prod-incidents. 
    - The documentation should be packagable as html - say mkdocs or hugo 