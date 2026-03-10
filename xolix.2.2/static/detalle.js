// ── Sesión ───────────────────────────────────────────────
const token = localStorage.getItem("token");
const rol   = localStorage.getItem("rol");

if (!token) window.location.href = "/";

// ── ID desde la URL ──────────────────────────────────────
const id = window.location.pathname.split("/").pop();

// ── Mostrar botón editar solo a director/coordinador ─────
if (rol === "director" || rol === "coordinador") {
    document.getElementById("btnEditar").style.display = "block";
}

function irEditar() {
    window.location.href = `/editar/${id}`;
}

// ── Carga y renderizado del usuario ─────────────────────
async function cargarUsuario() {
    try {
        const res = await fetch(`/usuarios/${id}`, {
            headers: { "Authorization": "Bearer " + token }
        });

        if (!res.ok) {
            document.getElementById("error").style.display = "block";
            return;
        }

        const u = await res.json();
        document.getElementById("subtitulo").textContent = "Datos del personal";

        document.getElementById("detalles").innerHTML = `
            <div class="detail-item">
                <label>Nombre completo</label>
                <span>${u.nombre_completo}</span>
            </div>
            <div class="detail-item">
                <label>Correo</label>
                <span>${u.correo}</span>
            </div>
            <div class="detail-item">
                <label>RFC</label>
                <span>${u.rfc}</span>
            </div>
            <div class="detail-item">
                <label>CURP</label>
                <span>${u.curp}</span>
            </div>
            <div class="detail-item">
                <label>Sexo</label>
                <span>${u.sexo === "M" ? "Masculino" : "Femenino"}</span>
            </div>
            <div class="detail-item">
                <label>Edad</label>
                <span>${u.edad} años</span>
            </div>
            <div class="detail-item" style="grid-column: 1 / -1;">
                <label>Dirección</label>
                <span>${u.direccion}</span>
            </div>
            <div class="detail-item">
                <label>Tipo de personal</label>
                <span style="text-transform:capitalize;">${u.tipo_personal}</span>
            </div>
            <div class="detail-item">
                <label>Rol</label>
                <span style="text-transform:capitalize;">${u.rol}</span>
            </div>
            <div class="detail-item">
                <label>Estado</label>
                <span class="badge ${u.activo ? "badge-active" : "badge-inactive"}">
                    ${u.activo ? "Activo" : "Inactivo"}
                </span>
            </div>
            <div class="detail-item">
                <label>Fecha de registro</label>
                <span>${u.fecha_creacion ? new Date(u.fecha_creacion).toLocaleDateString("es-MX") : "N/A"}</span>
            </div>
        `;

        document.getElementById("contenido").style.display = "block";

    } catch {
        document.getElementById("error").style.display = "block";
    }
}

// ── Arranque ─────────────────────────────────────────────
cargarUsuario();