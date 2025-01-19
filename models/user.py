from models.database import get_database

db = get_database()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def __init__(self, name, mail, pswrd) -> None:
        self.username = name
        self.email = mail
        self.password = pswrd
    
    def __repr__(self) -> str:
        return '<User %r>' % self.username
