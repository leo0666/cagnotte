document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const err = document.querySelector("#error-message");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {};

        formData.forEach((value, key) => {
            data[key] = value;
        });

        if (data.pwd !== data.pwd_confirmed) {
            if (err) {
                err.textContent = "La confirmation du mot de passe ne correspond pas avec le mot de passe.";
            }
            return;
        }

        delete data.pwd_confirmed;

        const response = await fetch("/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const html = await response.text();
            document.body.innerHTML = html;
        }
    });
});