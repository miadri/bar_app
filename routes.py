from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from app.models import RolLogin, Pedido, Producto, Mesa, Inventario, InventarioSede, Estado, Sede, DetallePedido, db, Usuario, Venta
from datetime import datetime

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def index():
    return render_template('index.html')

@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contraseña = request.form['contraseña']

        # Verificar las credenciales del usuario en la base de datos
        user = RolLogin.query.filter_by(nombre=nombre).first()

        if user and user.check_password(contraseña):
            # Las credenciales son válidas, guardar el rol del usuario en la sesión
            session['rol'] = user.rol
            session['SedeID'] = user.SedeID  # Agregar el ID de la sede a la sesión

            # Redirigir al usuario en función de su rol
            if user.rol == 'Administrador':
                return redirect(url_for('routes.admin_panel'))
            elif user.rol == 'Mesero':
                return redirect(url_for('routes.gestion_mesas'))
            elif user.rol == 'Cajero':
                return redirect(url_for('routes.facturar'))
        else:
            # Las credenciales son inválidas, mostrar un mensaje de error
            error_message = 'Nombre de usuario o contraseña incorrectos'
            flash(error_message, 'error')
            return redirect(url_for('routes.login'))  # Redirigir de nuevo al formulario de inicio de sesión
    else:
        # Si el método de solicitud es GET, simplemente renderizar el formulario de inicio de sesión
        return render_template('login.html')


        
@routes_bp.route('/gestion_mesas', methods=['GET', 'POST'])
def gestion_mesas():
    if session.get('rol') != 'Mesero':
        flash('No tienes permisos para ver esta página', 'error')
        return redirect(url_for('routes.index'))

    if request.method == 'POST':
        # Procesar la creación del pedido
        mesa_id = request.form.get('mesa_id')
        productos = request.form.getlist('producto_id')
        cantidades = request.form.getlist('cantidad')

        # Validar que se haya seleccionado al menos un producto
        if not productos:
            flash('Debe seleccionar al menos un producto para crear un pedido', 'error')
            return redirect(url_for('routes.gestion_mesas'))

        # Crear el pedido en la base de datos
        nuevo_pedido = Pedido(MesaID=mesa_id, Estado='activo')
        db.session.add(nuevo_pedido)
        db.session.commit()

        for producto_id, cantidad in zip(productos, cantidades):
            nuevo_detalle_pedido = DetallePedido(PedidoID=nuevo_pedido.PedidoID, ProductoID=producto_id, Cantidad=cantidad)
            db.session.add(nuevo_detalle_pedido)

        db.session.commit()

        flash('Pedido creado exitosamente', 'success')
        return redirect(url_for('routes.gestion_mesas'))
    else:
        # Obtener la sede del usuario desde la sesión
        sede_usuario = Sede.query.get(session.get('SedeID'))

        if sede_usuario:
            # Obtener las mesas de la sede del usuario
            mesas_usuario = Mesa.query.filter_by(SedeID=sede_usuario.SedeID).all()

            # Obtener los productos disponibles en la sede del usuario
            productos = db.session.query(Producto, Inventario.Cantidad) \
                .join(Inventario, Producto.ProductoID == Inventario.ProductoID) \
                .filter(Inventario.SedeID == sede_usuario.SedeID) \
                .all()

            return render_template('gestion_mesas.html', sede=sede_usuario, mesas=mesas_usuario, productos=productos)
        else:
            # Manejar el caso donde no se encuentra la sede del usuario
            flash('No se pudo encontrar la sede del usuario', 'error')
            return redirect(url_for('routes.index'))


@routes_bp.route('/obtener_pedido_actual', methods=['GET'])
def obtener_pedido_actual():
    # Obtener el ID de la mesa del usuario desde la sesión
    mesa_id = session.get('mesa_id')

    # Buscar el último pedido activo para la mesa actual
    pedido_actual = Pedido.query.filter_by(MesaID=mesa_id, Estado='activo').order_by(Pedido.PedidoID.desc()).first()

    if pedido_actual:
        # Si se encuentra un pedido activo, obtener los detalles del pedido
        detalles_pedido = DetallePedido.query.filter_by(PedidoID=pedido_actual.PedidoID).all()

        # Crear una lista para almacenar los detalles del pedido
        detalles_pedido_json = []
        for detalle in detalles_pedido:
            detalles_pedido_json.append({
                'producto_id': detalle.ProductoID,
                'cantidad': detalle.Cantidad
                # Puedes agregar más detalles según sea necesario
            })

        # Construir el objeto JSON del pedido actual
        pedido_actual_json = {
            'pedido_id': pedido_actual.PedidoID,
            'detalles_pedido': detalles_pedido_json
            # Puedes agregar más detalles del pedido según sea necesario
        }

        return jsonify(pedido_actual_json)
    else:
        # Si no se encuentra ningún pedido activo para la mesa actual, devolver un mensaje indicando lo mismo
        return jsonify({'message': 'No hay pedido activo para esta mesa'})

@routes_bp.route('/eliminar_producto', methods=['POST'])
def eliminar_producto():
    data = request.json
    producto_id = data.get('producto_id')
    mesa_id = session.get('mesa_id')

    # Buscar el pedido actual para la mesa actual
    pedido_actual = Pedido.query.filter_by(MesaID=mesa_id, Estado='activo').first()

    if pedido_actual:
        # Eliminar el detalle del pedido correspondiente al producto
        detalle_pedido = DetallePedido.query.filter_by(PedidoID=pedido_actual.PedidoID, ProductoID=producto_id).first()
        if detalle_pedido:
            db.session.delete(detalle_pedido)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Producto eliminado del pedido correctamente'}), 200
        else:
            return jsonify({'error': 'El producto no se encuentra en el pedido actual'}), 404
    else:
        return jsonify({'error': 'No hay pedido activo para esta mesa'}), 404


@routes_bp.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    data = request.json
    mesa_id = int(data.get('mesa_id'))  # Convertir mesa_id a entero
    usuario_id = session.get('usuario_id')
    nombre_cliente = data.get('nombre_cliente')
    cliente_id = data.get('cliente_id')
    productos = data.get('productos')
    # Verificar si la variable productos es una lista válida
    if not isinstance(productos, list) or len(productos) == 0:
        return jsonify({'error': 'No se proporcionaron productos válidos'}), 400

    # Buscar el pedido actual para la mesa actual
    pedido_actual = Pedido.query.filter_by(MesaID=mesa_id, Estado='activo').first()

    if pedido_actual:
        # Actualizar el pedido actual con los nuevos productos
        for producto in productos:
            producto_id = producto.get('producto_id')
            cantidad = producto.get('cantidad')
            valor_venta = producto.get('valor_venta')

            nuevo_detalle_pedido = DetallePedido(
                pedido_id=pedido_actual.PedidoID,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=valor_venta,
                valor_total=valor_venta * cantidad
            )
            db.session.add(nuevo_detalle_pedido)

            # Actualizar los valores del pedido
            pedido_actual.Valor_bruto += nuevo_detalle_pedido.valor_total
            pedido_actual.Valor_venta += nuevo_detalle_pedido.valor_total
            pedido_actual.Valor_total = pedido_actual.Valor_venta

        # Si el pedido se ha pagado, crear una nueva entrada en la tabla "Ventas"
        if pedido_actual.Estado == 'pagado':
            nueva_venta = Venta(PedidoID=pedido_actual.PedidoID, ValorTotal=pedido_actual.Valor_total)
            db.session.add(nueva_venta)

        db.session.commit()

        return jsonify({'success': True, 'message': 'Productos agregados al pedido correctamente'}), 200
    else:
        # Crear un nuevo pedido
        nuevo_pedido = Pedido(
            MesaID=mesa_id,
            UsuarioID=usuario_id,
            FechaHora=datetime.utcnow(),
            NombreCliente=nombre_cliente,
            ClienteID=cliente_id,
            Estado='activo'
        )
        db.session.add(nuevo_pedido)
        db.session.flush()  # Generar el valor de PedidoID

        for producto in productos:
            producto_id = producto.get('producto_id')
            cantidad = producto.get('cantidad')
            valor_venta = producto.get('valor_venta')

            nuevo_detalle_pedido = DetallePedido(
                pedido_id=nuevo_pedido.PedidoID,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=valor_venta,
                valor_total=valor_venta * cantidad
            )
            db.session.add(nuevo_detalle_pedido)

            # Actualizar los valores del pedido
            nuevo_pedido.Valor_bruto += nuevo_detalle_pedido.valor_total
            nuevo_pedido.Valor_venta += nuevo_detalle_pedido.valor_total
            nuevo_pedido.Valor_total = nuevo_pedido.Valor_venta

        db.session.commit()

        return jsonify({'success': True, 'message': 'Pedido creado exitosamente', 'pedido_id': nuevo_pedido.PedidoID}), 200


@routes_bp.route('/admin_panel', methods=['GET'])
def admin_panel():
    # Aquí puedes agregar la lógica para la página del panel de administración
    return render_template('admin_panel.html')




def obtener_pedidos_activos():
    pedidos = Pedido.query.filter_by(Estado='activo').all()
    resultado = []
    for pedido in pedidos:
        print("Pedido:", pedido)
        print("Pedido ID:", pedido.PedidoID)
        print("Mesa ID:", pedido.MesaID)
        print("Valor Total:", pedido.Valor_total)  # Verificar el valor de Valor_total

        # Verificar si Valor_total es nulo o undefined
        if pedido.Valor_total is not None:
            # Asignar el valor total del pedido
            valor_total = float(pedido.Valor_total)
        else:
            # Manejar el caso cuando Valor_total es nulo o undefined
            valor_total = None

        resultado.append({
            'pedido_id': pedido.PedidoID,
            'mesa_id': pedido.MesaID,
            'usuario_id': pedido.UsuarioID,
            'fecha_hora': pedido.FechaHora,
            'producto_id': pedido.ProductoID,
            'cantidad': pedido.Cantidad,
            'estado': pedido.Estado,
            'valor_bruto': float(pedido.Valor_bruto),
            'ValorVenta': float(pedido.ValorVenta),
            'valor_total': valor_total  # Pasar el valor total correctamente
        })

    return resultado

@routes_bp.route('/facturar')
def facturar():
    if session.get('rol') == 'Cajero':
        usuario = {
            'nombre': session.get('nombre'),
            'sede': {'nombre': session.get('sede_nombre')}
        }

        lista_pedidos = obtener_pedidos_activos()
        print("Lista de pedidos activos:", lista_pedidos)

        return render_template('facturar.html', usuario=usuario, lista_pedidos=lista_pedidos)
    else:
        return redirect(url_for('routes.index'))

    


@routes_bp.route('/seleccionar_mesa', methods=['POST'])
def seleccionar_mesa():
    data = request.get_json()
    mesa_id = data['mesa_id']

    # Actualizar el estado de la mesa a 'ocupada'
    mesa = Mesa.query.get(mesa_id)
    if mesa:
        mesa.Estado = 'ocupada'
        db.session.commit()

        # Puedes agregar aquí la lógica para cambiar el color de la mesa en el frontend
        # Por ejemplo, retornar un mensaje indicando que la mesa ha sido seleccionada
        return jsonify({'success': True, 'message': f'Mesa {mesa.Numero} seleccionada y ocupada'})
    else:
        return jsonify({'error': 'No se encontró la mesa especificada'}), 404
    
@routes_bp.route('/pedidos', methods=['POST'])
def crear_pedido():
    data = request.get_json()
    mesa_id = data['mesa_id']
    productos = data['productos']  # Asegúrate de que el JSON enviado incluya una lista de productos

    # Validar que se hayan seleccionado productos
    if not productos:
        return jsonify({'error': 'Debe seleccionar al menos un producto para crear un pedido'}), 400

    # Crear el pedido
    nuevo_pedido = Pedido(MesaID=mesa_id, Estado='activo')
    db.session.add(nuevo_pedido)
    db.session.commit()

    # Agregar los productos al pedido
    for producto in productos:
        producto_id = producto['ProductoID']
        cantidad = producto['Cantidad']
        nuevo_detalle_pedido = DetallePedido(PedidoID=nuevo_pedido.PedidoID, ProductoID=producto_id, Cantidad=cantidad)
        db.session.add(nuevo_detalle_pedido)

    db.session.commit()

    return jsonify({'success': True, 'message': 'Pedido creado exitosamente'})

# READ: Obtener todos los pedidos activos
#@routes_bp.route('/pedidos', methods=['GET'])
#def obtener_pedidos_activos():
 #   pedidos = Pedido.query.filter_by(Estado='activo').all()
  #  resultado = []
   # for pedido in pedidos:
    #    detalles_pedido = DetallePedido.query.filter_by(PedidoID=pedido.PedidoID).all()
     #   productos = [{'ProductoID': detalle.ProductoID, 'Cantidad': detalle.Cantidad} for detalle in detalles_pedido]
      #  resultado.append({
       #     'id': pedido.PedidoID,
        #    'mesa_id': pedido.MesaID,
         #   'productos': productos,
          #  'estado': pedido.Estado
       # })
    #return jsonify({'pedidos_activos': resultado})

# UPDATE: Actualizar el estado de un pedido
@routes_bp.route('/pedidos/<int:id>', methods=['PUT'])
def actualizar_estado_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    data = request.get_json()
    nuevo_estado = data['estado']

    if nuevo_estado == 'finalizado':
        # Realizar acciones adicionales al finalizar el pedido
        # (por ejemplo, descontar el inventario, generar factura, etc.)
        pass

    pedido.Estado = nuevo_estado
    db.session.commit()

    return jsonify({'success': True, 'message': 'Estado del pedido actualizado exitosamente'})

# DELETE: Cancelar un pedido
@routes_bp.route('/pedidos/<int:id>', methods=['DELETE'])
def cancelar_pedido(id):
    pedido = Pedido.query.get_

# Modificar la consulta para obtener el inventario de una sede específica
def obtener_inventario_por_sede(sede_id):
    inventario_sede = db.session.query(Inventario).join(InventarioSede).filter(InventarioSede.SedeID == sede_id).all()
    return inventario_sede

# Ejemplo de cómo agregar una relación entre una sede y un elemento de inventario
def agregar_inventario_a_sede(sede_id, inventario_id):
    nueva_relacion = InventarioSede(SedeID=sede_id, InventarioID=inventario_id)
    db.session.add(nueva_relacion)
    db.session.commit()




# Ruta para registrar nuevos usuarios
@routes_bp.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    nombre = datos.get('nombre')
    contraseña = datos.get('contraseña')
    rol = datos.get('rol')
    sede_id = datos.get('sede_id')

    # Cifrar la contraseña antes de guardarla
    contraseña_cifrada = generar_hash(contraseña)

    nuevo_usuario = RolLogin(nombre=nombre, contraseña=contraseña_cifrada, rol=rol, SedeID=sede_id)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'mensaje': 'Usuario registrado correctamente'})

# Ruta para cambiar contraseñas de usuarios existentes
@routes_bp.route('/cambiar_contraseña', methods=['PUT'])
def cambiar_contraseña():
    datos = request.get_json()
    usuario_id = datos.get('usuario_id')
    contraseña_actual = datos.get('contraseña_actual')
    nueva_contraseña = datos.get('nueva_contraseña')

    usuario = RolLogin.query.get(usuario_id)
    if usuario and usuario.check_password(contraseña_actual):
        nueva_contraseña_cifrada = generar_hash(nueva_contraseña)
        usuario.contraseña = nueva_contraseña_cifrada
        db.session.commit()
        return jsonify({'mensaje': 'Contraseña actualizada correctamente'})
    else:
        return jsonify({'error': 'Contraseña actual incorrecta'}), 401

# Ruta para cambiar el estado de las mesas
@routes_bp.route('/cambiar_estado_mesa', methods=['PUT'])
def cambiar_estado_mesa():
    datos = request.get_json()
    mesa_id = datos.get('mesa_id')
    nuevo_estado = datos.get('nuevo_estado')

    mesa = Mesa.query.get(mesa_id)
    if mesa:
        mesa.Estado = nuevo_estado
        db.session.commit()
        return jsonify({'mensaje': 'Estado de la mesa actualizado correctamente'})
    else:
        return jsonify({'error': 'Mesa no encontrada'}), 404

# Ruta para agregar nuevos productos al inventario
@routes_bp.route('/agregar_producto_inventario', methods=['POST'])
def agregar_producto_inventario():
    datos = request.get_json()
    producto_id = datos.get('producto_id')
    cantidad = datos.get('cantidad')
    proveedor = datos.get('proveedor')
    sede_id = datos.get('sede_id')

    nuevo_inventario = Inventario(ProductoID=producto_id, Cantidad=cantidad, Proveedor=proveedor)
    db.session.add(nuevo_inventario)
    db.session.flush()  # Generar el valor de InventarioID

    nueva_relacion = InventarioSede(InventarioID=nuevo_inventario.InventarioID, SedeID=sede_id)
    db.session.add(nueva_relacion)
    db.session.commit()

    return jsonify({'mensaje': 'Producto agregado al inventario correctamente'})

# Ruta para obtener las ventas/pedidos filtrados por fecha
@routes_bp.route('/obtener_ventas_por_fecha', methods=['GET'])
def obtener_ventas_por_fecha():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    ventas = Venta.query.join(Pedido).filter(Pedido.FechaHora >= fecha_inicio, Pedido.FechaHora <= fecha_fin).all()

    resultados = []
    for venta in ventas:
        pedido = venta.Pedido
        resultados.append({
            'id_venta': venta.VentaID,
            'id_pedido': pedido.PedidoID,
            'fecha_hora': pedido.FechaHora.isoformat(),
            'valor_total': float(pedido.Valor_total),
            # Agrega otros campos necesarios
        })

    return jsonify(resultados)

# Función auxiliar para cifrar contraseñas
from werkzeug.security import generate_password_hash

def generar_hash(contraseña):
    return generate_password_hash(contraseña)
    


    