
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Crear una instancia de SQLAlchemy sin asociarla a una aplicación Flask
db = SQLAlchemy()

# Define la función para crear la aplicación Flask
def create_app():
    app = Flask(__name__)

    # Configuración de la URI de SQLAlchemy para SQL Server con autenticación de Windows
    # Configuración de la URI de SQLAlchemy para SQL Server con autenticación de Windows
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://MiguelMartinez:Mandato2024@10.30.146.6/Bar_app?driver=ODBC+Driver+17+for+SQL+Server'


    # Configuración adicional opcional
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva el seguimiento de modificaciones
    app.config['SQLALCHEMY_ECHO'] = True  # Muestra las consultas SQL generadas en la consola
    app.secret_key = 'tu_clave_secreta_aqui'
    # Inicializar la extensión SQLAlchemy con la aplicación Flask
    db.init_app(app)

    # Importa los modelos después de inicializar la base de datos
    from app.models import RolLogin

    # Crear usuarios (opcionalmente dentro de una función para mayor modularidad)
    def create_admin_user():
        with app.app_context():
            # Verificar si el usuario ya existe
            existing_user = RolLogin.query.filter_by(nombre='Miguel Redondo').first()

            if existing_user is None:
                # Hashear la contraseña
                password = 'qwerty'
                nuevo_usuario = RolLogin(nombre='Miguel Redondo', rol='Administrador')
                nuevo_usuario.set_password(password)  # Establecer la contraseña antes de guardar

                # Agregar el usuario a la sesión y confirmar la transacción
                db.session.add(nuevo_usuario)
                db.session.commit()

    # Llama a la función para crear el usuario administrador
    create_admin_user()

    # Registra los blueprints después de inicializar la aplicación Flask
    from app.routes import routes_bp
    app.register_blueprint(routes_bp)

    return app