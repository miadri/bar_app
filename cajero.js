// No necesitamos simular datos, los obtendremos desde el backend

// Obtener la referencia a la tabla
const pedidosTable = document.getElementById('pedidosTable');

// Función para renderizar los pedidos en la tabla
function renderizarPedidos(pedidos) {
    const tbody = pedidosTable.getElementsByTagName('tbody')[0];
    tbody.innerHTML = ''; // Limpiar la tabla antes de renderizar los pedidos

    pedidos.forEach(pedido => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${pedido.PedidoID}</td>
            <td>${pedido.MesaID}</td>
            <td>${pedido.UsuarioID}</td>
            <td>${pedido.FechaHora}</td>
            <td>${pedido.ProductoID}</td>
            <td>${pedido.Cantidad}</td>
            <td>${pedido.Estado}</td>
            <td>${pedido.ValorBruto}</td>
            <td>${pedido.ValorVenta}</td>
            <td>${pedido.ValorTotal}</td>
            <td>
                <button class="btn btn-danger" onclick="cancelarPedido(${pedido.PedidoID})">Cancelar Pedido</button>
                <button class="btn btn-success" onclick="pagarPedido(${pedido.PedidoID})">Pagar Pedido</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Función para cancelar un pedido
function cancelarPedido(pedidoID) {
    const pedidosTable = document.getElementById('pedidosTable');
    if (pedidosTable) {
        const filas = pedidosTable.getElementsByTagName('tr');
        for (let i = 0; i < filas.length; i++) {
            const fila = filas[i];
            const primeraColumna = fila.cells[0].textContent;
            if (primeraColumna === pedidoID.toString()) {
                fila.remove();
                break;
            }
        }
    }
}

// Función para pagar un pedido
function pagarPedido(pedidoID) {
    // Lógica para pagar el pedido (normalmente una llamada al backend)
    console.log(`Pagando pedido ${pedidoID}`);
    // Actualizar el estado del pedido en la tabla
    const row = pedidosTable.querySelector(`tr td:first-child:contains(${pedidoID})`).parentNode;
    row.cells[6].textContent = 'pagado';
}

// Función para abrir la ventana modal de pago
function abrirModalPago(pedido) {
    console.log('Abriendo modal de pago para el pedido:', pedido);
    const modal = document.getElementById('modalPago');
    const valorTotal = document.getElementById('valorTotal');
    const dineroIngresado = document.getElementById('dineroIngresado');
    const cambio = document.getElementById('cambio');
    const billetes = document.getElementById('billetes');
    const confirmarPago = document.getElementById('confirmarPago');

    // Asignar el valor total del pedido
    valorTotal.textContent = `$${pedido.ValorTotal}`;
     // Verificar si valor_total es nulo o undefined
     if (pedido.valor_total !== null && pedido.valor_total !== undefined) {
        // Asignar el valor total del pedido
        valorTotal.textContent = `$${pedido.ValorTotal}`;
    } else {
        // Manejar el caso cuando valor_total es nulo o undefined
        valorTotal.textContent = 'Valor total no disponible';
    }

    // Calcular el cambio cuando se ingresa el dinero
    // Calcular el cambio cuando se ingresa el dinero
dineroIngresado.addEventListener('input', () => {
    const valorTotalNum = parseFloat(pedido.valor_total);
    const dineroIngresadoNum = parseFloat(dineroIngresado.value);
    console.log('Valor total:', valorTotalNum);
    console.log('Dinero ingresado:', dineroIngresadoNum);

    // Validar si el valor ingresado es un número válido
    if (!isNaN(dineroIngresadoNum)) {
        const cambioNum = dineroIngresadoNum - valorTotalNum;

        if (cambioNum >= 0) {
            cambio.textContent = `Cambio: $${cambioNum.toFixed(2)}`;
            // Resto del código para calcular los billetes
        } else {
            cambio.textContent = 'Dinero insuficiente';
            billetes.textContent = '';
        }
    } else {
        cambio.textContent = 'Ingrese un número válido';
        billetes.textContent = '';
    }
});

    // Mostrar la ventana modal
    modal.style.display = 'block';

    // Cerrar la ventana modal cuando se hace clic en la "x"
    const span = document.getElementsByClassName('close')[0];
    span.onclick = function () {
        modal.style.display = 'none';
    };

    // Cerrar la ventana modal cuando se hace clic fuera de ella
    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Lógica para confirmar el pago
    confirmarPago.addEventListener('click', function () {
        const dineroIngresadoNum = parseFloat(dineroIngresado.value);
        const valorTotalNum = parseFloat(pedido.valor_total);

        if (dineroIngresadoNum >= valorTotalNum) {
            // Realizar la lógica para guardar la venta en la nueva tabla
            // Puedes hacer una llamada al backend aquí

            // Eliminar la fila del pedido de la tabla
            const row = pedidosTable.querySelector(`tr td:first-child:contains(${pedido.pedido_id})`).parentNode;
            row.remove();

            // Cerrar la ventana modal
            modal.style.display = 'none';
        } else {
            alert('Dinero insuficiente');
        }
    });
}

// Función para obtener los datos de un pedido por su ID
function obtenerDatosPedido(pedidoID) {
    // Lógica para obtener los datos del pedido desde el backend
    // o buscar el pedido en la lista lista_pedidos
    // Por ahora, simplemente devolvemos un objeto con datos de ejemplo
    const pedido = {
        PedidoID: pedidoID,
        MesaID: 'Mesa 1',
        UsuarioID: 'Usuario 123',
        FechaHora: '2024-05-21 10:00:00',
        ProductoID: 'Producto 456',
        Cantidad: 2,
        Estado: 'Activo',
        ValorBruto: 20,
        ValorVenta: 18,
        ValorTotal: 36
    };
    return pedido;
}

// Evento cuando el documento HTML está completamente cargado
document.addEventListener('DOMContentLoaded', function () {
    // Asignar eventos de clic a los botones de cancelar y pagar
    const cancelarBotones = document.querySelectorAll('.btn-danger');
    const pagarBotones = document.querySelectorAll('.btn-success');

    cancelarBotones.forEach(boton => {
        boton.addEventListener('click', () => {
            const pedidoID = parseInt(boton.dataset.pedidoId);
            cancelarPedido(pedidoID);
        });
    });

    pagarBotones.forEach(boton => {
        boton.addEventListener('click', () => {
            const pedidoID = parseInt(boton.dataset.pedidoId);
            const pedido = obtenerDatosPedido(pedidoID);
            abrirModalPago(pedido);
        });
    });
});
