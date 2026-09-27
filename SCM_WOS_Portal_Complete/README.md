# SCM PORTAL FOR WESTERN OFFSHORE ASSETS (WOS)

A Flask + PostgreSQL web portal covering the SCM lifecycle:

**Indent → Assignment → PR → Tender → Technical/Price Evaluation → Award → Contract/PO → Delivery/Payment → Post Contract → SD/PBG/EMD → Demurrage → Reports**

## Technology
- Python 3.11+
- Flask
- PostgreSQL 15+
- SQLAlchemy
- HTML/CSS/JavaScript
- Chart.js

## 1. Create PostgreSQL database
Open pgAdmin or psql and create a database named `scm_wos`.

Example:
```sql
CREATE DATABASE scm_wos;
```

## 2. Configure environment
Copy `.env.example` to `.env` and change the PostgreSQL username/password.

Example:
`DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/scm_wos`

## 3. Install
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux
source .venv/bin/activate

pip install -r requirements.txt
python database/seed.py
```

## 4. Run
```bash
python run.py
```
Open `http://localhost:5000`

### Demo users
- admin / Admin@123
- hpo1 / Hpo@123
- hpo2 / Hpo@123
- do1 / Do@1231 through do4 / Do@1234

**Change all passwords before production use.**

## Current modules
1. Home Dashboard
2. Assign Indent
3. Update / Track Indent
4. Contract / Order Status
5. Post Contract Issues
6. SD/PBG/EMD Tracking
7. Demurrage
8. Monthly Reports
9. Role-based login foundation
10. CSV export
11. 90/60/30-day instrument alerts
12. Audit log foundation

## Production enhancements recommended
- Corporate SSO/LDAP/AD instead of local passwords.
- HTTPS and reverse proxy (IIS/Nginx).
- Full CRUD screens for SD/PBG/EMD, post-contract and demurrage.
- PostgreSQL migrations (Alembic/Flask-Migrate).
- Fine-grained permissions by HPO, asset and section.
- Email/SMTP or corporate notification gateway.
- DISHA hyperlink/file repository integration.
- SAP PO interface through an approved API/middleware.
- GePNIC/GeM integration only through approved organizational interfaces.
- CPA approval workflow with maker/checker and electronic audit trail.
- Gantt timeline and configurable SLA/target-day master.
- Delay-reason master and automatic stage-delay calculations.
- Excel/PDF report generation.
- Backup, archival, monitoring, logging and security hardening.
- Data validation and duplicate prevention rules.
