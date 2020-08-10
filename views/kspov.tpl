%from model import KamenSkarjePapirOgenjVoda as kspov
%rebase('views/base.tpl')

<h3>KAMEN ŠKARJE PAPIR OGENJ VODA</h3>

<BLOckquote>
    Dobrodošli v igri Kamen Škarje Papir Ogenj Voda. Igrali boste proti računalniku.
    Igralo se bo minimalno 14 iger 
</BLOckquote>

<h2>REZULTAT: {{kspov.delni_izid_igralca_1()}} : {{kspov.delni_izid_racunalnika_1()</h2>

% if ksp.zmaga_igralca() == True:
    <h1>BRAVO, ZMAGAL SI MOGOČNI STROJ Z IZIDOM: {{kspov.koncni_izid_igralca_1()}} : {{kspov.koncni_izid_racunalnika_1()}}</h1>
% else:
    <h1>IZGUBIL SI PROTI RAČUNALNIKU Z IZIDOM: {{kspov.koncni_izid_racunalnika_1()}} : {{kspov.koncni_izid_igralca_1()}}</h1>
%end

<form action="/ksp/" method="POST">
    <input type="radio" name="orozje" value="0">
    Kamen
    <input type="radio" name="orozje" value="1">
    Škarje
    <input type="radio" name="orozje" value="2">
    Papir
    <input type="radio" name="orozje" value="3">
    Ogenj
    <input type="radio" name="orozje" value="4">
    Voda
    <input type="submit" value="Potrdi">
</form>