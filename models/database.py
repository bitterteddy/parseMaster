from typing import Any, List, Dict
from sqlalchemy import MetaData, text, select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
metadata = MetaData()

def initialize(app, database_name:str):
    # uri = 'mysql+pymysql://admin:1PkmXCqeCRhxTfnpdHLvdrZ0:@localhost:3306/'+database_name
    uri = 'mysql+pymysql://root:@localhost/'+database_name
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

def get_database():
    return db

def get_items(app, statement):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            res = session.scalars(statement).all()
        except Exception as e:
            res = []
        finally:
            session.close()
    return res

def get_item(app, statement):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            res = session.scalars(statement).one_or_none()
        except Exception as e:
            res = None
        finally:
            session.close()
    return res

def get_items_as_dicts(app, statement):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            rows = session.execute(statement).all()
            result = [r._asdict() for r in rows]
        except Exception as e:
            res = []
        finally:
            session.close()
    return res

def add_item(app, item):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            session.add(item)
            session.commit()
        except Exception as e:
            session.rollback()
            print (f"Error inserting {item.__repr__()}: {str(e)}")
        finally:
            session.close()

def add_items(app, items:List[Any]):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            session.add_all(items)
            session.commit()
        except Exception as e:
            session.rollback()
            print (f"Error inserting items: {str(e)}")
        finally:
            session.close()

def create_custom_table(app, table_name:str, column_params:List[Dict[str, Any]]):
    pass
    # with app.app_context():
    #     columns = [
    #         db.Column("id", db.Integer, primary_key=True, autoincrement=True),  # ID �������
    #     ]

    #     for element in column_params:
    #         column_name = element["name"]
    #         column_type = db.Text if element.get("multiple", False) else db.String(255)
    #         columns.append(db.Column(column_name, column_type))
        
    #     table = db.Table(table_name, metadata, *columns, extend_existing=True)
    #     metadata.create_all(bind=db.engine)
    # return table

def fill_custom_table(app, table_name:str, results:List[Dict[str, str]]):
    pass
    # with app.app_context():
    #     table = db.Table(table_name, metadata, autoload_with=db.engine)

      