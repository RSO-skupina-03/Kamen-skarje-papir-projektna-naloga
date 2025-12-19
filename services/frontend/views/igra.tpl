%rebase('views/base.tpl')
<div class="pozdrav">
    <h2>DOBRODOŠLI {{uporabnik}} IZBERITE SI IGRO </h2>
    
    <form action="/ksp" method="GET">
        <button type="submit" class="gumb">KŠP</button>
    </form>
    <form action="/kspov/" method="GET">
        <button type="submit" class="gumb">KŠPOV</button>
    </form>
</div>



