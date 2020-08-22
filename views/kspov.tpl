%import model
%rebase('views/base.tpl')

<h3>KAMEN ŠKARJE PAPIR OGENJ VODA</h3>

<BLOckquote>
    Dobrodošli v igri Kamen Škarje Papir Ogenj Voda. Igrali boste proti računalniku.
    Igralo se bo minimalno 14 iger 
</BLOckquote>

<h2>REZULTAT: {{igra.delni_izid_igralca()}} : {{igra.delni_izid_racunalnika()}}</h2>


<form action="/kspov/" method="POST">
    Kamen
    <input type="radio" name="orozje" value="0">
    Škarje
    <input type="radio" name="orozje" value="1">
    Papir
    <input type="radio" name="orozje" value="2">
    Ogrenj
    <input type="radio" name="orozje" value="3">
    Voda
    <input type="radio" name="orozje" value="4">
    
    <input type="submit" value="Potrdi">
</form>

% if igra.zmaga_igralca_1() == True:
    <h1>BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM {{igra.koncni_izid_igralca_1()}} : {{igra.koncni_izid_racunalnika_1()}}</h1>
    <form action="/" method="GET">
        <button type="submit">ZACETNI MENI</button>
    </form>
%end

% if igra.zmaga_racunalnika_1() == True:
    <h1>IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM {{igra.koncni_izid_racunalnika_1()}} : {{igra.koncni_izid_igralca_1()}}</h1>
    <form action="/" method="GET">
        <button type="submit">ZACETNI MENI</button>
    </form>
%end



