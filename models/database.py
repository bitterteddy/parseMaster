from typing import Any, List, Dict
from uu import Error
from sqlalchemy import MetaData, text, select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
metadata = MetaData()

def initialize(app, database_name:str):
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

def get_item_by_id(app, table, id):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            res = session.get(table, id)
        except Exception as e:
            res = e
        finally:
            session.close()
    return res

def get_items_as_dicts(app, statement):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            rows = session.execute(statement).all()
            res = [r._asdict() for r in rows]
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

def update_item(app, item, upd_func, par):
    table = type(item)
    id = item.id
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            temp_item = session.get(table, id)
            upd_func(temp_item, par)
            session.commit()
        except Exception as e:
            print(e)
        else:
            upd_func(item, par)
        finally:
            session.close()

def create_custom_table(app, table_name:str, column_params:List[Dict[str, Any]]):
    with app.app_context():
        columns = [
            db.Column("id", db.Integer, primary_key=True, autoincrement=True),
        ]

        for element in column_params:
            column_name = element["name"]
            column_type = db.Text if element.get("multiple", False) else db.String(255)
            columns.append(db.Column(column_name, column_type))
        
        table = db.Table(table_name, metadata, *columns, extend_existing=True)
        metadata.create_all(bind=db.engine)
    return table

def fill_custom_table(app, table_name:str, results:Dict[str, Any]):
    with app.app_context():
        table = db.Table(table_name, metadata, autoload_with=db.engine)
        insert_values = [
            {key: (",".join(value) if isinstance(value, list) else value) for key, value in result.items()}
            for result in results
        ]
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            session.execute(table.insert().values(insert_values))
            session.commit()
        except Error as e:
            print(e)
        finally:
            session.close()

def get_result(app, table_name):
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            query = text(f"SELECT * FROM {table_name}") 
            result = session.execute(query).fetchall()
            
            print(result)

        
        except Exception as e:
            print(f"Error fetching data from {table_name}: {e}")
            return {"error": str(e)}, []
        finally:
            session.close()
    return 

