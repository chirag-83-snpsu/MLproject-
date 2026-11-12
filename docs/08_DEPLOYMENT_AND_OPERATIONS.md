
# DEPLOYMENT & SRE OPERATIONAL RUNBOOK
## CredX AI — Explainable Credit Risk Platform

**Document ID:** OPS-001  
**Version:** 1.0.0  

---

### 1. Local Development Launch

To launch CredX AI locally in the Antigravity environment:

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\activate

# 2. Start the FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive UI Dashboard**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger / OpenAPI Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 2. Standard Demo Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Senior Underwriter** | `sarah.officer@credx.ai` | `Officer@123` | Submit apps, run assessments, record underwriting decisions & overrides |
| **Quantitative Risk Lead** | `david.analyst@credx.ai` | `Analyst@123` | Portfolio analytics, model health metrics, drift monitoring |
| **Compliance Officer** | `elena.compliance@credx.ai` | `Compliance@123` | Fair lending audit reports, disparate impact ratios, audit logs |
| **System Administrator** | `admin@credx.ai` | `Admin@123` | Full administrative control & user provisioning |

---

### 3. Docker Container Deployment

```bash
# Build and run using Docker Compose
docker-compose up --build -d

# Verify container health
docker ps
curl http://localhost:8000/health
```

---

### 4. CI/CD & Automated Model Governance Pipeline

1. **Continuous Integration**:
   - Automated linting & type checks.
   - Execution of unit & integration tests (`pytest tests/`).
2. **Continuous Deployment**:
   - Containerized build artifact published to container registry.
   - Automated migration check on SQLite / PostgreSQL database.
3. **Model Drift Monitoring & Retraining**:
   - Cron-scheduled or event-triggered calculation of Population Stability Index (PSI).
   - If PSI > 0.15, an alert is dispatched to `david.analyst@credx.ai` and retraining workflow is initiated on newly seasoned loan repayment data.
