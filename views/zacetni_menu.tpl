%rebase('views/base.tpl')
<div class="pozdrav">
    <h2>DOBRODOŠLI {{uporabnik}} IZBERITE SI IGRO </h2>
    
    <form action="/nova_igra_ksp/" method="GET">
        <button type="submit" class="gumb">KŠP</button>
    </form>
    <form action="/nova_igra_kspov/" method="GET">
        <button type="submit" class="gumb">KŠPOV</button>
    </form>
</div>



