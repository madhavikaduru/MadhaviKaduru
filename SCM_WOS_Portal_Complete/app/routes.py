from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.api import DashboardService
from app.models import Indent, User

from sqlalchemy import or_, cast, String
from app.models import Indent

from flask import redirect, url_for
from flask_login import logout_user, login_required
# Define the Blueprint ONCE at the top
main_bp = Blueprint('main', __name__)

# To this (or redirect to your dashboard):
@main_bp.route('/')
@login_required
def home():
    context = DashboardService.get_dashboard_context()
    return render_template('dashboard.html', **context)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    context = DashboardService.get_dashboard_context()
    return render_template('dashboard.html', **context)


# --- INDENT MANAGEMENT ROUTES ---

@main_bp.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
    if request.method == 'POST':
        indent_no = request.form.get('indent_no')
        asset = request.form.get('asset')
        hpo = request.form.get('hpo')
        disha_file_no = request.form.get('disha_file_no')
        assignment_date = request.form.get('assignment_date')
        description = request.form.get('description')
        section = request.form.get('section')
        indent_type = request.form.get('indent_type')
        dealing_officer_id = request.form.get('dealing_officer_id')

        new_indent = Indent(
            indent_no=indent_no,
            asset=asset,
            hpo=hpo,
            disha_file_no=disha_file_no,
            assignment_date=assignment_date,
            description=description,
            section=section,
            indent_type=indent_type,
            dealing_officer_id=dealing_officer_id
        )

        db.session.add(new_indent)
        db.session.commit()

        flash('Indent assigned successfully!', 'success')
        return redirect(url_for('main.view_indents'))

    officers = User.query.filter_by(role='DO').all()
    return render_template('assign_indent.html', officers=officers)


@main_bp.route('/view-indents', methods=['GET'])
@login_required
def view_indents():
    indents = Indent.query.all()
    return render_template('view_indents.html', indents=indents)



# In app/routes.py

@main_bp.route('/update-indent', defaults={'indent_no': None}, methods=['GET', 'POST'])
@main_bp.route('/update-indent/<int:indent_no>', methods=['GET', 'POST'])
@login_required
def update_indent(indent_no):
    indents = Indent.query.all()
    indent = Indent.query.get(indent_no) if indent_no else None

    if request.method == 'POST':
        flash('Indent updated successfully!', 'success')
        return redirect(url_for('main.view_indents'))

    return render_template('update_indent.html', indents=indents, indent=indent)


@main_bp.route('/search-indent', methods=['GET'])
@login_required
def search_indent():
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        results = Indent.query.filter(
            or_(
                # Cast the integer column to String for ILIKE matching
                cast(Indent.indent_no, String).ilike(f"%{query}%"),
                Indent.disha_file_no.ilike(f"%{query}%"),
                Indent.description.ilike(f"%{query}%")
            )
        ).all()

    return render_template('search_indent.html', query=query, results=results)


@main_bp.route('/indent/<int:indent_no>/edit', methods=['GET', 'POST'])
@login_required
def edit_indent(indent_no):
    indent = Indent.query.get_or_404(indent_no)
    if request.method == 'POST':
        flash('Indent updated successfully!', 'success')
        return redirect(url_for('main.view_indents'))
    return render_template('update_indent.html', indent=indent)


# --- SECONDARY MODULE ROUTES ---

@main_bp.route('/contracts')
@login_required
def contracts():
    return render_template('contracts.html')


@main_bp.route('/post-contract')
@login_required
def post_contract():
    return render_template('post_contract.html')


@main_bp.route('/instruments')
@login_required
def instruments():
    return render_template('instruments.html')


@main_bp.route('/demurrage')
@login_required
def demurrage():
    return render_template('demurrage.html')


@main_bp.route('/reports')
@login_required
def reports():
    return render_template('reports.html')


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


    # Add to app/routes.py
@main_bp.route('/register')
def register_redirect():
    return redirect(url_for('auth.register'))


    # In app/routes.py

@main_bp.route('/login')
def login_redirect():
    return redirect(url_for('auth.login'))