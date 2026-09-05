# QAOA Combinatorial Optimizer

> **Domain:** Quantum Computing & Combinatorial Optimization
> **Standard:** QAOA Quantum Optimization Protocol

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

QAOA Combinatorial Optimizer is a Python-based framework implementing the Quantum Approximate Optimization Algorithm (QAOA) for solving combinatorial optimization problems, particularly Max-Cut on Ising Hamiltonians. It provides a multi-agent evaluation system with configurable worker agents that audit parameters against domain-specific thresholds and protocols.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Core QAOA Engine**: Parameter evaluation against operational thresholds for Ising cost Hamiltonians.
- **Multi-Agent Worker System**: Specialized sub-auditors (IsingHamiltonianAgent, MixerHamiltonianAgent, ApproximationRatioAgent) for boundary checking and anomaly detection.
- **Enrichment Suite**: Extensible feature engines for Multi-QAOA with alternating mixer Hamiltonians, parameter-free QAOA via Nelder-Mead warm start, and more.
- **Zero-PHI Outbound Guard**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers from outbound data.
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation and state transition.
- **FastAPI REST Server**: Exposes OpenAPI-compatible REST endpoints for programmatic access.
- **Prometheus Telemetry**: Operational metrics export for monitoring.

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/qaoa-combinatorial-optimizer.git
cd qaoa-combinatorial-optimizer

# Install dependencies
pip install fastapi uvicorn pydantic pytest

# Set the required audit secret key (minimum 32 characters)
export AUDIT_SECRET_KEY="your-secure-audit-key-here-min-32-chars"
```

---

## ⚙️ CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. System Configuration Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task / case identifier
- `--target`: Entity or target key
- `--primary`: Primary domain measurement (float)
- `--secondary`: Secondary kinetic or confidence score (float)
- `--critical`: Emergency escalation flag
- `--status`: Status code or phenotype descriptor

### Input Data Schema (CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Task identifier | Required |
| `target_identifier` | Target entity key | Required |
| `primary_metric` | Primary measurement (float) | Required |
| `secondary_metric` | Secondary score (float) | Required |
| `is_critical_flag` | Critical escalation flag | Optional |
| `status_descriptor` | Status code descriptor | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs. Requires `AUDIT_SECRET_KEY` environment variable (minimum 32 characters).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances, Claude, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
# Set test key and run tests
export AUDIT_SECRET_KEY="test-secret-key-for-pytest-suite-32chars!"
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t qaoa-combinatorial-optimizer .
docker run -e AUDIT_SECRET_KEY="your-secure-key-here-min-32-chars" -p 8000:8000 qaoa-combinatorial-optimizer
```

---

## 📁 Project Structure

```
qaoa-combinatorial-optimizer/
├── agents/                  # Enterprise agent system (supervisor, workers, audit)
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # Security guards, HMAC audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   └── ...
├── qaoa_optimizer/         # Core QAOA engine and agents
│   ├── engine.py           # Algorithmic evaluation engine
│   ├── agents.py           # Sub-agent implementations
│   ├── models.py           # Data models
│   └── ...
├── tests/                  # Pytest test suite
├── cli.py                  # Main CLI entry point
├── simulator.py            # High-throughput simulation
├── enrichment.py           # Feature enrichment engines
├── Dockerfile              # Container build config
└── pyproject.toml          # Project metadata and dependencies
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
