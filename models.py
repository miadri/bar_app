
import bcrypt
from . import db
from datetime import datetime


class RolLogin(db.Model):
    __tablename__ = 'rol_login'

    id = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    contraseña = db.Column(db.String(128), nullable=False)
    sede = db.Column(db.String(20))
    SedeID = db.Column(db.Integer)

    def set_password(self, contraseña):
        self.contraseña = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.contraseña.encode('utf-8'))
    

class Sede(db.Model):
    __tablename__ = 'Sede'

    SedeID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100))

    def __repr__(self):
        return f"Sede(SedeID={self.SedeID}, Nombre={self.Nombre})"
    

class Mesa(db.Model):
    __tablename__ = 'Mesa'

    MesaID = db.Column(db.Integer, primary_key=True)
    Numero = db.Column(db.Integer)
    SedeID = db.Column(db.Integer, db.ForeignKey('Sede.SedeID'))
    Estado = db.Column(db.String(10))

    def __repr__(self):
        return f"Mesa(MesaID={self.MesaID}, Numero={self.Numero}, SedeID={self.SedeID}, Estado={self.Estado})"

class Usuario(db.Model):
    __tablename__ = 'Usuario'

    UsuarioID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100))
    RolID = db.Column(db.Integer, db.ForeignKey('rol_login.id'))

    def __repr__(self):
        return f"Usuario(UsuarioID={self.UsuarioID}, Nombre={self.Nombre}, RolID={self.RolID})"


class Pedido(db.Model):
    __tablename__ = 'Pedido'
    PedidoID = db.Column(db.Integer, primary_key=True)
    MesaID = db.Column(db.Integer, db.ForeignKey('Mesa.MesaID'), nullable=False)
    FechaHora = db.Column(db.DateTime)
    ProductoID = db.Column(db.Integer, db.ForeignKey('Producto.ProductoID'))
    Cantidad = db.Column(db.Integer)
    Estado = db.Column(db.String(20))
    Valor_bruto = db.Column(db.Numeric(10, 2))
    ValorVenta = db.Column(db.Numeric(10, 2))  # Agrega esta línea
    Valor_total = db.Column(db.Numeric(10, 2))
    UsuarioID = db.Column(db.Integer, db.ForeignKey('Usuario.UsuarioID'))  # Agregar este atributo

def __repr__(self):
    return f"Pedido(PedidoID={self.PedidoID}, MesaID={self.MesaID}, FechaHora={self.FechaHora}, ProductoID={self.ProductoID}, Cantidad={self.Cantidad}, Estado={self.Estado}, Valor_bruto={self.Valor_bruto}, Valor_total={self.Valor_total}, UsuarioID={self.UsuarioID})"

class Producto(db.Model):
    __tablename__ = 'Producto'

    ProductoID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100))
    Precio = db.Column(db.DECIMAL(10, 2))

    def __repr__(self):
        return f"Producto(ProductoID={self.ProductoID}, Nombre={self.Nombre}, Precio={self.Precio})"

class Inventario(db.Model):
    __tablename__ = 'Inventario'

    InventarioID = db.Column(db.Integer, primary_key=True)
    ProductoID = db.Column(db.Integer, db.ForeignKey('Producto.ProductoID'))
    Cantidad = db.Column(db.Integer)
    Proovedor = db.Column(db.String(200))
    SedeID = db.Column(db.Integer, db.ForeignKey('Sede.SedeID'))

    def __repr__(self):
        return f"Inventario(InventarioID={self.InventarioID}, ProductoID={self.ProductoID}, Cantidad={self.Cantidad}, Proovedor={self.Proovedor}, SedeID={self.SedeID})"

class InventarioSede(db.Model):
    __tablename__ = 'InventarioSede'

    id = db.Column(db.Integer, primary_key=True)
    SedeID = db.Column(db.Integer, db.ForeignKey('Sede.SedeID'))
    InventarioID = db.Column(db.Integer, db.ForeignKey('Inventario.InventarioID'))

    # Define la relación con la tabla Sede
    sede = db.relationship('Sede', backref=db.backref('inventarios', lazy=True))

    # Define la relación con la tabla Inventario
    inventario = db.relationship('Inventario', backref=db.backref('sedes', lazy=True))

    def __repr__(self):
        return f"InventarioSede(id={self.id}, SedeID={self.SedeID}, InventarioID={self.InventarioID})"
    # Crear una relación entre la sede con ID 1 y el inventario con ID 1

class Estado(db.Model):
    __tablename__ = 'Estados'

    EstadoID = db.Column(db.Integer, primary_key=True)
    EstadoNombre = db.Column(db.String(50), nullable=False)
    MesaID = db.Column(db.Integer, db.ForeignKey('Mesa.MesaID'), nullable=False)

    def __repr__(self):
        return f"Estado(EstadoID={self.EstadoID}, EstadoNombre='{self.EstadoNombre}', MesaID={self.MesaID})"

class DetallePedido(db.Model):
    __tablename__ = 'DetallePedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('Pedido.PedidoID'))
    producto_id = db.Column(db.Integer, db.ForeignKey('Producto.ProductoID'))
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.DECIMAL(10, 2))
    valor_total = db.Column(db.DECIMAL(10, 2))

    # Define la relación con la tabla Pedido
    pedido = db.relationship('Pedido', backref=db.backref('detalles', lazy=True))

    # Define la relación con la tabla Producto
    producto = db.relationship('Producto', backref=db.backref('detalles', lazy=True))

    def __repr__(self):
        return f"DetallePedido(id={self.id}, pedido_id={self.pedido_id}, producto_id={self.producto_id}, cantidad={self.cantidad}, precio_unitario={self.precio_unitario}, valor_total={self.valor_total})"

class Venta(db.Model):
    __tablename__ = 'Ventas'
    VentaID = db.Column(db.Integer, primary_key=True)
    PedidoID = db.Column(db.Integer, db.ForeignKey('Pedido.PedidoID'))
    FechaHora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ValorTotal = db.Column(db.Numeric(10, 2), nullable=False)