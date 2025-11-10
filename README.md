# Cheese App - CI/CD Tutorial

In this tutorial we will setup Continuous Integration and Continuous Deployment (CI/CD) for a containerized Python API application. We'll learn how to automate code quality checks, testing, and deployment pipelines.

## Prerequisites
* Have Docker installed
* Python 3.9+ installed locally
* Git installed
* GitHub account

## Tutorial: Adding CI/CD to the Cheese App

This tutorial demonstrates how to add automation to a Python FastAPI application using:
* **Pre-commit hooks** for local code quality checks (linting/formatting)
* **Pytest** for automated testing (unit & integration tests)
* **GitHub Actions** for remote CI/CD pipelines
* **Docker** for containerized development and deployment

### Clone the repository
- Clone or download from your repository

### Project Structure
```
cheese-app-cicd-tutorial/
├── .pre-commit-config.yaml          # Pre-commit hooks configuration
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Main CI/CD pipeline
│       └── docker-build.yml         # Docker build test
├── Dockerfile                       # Container definition
├── docker-shell.sh                  # Start interactive container
├── docker-entrypoint.sh             # Container entrypoint
├── pyproject.toml                   # Python dependencies
├── pytest.ini                       # Pytest configuration
├── src/
│   └── api-service/
│       └── api/
│           ├── __init__.py
│           ├── service.py           # FastAPI application
│           └── utils.py             # Utility functions (power)
└── tests/
    ├── unit/
    │   └── test_utils.py            # Unit tests for utils
    ├── integration/
    │   └── test_api.py              # Integration tests (TestClient)
    └── system/
        └── test_api.py              # System tests (real HTTP)
```

---

## Part 1: Local Development with Docker

### Build & Run the Container

1. **Build and start the Docker container**
```bash
sh docker-shell.sh
```

This will start an interactive bash shell inside the container.

2. **Start the Development Server**

Within the container, run:
```bash
uvicorn api.service:app --host 0.0.0.0 --port 9000 --reload
```

3. **Test the API**

Open your browser to:
- `http://localhost:9000` - Welcome message
- `http://localhost:9000/health` - Health check endpoint
- `http://localhost:9000/euclidean_distance/?x=3&y=4` - Calculate Euclidean distance (returns 5.0)

### Run Tests

All tests can be run inside the Docker container to ensure consistency with the CI/CD environment.

#### Option 1: Run Tests with Docker Commands (Recommended)

```bash
# Build the image first
docker build -t cheese-app-api:local .

# Run unit tests
docker run --rm cheese-app-api:local pytest tests/unit/ -v

# Run integration tests (using FastAPI TestClient)
docker run --rm cheese-app-api:local pytest tests/integration/ -v

# Run all tests
docker run --rm cheese-app-api:local pytest tests/ -v

# Run tests with coverage
docker run --rm cheese-app-api:local pytest tests/unit/ --cov=api --cov-report=term
```

#### Option 2: Run Tests Inside Interactive Container

Open a new terminal and start a container:
```bash
sh docker-shell.sh
```

Within the container, run:
```bash
# Run only unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/unit/ --cov=api --cov-report=html
```

#### Option 3: System Tests Against Live Server

System tests make real HTTP requests to a running server, testing the complete system end-to-end:

```bash
# Terminal 1: Start the API server
docker run -d --name api-server -p 9000:9000 -e DEV=1 cheese-app-api:local

# Terminal 2: Run system tests against the live server
docker run --rm --network host cheese-app-api:local pytest tests/system/ -v

# Clean up when done
docker stop api-server && docker rm api-server
```

System tests will:
- Check if the API server is running at `http://localhost:9000`
- Make real HTTP requests to test the complete system
- Skip tests if server is not accessible

---

## Part 2: Pre-commit Hooks (Local CI)

### Check the Messy Code (Optional but Recommended)

Before setting up pre-commit hooks, let's see what issues exist in our code.

Within the Docker container:
```bash
# Check formatting issues with Black
black --check api/

# Check formatting issues with detailed diff view
black --check --diff api/
```

Or locally (if you have Python installed):
```bash
pip install black

# Check formatting issues
python3 -m black --check src/api-service/api/
python3 -m black --check --diff src/api-service/api/
```

You'll see formatting inconsistencies. This shows why automation is important!

### Install Pre-commit Framework

Outside the container:
```bash
pip install pre-commit
```

### Install the Hooks
```bash
# From the root directory
pre-commit install
```

This installs Git hooks that will run automatically before each commit.

### Test the Hooks
```bash
# Run on all files
pre-commit run --all-files
```

### What Gets Checked?
- **trailing-whitespace**: Remove trailing spaces
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML syntax
- **black**: Auto-format Python code (120 char lines)
- **flake8**: Check Python code quality

---

## Part 3: Testing with Pytest

### Test Structure - The Testing Pyramid

**Unit Tests** (`tests/unit/test_utils.py`):
- Test utility functions in isolation
- Test the `power()` function with various inputs
- Fast execution, no dependencies
- Example: `power(2, 3)` should return `8`
- **Run inside container**

**Integration Tests** (`tests/integration/test_api.py`):
- Test API endpoints using FastAPI TestClient
- Verify routing, validation, and response serialization
- Test integration between FastAPI and business logic
- No real HTTP server needed (uses TestClient)
- Example: `GET /euclidean_distance/?x=3&y=4` should return `5.0`
- **Run inside container in CI/CD**

**System Tests** (`tests/system/test_system_api.py`):
- Test the complete running system as a black box
- Make real HTTP requests to live server at `localhost:9000`
- Test the full HTTP stack end-to-end
- Most realistic, but slowest tests
- Example: `curl http://localhost:9000/euclidean_distance/?x=3&y=4`
- **Run in CI/CD and locally using Docker with --network host**

---

## Part 4: GitHub Actions (Remote CI/CD)

All CI/CD tests run inside Docker containers using Python 3.11 (same as production), ensuring complete consistency between local development, CI, and production environments.

### Workflow 1: Main CI Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request to `main`:

1. **Build Job**: Builds Docker image once and shares it across all jobs
2. **Lint Job**: Run Black formatter check and Flake8 linter inside container
3. **Unit Tests Job**: Run pytest unit tests with coverage inside container
4. **Integration Tests Job**: Test API endpoints inside container using FastAPI TestClient
5. **System Tests Job**: Start server container and run end-to-end tests with real HTTP requests
6. **Test Summary Job**: Aggregates results from all test jobs

**Key Benefits:**
- ✅ Same Python version (3.11) in CI as production
- ✅ Same dependencies from `pyproject.toml`
- ✅ Build once, test everywhere
- ✅ No dependency conflicts between CI and Docker
- ✅ Complete testing pyramid: Unit → Integration → System

### Workflow 2: Docker Build Test (`.github/workflows/docker-build.yml`)

Verifies that Docker builds succeed and the server can start:
- Builds the api-service container
- Starts container as a server and verifies it responds
- Ensures the Docker image works correctly in server mode

### Push to GitHub
```bash
git add .
git commit -m "Add CI/CD pipeline"
git push
```

### Watch GitHub Actions

1. Go to your GitHub repository
2. Click the "Actions" tab
3. See workflows running automatically
4. Green checkmark = success ✅
5. Red X = failure ❌

---

## Part 5: Branch Protection (Optional)

### Configure Branch Rules

1. Go to **Settings** → **Branches** → **Add rule**
2. Branch name pattern: `main`
3. Enable:
   - ☑ Require a pull request before merging
   - ☑ Require status checks to pass before merging
   - Select: `lint-and-format`, `unit-tests`, `integration-tests`, `system-tests`
4. Save changes

### Test the Protection

```bash
# Create a new branch
git checkout -b feature/test-protection

# Make a change that breaks tests
echo "def broken(): assert False" >> tests/unit/test_utils.py

# Commit and push
git add .
git commit -m "Intentionally break tests"
git push origin feature/test-protection

# Create a pull request on GitHub
# You'll see: ❌ Tests must pass before merging!
```

---

## Student Exercise: Add a New Endpoint with Full CI/CD

1. **Add a new endpoint** to `src/api-service/api/service.py`:

```python
@app.get("/add/")
async def add_numbers(x: float = 0, y: float = 0):
    """Add two numbers"""
    return {"result": x + y}
```

2. **Write integration test** in `tests/integration/test_api.py`:

```python
def test_add_endpoint():
    response = client.get("/add/?x=10&y=20")
    assert response.status_code == 200
    assert response.json()["result"] == 30
```

3. **Test in Docker**:

Start the container and run tests:
```bash
sh docker-shell.sh
pytest tests/ -v
```

Auto-format code:
```bash
black src/api-service/api/
```

4. **Push to GitHub**:

```bash
git add .
git commit -m "Add addition endpoint with tests"
git push
```

5. **Watch CI/CD pipeline run automatically**

---

## Quick Command Reference

### Docker-First Workflow (Recommended - Matches CI/CD)
```bash
# Build Docker image
docker build -t cheese-app-api:local .

# Run tests (same commands used in CI)
docker run --rm cheese-app-api:local pytest tests/unit/ -v
docker run --rm cheese-app-api:local pytest tests/integration/ -v
docker run --rm cheese-app-api:local pytest tests/ -v

# Run system tests (requires running server)
# First, start server in one terminal:
docker run -d --name api-server -p 9000:9000 -e DEV=1 cheese-app-api:local
# Then run system tests:
docker run --rm --network host cheese-app-api:local pytest tests/system/ -v
# Stop server when done:
docker stop api-server && docker rm api-server

# Run linting (same commands used in CI)
docker run --rm cheese-app-api:local black --check --line-length 120 api/
docker run --rm cheese-app-api:local flake8 --max-line-length=120 api/

# Start development server
sh docker-shell.sh
# Inside container: uvicorn api.service:app --host 0.0.0.0 --port 9000 --reload
```

### Interactive Container Workflow
```bash
# Start interactive Docker container
sh docker-shell.sh

# Inside the container:
uvicorn api.service:app --host 0.0.0.0 --port 9000 --reload  # Start server
pytest tests/unit/ -v                                        # Run unit tests
pytest tests/integration/ -v                                 # Run integration tests
black --check api/                                           # Check formatting
black api/                                                   # Auto-format
```

### Run Locally Without Docker (Requires Python Installation)
```bash
# Code Quality Checks
python3 -m black --check src/api-service/api/              # Check formatting
python3 -m black src/api-service/api/                      # Auto-format code
python3 -m flake8 src/api-service/api/                     # Run linter

# Pre-commit Hooks
pip install pre-commit                                      # Install framework
pre-commit install                                          # Setup hooks
pre-commit run --all-files                                 # Run all checks

# Testing (requires PYTHONPATH setup)
PYTHONPATH=src/api-service pytest tests/unit/ -v          # Unit tests
PYTHONPATH=src/api-service pytest tests/integration/ -v   # Integration tests
```

---

## Troubleshooting

### Issue: Pre-commit hooks not running
```bash
pre-commit install
```

### Issue: Black formatting conflicts
```bash
# If Black and your editor disagree, trust Black:
python3 -m black src/api-service/api/

# To see what Black will change before applying:
python3 -m black --check --diff src/api-service/api/
```

### Issue: Tests fail locally
```bash
# Make sure you're in the project root
pytest tests/ -v

# Run with more verbose output:
pytest tests/ -vv --tb=long

# Run specific test file:
pytest tests/integration/test_api.py -v
```

### Issue: Docker build fails
```bash
docker build -t cheese-app-test . --no-cache
```

### Issue: Can't access API at localhost:9000
```bash
# Check if container is running
docker ps

# Check logs
docker logs <container-name>
```

### Issue: GitHub Actions failing
- Check the "Actions" tab for detailed logs
- Common issue: Missing dependencies in pyproject.toml
- Common issue: Wrong file paths in workflow
- Common issue: Black/Flake8 version mismatch between local and CI

---

## Key Takeaways

✅ **Pre-commit hooks** catch issues before they're committed
✅ **Automated testing** ensures code works as expected
✅ **GitHub Actions** runs tests on every push automatically
✅ **Docker** ensures consistent environment across dev/CI/prod
✅ **Branch protection** prevents broken code from reaching main

---

## Docker Cleanup

### Make sure we do not have any running containers and clear up unused images
* Run `docker container ls`
* Stop any container that is running
* Run `docker system prune`
* Run `docker image ls`
