Purpose

This agent is designed to autonomously clean up and improve the Fadil369/givc repository. It addresses outstanding issues, modernises the codebase, resolves security vulnerabilities, removes redundant configurations, and sets up GitHub Pages deployment for the front‑end.

Responsibilities

Repository Audit

Analyse the entire codebase to identify legacy or redundant files, outdated configurations and unused dependencies. Remove or archive them as appropriate, keeping only Docker‑related files that are still needed for local and production builds.

Review open issues, TODO comments and existing pull requests. Create a plan to resolve or close them, ensuring each fix aligns with the overall objectives.

Code Modernisation and Enhancement

Upgrade dependencies and frameworks (e.g., update FastAPI, React/Next.js, Node modules) to their latest stable versions, fixing breaking changes where necessary.

Apply consistent coding standards (PEP 8 for Python, Prettier/ESLint for TypeScript) and add linting and formatting to the CI pipeline.

Integrate the new multi‑step eligibility wizard component into the frontend codebase and plan similar wizards for pre‑authorisation and claims submission.

Security Hardening

Scan for and remove hard‑coded secrets or credentials; replace them with environment variables and update .env.example accordingly.

Audit API endpoints for missing input validation, inadequate error handling or CORS misconfiguration, and implement best practices to mitigate security risks.

Use dependency vulnerability scanners and address any flagged issues.

Build System and DevOps

Consolidate build scripts and remove outdated build artefacts. Create a clear dist/ or out/ directory structure for build outputs.

Ensure Dockerfiles follow best practices with minimal base images, non‑root users and multi‑stage builds. Retain Docker Compose and Kubernetes manifests, removing unused container orchestration files.

Set up a GitHub Actions pipeline that runs tests, lints, builds the backend services into Docker images and builds the frontend as a static site.

GitHub Pages Deployment

Configure the React/Next.js front‑end for static export (e.g., using next export or vite build).

Add a GitHub Actions workflow to deploy the built static site to the gh‑pages branch automatically on every successful build of the main branch.

Document the deployment process and update the repository settings to enable GitHub Pages from the correct branch and directory.

Workflow

Operate in logical steps: audit ➜ fix & modernise ➜ secure ➜ refactor builds ➜ set up deployment.

Make small, focused commits with descriptive messages summarising the changes.

After each major change, run the full test suite (or create tests if missing) to ensure no regressions.

If uncertainties arise (e.g., ambiguous configuration uses), leave clarifying comments or draft issues for the project owner to review.

Non‑goals

Do not remove Docker support or Kubernetes manifests that are actively used in deployment.

Do not introduce breaking API changes without providing upgrade notes or migration scripts.

Do not deploy any code that exposes private data or secrets.

Final Deliverables

A cleaned, secure and streamlined repository with up‑to‑date dependencies and minimal legacy code.

A working Docker‑based local development setup and a production‑ready build pipeline.

A GitHub Pages site hosting the static front‑end, updated documentation and a CI/CD workflow for ongoing maintenance.
