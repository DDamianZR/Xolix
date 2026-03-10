document.getElementById("loginForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const msg = document.getElementById("mensaje");
    msg.textContent = "Verificando...";
    msg.style.color  = "#6c7a96";

    try {
        const res = await fetch("/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                correo:   document.getElementById("correo").value,
                password: document.getElementById("password").value
            })
        });
        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("rol", data.rol);
            msg.textContent = "Login exitoso ✓";
            msg.style.color  = "#4CAF50";
            setTimeout(() => window.location.href = "/dashboard", 800);
        } else {
            msg.textContent = data.detail;
            msg.style.color  = "#E57373";
        }
    } catch {
        msg.textContent = "Error de conexión con el servidor";
        msg.style.color  = "#E57373";
    }
});