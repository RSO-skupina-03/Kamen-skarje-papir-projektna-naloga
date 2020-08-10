%from model import KamenSkarjePapir as ksp
%rebase('views/base.tpl')

<h3>KAMEN ŠKARJE PAPIR</h3>

<BLOckquote>
    Dobrodošli v igri Kamen Škarje Papir. Igrali boste proti računalniku.
    Igralo se bo minimalno 7 iger 
</BLOckquote>

<h2>REZULTAT: {{ksp.delni_izid_igralca()}} : {{ksp.delni_izid_racunalnika()</h2>

% if ksp.zmaga_igralca() == True:
    <h1>BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: {{igra.koncni_izid_igralca()}} : {{igra.koncni_izid_racunalnika()}}</h1>
% else:
    <h1>IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: {{igra.koncni_izid_racunalnika()}} : {{igra.koncni_izid_igralca()}}</h1>
%end

<form action="/ksp/" method="POST">
    <input type="radio" name="orozje" value="0">
    Kamen
    <input type="radio" name="orozje" value="1">
    Škarje
    <input type="radio" name="orozje" value="2">
    Papir
    <input type="submit" value="Potrdi">
</form>

