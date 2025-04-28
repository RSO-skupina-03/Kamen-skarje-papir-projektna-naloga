function Uporabnik() {
    
    var user = document.getElementById("uporabnik").value;
    fetch("/zacetni_menu/", {
        method: "PUT", 
        body: JSON.stringify({ uporabnik: user }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(error => console.error("Napaka:", error));
}

function Gost() {

    fetch("/zacetni_menu/", {
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