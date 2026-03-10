document.getElementById("registroForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const mensajeDiv = document.getElementById("mensaje");
    mensajeDiv.textContent = "";
    mensajeDiv.style.color = "black";

    const datosUsuario = {
        nombre_completo: document.getElementById("nombre").value,
        correo: document.getElementById("correo").value,
        rfc: document.getElementById("rfc").value,
        curp: document.getElementById("curp").value,
        sexo: document.getElementById("sexo").value,
        edad: parseInt(document.getElementById("edad").value),
        direccion: document.getElementById("direccion").value,
        tipo_personal: document.getElementById("tipo_personal").value,
        rol: document.getElementById("rol").value,
        password: document.getElementById("password").value
    };

    try {
        const response = await fetch("http://localhost:8000/usuarios/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json" 
            },
            body: JSON.stringify(datosUsuario)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Error desconocido");
        }

        // ✅ ÉXITO
        mensajeDiv.style.color = "green";
        mensajeDiv.textContent = data.mensaje;

        // Limpiar formulario
        document.getElementById("registroForm").reset();

        // Redirigir después de 2 segundos (opcional)
        setTimeout(() => {
            window.location.href = "login.html";
        }, 2000);

    } catch (error) {
        // ❌ ERROR
        mensajeDiv.style.color = "red";
        mensajeDiv.textContent = error.message;
    }
});
