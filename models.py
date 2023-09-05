from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
import db  # Este import lo realizamos para poder traernos Base y poder convertir las clases en tablas
from sqlalchemy.orm import relationship

# Clase para crear la tabla que lleve el registro de los proveedores que tenemos
class Registro_proveedores(db.Base):  # Herencia, desde db.py, para poder convertirla en tablas
    __tablename__ = "proveedores"  # Nombramos la segunda tabla para almacenar los proveedores
    __table_args__ = {'sqlite_autoincrement' : True}  # Aquí ponemos el autoincremento para id de referencia-primary key
    id = Column(Integer, primary_key=True)  # Autoincremento para tener clasificados los proveedores
    proveedor = Column(String(200), nullable=False)  # No puede ser None
    telefono = Column(Integer, nullable=False)
    direccion = Column(String(200), nullable=False)
    cif = Column(Integer, nullable=False)
    facturacion = Column(Float, nullable=False)  # Apartado en el que se mostrarán las ganancias del proveedor

    # Constructor de la clase "Registro_proveedores"
    def __init__(self, proveedor, telefono, direccion, cif, facturacion):
        self.proveedor = proveedor
        self.telefono = telefono
        self.direccion = direccion
        self.cif = cif
        self.facturacion = facturacion

    # Comprobación de que todos los elementos existen
    def __str__(self):
        return "Proveedor {} -> {} -> {} -> {} -> {} -> {}".format(self.id,
                                                                   self.proveedor,
                                                                   self.telefono,
                                                                   self.direccion,
                                                                   self.cif,
                                                                   self.facturacion)

# Creamos esta clase para hacer la tabla con todos los productos a ser vendidos
class Registro_productos(db.Base):  # Herencia, desde db.py, para poder convertirla en tablas
    __tablename__ = "productos"  # Nombramos la primera tabla para almacenar los productos
    __table_args__ = {'sqlite_autoincrement' : True}  # Aquí ponemos el autoincremento para id de referencia-primary key
    id = Column(Integer, primary_key=True)  # Autoincremento para tener clasificados los productos
    # Importamos el id de proveedores
    id_proveedor = Column(Integer, ForeignKey("proveedores.id", ondelete="CASCADE"), nullable=False)
    proveedor = relationship("Registro_proveedores") # Relación para obtener la información del proveedor
    nombre = Column(String(200), nullable=False)  # No puede ser None
    tipo = Column(String(200), nullable=False)
    cantidad = Column(Integer, nullable=False)
    cantidad_requerida = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    iva = Column(Float, nullable=False)
    descuento = Column(Float, nullable=False)
    precio_descontado = Column(Float) # No le indico nullable=False porque puede estar vacío
    dimension = Column(String(200), nullable=False)
    lugar = Column(String(200), nullable=False)


    # Constructor de la clase "Registro_productos"
    def __init__(self, nombre, tipo, cantidad, cantidad_requerida, precio, iva, descuento, precio_descontado, dimension, lugar, proveedor, id_proveedor):
        self.nombre = nombre
        self.tipo = tipo
        self.cantidad = cantidad
        self.cantidad_requerida = cantidad_requerida
        self.precio = precio
        self.iva = iva
        self.descuento = descuento
        self.precio_descontado = precio_descontado
        self.dimension = dimension
        self.lugar = lugar
        self.proveedor = proveedor
        self.id_proveedor = id_proveedor

    # Comprobación de que todos los elementos existen
    def __str__(self):
        return "Producto {} -> {} -> {} -> {} -> {} -> {} -> {} -> {} -> {} -> {} -> {} -> {} -> {}".format(self.id,
                                                                                                      self.nombre,
                                                                                                      self.tipo,
                                                                                                      self.cantidad,
                                                                                                      self.cantidad_requerida,
                                                                                                      self.precio,
                                                                                                      self.iva,
                                                                                                      self.descuento,
                                                                                                      self.precio_descontado,
                                                                                                      self.dimension,
                                                                                                      self.lugar,
                                                                                                      self.proveedor,
                                                                                                      self.id_proveedor)

# Clase creada para llevar el registro de las ventas que se produzcan
class Facturacion(db.Base):
    __tablename__ = "facturacion"  # Nombramos la segunda tabla para almacenar las ventas
    __table_args__ = {'sqlite_autoincrement': True}  # Aquí ponemos el autoincremento para id de referencia-primary key
    id = Column(Integer, primary_key=True)  # Autoincremento para tener clasificadas las compras
    nombre = Column(String(200), nullable=False)
    direccion = Column(String(200), nullable=False)

    # Constructor de la clase "Registro_ventas"
    def __init__(self, nombre, direccion):
        self.nombre = nombre
        self.direccion = direccion

    # Comprobación de que todos los elementos existen
    def __str__(self):
        return "Compra {} -> {} -> {}".format(self.id,self.nombre, self.direccion)

# Clase creada para llevar el detalle del registro de cada una de las ventas que se produzcan
class Facturacion_detalle(db.Base):
    __tablename__ = "facturacion_detalle"  # Nombramos la tercera tabla para almacenar el detalle de las ventas
    __table_args__ = {'sqlite_autoincrement': True}  # Aquí ponemos el autoincremento para id de referencia-primary key
    id = Column(Integer, primary_key=True)  # Autoincremento para tener clasificadas las compras
    # Importamos el id de la venta
    id_factura = Column(Integer, ForeignKey("facturacion.id", ondelete="CASCADE"), nullable=False)
    factura = relationship("Facturacion") # Relación para obtener la información de la venta
    # Importamos el id de productos
    id_producto = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    producto = relationship("Registro_productos") # Relación para obtener la información de los productos
    cantidad = Column(Integer, nullable=False)
    valor = Column(Float, nullable=False)

    # Constructor de la clase "Registro_ventas"
    def __init__(self, id_factura, id_producto, cantidad, valor):
        self.id_factura = id_factura
        self.id_producto = id_producto
        self.cantidad = cantidad
        self.valor = valor

    # Comprobación de que todos los elementos existen
    def __str__(self):
        return "Compra {} -> {} -> {} -> {} -> {} ->".format(self.id,
                                                             self.id_factura,
                                                             self.id_producto,
                                                             self.cantidad,
                                                             self.valor)

# Clase para crear en la base de datos una tabla con todos los usuarios y sus claves
class Claves(db.Base):  # Herencia, desde db.py, para poder convertirla en tablas
    __tablename__ = "claves"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    usuario = Column(String(200), nullable=False)  # No puede ser None
    clave = Column(String(200), nullable=False)
    perfil = Column(String(200), nullable=False)

    # Constructor de nuestra clase "Claves"
    def __init__(self, id, usuario, clave, perfil):
        self.id = id
        self.usuario = usuario
        self.clave = clave
        self.perfil = perfil

    # Comprobación de que todos los elementos existen
    def __str__(self):
        return "Acceso {} -> {} -> {} -> {}".format(self.id,
                                                    self.usuario,
                                                    self.clave,
                                                    self.perfil)

# Clase para crear la tabla temporal que nos guarde la cesta de la compra hasta que la compra se realice
class Cesta_temporal(db.Base):  # Herencia, desde db.py, para poder convertirla en tablas
    __tablename__ = "cesta"  # Nombramos la segunda tabla para almacenar los proveedores
    __table_args__ = {'sqlite_autoincrement' : True}  # Aquí ponemos el autoincremento para id de referencia-primary key
    id = Column(Integer, primary_key=True)  # Autoincremento para tener clasificados los proveedores
    # Importamos el id del producto
    id_producto = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"), nullable=False)
    producto = relationship("Registro_productos")  # Relación para obtener la información de los productos
    precio = Column(Float, nullable=False) # Precio incluido impuestos y descuento

    # Constructor de la clase "Cesta_temporal"
    def __init__(self, id_producto, precio):
        self.id_producto = id_producto
        self.precio = precio

    # Comprobación de que todos los elementos existen
    def __str__(self):
        return "Proveedor {} -> {} -> {}".format(self.id,
                                                 self.id_producto,
                                                 self.precio)