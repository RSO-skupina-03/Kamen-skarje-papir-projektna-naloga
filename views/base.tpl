<!DOCTYPE html>
<html>
<head>
    <title>KAMEN ŠKARJE PAPIR</title>
    <meta charset="UTF-8">
    <style>

* 
{
    margin: 0;
    padding: 0;
}

body
{
    background-color: rgba(112, 103, 103, 0.7);
    font-family:Arial, Helvetica, sans-serif;
}

nav
{
    width: 100%;
    height: 50px;
    background-color: black;
    border: 1px solid blanchedalmond;
}

nav p
{
    color: blanchedalmond;
    font-size: 28px;
    text-align: center;
    padding: 10px 25px;
}

.gumb
{
    border: 3px solid blanchedalmond;
    background: black;
    padding: 25px 60px;
    font-size: 30px;
    margin: 300px auto;
    cursor: pointer;
    font-weight: normal;
    text-align: center;
    border-radius: 6px;
    color: blanchedalmond;
    display: block;
    transition: 0.5s;
}

.container
{
    text-align: center;
    margin-top: 100px;
}

.gumb:hover
{
    color: darkcyan;
    background-color: blanchedalmond;
}

.center, .content, .radio
{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.content
{
    width: 500px;
    height: 350px;
    border: 1px solid blanchedalmond;
    background: black;
    border-radius: 5px;
    box-shadow: 0 4px 14px 0 rgba(250, 250, 250, .6);
    transition: .2s ease-in;
}

.glava
{
    height: 130px;
    background: black;
    overflow: hidden;
    border-radius: 5px 5px 0 0;
}

.glava h2
{
    padding-left: 20px;
    padding-top: 30px;
    font-weight: normal;
}

p
{
    padding-top: 20px;
    font-size: 16px;
    color: blanchedalmond;
    text-align: center;
}

.zacetni
{
    position: absolute;
    bottom: 20px;
    right: 35px;
    border: 1px solid black;
    color: blanchedalmond;
    background: black;
    font-size: 14px;
    cursor: pointer;
}

.wrapper button:hover, .zacetni:hover
{
    color: darkcyan;
    transition: 0.5s;
}

.zmaga
{
    color: green;
}

.poraz
{
    color: red;
}

input[type="radio"]
{
    display: none;
}

label
{
    position: relative;
    color: black;
    font-size: 40px;
    border: 2px solid black;
    border-radius: 5px;
    padding: 15px 50px;
    display: flex;
    align-items: center;
    margin: 30px 30px;
    top: 200px;
}

.wrapper button:hover, label:hover
{
    color: darkcyan;
    background-color: blanchedalmond;
    transition: 0.1s;
}

input[type="radio"]:checked + label
{
    color: darkcyan;
    background-color: blanchedalmond
}

.potrdi
{
    position: relative;
    top: 120px;
    left: 350px;
    border: 2px soild black;
    cursor: pointer;
    padding: 15px 50px;
    font-size: 40px;
    border-radius: 5px;
    background:rgba(112, 103, 103, 0.7);
    color: black;
}

.rezultat1
{
    position: relative;
    top: 60px;
    font-size: 30px;
}

.pozdrav
{
    position: relative;
    bottom: 20px;
    font-size: medium;
}

h3
{
    position: relative;
    bottom: 60px;
}

.rezultat
{
    position: relative;
    top: 120px;
    font-size: 30px;
}

.wrapper
{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 420px;
    color: #fff;
}

        
.wrapper h2
{
    color: black;
    font-size: 36px;
    text-align: center;
}

.wrapper .input-box
{
    width: 100%;
    height: 50px;
    margin: 40px 0px;
}

.input-box input
{
    width: 100%;
    height: 70%;
    background: transparent;
    border: none;
    outline: none;
    border: 2px solid blanchedalmond;
    border-radius: 40px;
    font-size: 20px;
    color: #fff;
    padding: 10px 10px 10px 20px
    
}

.input-box input::placeholder
{
    color: black;
}

.wrapper button
{
    width: 110%;
    height: 45px;
    margin: 10px 0px;
    background: #fff;
    border-radius: 40px;
    cursor: pointer;
    font-size: 18px;
    border: 2px soild black;
    background:rgba(112, 103, 103, 0.7);
    color: black;
    font-weight: 500;
}
    </style>
</head>
<body>
    <nav>
        <p>KŠP</p>
    </nav>
    <div class="container">
        {{!base}}
    </div>

    <!-- Tukaj dodamo še javascript-->
    <script>
        document.getElementById("prijava").addEventListener("click", function() {
            event.preventDefault(); // preprečimo običajno pošiljanje obrazca
            
            var user = document.getElementById("uporabnik").value;
            
            // Pošlji PUT zahtevo z uporabo fetch API
            fetch("/zacetni_menu/", {
                method: "PUT", 
                body: JSON.stringify({ uporabnik: user }),
                headers: { "Content-Type": "application/json" }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url; // Preusmeritev na novo stran
                }
            })
            .catch(error => console.error("Napaka:", error));
        });

        document.getElementById("gostBtn").addEventListener("click", function() {
            fetch("/zacetni_menu/", {
                method: "PUT", 
                body: JSON.stringify({ uporabnik: "Gost" }),
                headers: { "Content-Type": "application/json" }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url; // Preusmeritev na novo stran
                }
            })
            .catch(error => console.error("Napaka:", error));
        });
    </script>
</body>
</html>