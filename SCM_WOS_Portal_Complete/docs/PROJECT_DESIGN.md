# SCM WOS Portal – Functional & Technical Design

## Core master data
- Users / Roles
- Assets: MH Asset, B&S & NH Asset
- HPOs: HPO-1, HPO-2
- Sections: Maintenance, Surface, Chemistry, HSE, HR, Infocom, SPM, ATSM, AIMS, IMR, IPEOT, PLINE
- PR Types
- Tender Modes
- Indent Statuses
- Delivery / Payment statuses
- Instrument types/statuses
- Post-contract issue types/statuses
- Delay reasons
- CPA approval levels
- SLA target-day matrix

## Core transactional entities
### Indent
One row per indent. Stores assignment, PR, financial, CPA, tender and milestone information.

### Contract
One-to-zero/one relationship from indent to contract/PO in the starter implementation. If one indent can generate multiple POs in the actual business process, change this to one-to-many.

### Post Contract Issue
Many issues can belong to one indent/PO.

### Instrument
Use `instrument_category = SD`, `PBG`, or `EMD`. The same table supports all three.

### Demurrage
One row per shipment/demurrage event.

### CPA Approval
Multiple approval levels per indent.

### Audit Log
Captures who performed key actions and when.

## Delay engine
Configure target days by stage:
1. Indent Receipt → PR Release
2. PR Release → Tender
3. Tender → TBO
4. TBO → Technical Evaluation
5. Technical Evaluation → PBO
6. PBO → Award
7. Award → Completion

For each stage:
`Actual Days = End Date - Start Date`
`Delay Days = max(Actual Days - Target Days, 0)`

If an end date is missing, use today's date for ageing/ongoing delay indicators.

## Traffic-light rules
- Green: completed within target
- Yellow: ongoing and not yet beyond target
- Red: beyond target

Make target days configurable in an SLA master rather than hard-coding them.

## Security model
- ADMIN: all modules and masters.
- HPO: assign/transfer/close cases in own HPO and view dashboards.
- DO: update assigned indents and manage assigned contracts/issues.
- FINANCE: payment, SD/PBG/EMD finance-side actions.
- SECTION: submit/track technical inputs for own section.

## Integration boundaries
### DISHA
Store a canonical file reference/URL. Do not store credentials in the application database.

### SAP
Use an approved middleware/API to retrieve PO, vendor, GR/IR and payment status. Keep an integration log and last-sync timestamp.

### Email
Use corporate SMTP/API. Store reminder history to prevent duplicate notifications.

## Suggested deployment
Browser → IIS/Nginx → Flask/Gunicorn → PostgreSQL
                             ↘ Corporate SMTP
                             ↘ Approved SAP middleware
                             ↘ Approved DISHA integration

## Recommended indexes
- indents(indent_no)
- indents(pr_no)
- indents(tender_no)
- indents(disha_file_no)
- indents(status)
- indents(dealing_officer_id)
- contracts(po_no)
- instruments(validity_date)
- post_contract_issues(status)
