from app import create_app, db
from app.models import User
app=create_app()
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        u=User(username='admin',full_name='SCM Administrator',role='ADMIN',hpo=None);u.set_password('Admin@123');db.session.add(u)
    if not User.query.filter_by(username='hpo1').first():
        u=User(username='hpo1',full_name='HPO-1 Head',role='HPO',hpo='HPO-1');u.set_password('Hpo@123');db.session.add(u)
    if not User.query.filter_by(username='hpo2').first():
        u=User(username='hpo2',full_name='HPO-2 Head',role='HPO',hpo='HPO-2');u.set_password('Hpo@123');db.session.add(u)
    for i,h in [(1,'HPO-1'),(2,'HPO-1'),(3,'HPO-2'),(4,'HPO-2')]:
        name=f'Dealing Officer {i}'
        if not User.query.filter_by(username=f'do{i}').first():
            u=User(username=f'do{i}',full_name=name,role='DO',hpo=h);u.set_password(f'Do@123{i}');db.session.add(u)
    db.session.commit()
    print('Seed complete.')
