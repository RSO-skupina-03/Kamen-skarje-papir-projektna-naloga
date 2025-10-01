%import model
%rebase('views/base.tpl')

<h3>KAMEN ŠKARJE PAPIR OGENJ VODA</h3>

<BLOckquote>
    Dobrodošli v igri kamen škarje papir ogenj voda. Igrali boste proti računalniku.
    Igrali boste minimalno 15 iger.
    Igra se točkuje: igralec : računalnik
</BLOckquote>

<div class="rezultat1">
    <h2>{{igra.delni_izid_igralca()}} : {{igra.delni_izid_racunalnika()}}</h2>
</div>

<div class="radio">
    <form action="/kspov/" method="POST">
        <input type="radio" name="orozje" value="0" id="kamen">
        <label for="kamen">KAMEN</label>

        <input type="radio" name="orozje" value="1" id="skarje">
        <label for="skarje">ŠKARJE</label>

        <input type="radio" name="orozje" value="2" id="papir">
        <label for="papir">PAPIR</label>

        <input type="radio" name="orozje" value="3" id="ogenj">
        <label for="ogenj">OGENJ</label>
        
        <input type="radio" name="orozje" value="4" id="voda">
        <label for="voda">VODA</label>

        <div class="gumbi">
            <button type="submit" class="potrdi">Potrdi</button>
            % if is_subscriber == True:
            <button type="button" class="potrdi" onclick="window.location.href='/zgodovina_kspov/'">Zgodovina</button>
            <button type="button" class="potrdi" onclick="window.location.href='/end/'">Nazaj</button>
            % end
        </div>
    </form>
</div>

% if igra.zmaga_igralca_1() == True:
<div class="center">
    <div class="content">
        <div class="glava zmaga">
            <h2>ZMAGA</h2>
        </div>
        <P>BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM {{igra.koncni_izid_igralca_1()}} : {{igra.koncni_izid_racunalnika_1()}}</P>
        <form action="/nova_igra_kspov/" method="GET">
            <button type="submit" class="zacetni">BRAVO !!!</button>
        </form>
    </div>
</div>
%end

% if igra.zmaga_racunalnika_1() == True:
<div class="center">
    <div class="content">
        <div class="glava poraz">
            <h2>PORAZ</h2>
        </div>
        <P>IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM {{igra.koncni_izid_igralca_1()}} : {{igra.koncni_izid_racunalnika_1()}}</P>
        <form action="/nova_igra_kspov/" method="GET">
            <button type="submit" class="zacetni">BAD LUCK</button>
        </form>
    </div>
</div>
%end





