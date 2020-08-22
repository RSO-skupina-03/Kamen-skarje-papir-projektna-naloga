%import model
%rebase('views/base.tpl')

<h3>KAMEN ŠKARJE PAPIR</h3>

<BLOckquote>
    Dobrodošli v igri Kamen Škarje Papir. Igrali boste proti računalniku.
    Igralo se bo minimalno 7 iger 
</BLOckquote>

<h2>REZULTAT: {{igra.delni_izid_igralca()}} : {{igra.delni_izid_racunalnika()}}</h2>



<form action="/ksp/" method="POST">
    Kamen
    <input type="radio" name="orozje" value="0">
    Škarje
    <input type="radio" name="orozje" value="1">
    Papir
    <input type="radio" name="orozje" value="2">
    
    <button type="submit">Potrdi</button>
</form>

% if igra.zmaga_igralca() == True:
    <h1>BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM {{igra.koncni_izid_igralca()}} : {{igra.koncni_izid_racunalnika()}}</h1>
    <form action="/" method="GET">
        <button type="submit">ZACETNI MENI</button>
    </form>
%end

% if igra.zmaga_racunalnika() == True:
    <h1>IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM {{igra.koncni_izid_racunalnika()}} : {{igra.koncni_izid_igralca()}}</h1>
    <form action="/" method="GET">
        <button type="submit">ZACETNI MENI</button>
    </form>
%end
