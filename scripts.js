// Función para seleccionar una mesa
function seleccionarMesa(numeroMesa) {
  fetch('/seleccionar_mesa', {
    method: 'POST',
    body: JSON.stringify({ mesa_id: numeroMesa }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => {
      if (response.ok) {
        // Cambiar el color de fondo de la mesa seleccionada
        const mesaElement = document.getElementById(`mesa_${numeroMesa}`);
        mesaElement.classList.remove('mesa-libre');
        mesaElement.classList.add('mesa-seleccionada');
        console.log(`Mesa ${numeroMesa} seleccionada`);

        // Almacenar el ID de la mesa seleccionada
        mesaSeleccionada = numeroMesa;
      } else {
        console.error('Error al seleccionar mesa');
      }
    })
    .catch(error => console.error('Error:', error));
}

// Variable para almacenar el ID de la mesa seleccionada
let mesaSeleccionada = null;


// Función para agregar un producto al pedido
function agregarProductoPedido(productoId, cantidad) {
  if (mesaSeleccionada === null) {
    console.error('Debes seleccionar una mesa primero');
    return;
  }

  fetch('/agregar_producto', {
    method: 'POST',
    body: JSON.stringify({ mesa_id: mesaSeleccionada, producto_id: productoId, cantidad: cantidad }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => {
      if (response.ok) {
        mostrarPedido(); // Actualizar la tabla de pedidos
      } else {
        console.error('Error al agregar producto al pedido');
      }
    })
    .catch(error => console.error('Error:', error));
}

// Función para mostrar el pedido actualizado
function mostrarPedido() {
  if (mesaSeleccionada === null) {
    console.error('Debes seleccionar una mesa primero');
    return;
  }

  fetch(`/obtener_pedido_actual?mesa_id=${mesaSeleccionada}`)
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Error al obtener el pedido actual');
      }
    })
    .then(pedido => {
      const tableBody = document.getElementById('pedido-table-body');
      tableBody.innerHTML = ''; // Limpiar la tabla antes de actualizarla
      let total = 0;

      if (pedido.detalles_pedido.length === 0) {
        const newRow = tableBody.insertRow();
        newRow.innerHTML = '<td colspan="5">No hay productos en el pedido</td>';
      } else {
        pedido.detalles_pedido.forEach(producto => {
          const newRow = tableBody.insertRow();
          const valorTotal = producto.cantidad * producto.valor_unitario;
          total += valorTotal;
          newRow.innerHTML = `
            <td>${producto.nombre}</td>
            <td>${producto.cantidad}</td>
            <td>${producto.valor_unitario}</td>
            <td>${valorTotal}</td>
            <td><button onclick="eliminarProductoDelPedido(${producto.producto_id})">Eliminar</button></td>
          `;
        });
      }

      // Mostrar el valor total del pedido
      const totalElement = document.getElementById('total-pedido');
      totalElement.textContent = `Total: $${total.toFixed(2)}`;
    })
    .catch(error => console.error('Error:', error));
}

// Función para eliminar un producto del pedido
function eliminarProductoDelPedido(productoId) {
  if (mesaSeleccionada === null) {
    console.error('Debes seleccionar una mesa primero');
    return;
  }

  fetch('/eliminar_producto', {
    method: 'POST',
    body: JSON.stringify({ producto_id: productoId }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => {
      if (response.ok) {
        mostrarPedido(); // Actualizar la tabla de pedidos después de eliminar el producto
      } else {
        console.error('Error al eliminar producto del pedido');
      }
    })
    .catch(error => console.error('Error:', error));
}

// Llamar a la función para mostrar el pedido al cargar la página
window.onload = mostrarPedido;
document.addEventListener('DOMContentLoaded', function() {
  // Asignar eventos de clic a los botones
  const cancelarBotones = document.querySelectorAll('.btn-danger');
  const pagarBotones = document.querySelectorAll('.btn-success');

  cancelarBotones.forEach(boton => {
    boton.addEventListener('click', () => {
      const pedidoID = boton.dataset.pedidoId;
      cancelarPedido(pedidoID);
    });
  });

  pagarBotones.forEach(boton => {
    boton.addEventListener('click', () => {
      const pedidoID = boton.dataset.pedidoId;
      pagarPedido(pedidoID);
    });
  });
});