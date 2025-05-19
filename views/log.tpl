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

% if valid == False:
<div class="center">
    <div class="content">
        <div class="glava zmaga">
            <h2>POZOR!!!</h2>
        </div>
        <P>NAPAČNO IME ALI GESLO</P>
        <form action="/" method="GET">
            <button type="submit" class="zacetni">PROBAJ ZNOVA</button>
        </form>
    </div>
</div>
%end
