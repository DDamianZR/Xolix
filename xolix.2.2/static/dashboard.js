// ── Estado global ────────────────────────────────────────
let todosUsuarios = [];
let usuarioAEliminar = null;

const token = localStorage.getItem("token");
const rol   = localStorage.getItem("rol");

// Redirigir si no hay sesión
if (!token) window.location.href = "/";

// ── Inicialización ───────────────────────────────────────
document.getElementById("infoRol").textContent = `Sesión: ${rol || "usuario"}`;

// Mostrar botón agregar ssolo a director/coordinador
if (rol === "director" || rol === "coordinador"|| rol === "Quien sabe pero cae chido") {
    document.getElementById("btnAgregar").style.display = "inline-block";
}

// ── Carga de usuarios ────────────────────────────────────
async function cargarUsuarios() {
    try {
        const res = await fetch("/usuarios/", {
            headers: { "Authorization": "Bearer " + token }
        });

        if (res.status === 401) { cerrarSesion(); return; }

        const usuarios = await res.json();
        todosUsuarios = usuarios;
        renderTabla(usuarios);

        document.getElementById("cargando").style.display = "none";
        document.getElementById("tablaWrap").style.display = "block";

    } catch {
        document.getElementById("cargando").textContent = "Error al cargar usuarios.";
    }
}

// ── Renderizado de tabla ─────────────────────────────────
function renderTabla(usuarios) {
    const tbody  = document.getElementById("tablaUsuarios");
    const sinRes = document.getElementById("sinResultados");

    if (usuarios.length === 0) {
        tbody.innerHTML = "";
        sinRes.style.display = "block";
        document.getElementById("tablaWrap").style.display = "none";
        return;
    }

    sinRes.style.display = "none";
    document.getElementById("tablaWrap").style.display = "block";

    const puedeGestionar = rol === "director" || rol === "coordinador";

    tbody.innerHTML = usuarios.map((u, i) => `
        <tr>
            <td>${i + 1}</td>
            <td><strong>${u.nombre_completo}</strong></td>
            <td>${u.correo}</td>
            <td><span class="badge badge-rol">${u.rol}</span></td>
            <td>${u.tipo_personal}</td>
            <td>
                <span class="badge ${u.activo ? "badge-active" : "badge-inactive"}">
                    ${u.activo ? "Activo" : "Inactivo"}
                </span>
            </td>
            <td>
                <div class="btn-actions">
                    <a class="btn-sm btn-view" href="/usuario/${u.id}">Ver</a>
                    ${puedeGestionar ? `
                        <a class="btn-sm btn-edit" href="/editar/${u.id}">Editar</a>
                        <button class="btn-sm ${u.activo ? "btn-toggle-on" : "btn-toggle-off"}"
                            onclick="toggleAcceso(${u.id}, ${u.activo})">
                            ${u.activo ? "Revocar" : "Activar"}
                        </button>
                        <button class="btn-sm btn-delete" onclick="pedirEliminar(${u.id})">Eliminar</button>
                    ` : ""}
                </div>
            </td>
        </tr>
    `).join("");
}

// ── Búsqueda / filtro ────────────────────────────────────
function filtrarTabla() {
    const q = document.getElementById("busqueda").value.toLowerCase();
    const filtrados = todosUsuarios.filter(u =>
        u.nombre_completo.toLowerCase().includes(q) ||
        u.correo.toLowerCase().includes(q)           ||
        u.rol.toLowerCase().includes(q)
    );
    renderTabla(filtrados);
}

// ── Revocar / Activar acceso ─────────────────────────────
async function toggleAcceso(id, estadoActual) {
    const nuevoEstado = !estadoActual;
    const res = await fetch(`/usuarios/${id}/acceso?activo=${nuevoEstado}`, {
        method: "PATCH",
        headers: { "Authorization": "Bearer " + token }
    });
    if (res.ok) cargarUsuarios();
    else alert("Error al cambiar acceso");
}

// ── Modal eliminar ───────────────────────────────────────
function pedirEliminar(id) {
    usuarioAEliminar = id;
    document.getElementById("modalEliminar").classList.add("active");
}

function cerrarModal() {
    usuarioAEliminar = null;
    document.getElementById("modalEliminar").classList.remove("active");
}

async function confirmarEliminar() {
    if (!usuarioAEliminar) return;
    const res = await fetch(`/usuarios/${usuarioAEliminar}`, {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + token }
    });
    cerrarModal();
    if (res.ok) cargarUsuarios();
    else alert("Error al eliminar usuario");
}

// ── Cerrar sesión ────────────────────────────────────────
function cerrarSesion() {
    localStorage.removeItem("token");
    localStorage.removeItem("rol");
    window.location.href = "/";
}

// ── Arranque ─────────────────────────────────────────────
cargarUsuarios();