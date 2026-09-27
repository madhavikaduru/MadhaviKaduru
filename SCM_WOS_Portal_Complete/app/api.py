import csv
import io
from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import Blueprint, Response, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from app import db
from app.models import AuditLog, Contract, Demurrage, Indent, Instrument, PostContract, Tender, User

api_bp = Blueprint("api", __name__)


def parse_date(dt_str):
    """Safely parse standard YYYY-MM-DD strings."""
    if not dt_str:
        return None
    try:
        return datetime.strptime(str(dt_str).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def log(action, entity, entity_id, details=""):
    db.session.add(
        AuditLog(
            user_id=current_user.user_id,
            action=f"{action} {entity} #{entity_id} {details}".strip()
        )
    )


# --- DASHBOARD SERVICE CLASS ---

class DashboardService:

    @classmethod
    def _get_summary_counts(cls) -> dict:
        total = db.session.query(func.count(Indent.indent_no)).scalar() or 0
        nit_invited = db.session.query(func.count(Tender.indent_no)).filter(Tender.tender_status.ilike("%BidInvited%")).scalar() or 0
        under_progress = db.session.query(func.count(Tender.indent_no)).filter(Tender.tender_status.ilike("%TechnicalEvaluation%")).scalar() or 0
        negotiation = db.session.query(func.count(Tender.indent_no)).filter(Tender.tender_status.ilike("%PriceEvaluation%")).scalar() or 0
        awarded = db.session.query(func.count(Tender.indent_no)).filter(Tender.tender_status.ilike("%Awarded%")).scalar() or 0
        retendered = db.session.query(func.count(Tender.indent_no)).filter(Tender.tender_status.ilike("%ReTendered%")).scalar() or 0
        post_contract_indents = db.session.query(func.count(Indent.indent_no)).filter(Indent.indent_status.ilike("%PostContract%")).scalar() or 0
        
        return {
            "total": total,
            "nit_invited": nit_invited,
            "under_progress": under_progress,
            "negotiation": negotiation,
            "awarded": awarded,
            "retendered": retendered,
            "post_contract_indents": post_contract_indents,
        }

    @classmethod
    def _get_delay_metrics(cls) -> dict:
        today = date.today()
        nit_cutoff_date = today - timedelta(days=30)
        noa_cutoff_date = today - timedelta(days=90)
        
        receipt_to_nit = (
            db.session.query(func.count(Indent.indent_no))
            .outerjoin(Tender, Indent.indent_no == Tender.indent_no)
            .filter(
                Tender.nit_date.is_(None),
                Tender.tender_status != "Retendered",
                Indent.assignment_date < nit_cutoff_date,
            )
            .scalar() or 0
        )

        nit_to_noa = (
            db.session.query(func.count(Tender.indent_no))
            .filter(
                Tender.nit_date.isnot(None),
                Tender.award_date.is_(None),
                Tender.nit_date < noa_cutoff_date,
            )
            .scalar() or 0
        )

        board_purchase = (
            db.session.query(func.count(Indent.indent_no))
            .filter(
                Indent.cpa == "Board",
                Indent.assignment_date < nit_cutoff_date,
            )
            .scalar() or 0
        )

        return {
            "receipt_to_nit": receipt_to_nit,
            "nit_to_noa": nit_to_noa,
            "board_purchase": board_purchase,
        }

    @classmethod
    def get_delayed_indents_nit_over_30_days(cls):
        """Fetch tuples of (Indent, Tender) where nit_date > 30 days after assignment_date."""
        return (
            db.session.query(Indent, Tender)
            .join(Tender, Indent.indent_no == Tender.indent_no)
            .filter(
                Tender.nit_date.isnot(None),
                Indent.assignment_date.isnot(None),
                (Tender.nit_date - Indent.assignment_date) > 30,
            )
            .all()
        )

    @classmethod
    def get_delayed_indents_award_over_90_days(cls):
        """Fetch indents where award_date is > 90 days after nit_date."""
        return (
            db.session.query(Indent)
            .join(Tender, Indent.indent_no == Tender.indent_no)
            .filter(
                Tender.award_date.isnot(None),
                Tender.nit_date.isnot(None),
                (Tender.award_date - Tender.nit_date) > 90,
            )
            .all()
        )

    @classmethod
    def get_dashboard_context(cls):
        """Consolidates summary metrics and detailed delayed indents for the dashboard."""
        nit_delayed_indents = cls.get_delayed_indents_nit_over_30_days()
        award_delayed_indents = cls.get_delayed_indents_award_over_90_days()

        # Extract indent_no correctly whether 'i' is an Indent object or a (Indent, Tender) tuple
        combined_delayed_ids = {
            (i[0].indent_no if isinstance(i, (tuple, list)) else getattr(i, "Indent", i).indent_no)
            for i in (nit_delayed_indents + award_delayed_indents)
        }

        all_delayed_indents = (
            db.session.query(Indent)
            .filter(Indent.indent_no.in_(combined_delayed_ids))
            .all()
            if combined_delayed_ids
            else []
        )

        return {
            "summary": cls._get_summary_counts(),
            "delays": cls._get_delay_metrics(),
            "counts": {
                "nit_delay_count": len(nit_delayed_indents),
                "award_delay_count": len(award_delayed_indents),
                "total_delayed_count": len(all_delayed_indents),
            },
            "nit_delayed_indents": nit_delayed_indents,
            "award_delayed_indents": award_delayed_indents,
            "all_delayed_indents": all_delayed_indents,
        }


# --- ROUTES ---

@api_bp.get("/")
@login_required
def dashboard():
    context = DashboardService.get_dashboard_context()
    return render_template("dashboard.html", **context)


@api_bp.get("/dashboard/data")
@login_required
def dashboard_data():
    total = Indent.query.count()
    pci = PostContract.query.filter(PostContract.status.notin_(["Implemented", "Rejected"])).count()

    assets = db.session.query(Indent.asset, func.count(Indent.indent_no)).group_by(Indent.asset).all()
    hpos = db.session.query(Indent.hpo, func.count(Indent.indent_no)).group_by(Indent.hpo).all()
    sections = db.session.query(Indent.hpo, Indent.section, func.count(Indent.indent_no)).group_by(Indent.hpo, Indent.section).all()

    officers = (
        db.session.query(User.user_name, func.count(Indent.indent_no))
        .join(Indent, Indent.dealing_officer_id == User.user_id, isouter=True)
        .filter(User.role == "DO")
        .group_by(User.user_id, User.user_name)
        .order_by(func.count(Indent.indent_no).desc())
        .all()
    )

    return jsonify({
        "summary": {"total": total, "post_contract": pci},
        "assets": [{"name": a, "count": c} for a, c in assets],
        "hpos": [{"name": a, "count": c} for a, c in hpos],
        "sections": [{"hpo": a, "section": b, "count": c} for a, b, c in sections],
        "officers": [{"name": a, "count": c} for a, c in officers]
    })


@api_bp.get("/officers")
@login_required
def officers():
    xs = User.query.filter_by(role="DO", active=True).order_by(User.user_name).all()
    return jsonify([{"id": x.user_id, "name": x.user_name} for x in xs])


@api_bp.get("/indents")
@login_required
def list_indents():
    q = request.args.get("q", "").strip()
    query = Indent.query
    if q:
        query = query.filter(or_(
            Indent.indent_no.ilike(f"%{q}%"),
            Indent.disha_file_no.ilike(f"%{q}%"),
            Indent.description.ilike(f"%{q}%")
        ))
    items = query.order_by(Indent.id.desc()).limit(500).all()
    return jsonify([{
        "indent_no": x.indent_no,
        "asset": x.asset,
        "hpo": x.hpo,
        "disha_file_no": x.disha_file_no,
        "description": x.description,
        "section": x.section,
        "assignment_date": x.assignment_date.isoformat() if x.assignment_date else "",
        "officer": x.dealing_officer.user_name if x.dealing_officer else ""
    } for x in items])


@api_bp.post("/indents")
@login_required
def create_indent():
    d = request.json or {}
    required_fields = ["asset", "hpo", "indent_no", "disha_file_no", "description", "section", "dealing_officer_id"]

    for field in required_fields:
        if not d.get(field) or str(d.get(field)).strip() == "":
            field_name = field.replace('_', ' ').title()
            return jsonify({"ok": False, "error": f"{field_name} is required."}), 400

    indent_no = d.get('indent_no')
    if Indent.query.filter_by(indent_no=indent_no).first():
        return jsonify({
            'ok': False,
            'error': f'Indent No. {indent_no} already exists in the system.'
        }), 400

    try:
        indent_no_val = int(indent_no)
        assign_date_val = parse_date(d.get('assignment_date')) or date.today()

        new_indent = Indent(
            indent_no=indent_no_val,
            disha_file_no=d.get('disha_file_no'),
            asset=d.get('asset'),
            hpo=d.get('hpo'),
            section=d.get('section'),
            dealing_officer_id=int(d.get('dealing_officer_id')),
            description=d.get('description'),
            assignment_date=assign_date_val
        )
        db.session.add(new_indent)
        db.session.commit()

        officer_name = new_indent.dealing_officer.user_name if new_indent.dealing_officer else f"User #{new_indent.dealing_officer_id}"

        return jsonify({
            "ok": True,
            "message": f"Indent No. {new_indent.indent_no} assigned to {officer_name} on {assign_date_val.strftime('%Y-%m-%d')}",
            "indent_no": new_indent.indent_no
        }), 201

    except ValueError:
        db.session.rollback()
        return jsonify({"ok": False, "error": "Invalid numerical values provided."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.put("/indents/<int:iid>")
@login_required
def update_indent(iid):
    x = db.session.get(Indent, iid)
    if not x:
        return jsonify({"ok": False, "error": "Indent not found"}), 404

    d = request.json or {}

    indent_fields = [
        "disha_file_no", "asset", "hpo", "section", "description",
        "dealing_officer_id", "assignment_date", 
        "pr_no", "pr_type", "pr_value", "pr_currency", "cpa", "indent_type", "indent_status"
    ]

    for k in indent_fields:
        if k in d:
            if k == "assignment_date":
                setattr(x, k, parse_date(d[k]))
            elif k == "pr_value" and d[k] is not None:
                setattr(x, k, Decimal(str(d[k])))
            else:
                setattr(x, k, d[k])

    tender_no = d.get("tender_no")
    if tender_no:
        tender = Tender.query.filter_by(indent_no=x.indent_no).first()
        if not tender:
            tender = Tender(
                indent_no=x.indent_no,
                tender_no=tender_no,
                pr_no=d.get("pr_no") or x.pr_no,
            )
            db.session.add(tender)
        else:
            tender.tender_no = tender_no

        if "tender_mode" in d:
            tender.tender_mode = d.get("tender_mode")
        if "tender_status" in d:
            tender.tender_status = d.get("tender_status")

        tender_date_fields = ["nit_date", "prebid_date", "tbo_date", "clarification_date", "pbo_date", "award_date"]
        for field in tender_date_fields:
            if field in d:
                setattr(tender, field, parse_date(d.get(field)))

    db.session.commit()
    log("UPDATE", "Indent", iid, x.indent_no)

    return jsonify({"ok": True, "message": "Indent updated successfully"})


@api_bp.post("/tenders")
@login_required
def create_tender():
    d = request.json or {}
    tender_no = d.get("tender_no")
    indent_no = d.get("indent_no")

    if not tender_no or not indent_no:
        return jsonify({"ok": False, "error": "Tender No and Indent No are required."}), 400

    try:
        new_tender = Tender(
            tender_no=tender_no,
            indent_no=int(indent_no),
            tender_mode=d.get("tender_mode"),
            nit_date=parse_date(d.get("nit_date")),
            prebid_date=parse_date(d.get("prebid_date")),
            tbo_date=parse_date(d.get("tbo_date")),
            clarification_date=parse_date(d.get("clarification_date")),
            pbo_date=parse_date(d.get("pbo_date")),
            award_date=parse_date(d.get("award_date")),
            tender_status=d.get("tender_status", "Draft")
        )
        db.session.add(new_tender)
        db.session.commit()
        return jsonify({"ok": True, "message": f"Tender {tender_no} created successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.post("/contracts")
@login_required
def create_contract():
    d = request.json or {}
    if not d.get("indent_no"):
        return jsonify({"ok": False, "error": "Indent No is required."}), 400

    try:
        x = Contract(
            indent_no=int(d["indent_no"]),
            vendor_name=d.get("vendor_name"),
            contract_no=d.get("contract_no"),
            value=Decimal(str(d.get("value", 0))),
            award_date=parse_date(d.get("award_date"))
        )
        db.session.add(x)
        db.session.commit()
        log("CREATE", "Contract", x.id, x.contract_no)
        return jsonify({"ok": True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": str(e)}), 500


@api_bp.get("/contracts")
@login_required
def list_contracts():
    xs = Contract.query.all()
    return jsonify([{
        "id": x.id,
        "indent_no": x.indent_no,
        "vendor_name": x.vendor_name,
        "contract_no": x.contract_no,
        "value": float(x.value or 0),
        "award_date": x.award_date.isoformat() if x.award_date else ""
    } for x in xs])


@api_bp.get("/instruments")
@login_required
def list_instruments():
    xs = Instrument.query.all()
    return jsonify([{
        "id": x.id,
        "type": x.instrument_type,
        "ref_no": x.ref_no,
        "amount": float(x.amount or 0),
        "expiry_date": x.expiry_date.isoformat() if x.expiry_date else ""
    } for x in xs])


@api_bp.get("/export/indents.csv")
@login_required
def export_indents_csv():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["Indent No", "Asset", "HPO", "Section", "Description", "DO", "Assignment Date"])
    for x in Indent.query.order_by(Indent.indent_no).all():
        w.writerow([
            x.indent_no, x.asset, x.hpo, x.section, x.description,
            x.dealing_officer.user_name if x.dealing_officer else "",
            x.assignment_date 
        ])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=scm_indents.csv"})


@api_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('auth.login'))