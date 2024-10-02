document.addEventListener('DOMContentLoaded', () => {
    // Obtener el carrito del localStorage
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

    // Mostrar los productos en la tabla
    const cartItemsContainer = document.getElementById('cart-items');
    let subtotal = 0;

    carrito.forEach(item => {
        const fila = document.createElement('tr');
        const subtotalProducto = item.precio * item.cantidad;
        subtotal += subtotalProducto;

        fila.innerHTML = `
            <th scope="row">
                <div class="d-flex align-items-center">
                    <img src="${item.imagen}" class="img-fluid me-5 rounded-circle" style="width: 80px; height: 80px;" alt="">
                </div>
            </th>
            <td>
                <p class="mb-0 mt-4">${item.nombre}</p>
            </td>
            <td>
                <p class="mb-0 mt-4">$${item.precio.toFixed(2)}</p>
            </td>
            <td>
                <div class="input-group quantity mt-4" style="width: 100px;">
                    <div class="input-group-btn">
                        <button class="btn btn-sm btn-minus rounded-circle bg-light border">
                            <i class="fa fa-minus"></i>
                        </button>
                    </div>
                    <input type="text" class="form-control form-control-sm text-center border-0" value="${item.cantidad}">
                    <div class="input-group-btn">
                        <button class="btn btn-sm btn-plus rounded-circle bg-light border">
                            <i class="fa fa-plus"></i>
                        </button>
                    </div>
                </div>
            </td>
            <td>
                <p class="mb-0 mt-4">$${subtotalProducto.toFixed(2)}</p>
            </td>
            <td>
                <button class="btn btn-md rounded-circle bg-light border mt-4">
                    <i class="fa fa-times text-danger"></i>
                </button>
            </td>
        `;
        cartItemsContainer.appendChild(fila);
    });

    // Calcular el total
    const shippingCost = 3.00;
    const total = subtotal + shippingCost;

    // Actualizar el HTML con los valores calculados
    document.getElementById('subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('total').textContent = `$${total.toFixed(2)}`;
});