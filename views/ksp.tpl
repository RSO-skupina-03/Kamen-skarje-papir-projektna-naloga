%import model
%rebase('views/base.tpl')
<h3>KAMEN ŠKARJE PAPIR</h3>
<BLOckquote>
    Dobrodošli v igri kamen škarje papir. Igrali boste proti računalniku.
    Igrali boste minimalno 7 iger.
    Igra se točkuje: igralec : računalnik
</BLOckquote>
<div class="rezultat">
    <h2>{{igra.delni_izid_igralca()}} : {{igra.delni_izid_racunalnika()}}</h2>
</div>


<div class="radio">
    <form action="/ksp/" method="POST" class="obrazec">
        <input type="radio" name="orozje" value="0" id="kamen">
        <label for="kamen">KAMEN</label>

        <input type="radio" name="orozje" value="1" id="skarje">
        <label for="skarje">ŠKARJE</label>

        <input type="radio" name="orozje" value="2" id="papir">
        <label for="papir">PAPIR</label>

        <div class="gumbi">
            <button type="submit" class="potrdi">Potrdi</button>
            <button type="button" class="potrdi" onclick="window.location.href='/end/'">Zgodovina</button>
        </div>
    </form>
</div>

% if igra.zmaga_igralca() == True:
<div class="center">
    <div class="content">
        <div class="glava zmaga">
            <h2>ZMAGA</h2>
        </div>
        <P>BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM {{igra.koncni_izid_igralca()}} : {{igra.koncni_izid_racunalnika()}}</P>
        <form action="/end/" method="GET">
            <button type="submit" class="zacetni">ZACETNI MENI</button>
        </form>
    </div>
</div>
%end


% if igra.zmaga_racunalnika() == True:
<div class="center">
    <div class="content">
        <div class="glava poraz">
            <h2>PORAZ</h2>
        </div>
        <P>IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM {{igra.koncni_izid_igralca()}} : {{igra.koncni_izid_racunalnika()}}</P>
        <form action="/end/" method="GET">
            <button type="submit" class="zacetni">ZACETNI MENI</button>
        </form>
    </div>
</div>
%end
