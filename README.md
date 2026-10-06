# User Authentication and Authorization Service

## Project Description

A centralized backend service to handle user registration, login, and role-based access control for multiple applications.

This repository contains the source code and documentation for the User Authentication and Authorization Service project, developed as part of the UE23CS341A course at PES University.


## Getting Started

### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/pestechnology/PESU_EC_CSE_F_P70_User_Authentication_and_Authorization_Service_SEe-project.git
   cd PESU_EC_CSE_F_P70_User_Authentication_and_Authorization_Service_SEe-project
   ```

2. Install dependencies
   ```bash
   # Add your installation commands here
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   # Add your run commands here
   python manage.py runserver
   ```

## 📁 Project Structure

```
PESU_EC_CSE_F_P70_User_Authentication_and_Authorization_Service_SEe-project/
├── src/                 # Source code
├── docs/               # Documentation
├── tests/              # Test files
├── .github/            # GitHub workflows and templates
├── README.md          # This file
└── ...
```

## Development Guidelines

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

### Commit Messages
Follow conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test-related changes

### Code Review Process
1. Create feature branch from `develop`
2. Make changes and commit
3. Create Pull Request to `develop`
4. Request review from team members
5. Merge after approval

## Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

## CI/CD Pipeline Documentation

### Overview

This project uses a continuous integration (CI) pipeline implemented using GitHub Actions.  
The pipeline is automatically triggered on:

- Pushes to the `main` and `feature/*` branches  
- Pull requests targeting `main`  

The CI workflow verifies code quality, enforces security standards, executes automated tests, and generates a deployment-ready artifact.

---

## Pipeline Stages

### 1. Environment Setup

This stage prepares the execution environment required for backend testing and validation. It performs the following tasks:

- Checks out the repository  
- Sets up Python 3.12  
- Installs dependencies using `requirements.txt`  
- Installs development tools (pytest, pylint, bandit, safety)  
- Creates a `.env` file used during CI  
- Initializes a MySQL 8 database service  

---

### 2. Test Execution and Coverage

All automated tests are executed using `pytest`.  
This stage:

- Runs the entire test suite  
- Generates a coverage report (`coverage.xml`)  
- Produces an HTML coverage report (`htmlcov/`)  
- Enforces a minimum coverage requirement of **60%**  
- Fails the pipeline if requirements are not met  

---

### 3. Static Code Analysis (Linting)

The project uses `pylint` to enforce coding standards.

This stage:

- Runs `pylint` on the backend source directory (`src/`)  
- Generates a lint report (`pylint-report.txt`)  
- Calculates an overall lint score  
- Requires a minimum lint score of **7.5**  
- Fails the pipeline if the score is below threshold  

---

### 4. Security Scanning

Two security tools are included:

**Bandit**  
- Scans Python code for common security vulnerabilities  
- Produces an HTML report (`bandit-report.html`)  

**Safety**  
- Analyzes Python dependencies for known security issues  
- Outputs a JSON report (`safety-report.json`)  

Both security reports are uploaded as CI artifacts.

---

### 5. Deployment Artifact Packaging

A deployment-ready ZIP file is automatically generated at the end of the workflow.  
The artifact contains:

- Complete project source code (`src/`)  
- Test files (`tests/`)  
- HTML coverage report (`htmlcov/`)  
- Lint report (`pylint-report.txt`)  
- Security scan reports (`bandit-report.html`, `safety-report.json`)  
- `README.md`  
- `requirements.txt`  
- CI-generated environment configuration  

The packaged file is uploaded as `uaas-deployment-artifact` and is available for download in the GitHub Actions run summary.

---

## Running CI Checks Locally

Developers may replicate CI checks using the following commands.

### Run Tests with Coverage
```bash
pytest --cov


## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```


