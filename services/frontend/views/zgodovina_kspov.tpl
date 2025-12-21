%rebase('views/base.tpl')
<div>
    <h2>ZGODOVINA IGER KŠPOV UPORABNIK: {{uporabnik}}</h2>

    % if igre:
        <ul>
            % for igra in igre:
                <li>ID {{igra['game_id']}} : igralec - {{igra['player']}} računalnik - {{igra['computer']}}</li>
            % end
        </ul>
    % else:
        <p>Ni še odigranih iger.</p>
    % end
    <div class="back">
        <button type="button" class="zacetni" onclick="BrisiKSPOV()">BRIŠI</button>
        <button type="button" class="zacetni" onclick="window.location.href='/kspov'">NAZAJ</button>
    </div>
</div>