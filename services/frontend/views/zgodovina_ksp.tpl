%rebase('views/base.tpl')
<div>
    <h2>ZGODOVINA IGER KŠP UPORABNIK: {{uporabnik}}</h2>

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
        <button type="button" class="zacetni" onclick="BrisiKSP()">BRIŠI</button>
        <button type="button" class="zacetni" onclick="window.location.href='/ksp/'">NAZAJ</button>
    </div>
</div>