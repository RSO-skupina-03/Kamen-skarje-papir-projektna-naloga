%rebase('views/base.tpl')
<div>
    <h2>Zgodovina iger</h2>

    % if igre:
        <ul>
            % for igra in igre:
                <li>{{ igra }}</li>
            % end
        </ul>
    % else:
        <p>Ni še odigranih iger.</p>
    % end
    <div class="back">
        <button type="button" class="zacetni" onclick="window.location.href='/end/'">XML</button>
        <button type="button" class="zacetni" onclick="window.location.href='/end/'">JSON</button>
        <button type="button" class="zacetni" onclick="window.location.href='/end/'">BRIŠI</button>
        <button type="button" class="zacetni" onclick="window.location.href='/ksp/'">NAZAJ</button>
    </div>
</div>