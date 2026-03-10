// Verificar sesión al cargar la página
const token = localStorage.getItem("token");
if (!token) {
    window.location.href = "/";
}

document.getElementById("registroForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const msg = document.getElementById("mensaje");
    msg.textContent = "";

    const datos = {
        nombre_completo: document.getElementById("nombre").value,
        correo: document.getElementById("correo").value,
        rfc: document.getElementById("rfc").value,
        curp: document.getElementById("curp").value,
        sexo: document.getElementById("sexo").value,
        fecha_nacimiento: document.getElementById("fecha_nacimiento").value, // YYYY-MM-DD
        direccion: document.getElementById("direccion").value,
        tipo_personal: document.getElementById("tipo_personal").value,
        rol: document.getElementById("rol").value,
        password: document.getElementById("password").value
    };

    try {
        const res = await fetch("/usuarios/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify(datos)
        });

        const data = await res.json();

        if (res.ok) {
            msg.style.color = "#4CAF50";
            msg.textContent = data.mensaje || "Usuario registrado correctamente";
            document.getElementById("registroForm").reset();
            setTimeout(() => window.location.href = "/dashboard", 1500);
        } else {
            msg.style.color = "#E57373";
            msg.textContent = data.detail || "Error al registrar";
        }

    } catch (error) {
        msg.style.color = "#E57373";
        msg.textContent = "Error de conexión con el servidor";
    }
});