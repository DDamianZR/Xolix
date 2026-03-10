// ── Sesión y permisos ────────────────────────────────────
const token = localStorage.getItem("token");
const rol   = localStorage.getItem("rol");

if (!token) window.location.href = "/";
if (rol !== "director" && rol !== "coordinador") window.location.href = "/dashboard";

// ── ID desde la URL ──────────────────────────────────────
const id = window.location.pathname.split("/").pop();

// ── Carga de datos del usuario ───────────────────────────
async function cargarUsuario() {
    try {
        const res = await fetch(`/usuarios/${id}`, {
            headers: { "Authorization": "Bearer " + token }
        });

        if (!res.ok) {
            document.getElementById("loadingUser").style.display = "none";
            document.getElementById("cargando").textContent = "Error al cargar usuario.";
            return;
        }

        const u = await res.json();

        // Ocultar avatar de carga
        document.getElementById("loadingUser").style.display = "none";

        // Llenar formulario
        document.getElementById("nombre").value            = u.nombre_completo || "";
        document.getElementById("correo").value            = u.correo || "";
        document.getElementById("rfc").value               = u.rfc || "";
        document.getElementById("curp").value              = u.curp || "";
        document.getElementById("fecha_nacimiento").value  = u.fecha_nacimiento || "";
        document.getElementById("sexo").value              = u.sexo || "";
        document.getElementById("direccion").value         = u.direccion || "";
        document.getElementById("tipo_personal").value     = u.tipo_personal || "";
        document.getElementById("rol").value               = u.rol || "";

        // Mostrar formulario
        document.getElementById("editarForm").style.display = "block";

    } catch (error) {
        document.getElementById("loadingUser").style.display = "none";
        document.getElementById("cargando").textContent = "Error de conexión.";
    }
}

// ── Envío del formulario ─────────────────────────────────
document.getElementById("editarForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const msg = document.getElementById("mensaje");
    msg.textContent = "Guardando...";
    msg.style.color = "#6c7a96";

    const datos = {
        nombre_completo: document.getElementById("nombre").value,
        correo: document.getElementById("correo").value,
        rfc: document.getElementById("rfc").value,
        curp: document.getElementById("curp").value,
        fecha_nacimiento: document.getElementById("fecha_nacimiento").value,
        sexo: document.getElementById("sexo").value,
        direccion: document.getElementById("direccion").value,
        tipo_personal: document.getElementById("tipo_personal").value,
        rol: document.getElementById("rol").value,
    };

    const nuevaPass = document.getElementById("password").value;
    if (nuevaPass) datos.password = nuevaPass;

    try {
        const res = await fetch(`/usuarios/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(datos)
        });

        const data = await res.json();

        if (res.ok) {
            msg.textContent = "Cambios guardados correctamente ✓";
            msg.style.color = "#4CAF50";
            setTimeout(() => window.location.href = `/usuario/${id}`, 1200);
        } else {
            msg.textContent = data.detail || "Error al guardar";
            msg.style.color = "#E57373";
        }

    } catch {
        msg.textContent = "Error de conexión";
        msg.style.color = "#E57373";
    }
});

// ── Arranque ─────────────────────────────────────────────
cargarUsuario();