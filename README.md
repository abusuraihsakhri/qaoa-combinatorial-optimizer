# QAOA Combinatorial Optimizer

Small-graph **weighted Max-Cut** with a classical state-vector simulation of the Quantum Approximate Optimization Algorithm (QAOA). The repository also retains an earlier parameter-auditing CLI and FastAPI service for backwards compatibility.

## What works

- **Browser application (`web/`)**: enter undirected edges and positive weights, choose 1–3 QAOA layers, run parameter search, inspect the most probable partition and state probabilities, and export results to JSON. Computation stays in the browser without a backend, quantum hardware, or remote data transfer.
- **Python QAOA simulator**: exact state-vector evolution with cost and transverse-X mixer unitaries; deterministic grid initialization followed by coordinate refinement.
- **Comparison against exact Max-Cut**: exhaustive enumeration gives the exact optimum and an expected-value approximation ratio for reference. The most likely bitstring is not necessarily the optimal partition.
- **CLI and API**: optimize graph JSON from the command line or send it to `POST /api/maxcut`.
- **Legacy audit interface**: `audit`, `batch`, `chat`, `verify-audit`, and `serve` commands remain available. These perform rule-based parameter checks; they are **not** QAOA solvers.

The simulator accepts **2–9 vertices**, **positive finite edge weights**, and **1–3 layers**. It uses a classical state vector and exponential memory/time in vertex count. There is no quantum-hardware execution, convergence guarantee, or general-purpose combinatorial optimizer.

## Browser usage

Serve the static files with Python (required for ES modules):

```bash
python -m http.server 8001 --directory web
```

Visit http://localhost:8001/. Enter one `u,v,weight` edge per line with zero-based vertex indices. Run QAOA to view the expected cut weight, exact optimum, approximation ratio, angles, and bitstring probabilities. **Export results JSON** downloads the computed result.

GitHub Pages deployment is defined in `.github/workflows/pages.yml`. Availability depends on GitHub Pages being enabled and configured to use GitHub Actions; consult the repository's Actions/Pages status for confirmation.

## Python CLI

Python 3.10+ is covered by CI. Install and run:

```bash
python -m pip install -e ".[server,test]"
python cli.py maxcut --graph examples/square.json --layers 2 --grid 10
```

Graph file schema:

```json
{
  "vertices": 4,
  "edges": [[0, 1, 1], [1, 2, 1], [2, 3, 1], [3, 0, 1]]
}
```

The installed `qaoa-combinatorial-optimizer` entry point also supports `maxcut`. Weighted undirected edges must be unique; no self-loops or negative weights.

## FastAPI

```bash
export AUDIT_SECRET_KEY="replace-with-a-unique-32-character-or-longer-random-secret"
python cli.py serve --host 127.0.0.1 --port 8000
```

`POST http://127.0.0.1:8000/api/maxcut` accepts the graph schema above with optional `layers` (1–3) and `grid` (4–24). `GET /health` exposes service health. Existing `/api/audit`, `/api/chat`, and `/api/audit/logs` endpoints serve the legacy audit workflow.

The legacy audit workflow requires `AUDIT_SECRET_KEY` (at least 32 characters). The audit chain is signed with HMAC-SHA256 and validated against the configured key, but **its records are process-local and not durable**. The PHI filter is regex-based and must not be relied upon as comprehensive de-identification or regulatory compliance. Avoid submitting real patient identifiers.

To run the backend with Docker Compose, supply the audit secret in the host environment. No production key is included in the current configuration.

## Testing

```bash
python -m pytest -q
node --test tests/test_web_qaoa.mjs
python -m compileall -q agents qaoa_optimizer cli.py
```

GitHub Actions runs the Python tests across 3.10–3.13 and the JavaScript simulator tests. The frontend requires no npm installation or external JavaScript dependencies.

## Privacy and compatibility

The standalone browser simulation does not send graph inputs to a server and does not persist results automatically. JSON export occurs locally. It uses standard ES modules and typed arrays in current Chrome, Firefox, Safari, and Edge browsers. Python API access, if used, sends input to the configured server.

## License

MIT — see [LICENSE](LICENSE).
