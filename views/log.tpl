%rebase('views/base.tpl')
<div class="wrapper">
        <div class="input-box">
            <input type="text" placeholder="Uporabnik" name="uporabnik" id="uporabnik">
        </div>
        <div class="input-box">
            <input type="password" placeholder="Geslo" name="password" id="password">
        </div>
        <button type="button" class="btn" onclick="Uporabnik()">Prijava</button>
        <button type="button" class="btn" onclick="Gost()">Gost</button>
</div>