# -*- coding: utf-8 -*-
"""Medidas HTML (HTML Content) da VoltEx Comercial."""
from model_measures import m, VEND_CTX

F = '91 HTML'

def num(x, fmt='#,0'):
    return f'FORMAT ( {x}, "{fmt}" )'

def mil(x):
    """Quantidade em milhares, texto com unidade pequena."""
    return f'FORMAT ( {x} / 1000, "#,0.0" ) & "<small>mil</small>"'

def mi(x):
    return f'"R$ " & FORMAT ( {x} / 1000000, "#,0.0" ) & "<small>mi</small>"'

def mi_plain(x):
    return f'"R$ " & FORMAT ( {x} / 1000000, "#,0.0" ) & " mi"'

def kpi(label, value, sub):
    return (f'"<div class=\'k\'><div class=\'kl\'>{label}</div><div class=\'kv\'>" & {value} & '
            f'"</div><div class=\'ks\'>" & {sub} & "</div></div>"')

def band(*items, h=78, cls=''):
    body = ' & '.join(items)
    return f'"<div class=\'vx kb {cls}\' style=\'height:{h}px\'>" & {body} & "</div>"'

def delta_var(v, suffix='vs mesmo período AA', empty='sem base no ano anterior'):
    """DAX que devolve <span> ▲/▼ x% + sufixo, a partir de uma expressão de variação."""
    return (f'IF ( ISBLANK ( {v} ), "<span class=\'mut\'>{empty}</span>", '
            f'"<span class=\'" & IF ( {v} >= 0, "up", "dn" ) & "\'>" & IF ( {v} >= 0, "▲ ", "▼ " ) '
            f'& FORMAT ( ABS ( {v} ), "0.0%" ) & "</span> {suffix}" )')

# ---------------------------------------------------------------- trilha e headers
m('Qtd Filtros Ativos', '''
ISFILTERED ( Dim_Calendario[Ano] ) + ISFILTERED ( Dim_Filial[Filial_Curta] )
    + ISFILTERED ( Dim_Vendedor[Nome_Vendedor] ) + ISFILTERED ( Dim_Produto[Linha] )
    + ISFILTERED ( Dim_Cliente[Ramo_Atividade] ) + ISFILTERED ( Dim_Municipio[Municipio] )''', '0', F)

def chip(col, label, many=3):
    return f'''IF ( ISFILTERED ( {col} ),
        VAR _n = COUNTROWS ( VALUES ( {col} ) )
        RETURN _Ch & "{label} · "
            & IF ( _n > {many}, _n & " selecionados", CONCATENATEX ( VALUES ( {col} ), {col}, ", ", {col}, ASC ) )
            & _Fe )'''

m('Trilha Filtros HTML', f'''
VAR _Ch = "<span class='chip'>"
VAR _Fe = "</span>"
VAR _Chips =
    {chip('Dim_Calendario[Ano]', 'Ano')}
    & {chip('Dim_Filial[Filial_Curta]', 'Filial')}
    & {chip('Dim_Vendedor[Nome_Vendedor]', 'Vendedor', 2)}
    & {chip('Dim_Produto[Linha]', 'Linha')}
    & {chip('Dim_Cliente[Ramo_Atividade]', 'Ramo', 2)}
    & {chip('Dim_Municipio[Municipio]', 'Município', 2)}
VAR _Per =
    "<span class='per'>" & FORMAT ( MIN ( Dim_Calendario[Data] ), "dd/mm/yy" ) & " – "
        & FORMAT ( MAX ( Dim_Calendario[Data] ), "dd/mm/yy" ) & "</span>"
RETURN
    _Per & IF ( _Chips = "", "<span class='per'>· visão consolidada, sem filtros</span>", _Chips )''', None, F)

PAGES = [
    ('Visao', 'VISÃO COMERCIAL', 'Volume, receita e cobertura num relance'),
    ('Metas', 'METAS · LINHA LEVE', 'Atingimento, tendência e disciplina de carteira por vendedor'),
    ('Carteira', 'CARTEIRA E COBERTURA', 'Quem compra, com que frequência e quem está esfriando'),
    ('Mercado', 'POTENCIAL E SHARE', 'Quanto do mercado de cada praça já é nosso'),
    ('SWOT', 'SWOT DA CARTEIRA', 'Porte do cliente × tendência contra o ano anterior'),
    ('Mix', 'MIX DE PRODUTOS', 'Linhas, famílias e o preço que cada uma sustenta'),
    ('Sucata', 'SUCATA · ECOCICLO', 'Cascos devidos, atraso e onde a sucata está parada'),
]
for key, ov, tit in PAGES:
    m(f'Header {key}', f'''
"<div class='vx hd' style='height:48px'><div><div class='ov'>{ov}</div><div class='tt'>{tit}</div></div><div class='chips'>"
    & [Trilha Filtros HTML] & "</div></div>"''', None, F)

m('Drawer Header HTML', '''
"<div class='vx' style='padding:2px 0'><div class='ov'>PAINEL DE FILTROS</div>"
    & "<div class='tt' style='font-size:20px'>Refinar a análise</div>"
    & "<div style='margin-top:10px;font-size:11px;color:#9AA6B0'>"
    & IF ( [Qtd Filtros Ativos] = 0, "Nenhum filtro ativo", [Qtd Filtros Ativos] & " filtro(s) ativo(s)" )
    & "</div><div class='chips' style='justify-content:flex-start;margin-top:8px;max-width:100%'>" & [Trilha Filtros HTML] & "</div></div>"''', None, F)

FONTE = '''"<span class='src'>Fonte: base comercial VoltEx · corte em " & FORMAT ( [Data Corte], "dd/mm/yyyy" ) & "</span>"'''

def insight(name, body_dax):
    m(name, body_dax + f'''
RETURN
    "<div class='vx ins' style='height:48px'><span class='dot'></span><div>" & _Frase & "</div>" & {FONTE} & "</div>"''', None, F)

PARCIAL = '''VAR _Corte = [Data Corte]
VAR _Parcial = DAY ( _Corte ) < DAY ( EOMONTH ( _Corte, 0 ) )
VAR _MesTxt = FORMAT ( _Corte, "mmmm" )'''

# ---------------------------------------------------------------- Aba 1
m('KPI Visao', f'''
VAR _vq = [Var % Qtd AA]
VAR _vf = [Var % Fat AA]
VAR _sh = [Share Potencial]
VAR _pp = [Var Share p.p.]
VAR _at = [% Atingimento Meta]
VAR _td = [% Tendência Meta]
RETURN
''' + band(
    kpi('Quantidade', num('[Quantidade]') + ' & "<small>un</small>"', delta_var('_vq')),
    kpi('Faturamento', mi('[Faturamento]'), delta_var('_vf')),
    kpi('Cobertura', 'FORMAT ( [% Cobertura], "0.0%" )',
        'FORMAT ( [Clientes Positivados], "#,0" ) & " de " & FORMAT ( [Carteira Ativa], "#,0" ) & " ativos compraram"'),
    kpi('Ticket por cliente', '"R$ " & FORMAT ( [Ticket por Cliente] / 1000, "#,0.0" ) & "<small>mil</small>"',
        '"preço médio R$ " & FORMAT ( [Preço Médio], "#,0" ) & "/un"'),
    kpi('Share do potencial', 'IF ( ISBLANK ( _sh ), "—", FORMAT ( _sh, "0.0%" ) )',
        'IF ( ISBLANK ( _sh ), "<span class=\'mut\'>potencial é por município</span>", '
        'IF ( ISBLANK ( _pp ), "gap de " & FORMAT ( [Gap Potencial] / 1000, "#,0" ) & " mil un", '
        '"<span class=\'" & IF ( _pp >= 0, "up", "dn" ) & "\'>" & FORMAT ( _pp, "+0.0;-0.0" ) & " p.p.</span> vs AA" ) )'),
    kpi('Meta Linha Leve', 'IF ( ISBLANK ( _at ), "—", FORMAT ( _at, "0%" ) )',
        'IF ( ISBLANK ( _at ), "<span class=\'mut\'>meta indisponível neste filtro</span>", '
        '"tendência <span class=\'" & IF ( _td >= 1, "up", IF ( _td >= 0.8, "wa", "dn" ) ) & "\'>" & FORMAT ( _td, "0%" ) & "</span>" )'),
    cls='k6'), None, F)

insight('Insight Visao', f'''
{PARCIAL}
VAR _vq = [Var % Qtd AA]
VAR _Frase =
    "<b>" & FORMAT ( [Quantidade], "#,0" ) & "</b> baterias no período"
        & IF ( ISBLANK ( _vq ), "", ", <b>" & FORMAT ( _vq, "+0.0%;-0.0%" ) & "</b> contra o mesmo recorte do ano anterior" )
        & ". A Linha Leve responde por <b>" & FORMAT ( [% Linha Leve no Volume], "0%" ) & "</b> do volume."
        & IF ( _Parcial, " " & UPPER ( LEFT ( _MesTxt, 1 ) ) & MID ( _MesTxt, 2, 20 ) & " é parcial (" & DAY ( _Corte ) & " de " & DAY ( EOMONTH ( _Corte, 0 ) ) & " dias) e aparece destacado no gráfico.", "" )''')

# ---------------------------------------------------------------- Aba 2
m('KPI Metas', '''
VAR _at = [% Atingimento Meta]
VAR _td = [% Tendência Meta]
VAR _vh = CALCULATE ( [Var % Qtd AA], KEEPFILTERS ( Dim_Produto[Familia] = "Linha Leve" ) )
RETURN
''' + band(
    kpi('Vendas Linha Leve', num('[Qtd Linha Leve]') + ' & "<small>un</small>"', delta_var('_vh')),
    kpi('Meta Linha Leve', 'IF ( ISBLANK ( [Meta Linha Leve] ), "—", ' + num('[Meta Linha Leve]') + ' & "<small>un</small>" )',
        'IF ( ISBLANK ( [Meta Linha Leve] ), "<span class=\'mut\'>sem meta neste filtro</span>", "gap de " & FORMAT ( [Gap Meta], "#,0" ) & " un" )'),
    kpi('Atingimento', 'IF ( ISBLANK ( _at ), "—", "<span class=\'" & IF ( _at >= 1, "up", IF ( _at >= 0.8, "", "dn" ) ) & "\'>" & FORMAT ( _at, "0.0%" ) & "</span>" )',
        '"realizado ÷ meta do período"'),
    kpi('Tendência', 'IF ( ISBLANK ( _td ), "—", FORMAT ( _td, "0.0%" ) )',
        '"mês corrente projetado até o fim"'),
    kpi('Abaixo de 80%', 'FORMAT ( [Vendedores Abaixo 80%], "0" ) & "<small>de " & FORMAT ( [Vendedores com Meta], "0" ) & "</small>"',
        '"vendedores"'),
), None, F)

insight('Insight Metas', '''
VAR _T =
    FILTER (
        ADDCOLUMNS ( VALUES ( Dim_Vendedor[Nome_Vendedor] ), "@at", [% Atingimento Meta] ),
        NOT ISBLANK ( [@at] )
    )
VAR _Pior = TOPN ( 1, _T, [@at], ASC )
VAR _Frase =
    IF (
        ISEMPTY ( _T ),
        "Meta Linha Leve indisponível neste filtro: ela existe só no grão vendedor × mês.",
        "<b>" & [Vendedores Abaixo 80%] & " de " & [Vendedores com Meta] & "</b> vendedores abaixo de 80% da meta da Linha Leve; o menor atingimento é <b>"
            & MAXX ( _Pior, Dim_Vendedor[Nome_Vendedor] ) & "</b> (" & FORMAT ( MAXX ( _Pior, [@at] ), "0%" ) & "). "
            & "<b>" & FORMAT ( [% Qtd Fora da UF], "0%" ) & "</b> do volume vai para clientes fora do estado da filial do vendedor: território e filial não se sobrepõem."
    )''')

# ---------------------------------------------------------------- Aba 3
m('KPI Carteira', '''
VAR _cob = [% Cobertura]
VAR _aa = [% Cobertura AA]
VAR _pp = ( _cob - _aa ) * 100
RETURN
''' + band(
    kpi('Carteira ativa', 'FORMAT ( [Carteira Ativa], "#,0" ) & "<small>clientes</small>"', 'FORMAT ( [Clientes Sem Compra 90d], "0" ) & " sem compra em 90 dias"'),
    kpi('Positivados', 'FORMAT ( [Clientes Positivados], "#,0" )', '"ativos com venda no período"'),
    kpi('Cobertura', 'FORMAT ( _cob, "0.0%" )',
        'IF ( ISBLANK ( _aa ), "<span class=\'mut\'>sem base no ano anterior</span>", "<span class=\'" & IF ( _pp >= 0, "up", "dn" ) & "\'>" & FORMAT ( _pp, "+0.0;-0.0;0.0" ) & " p.p.</span> vs AA" )'),
    kpi('Ticket por cliente', '"R$ " & FORMAT ( [Ticket por Cliente] / 1000, "#,0.0" ) & "<small>mil</small>"',
        'FORMAT ( DIVIDE ( [Quantidade], [Clientes Compradores] ), "#,0" ) & " un por cliente"'),
    kpi('Inativos comprando', '"<span class=\'" & IF ( [Clientes Não Ativos Comprando] > 0, "wa", "" ) & "\'>" & FORMAT ( [Clientes Não Ativos Comprando], "0" ) & "</span><small>clientes</small>"',
        'FORMAT ( [Qtd Clientes Não Ativos], "#,0" ) & " un para inativo/bloqueado"'),
), None, F)

insight('Insight Carteira', '''
VAR _Seg = TREATAS ( { "Campeões" }, Seg_RFQ[Segmento] )
VAR _nC = CALCULATE ( [RFQ Clientes], _Seg )
VAR _pC = CALCULATE ( [RFQ % Qtd 12M], _Seg )
VAR _nR = CALCULATE ( [RFQ Clientes], TREATAS ( { "Em risco" }, Seg_RFQ[Segmento] ) )
VAR _Frase =
    "<b>" & _nC & " clientes Campeões</b> compram " & FORMAT ( _pC, "0%" ) & " do volume dos últimos 12 meses"
        & IF ( _nR > 0, "; <b>" & _nR & "</b> " & IF ( _nR = 1, "está", "estão" ) & " em risco (sem compra há mais de 60 dias)", "; nenhum cliente em risco" ) & ". "
        & IF ( [Clientes Não Ativos Comprando] > 0,
            "<b>" & [Clientes Não Ativos Comprando] & " clientes inativos ou bloqueados</b> seguem comprando: revisar cadastro e crédito.",
            "Nenhuma venda para cliente inativo ou bloqueado." )''')

# ---------------------------------------------------------------- Aba 4
m('KPI Mercado', '''
VAR _sh = [Share Potencial]
VAR _pp = [Var Share p.p.]
RETURN
''' + band(
    kpi('Potencial do período', 'IF ( ISBLANK ( [Potencial Período] ), "—", ' + mil('[Potencial Período]') + ' )',
        'IF ( ISBLANK ( [Potencial Período] ), "<span class=\'mut\'>limpe vendedor, filial, linha e ramo</span>", FORMAT ( [Meses Equivalentes], "0.0" ) & " meses de mercado" )'),
    kpi('Vendido', mil('[Quantidade]'), '"baterias, venda + bonificação"'),
    kpi('Share', 'IF ( ISBLANK ( _sh ), "—", FORMAT ( _sh, "0.0%" ) )',
        'IF ( ISBLANK ( _pp ), "<span class=\'mut\'>sem base no ano anterior</span>", "<span class=\'" & IF ( _pp >= 0, "up", "dn" ) & "\'>" & FORMAT ( _pp, "+0.0;-0.0;0.0" ) & " p.p.</span> vs AA" )'),
    kpi('Gap não capturado', 'IF ( ISBLANK ( [Gap Potencial] ), "—", ' + mil('[Gap Potencial]') + ' )', '"baterias compradas da concorrência"'),
    kpi('Prospects contatáveis', 'FORMAT ( [Prospects Contatáveis], "#,0" )',
        'FORMAT ( [Prospects Pendentes], "#,0" ) & " pendentes de revisão"'),
), None, F)

insight('Insight Mercado', '''
VAR _T =
    ADDCOLUMNS (
        VALUES ( Dim_Municipio[Municipio] ),
        "@pot", CALCULATE ( SUM ( Dim_Municipio[Potencial_Baterias_Mes] ) ),
        "@sh", [Share Potencial],
        "@gap", [Gap Potencial],
        "@pr", [Prospects Contatáveis]
    )
VAR _TotPot = SUMX ( _T, [@pot] )
VAR _Big = TOPN ( 1, _T, [@gap], DESC )
VAR _Frase =
    IF (
        ISBLANK ( [Potencial Período] ),
        "O potencial é de mercado, por município: com filtro de vendedor, filial, linha ou ramo o share não tem denominador válido.",
        "<b>" & MAXX ( _Big, Dim_Municipio[Municipio] ) & "</b> concentra <b>" & FORMAT ( DIVIDE ( MAXX ( _Big, [@pot] ), _TotPot ), "0%" )
            & "</b> do potencial com share de <b>" & FORMAT ( MAXX ( _Big, [@sh] ), "0.0%" ) & "</b>: <b>"
            & FORMAT ( MAXX ( _Big, [@gap] ) / 1000, "#,0" ) & " mil</b> baterias não capturadas e <b>"
            & FORMAT ( MAXX ( _Big, [@pr] ), "#,0" ) & "</b> prospects liberados com telefone na praça."
    )''')

# ---------------------------------------------------------------- Aba 5
def swot_kpi(quad, label, cls):
    sel = f'TREATAS ( {{ "{quad}" }}, Seg_SWOT[Quadrante] )'
    return kpi(f"<span class='{cls}'>●</span> {label}",
               f'FORMAT ( CALCULATE ( [SWOT Clientes], {sel} ), "0" ) & "<small>clientes</small>"',
               f'FORMAT ( CALCULATE ( [SWOT % Qtd], {sel} ), "0%" ) & " do volume · " & '
               f'IF ( ISBLANK ( CALCULATE ( [SWOT Var Qtd], {sel} ) ), "sem AA", FORMAT ( CALCULATE ( [SWOT Var Qtd], {sel} ), "+0%;-0%" ) & " vs AA" )')

m('KPI SWOT', band(
    swot_kpi('Fortalezas', 'Fortalezas', 'up'),
    swot_kpi('Atenção', 'Atenção', 'wa'),
    swot_kpi('Oportunidades', 'Oportunidades', 'bl'),
    swot_kpi('Fraquezas', 'Fraquezas', 'dn'),
    kpi('Linha de corte', 'FORMAT ( [Média Qtd por Cliente], "#,0" ) & "<small>un</small>"', '"média por cliente no período"'),
), None, F)

insight('Insight SWOT', '''
VAR _A = TREATAS ( { "Atenção" }, Seg_SWOT[Quadrante] )
VAR _O = TREATAS ( { "Oportunidades" }, Seg_SWOT[Quadrante] )
VAR _Frase =
    IF (
        ISBLANK ( [Quantidade AA] ),
        "Sem base no ano anterior para este recorte: todo cliente aparece como crescendo. Selecione um ano com histórico.",
        "<b>" & CALCULATE ( [SWOT Clientes], _A ) & " clientes grandes estão encolhendo</b> (Atenção) e somam <b>"
            & FORMAT ( CALCULATE ( [SWOT % Qtd], _A ), "0%" ) & "</b> do volume: é a lista de visita desta semana. "
            & CALCULATE ( [SWOT Clientes], _O ) & " clientes pequenos crescendo formam a fila de desenvolvimento."
    )''')

# ---------------------------------------------------------------- Aba 6
m('Catalogo Linhas HTML', '''
VAR _Card =
    CONCATENATEX (
        VALUES ( Dim_Produto[Linha] ),
        VAR _img = CALCULATE ( MAX ( Dim_Produto[Imagem_Linha] ) )
        VAR _sh = [% Qtd s/ Total Produto]
        VAR _v = [Var % Qtd AA]
        RETURN
            "<div class='pc'><img src='" & _img & "'/><div><div class='pn'>" & Dim_Produto[Linha] & "</div><div class='pv'>"
                & FORMAT ( _sh, "0.0%" ) & "<small>do volume</small></div><div class='ks'>"
                & IF ( ISBLANK ( _v ), "R$ " & FORMAT ( [Preço Médio], "#,0" ) & "/un",
                    "<span class='" & IF ( _v >= 0, "up", "dn" ) & "'>" & FORMAT ( _v, "+0.0%;-0.0%" ) & "</span> · R$ " & FORMAT ( [Preço Médio], "#,0" ) & "/un" )
                & "</div></div></div>",
        "",
        CALCULATE ( MIN ( Dim_Produto[Ordem_Linha] ) ), ASC
    )
RETURN "<div class='vx pcs' style='height:76px'>" & _Card & "</div>"''', None, F)

insight('Insight Mix', '''
VAR _Tot = CALCULATE ( [Quantidade], ALLSELECTED ( Dim_Produto ) )
VAR _TotF = CALCULATE ( [Faturamento], ALLSELECTED ( Dim_Produto ) )
VAR _qP = DIVIDE ( CALCULATE ( [Quantidade], Dim_Produto[Linha] IN { "AGM", "EFB" } ), _Tot )
VAR _fP = DIVIDE ( CALCULATE ( [Faturamento], Dim_Produto[Linha] IN { "AGM", "EFB" } ), _TotF )
VAR _pS = CALCULATE ( [Preço Médio], Dim_Produto[Linha] = "SLI" )
VAR _pA = CALCULATE ( [Preço Médio], Dim_Produto[Linha] = "AGM" )
VAR _Frase =
    "<b>AGM e EFB</b> (start-stop) são <b>" & FORMAT ( _qP, "0%" ) & "</b> do volume e <b>" & FORMAT ( _fP, "0%" )
        & "</b> do faturamento. Uma AGM vale <b>" & FORMAT ( DIVIDE ( _pA, _pS ), "0.0" ) & "×</b> uma SLI (R$ "
        & FORMAT ( _pA, "#,0" ) & " vs R$ " & FORMAT ( _pS, "#,0" ) & "): cada troca de SLI por AGM no mesmo cliente multiplica o faturamento da venda."''')

# ---------------------------------------------------------------- Aba 7
m('KPI Sucata', '''
VAR _Corte = [Data Corte]
RETURN
''' + band(
    kpi('Sucata em aberto', 'FORMAT ( [Sucata em Aberto kg] / 1000, "#,0.0" ) & "<small>t</small>"',
        '"posição em " & FORMAT ( _Corte, "dd/mm/yyyy" )'),
    kpi('Lançamentos abertos', 'FORMAT ( [Lançamentos em Aberto], "#,0" )', 'FORMAT ( [Clientes com Sucata], "#,0" ) & " clientes devendo casco"'),
    kpi('Atraso médio', 'FORMAT ( [Atraso Médio Ponderado], "0" ) & "<small>dias</small>"', '"ponderado pelos kg em aberto"'),
    kpi('Acima de 60 dias', '"<span class=\'" & IF ( [% Sucata > 60 dias] > 0.3, "dn", "wa" ) & "\'>" & FORMAT ( [% Sucata > 60 dias], "0%" ) & "</span>"',
        'FORMAT ( [Sucata > 60 dias kg] / 1000, "#,0.0" ) & " t paradas há mais de 60 dias"'),
    kpi('Troca de casco no ato', 'FORMAT ( [% Vendas com Troca de Casco], "0.0%" )',
        'FORMAT ( [Baterias sem Casco], "#,0" ) & " vendidas sem casco no período"'),
), None, F)

m('Ranking Sucata HTML', f'''
{VEND_CTX}
VAR _T =
    CALCULATETABLE (
        ADDCOLUMNS (
            VALUES ( Dim_Cliente[Cliente_Rotulo] ),
            "@kg", CALCULATE ( SUM ( Fato_Sucata[Sucata_Em_Aberto_KG] ) ),
            "@d", CALCULATE ( MAX ( Fato_Sucata[Dias_Atraso] ) ),
            "@n", CALCULATE ( COUNTROWS ( Fato_Sucata ) )
        ),
        TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] )
    )
VAR _Top = TOPN ( 7, FILTER ( _T, [@kg] > 0 ), [@kg], DESC, Dim_Cliente[Cliente_Rotulo], ASC )
VAR _Max = MAXX ( _Top, [@kg] )
VAR _Rows =
    CONCATENATEX (
        _Top,
        "<div class='rk'><div class='rn'>" & Dim_Cliente[Cliente_Rotulo] & "<span>" & [@n] & " lanç. · até " & [@d] & " dias</span></div>"
            & "<div class='tr'><i style='width:" & FORMAT ( DIVIDE ( [@kg], _Max ) * 100, "0.0", "en-US" ) & "%;background:"
            & IF ( [@d] > 90, "#E5484D", IF ( [@d] > 60, "#F2B84B", "#FF8C00" ) ) & "'></i></div>"
            & "<b>" & FORMAT ( [@kg], "#,0" ) & " kg</b></div>",
        "", [@kg], DESC, Dim_Cliente[Cliente_Rotulo], ASC
    )
RETURN
    "<div class='vx'><div class='ov' style='color:#9AA6B0'>QUEM MAIS DEVE CASCO</div>"
        & "<div class='ks' style='margin:2px 0 10px'>kg em aberto · barra vermelha = mais de 90 dias</div>"
        & IF ( ISEMPTY ( _Top ), "<div class='ks'>Nenhuma sucata em aberto neste filtro.</div>", _Rows )
        & "<div class='nt'>Fato_Sucata é a posição atual dos cascos devidos: não responde ao filtro de ano.</div></div>"''', None, F)

insight('Insight Sucata', f'''
{VEND_CTX}
VAR _T =
    CALCULATETABLE (
        ADDCOLUMNS ( VALUES ( Dim_Municipio[Municipio] ), "@kg", CALCULATE ( SUM ( Fato_Sucata[Sucata_Em_Aberto_KG] ) ) ),
        TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] )
    )
VAR _Top = TOPN ( 1, _T, [@kg], DESC )
VAR _Frase =
    "<b>" & FORMAT ( [Sucata em Aberto kg] / 1000, "#,0.0" ) & " t</b> de sucata em aberto, <b>"
        & FORMAT ( [% Sucata > 60 dias], "0%" ) & "</b> com mais de 60 dias. <b>" & MAXX ( _Top, Dim_Municipio[Municipio] )
        & "</b> concentra " & FORMAT ( DIVIDE ( MAXX ( _Top, [@kg] ), SUMX ( _T, [@kg] ) ), "0%" )
        & ". Para o EcoCiclo, cada bateria vendida sem casco no ato vira débito a cobrar: <b>"
        & FORMAT ( 1 - [% Vendas com Troca de Casco], "0%" ) & "</b> das vendas do período."''')

# ---------------------------------------------------------------- Tooltips
m('TT Mes HTML', '''
VAR _mes = FORMAT ( MAX ( Dim_Calendario[Inicio_Mes] ), "mmmm/yyyy" )
VAR _Tot = [Quantidade]
VAR _v = [Var % Qtd AA]
VAR _parc = SELECTEDVALUE ( Dim_Calendario[Status_Mes] ) = "Parcial"
VAR _Bar = "<div class='tb'><span>"
VAR _Lin =
    CONCATENATEX (
        VALUES ( Dim_Produto[Linha] ),
        VAR _s = DIVIDE ( [Quantidade], _Tot )
        RETURN _Bar & Dim_Produto[Linha] & "</span><div class='tr'><i style='width:" & FORMAT ( _s * 100, "0.0", "en-US" )
            & "%'></i></div><b>" & FORMAT ( _s, "0%" ) & "</b></div>",
        "", CALCULATE ( MIN ( Dim_Produto[Ordem_Linha] ) ), ASC
    )
RETURN
    "<div class='vx tt2'><div class='ov'>" & UPPER ( _mes ) & IF ( _parc, " · PARCIAL", "" ) & "</div>"
        & "<div class='kv' style='font-size:24px'>" & FORMAT ( _Tot, "#,0" ) & "<small>baterias</small></div>"
        & "<div class='ks'>" & IF ( ISBLANK ( _v ), "sem base no ano anterior", "<span class='" & IF ( _v >= 0, "up", "dn" ) & "'>"
            & IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%" ) & "</span> vs mesmo mês do ano anterior" ) & "</div>"
        & "<div class='ov' style='color:#9AA6B0;margin-top:12px'>MIX POR LINHA</div>" & _Lin
        & "<div class='tf'><div>Cobertura <b>" & FORMAT ( [% Cobertura], "0.0%" ) & "</b></div><div>Faturamento <b>"
        & FORMAT ( [Faturamento] / 1000000, "#,0.00" ) & " mi</b></div><div>Linha Leve <b>" & FORMAT ( [% Linha Leve no Volume], "0%" ) & "</b></div></div></div>"''', None, F)

m('TT Vendedor HTML', '''
VAR _nm = SELECTEDVALUE ( Dim_Vendedor[Nome_Vendedor], "Vários vendedores" )
VAR _ini = IF ( HASONEVALUE ( Dim_Vendedor[Nome_Vendedor] ), "V" & SUBSTITUTE ( _nm, "Vendedor ", "" ), "··" )
VAR _rota = SELECTEDVALUE ( Dim_Vendedor[Area_Rota], "—" )
VAR _fil = SELECTEDVALUE ( Dim_Vendedor[Filial_Vendedor], "—" )
VAR _at = [% Atingimento Meta]
VAR _td = [% Tendência Meta]
VAR _w = MIN ( COALESCE ( _at, 0 ), 1.5 ) / 1.5 * 100
RETURN
    "<div class='vx tt2'><div style='display:flex;gap:12px;align-items:center'><div class='av'>" & _ini & "</div><div><div class='pn' style='font-size:15px'>"
        & _nm & "</div><div class='ks'>" & _rota & " · " & _fil & "</div></div></div>"
        & "<div class='tf' style='margin-top:12px'><div>Linha Leve<br><b>" & FORMAT ( [Qtd Linha Leve], "#,0" ) & "</b></div><div>Meta<br><b>"
        & IF ( ISBLANK ( [Meta Linha Leve] ), "—", FORMAT ( [Meta Linha Leve], "#,0" ) ) & "</b></div><div>Cobertura<br><b>"
        & FORMAT ( [% Cobertura], "0%" ) & "</b></div></div>"
        & "<div class='ov' style='color:#9AA6B0;margin-top:12px'>ATINGIMENTO · TENDÊNCIA " & FORMAT ( _td, "0%" ) & "</div>"
        & "<div class='tr' style='height:8px;margin-top:6px'><i style='width:" & FORMAT ( _w, "0.0", "en-US" ) & "%;background:"
        & IF ( _at < 0.8, "#E5484D", "#FF8C00" ) & "'></i></div><div class='ks' style='margin-top:4px'>" & FORMAT ( _at, "0%" )
        & " · carteira " & FORMAT ( [Carteira Ativa], "0" ) & " ativos · " & FORMAT ( [% Qtd Fora da UF], "0%" ) & " fora da UF da filial</div></div>"''', None, F)

m('TT Produto HTML', '''
VAR _one = HASONEVALUE ( Dim_Produto[ID_Produto] )
VAR _img = IF ( _one, SELECTEDVALUE ( Dim_Produto[Imagem_Base64] ), CALCULATE ( MAX ( Dim_Produto[Imagem_Linha] ) ) )
VAR _nm =
    IF ( _one, SELECTEDVALUE ( Dim_Produto[Produto] ),
        IF ( HASONEVALUE ( Dim_Produto[Linha] ), "Linha " & SELECTEDVALUE ( Dim_Produto[Linha] ), "Vários produtos" ) )
VAR _sub =
    IF ( _one, SELECTEDVALUE ( Dim_Produto[Codigo_Original] ) & " · " & SELECTEDVALUE ( Dim_Produto[Familia] ),
        CONCATENATEX ( VALUES ( Dim_Produto[Familia] ), Dim_Produto[Familia], ", " ) )
VAR _v = [Var % Qtd AA]
VAR _of =
    CONCATENATEX (
        VALUES ( Dim_Produto[ID_Produto_Oficial] ),
        LOOKUPVALUE ( Dim_Catalogo[Produto_Oficial], Dim_Catalogo[ID_Produto_Oficial], Dim_Produto[ID_Produto_Oficial] ),
        " · "
    )
RETURN
    "<div class='vx tt2'><div style='display:flex;gap:12px;align-items:center'>"
        & IF ( ISBLANK ( _img ), "", "<img class='timg' src='" & _img & "'/>" )
        & "<div><div class='ov'>" & UPPER ( CONCATENATEX ( VALUES ( Dim_Produto[Linha] ), Dim_Produto[Linha], " · " ) ) & "</div><div class='pn' style='font-size:15px'>" & _nm & "</div>"
        & "<div class='ks'>" & _sub & "</div></div></div>"
        & "<div class='tf' style='margin-top:10px'><div>Quantidade<br><b>" & FORMAT ( [Quantidade], "#,0" ) & "</b></div><div>Faturamento<br><b>"
        & FORMAT ( [Faturamento] / 1000000, "#,0.00" ) & " mi</b></div><div>Preço médio<br><b>R$ " & FORMAT ( [Preço Médio], "#,0" ) & "</b></div></div>"
        & "<div class='tf'><div>vs AA<br><b class='" & IF ( _v < 0, "dn", "up" ) & "'>" & IF ( ISBLANK ( _v ), "—", FORMAT ( _v, "+0.0%;-0.0%" ) ) & "</b></div><div>Garantia<br><b>"
        & FORMAT ( [% Garantia s/ Venda], "0.0%" ) & "</b></div><div>Sem casco<br><b>" & FORMAT ( 1 - [% Vendas com Troca de Casco], "0%" ) & "</b></div></div>"
        & "<div class='nt' style='margin-top:8px'>Catálogo oficial: " & _of & "</div></div>"''', None, F)

m('Capa HTML', '''
VAR _Fil = CONCATENATEX ( VALUES ( Dim_Filial[Filial_Curta] ), "<div>" & Dim_Filial[Filial_Curta] & "</div>", "", Dim_Filial[Filial_Curta], ASC )
RETURN
    "<div class='vx'><div class='cv-ov'>VOLTEX BATERIAS · PERFORMANCE COMERCIAL</div>"
        & "<div class='cv-t'>Vendas, carteira<br>e mercado em <span>um só fluxo</span></div>"
        & "<div class='cv-s'>Metas da Linha Leve, cobertura de carteira, share sobre o potencial de cada praça, SWOT de clientes e sucata do EcoCiclo. "
        & FORMAT ( [Itens de Nota], "#,0" ) & " itens de nota até " & FORMAT ( [Data Corte], "dd/mm/yyyy" ) & ".</div>"
        & "<div class='cv-l'>" & _Fil & "<div>" & FORMAT ( [Carteira Ativa], "0" ) & " clientes ativos</div><div>"
        & COUNTROWS ( Dim_Municipio ) & " praças</div></div></div>"''', None, F)
