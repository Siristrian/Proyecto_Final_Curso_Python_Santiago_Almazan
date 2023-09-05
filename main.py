from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import db
from models import Registro_productos, Registro_proveedores, Facturacion, Facturacion_detalle, Claves, Cesta_temporal

db.Base.metadata.create_all(bind=db.engine) # Comando para actualizar las tablas en los modelos
app = Flask(__name__)  # En app se encuentra nuestro servidor web de Flask

# Creamos a la función 'home'
@app.route("/")
def home():
    # Variable "lista_de_productos" para que se nos de la información de todos los productos
    lista_de_productos = todos_los_productos()
    facturacion_proveedor()
    grafica = grafica_ventas()
    return render_template("index.html", productos=lista_de_productos, grafica=grafica)

# Función para poder reutilizar el código y poder llamar a todos los productos que tenemos
def todos_los_productos():
    lista_de_productos = db.session.query(Registro_productos).all()
    # Bucle para modificar los precios en el caso de haber un descuento en ellos
    for listado in lista_de_productos:
        descuento = (listado.precio * listado.descuento) / 100
        precio_descontado = round(listado.precio - descuento, 2)
        datos_producto = db.session.query(Registro_productos).filter(Registro_productos.id == listado.id)
        # Modificamos la información del precio_descontado en la base de datos
        datos_producto.update(dict(precio_descontado=precio_descontado))
        db.session.commit()
    return lista_de_productos

# Creamos la ruta para ingresar a la pantalla de login del proveedor
@app.route("/login_proveedores", methods=["GET"])
def login():
    return render_template("login.html")

# Ruta para poder validar las credenciales y acceder como proveedor
@app.route("/login_proveedores", methods=["POST"])
def login_proveedores():
    try:
        proveedor=request.form.get("proveedor")
        clave=request.form.get("clave")
        if proveedor == "":
            raise Exception("Error, usuario vacío")
        if clave == "":
            raise Exception("Error, clave vacía")
        proveedor_a_mostrar = db.session.query(Claves).filter(Claves.usuario.like(proveedor)).filter(Claves.clave.like(clave)).first()
        if proveedor_a_mostrar == None:
            raise Exception("Error, usuario o contraseña incorrectos")
        datos_proveedor = db.session.query(Registro_proveedores).filter(Registro_proveedores.proveedor==proveedor).first()
        todos_los_productos = info_productos(datos_proveedor.id)
        grafica = grafica_compras()  # mostramos la gráfica
        return render_template("proveedores.html", proveedor=proveedor, info_proveedor=datos_proveedor, lista_productos=todos_los_productos, grafica=grafica)
    except Exception as error:
        mensaje = {'error': error}
        return render_template("login.html", mensaje=mensaje)

# Función creada para poder obtener un listado de todos los productos de cada proveedor y mostrarlos
def info_productos(id_proveedor:int):
    return db.session.query(Registro_productos).filter(Registro_productos.id_proveedor==id_proveedor).all()

# Función para buscar los datos del producto por el id
def info_producto(id_producto:int):
    return db.session.query(Registro_productos).filter(Registro_productos.id==id_producto).first()

# Función creada para poder obtener un listado de todos los proveedores
def info_proveedor(id_proveedor):
    return db.session.query(Registro_proveedores).filter(Registro_proveedores.id==id_proveedor).first()

# Ruta y función para mostrar la información del proveedor
@app.route("/info_proveedor/<int:id>", methods=["GET"])
def proveedor(id):
    proveedor_a_mostrar = info_proveedor(id)
    return render_template("editar_proveedor.html", proveedor=proveedor_a_mostrar)

# Ruta y función para actualizar la información del proveedor
@app.route("/info_proveedor", methods=["POST"])
def proveedor_actualizado():
    # Establecemos los campos de la tabla a poder ser modificados en este apartado
    id = request.form.get("id")
    direccion = request.form.get("direccion")
    telefono = request.form.get("telefono")
    cif = request.form.get("cif")
    # Filtramos la tabla de proveedores por el id
    datos_proveedor = db.session.query(Registro_proveedores).filter(Registro_proveedores.id == id)
    # Modificamos la información del proveedor en la base de datos
    datos_proveedor.update(dict(telefono=telefono, direccion=direccion, cif=cif))
    db.session.commit()  # Guardamos los cambios realizados
    # Leemos nuevamente la información modificada
    proveedor = datos_proveedor.first()
    todos_los_productos = info_productos(proveedor.id)
    grafica = grafica_compras()  # mostramos la gráfica
    return render_template("proveedores.html", info_proveedor=proveedor, lista_productos=todos_los_productos, grafica=grafica)

# Ruta y función para mostrar la información del producto
@app.route("/info_producto/<int:id>", methods=["GET"])
def producto(id):
    producto_a_mostrar = info_producto(id)
    return render_template("editar_productos.html", producto=producto_a_mostrar)

# Ruta y función para actualizar la información del producto
@app.route("/info_producto", methods=["POST"])
def producto_actualizado():
    # Establecemos los campos de la tabla a poder ser modificados en este apartado
    id = request.form.get("id")
    nombre = request.form.get("nombre")
    tipo = request.form.get("tipo")
    cantidad = request.form.get("cantidad")
    cantidad_requerida = request.form.get("cantidad_requerida")
    precio = request.form.get("precio")
    iva = request.form.get("iva")
    descuento = request.form.get("descuento")
    dimension = request.form.get("dimension")
    lugar = request.form.get("lugar")
    # Filtramos la tabla de proveedores por el id
    datos_producto = db.session.query(Registro_productos).filter(Registro_productos.id == id)
    datos_producto.update(dict(nombre=nombre,
                               tipo=tipo,
                               cantidad=cantidad,
                               cantidad_requerida=cantidad_requerida,
                               precio=precio,
                               iva=iva,
                               descuento=descuento,
                               dimension=dimension,
                               lugar=lugar))  # Modificamos la información del proveedor en la base de datos
    db.session.commit()  # Guardamos los cambios realizados
    # Leemos nuevamente la información modificada
    producto=datos_producto.first()
    todos_los_productos = info_productos(producto.id_proveedor)
    proveedor=info_proveedor(producto.id_proveedor)
    grafica = grafica_compras()  # mostramos la gráfica
    return render_template("proveedores.html", info_proveedor=proveedor, lista_productos=todos_los_productos, grafica=grafica)

# Ruta y función para que el administrador se loguee y tenga acceso a toda la información
@app.route("/login_admin", methods=["GET"])
def login_admin():
    return render_template("login_admin.html")

# Ruta para poder validar las credenciales y acceder como proveedor
@app.route("/login_admin", methods=["POST"])
def login_administrador():
    try:
        administrador=request.form.get("administrador")
        clave=request.form.get("clave")
        if administrador == "":
            raise Exception("Error, usuario vacío")
        if clave == "":
            raise Exception("Error, clave vacía")
        administrador_a_mostrar = db.session.query(Claves).filter(Claves.usuario.like(administrador)).filter(Claves.clave.like(clave)).first()
        if administrador_a_mostrar == None:
            raise Exception("Error, usuario o contraseña incorrectos")
        datos_proveedor = db.session.query(Registro_proveedores).all()
        todos_los_productos = db.session.query(Registro_productos).all()
        return render_template("admin.html", administrador=administrador, administrador_a_mostrar=administrador_a_mostrar, info_proveedor=datos_proveedor, lista_productos=todos_los_productos)
    except Exception as error:
        mensaje = {'error': error}
        return render_template("login_admin.html", mensaje=mensaje)

# Ruta y función para mostrar la información de los proveedores al administrador
@app.route("/info_proveedores_admin/<int:id>", methods=["GET"])
def proveedor_admin(id):
    proveedor_a_mostrar = info_proveedor(id)
    return render_template("editar_proveedor_admin.html", proveedor=proveedor_a_mostrar)

# Ruta y función para actualizar la información de los proveedores por el administrador
@app.route("/info_proveedores_admin", methods=["POST"])
def proveedor_actualizado_admin():
    # Establecemos los campos de la tabla a poder ser modificados en este apartado
    id = request.form.get("id")
    direccion = request.form.get("direccion")
    telefono = request.form.get("telefono")
    cif = request.form.get("cif")
    # Filtramos la tabla de proveedores por el id
    datos_proveedor = db.session.query(Registro_proveedores).filter(Registro_proveedores.id == id)
    # Modificamos la información del proveedor en la base de datos
    datos_proveedor.update(dict(telefono=telefono, direccion=direccion, cif=cif))
    db.session.commit()  # Guardamos los cambios realizados
    # Leemos nuevamente la información modificada
    proveedor = db.session.query(Registro_proveedores).all()
    todos_los_productos = db.session.query(Registro_productos).all()
    return render_template("admin.html", info_proveedor=proveedor, lista_productos=todos_los_productos)

# Ruta y función para mostrar la información del producto seleccionado para editar por el administrador
@app.route("/info_productos_admin/<int:id>", methods=["GET"])
def producto_admin(id):
    producto_a_mostrar = info_producto(id)
    return render_template("editar_productos_admin.html", producto=producto_a_mostrar)

# Ruta y función para actualizar la información del producto editado por el administrador
@app.route("/info_productos_admin", methods=["POST"])
def producto_actualizado_admin():
    # Establecemos los campos de la tabla a poder ser modificados en este apartado
    id = request.form.get("id")
    nombre = request.form.get("nombre")
    tipo = request.form.get("tipo")
    cantidad = request.form.get("cantidad")
    cantidad_requerida = request.form.get("cantidad_requerida")
    precio = request.form.get("precio")
    iva = request.form.get("iva")
    descuento = request.form.get("descuento")
    dimension = request.form.get("dimension")
    lugar = request.form.get("lugar")
    # Filtramos la tabla de proveedores por el id
    datos_producto = db.session.query(Registro_productos).filter(Registro_productos.id == id)
    datos_producto.update(dict(nombre=nombre,
                               tipo=tipo,
                               cantidad=cantidad,
                               cantidad_requerida=cantidad_requerida,
                               precio=precio,
                               iva=iva,
                               descuento=descuento,
                               dimension=dimension,
                               lugar=lugar))  # Modificamos la información del proveedor en la base de datos
    db.session.commit()  # Guardamos los cambios realizados
    # Leemos nuevamente la información modificada
    datos_proveedor = db.session.query(Registro_proveedores).all()
    todos_los_productos = db.session.query(Registro_productos).all()
    return render_template("admin.html", info_proveedor=datos_proveedor, lista_productos=todos_los_productos)

# Ruta y función para que el acceso al carrito de la compra, donde se muestra lo que tenemos en el carrito
@app.route("/carro_compra", methods=["GET"])
def carro_compra():
    cesta = db.session.query(Cesta_temporal).all()  # mostramos los productos en la cesta temporal
    total_precio = 0
    for datos in cesta:
        total_precio += datos.producto.precio_descontado
    total_precio = round(total_precio, 2)
    return render_template("carro_compra.html", cesta=cesta, total_cesta=total_precio)

# Ruta y función para crear la cesta temporal, en la que se inserta el producto
@app.route("/carro_compra/<int:id>", methods=["GET"])
def agregar_cesta(id):
    producto=info_producto(id) # Obtenemos los datos del producto
    precio=producto.precio_descontado # Obtenemos el precio del producto según su id
    cesta = Cesta_temporal(id_producto=id, precio=precio)
    db.session.add(cesta) # Añadimos el objeto cesta a la cesta temporal a la espera de que se realice la compra
    db.session.commit() # Guardamos
    cesta=db.session.query(Cesta_temporal).all() # mostramos los productos en la cesta temporal
    total_precio=0
    for datos in cesta:
        total_precio += datos.producto.precio_descontado
    total_precio = round(total_precio, 2)
    return render_template("carro_compra.html", cesta=cesta, total_cesta=total_precio)

# Función para eliminar todos los elemntos de la tabla "cesta" y poder reutilizarla
def eliminar_toda_la_cesta():
    db.session.query(Cesta_temporal).delete()  # Eliminamos los elementos
    db.session.commit()  # Guardamos los cambios

# Función y Ruta para eliminar todos los elementos del carro de compra cuando le damos al botón de eliminar
@app.route("/eliminar_carro", methods=["GET"])
def eliminar_cesta():
    eliminar_toda_la_cesta()
    return home() # Nos devuelve a nuestro "home"

# Función y ruta para comprar todos los productos y eliminarlos de la cesta temporal
@app.route("/compra", methods=["POST"])
def compra():
    try:
        # Recuperamos los datos de nombre y direccion del formulario en nuestro HTML, con la etiqueta "name"
        nombre = request.form.get("nombre")
        direccion = request.form.get("direccion")
        facturacion=Facturacion(nombre=nombre, direccion=direccion)
        db.session.add(facturacion) # Añadimos la información
        db.session.flush() # Refrescamos los cambios producidos en el objeto
        # Traemos los productos y los agrupamos para poder contarlo en la tabla de Facturacion_detalle
        grupo_productos=db.session.query(Cesta_temporal.id_producto, Cesta_temporal.precio, func.count(Cesta_temporal.id_producto)).group_by(Cesta_temporal.id_producto).all()
        id_facturacion = facturacion.id
        for productos in grupo_productos:
            # Realizamos la resta de productos que se compran
            datos_producto=db.session.query(Registro_productos).filter(Registro_productos.id==productos[0]).first()
            total_stock=datos_producto.cantidad
            iva=datos_producto.iva
            valor_iva=(productos[1]*iva)/100
            valor_sin_iva=round(productos[1]-valor_iva, 2)
            if total_stock < productos[2]:
                raise Exception("Error, no hay stock suficiente")
            else:
                cantidad_actualizada=total_stock - productos[2]
                db.session.query(Registro_productos).filter(Registro_productos.id==productos[0]).update(dict(cantidad=cantidad_actualizada))
            # Creamos la variable "detalle" para completar los campos de la tabla "Facturacion_detalle"
            detalle=Facturacion_detalle(id_factura=id_facturacion, id_producto=productos[0], valor=valor_sin_iva, cantidad=productos[2])
            db.session.add(detalle) # Añadimos a la tabla la información
        db.session.commit()  # Guardamos los cambios
        eliminar_toda_la_cesta()
        return home() # Nos devuelve a nuestro "home"
    except Exception as error:
        mensaje = {'error': error}
        return render_template("carro_compra.html", mensaje=mensaje)

# Función para sumar el valor de cada producto comprado para que se sepa la cantidad que factura el proveedor
def facturacion_proveedor():
    # Agrupamos en una suma el valor de lo que se ha vendido por cada producto
    valor_facturacion = db.session.query(Facturacion_detalle.id_producto, func.sum(Facturacion_detalle.valor)).group_by(Facturacion_detalle.id_producto).all()
    for facturacion in valor_facturacion: # Iteramos para obtener la información total de cada producto
        id_producto = facturacion[0] # Obtenemos el id del producto
        valor = facturacion[1] # Obtenemos la suma de los valores vendidos por el producto
        datos_producto = info_producto(id_producto) # Obtenemos la información del producto para saber quién es el proveedor
        # Actualizamos el campo facturacion para que cada proveedor sepa la cantidad que obtuvo de ganancias, tras restar iva y descuentos
        db.session.query(Registro_proveedores).filter(Registro_proveedores.id==datos_producto.id_proveedor).update(dict(facturacion=valor))
        db.session.commit() # Guardamos los cambios

# Función para crear la gráfica que muestre a los compradores los productos que son vendidos
def grafica_ventas():
    fig, ax = plt.subplots()

    # Obtenemos un listado de los productos vendidos
    productos_vendidos = db.session.query(Facturacion_detalle.id_producto, func.count(Facturacion_detalle.id_producto)).group_by(Facturacion_detalle.id_producto).all()
    lista_id_productos_vendidos = []
    lista_cantidad = []
    for productos in productos_vendidos:
        lista_id_productos_vendidos.append(productos[0])
        lista_cantidad.append(productos[1])

    ax.bar(lista_id_productos_vendidos, lista_cantidad)

    ax.set_ylabel('Cantidad vendida por producto')
    ax.set_xlabel('Cantidad de productos vendidos')
    ax.set_title('Productos vendidos')

    # Convertimos la gráfica en una imagen
    img = BytesIO() # Creamos una imagen vacía
    plt.savefig(img, format='png') # Guardamos la gráfica en la imagen previa
    plt.close() # Cerramos Matplotlib
    img.seek(0) # Cerramos la imagen
    plot_url = base64.b64encode(img.getvalue()).decode('utf8') # Codificamos la imagen para poder mostrarla en el html

    return plot_url # Retornamos la gráfica codificada

# Función que muestre a los proveedores cuáles de sus productos son los más comprados
def grafica_compras():
    fig, ax = plt.subplots()

    # Obtenemos un listado de los productos vendidos
    productos_vendidos = db.session.query(Facturacion_detalle.id_producto, func.count(Facturacion_detalle.id_producto)).group_by(Facturacion_detalle.id_producto).all()
    lista_id_productos_vendidos = []
    lista_cantidad = []
    for productos in productos_vendidos:
        lista_id_productos_vendidos.append(productos[0])
        lista_cantidad.append(productos[1])

    ax.bar(lista_id_productos_vendidos, lista_cantidad)

    ax.set_ylabel('Cantidad vendida por producto')
    ax.set_title('Productos vendidos')
    ax.legend(title='Cantidad de productos vendidos')

    # Convertimos la gráfica en una imagen
    img = BytesIO()  # Creamos una imagen vacía
    plt.savefig(img, format='png')  # Guardamos la gráfica en la imagen previa
    plt.close()  # Cerramos Matplotlib
    img.seek(0)  # Cerramos la imagen
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')  # Codificamos la imagen para poder mostrarla en el html

    return plot_url  # Retornamos la gráfica codificada

# Función principal
if __name__ == "__main__":
    db.Base.metadata.create_all(db.engine)
    app.run(debug=True)  # El método 'app.run' nos inicia el servidor web