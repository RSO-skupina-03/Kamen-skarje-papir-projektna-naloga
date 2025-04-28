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
    fetch('/izbrisi_igre/', {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Odgovor strežnika:', data);
        alert('Vse igre so bile uspešno izbrisane!');
        window.location.href = "/end/"; // Preusmeri nazaj na začetni meni
    })
    .catch(error => {
        console.error('Napaka:', error);
    });
}

function BrisiKSPOV() {
    fetch('/izbrisi_igre/', {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Odgovor strežnika:', data);
        alert('Vse igre so bile uspešno izbrisane!');
        window.location.href = "/end/"; // Preusmeri nazaj na začetni meni
    })
    .catch(error => {
        console.error('Napaka:', error);
    });
}