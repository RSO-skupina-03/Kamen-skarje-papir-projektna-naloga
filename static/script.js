function Uporabnik() {
  const user = document.getElementById("uporabnik").value;
  const pass = document.getElementById("password").value;

  try {
    const resp = fetch("/zacetni_menu/", {
      method: "PUT",
      redirect: "manual",                // ← don’t auto‐follow
      body: JSON.stringify({ uporabnik: user, password: pass }),
      headers: { "Content-Type": "application/json" }
    });

    // If we got a 303, read the Location header and navigate
    if (resp.status === 303) {
      const loc = resp.headers.get("Location");
      if (loc) {
        window.location.href = loc;
        return;
      }
    }

    // Otherwise handle errors or show feedback:
    alert("Napaka pri prijavi: " + resp.status);
  }
  catch (err) {
    console.error("Napaka:", err);
  }
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