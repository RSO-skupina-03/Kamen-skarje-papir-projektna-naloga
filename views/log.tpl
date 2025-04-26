%rebase('views/base.tpl')
<div class="wrapper">
        <h2>Prijava</h2>
        <div class="input-box">
            <input type="text" placeholder="Uporabnik" name="uporabnik">
        </div>
        <div class="input-box">
            <input type="password" placeholder="Geslo" name="geslo">
        </div>
        <button type="submit" class="btn">Prijava</button>
        <form action="/zacetni_menu/" method="POST">
            <button type="submit" class="btn">Gost</button>
        </form>
</div>