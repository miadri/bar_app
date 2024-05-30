// Función para obtener los usuarios
function obtenerUsuarios() {
    fetch('/obtener_usuarios')
      .then(response => response.json())
      .then(data => {
        const usuariosTable = document.querySelector('#tabla-usuarios tbody');
        usuariosTable.innerHTML = '';
  
        data.forEach(usuario => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${usuario.id}</td>
            <td>${usuario.nombre}</td>
            <td>${usuario.rol}</td>
            <td>${usuario.sede}</td>
            <td>
              <button class="btn btn-primary" onclick="editarUsuario(${usuario.id})">Editar</button>
              <button class="btn btn-danger" onclick="eliminarUsuario(${usuario.id})">Eliminar</button>
            </td>
          `;
          usuariosTable.appendChild(row);
        });
      })
      .catch(error => console.error('Error al obtener los usuarios:', error));
  }
  
  // Función para agregar un nuevo usuario
  function agregarUsuario() {
    const nombre = prompt('Ingrese el nombre del usuario:');
    const contraseña = prompt('Ingrese la contraseña del usuario:');
    const rol = prompt('Ingrese el rol del usuario (Administrador, Mesero o Cajero):');
    const sedeId = prompt('Ingrese el ID de la sede del usuario:');
  
    const datos = { nombre, contraseña, rol, sede_id: sedeId };
  
    fetch('/registrar_usuario', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(datos)
    })
      .then(response => response.json())
      .then(data => {
        console.log(data.mensaje);
        obtenerUsuarios(); // Actualizar la tabla de usuarios
      })
      .catch(error => console.error('Error al agregar el usuario:', error));
  }
  
  // Función para editar un usuario
  function editarUsuario(usuarioId) {
    const nombre = prompt('Ingrese el nuevo nombre del usuario:', '');
    const contraseña = prompt('Ingrese la nueva contraseña del usuario:', '');
    const rol = prompt('Ingrese el nuevo rol del usuario (Administrador, Mesero o Cajero):', '');
    const sedeId = prompt('Ingrese el nuevo ID de la sede del usuario:', '');
  
    if (nombre && contraseña && rol && sedeId) {
      const datos = { usuario_id: usuarioId, nombre, contraseña, rol, sede_id: sedeId };
  
      fetch('/editar_usuario', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
      })
        .then(response => response.json())
        .then(data => {
          console.log(data.mensaje);
          obtenerUsuarios(); // Actualizar la tabla de usuarios
        })
        .catch(error => console.error('Error al editar el usuario:', error));
    }
  }
  
  // Función para eliminar un usuario
  function eliminarUsuario(usuarioId) {
    if (confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      fetch(`/eliminar_usuario/${usuarioId}`, {
        method: 'DELETE'
      })
        .then(response => response.json())
        .then(data => {
          console.log(data.mensaje);
          obtenerUsuarios(); // Actualizar la tabla de usuarios
        })
        .catch(error => console.error('Error al eliminar el usuario:', error));
    }
  }
  
  // Función para obtener las sedes
  function obtenerSedes() {
    fetch('/obtener_sedes')
      .then(response => response.json())
      .then(data => {
        const sedesTable = document.querySelector('#tabla-sedes tbody');
        sedesTable.innerHTML = '';
  
        data.forEach(sede => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${sede.id}</td>
            <td>${sede.nombre}</td>
            <td>
              <button class="btn btn-primary" onclick="editarSede(${sede.id})">Editar</button>
              <button class="btn btn-danger" onclick="eliminarSede(${sede.id})">Eliminar</button>
            </td>
          `;
          sedesTable.appendChild(row);
        });
      })
      .catch(error => console.error('Error al obtener las sedes:', error));
  }
  
  // Función para agregar una nueva sede
  function agregarSede() {
    const nombre = prompt('Ingrese el nombre de la nueva sede:');
  
    if (nombre) {
      const datos = { nombre };
  
      fetch('/agregar_sede', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
      })
        .then(response => response.json())
        .then(data => {
          console.log(data.mensaje);
          obtenerSedes(); // Actualizar la tabla de sedes
        })
        .catch(error => console.error('Error al agregar la sede:', error));
    }
  }
  
  // Función para editar una sede
  function editarSede(sedeId) {
    const nuevoNombre = prompt('Ingrese el nuevo nombre de la sede:', '');
  
    if (nuevoNombre) {
      const datos = { sede_id: sedeId, nombre: nuevoNombre };
  
      fetch('/editar_sede', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
      })
        .then(response => response.json())
        .then(data => {
          console.log(data.mensaje);
          obtenerSedes(); // Actualizar la tabla de sedes
        })
        .catch(error => console.error('Error al editar la sede:', error));
    }
  }
  
  // Función para eliminar una sede
  function eliminarSede(sedeId) {
    if (confirm('¿Estás seguro de que deseas eliminar esta sede?')) {
      fetch(`/eliminar_sede/${sedeId}`, {
        method: 'DELETE'
      })
        .then(response => response.json())
        .then(data => {
          console.log(data.mensaje);
          obtenerSedes(); // Actualizar la tabla de sedes
        })
        .catch(error => console.error('Error al eliminar la sede:', error));
    }
  }
  
  // Función para obtener el inventario
  function obtenerInventario() {
    fetch('/obtener_inventario')
      .then(response => response.json())
      .then(data => {
        const inventarioTable = document.querySelector('#tabla-inventario tbody');
        inventarioTable.innerHTML = '';
  
        data.forEach(item => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${item.producto_id}</td>
            <td>${item.producto_nombre}</td>
            <td>${item.cantidad}</td>
            <td>${item.proveedor}</td>
            <td>${item.sede}</td>
            <td>
              <button class="btn btn-primary" onclick="editarInventario(${item.id})">Editar</button>
              <button class="btn btn-danger" onclick="eliminarInventario(${item.id})">Eliminar</button>
            </td>
          `;
          inventarioTable.appendChild(row);
        });
      })
      .catch(error => console.error('Error al obtener el inventario:', error));
  }
  
  // Función para agregar un nuevo producto al inventario
// Función para agregar un nuevo producto al inventario
function agregarProductoInventario() {
    const productoId = prompt('Ingrese el ID del producto:');
    const cantidad = prompt('Ingrese la cantidad del producto:');
    const proveedor = prompt('Ingrese el proveedor del producto:');
    const sedeId = prompt('Ingrese el ID de la sede donde se almacenará el producto:');
  
    if (productoId && cantidad && proveedor && sedeId) {
      const datos = { producto_id: productoId, cantidad, proveedor, sede_id: sedeId };
  
      fetch('/agregar_producto_inventario', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
      })
        .then(response => response.json())
        .then(data => {
          console.log(data.mensaje);
          obtenerInventario(); // Actualizar la tabla de inventario
        })
        .catch(error => console.error('Error al agregar el producto al inventario:', error));
    }
  }
  