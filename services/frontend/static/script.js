function Uporabnik() {
    
    var user = document.getElementById("uporabnik").value;
    var pass = document.getElementById("password").value;
    fetch("/login/", {
        method: "PUT", 
        body: JSON.stringify({ uporabnik: user, password: pass}),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => console.error("Napaka:", error));
}

function Prijava() {
  const { AUTH_URL, FRONTEND_URL } = window.__ENV__;
  const FRONTEND_RETURN = `${window.location.origin}/igra`;
  const url = `${AUTH_URL}/auth/google/login?redirect_to=${encodeURIComponent(FRONTEND_RETURN)}`;
  window.location.assign(url);
}

function Gost() {

    fetch("/login/", {
        method: "PUT", 
        body: JSON.stringify({ uporabnik: "Gost" }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => console.error("Napaka:", error));
}

function BrisiKSP() {
    fetch('/brisi_ksp/', {
        method: 'DELETE',
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => console.error("Napaka:", error));
}

function BrisiKSPOV() {
    fetch('/brisi_kspov/', {
        method: 'DELETE',
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => console.error("Napaka:", error));
}