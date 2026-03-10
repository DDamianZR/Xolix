document.getElementById("loginForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const correo = document.getElementById("correo").value;
    const password = document.getElementById("password").value;
    const mensaje = document.getElementById("mensaje");

    mensaje.textContent = "";

    try {
        const response = await fetch("http://localhost:8000/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail);
        }

        localStorage.setItem("token", data.access_token);

        mensaje.style.color = "#6BCB77";
        mensaje.textContent = "Login exitoso";

        setTimeout(() => {
            window.location.href = "/";
        }, 1500);

    } catch (error) {
        mensaje.style.color = "#FF6B6B";
        mensaje.textContent = error.message;
    }
});
