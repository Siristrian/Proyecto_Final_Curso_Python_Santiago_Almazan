# Importamos las librerías necesarias
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Creamos la base de datos 'productos'
engine = create_engine('sqlite:///database/registros.db', connect_args={'check_same_thread': False})
# 'connect_args' nos permite que la base de datos trabaje en segundo plano para evitar errores

# Creamos la sesión
Session = sessionmaker(bind=engine)
session = Session()

# Vinculamos la base de datos con nuestra clase
Base = declarative_base()
