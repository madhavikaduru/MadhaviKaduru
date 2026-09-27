from app import db
from datetime import datetime, date

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True,unique=True, nullable=False)
    user_name = db.Column(db.String(80),  nullable=False)
    password_hash= db.Column(db.String(255), nullable=False)   
    role = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return getattr(self, 'active', True)

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)




class Indent(db.Model):
    __tablename__ = 'indents'

    indent_no = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)      
    disha_file_no = db.Column(db.String(100))
    asset = db.Column(db.String(100))
    hpo = db.Column(db.String(100))
    section = db.Column(db.String(100))
    description = db.Column(db.Text)
    dealing_officer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))     
    dealing_officer = db.relationship('User', backref='indents', foreign_keys=[dealing_officer_id])
    assignment_date = db.Column(db.Date, default=date.today)   
    pr_no = db.Column(db.String(100))
    pr_type = db.Column(db.String(50))
    pr_value = db.Column(db.Numeric(12, 2))
    currency = db.Column(db.String(10), default="INR")
    cpa = db.Column(db.String(100))
    indent_type = db.Column(db.String(50))   
    indent_status = db.Column(db.String(50))
    tenders = db.relationship(
        "Tender", backref="indent", cascade="all, delete-orphan", lazy=True)
    

class Tender(db.Model):
    __tablename__ = 'tenders'
    
    pr_no = db.Column(db.Integer, primary_key=True)
    tender_no = db.Column(db.String(100),nullable=False)
    indent_no = db.Column(db.Integer, db.ForeignKey('indents.indent_no', ondelete='CASCADE'), nullable=False)
    tender_mode = db.Column(db.String(50))
    nit_date = db.Column(db.Date)
    prebid_date = db.Column(db.Date)
    tbo_date = db.Column(db.Date)
    clarification_date = db.Column(db.Date)
    pbo_date = db.Column(db.Date)
    award_date = db.Column(db.Date)
    tender_status = db.Column(db.String(50), default='Draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(100), unique=True)
    indent_no = db.Column(db.Integer, db.ForeignKey('indents.indent_no'))
    vendor_name = db.Column(db.String(200))
    value = db.Column(db.Numeric(15, 2))
    award_date = db.Column(db.Date)


class PostContract(db.Model):
    __tablename__ = 'post_contract'  # Make sure this matches the new database table name

    pc_status = db.Column(db.String(50))
   
    indent_no = db.Column(db.String(50), db.ForeignKey('indents.indent_no'), primary_key=True)
    issue_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    indent_type = db.Column(db.String(50), default="PostContract")
    pc_status = db.Column(db.String(50))
    indent = db.relationship('Indent', backref=db.backref('post_contracts', lazy=True))



class Instrument(db.Model):
    __tablename__ = 'instruments'

    id = db.Column(db.Integer, primary_key=True)
    instrument_type = db.Column(db.String(50))
    ref_no = db.Column(db.String(100))
    amount = db.Column(db.Numeric(15, 2))
    expiry_date = db.Column(db.Date)


class Demurrage(db.Model):
    __tablename__ = 'demurrage'

    id = db.Column(db.Integer, primary_key=True)
    vessel_name = db.Column(db.String(150))
    indent_no = db.Column(db.Integer, db.ForeignKey('indents.indent_no'))
    amount = db.Column(db.Numeric(15, 2))
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)