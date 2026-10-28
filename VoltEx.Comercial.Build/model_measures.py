# -*- coding: utf-8 -*-
"""Medidas DAX da VoltEx Comercial: (nome, expressão, formato, pasta)."""

BRL = 'R$ #,0'
BRL2 = 'R$ #,0.00'
PCT = '0.0%'
INT = '#,0'
DEC1 = '#,0.0'
VAR_PCT = '+0.0%;-0.0%;0.0%'

M = []
AA = lambda m: f'''
-- Mesmo recorte de dias, 12 meses antes. SAMEPERIODLASTYEAR estende até o fim do mês
-- quando a seleção termina no último dia do calendário (data de corte) e infla o AA.
VAR _Dias =
    SELECTCOLUMNS ( VALUES ( Dim_Calendario[Data] ), "Data", EDATE ( Dim_Calendario[Data], -12 ) )
RETURN
    CALCULATE ( {m}, REMOVEFILTERS ( Dim_Calendario ), TREATAS ( _Dias, Dim_Calendario[Data] ) )'''
def m(name, expr, fmt=None, folder=None):
    M.append((name, expr.strip('\n'), fmt, folder))

# Vendedores visíveis no contexto, respeitando também o filtro de filial.
# Dim_Vendedor e Dim_Filial não filtram Dim_Cliente/Fato_Sucata por relacionamento
# (evita caminho ambíguo até Fato_Vendas), então a carteira usa TREATAS.
VEND_CTX = '''VAR _VendCtx =
    CALCULATETABLE (
        VALUES ( Dim_Vendedor[ID_Vendedor] ),
        TREATAS ( VALUES ( Dim_Filial[ID_Filial] ), Dim_Vendedor[ID_Filial] )
    )'''

# ---------------------------------------------------------------- 01 Vendas
F = '01 Vendas'
m('Quantidade', '''
-- Regra do comercial: venda + bonificação. Troca em garantia fica fora.
CALCULATE (
    SUM ( Fato_Vendas[Quantidade] ),
    KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] IN { "Venda", "Bonificacao" } )
)''', INT, F)
m('Qtd Venda', '''
CALCULATE ( SUM ( Fato_Vendas[Quantidade] ), KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Venda" ) )''', INT, F)
m('Qtd Bonificação', '''
CALCULATE ( SUM ( Fato_Vendas[Quantidade] ), KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Bonificacao" ) )''', INT, F)
m('Qtd Troca Garantia', '''
CALCULATE ( SUM ( Fato_Vendas[Quantidade] ), KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Troca Garantia" ) )''', INT, F)
m('% Garantia s/ Venda', 'DIVIDE ( [Qtd Troca Garantia], [Qtd Venda] )', '0.00%', F)
m('Faturamento', '''
-- Bonificação e troca em garantia já vêm com faturamento zero da origem
SUM ( Fato_Vendas[Faturamento_RS] )''', BRL, F)
m('Preço Médio', 'DIVIDE ( [Faturamento], [Qtd Venda] )', BRL2, F)
m('Itens de Nota', '''
CALCULATE ( COUNTROWS ( Fato_Vendas ), KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Venda" ) )''', INT, F)
m('Quantidade AA', AA('[Quantidade]'), INT, F)
m('Faturamento AA', AA('[Faturamento]'), BRL, F)
m('Var % Qtd AA', '''
-- O calendário termina na data de corte, então "ano corrente" já é YTD
-- e o AA compara o mesmo recorte de dias do ano anterior.
VAR _AA = [Quantidade AA]
RETURN IF ( NOT ISBLANK ( _AA ), DIVIDE ( [Quantidade] - _AA, _AA ) )''', VAR_PCT, F)
m('Var % Fat AA', '''
VAR _AA = [Faturamento AA]
RETURN IF ( NOT ISBLANK ( _AA ), DIVIDE ( [Faturamento] - _AA, _AA ) )''', VAR_PCT, F)
m('Quantidade Mês Anterior', '''
CALCULATE ( [Quantidade], DATEADD ( Dim_Calendario[Data], -1, MONTH ) )''', INT, F)
m('% Qtd s/ Total Produto', '''
DIVIDE ( [Quantidade], CALCULATE ( [Quantidade], ALLSELECTED ( Dim_Produto ) ) )''', PCT, F)
m('% Fat s/ Total Produto', '''
DIVIDE ( [Faturamento], CALCULATE ( [Faturamento], ALLSELECTED ( Dim_Produto ) ) )''', PCT, F)
m('Data Corte', '''
-- Último dia carregado: Dim_Calendario vai até a data de corte (hoje)
CALCULATE ( MAX ( Dim_Calendario[Data] ), REMOVEFILTERS ( Dim_Calendario ) )''', 'dd/mm/yyyy', F)
m('Qtd Fora da UF da Filial', '''
-- Volume vendido a clientes de outro estado que não o da filial do vendedor
SUMX (
    FILTER (
        Fato_Vendas,
        Fato_Vendas[Tipo_Operacao] IN { "Venda", "Bonificacao" }
            && RELATED ( Dim_Filial[UF_Filial] ) <> RELATED ( Dim_Municipio[UF] )
    ),
    Fato_Vendas[Quantidade]
) + 0''', INT, F)
m('% Qtd Fora da UF', 'DIVIDE ( [Qtd Fora da UF da Filial], [Quantidade] )', PCT, F)

# ---------------------------------------------------------------- 02 Metas
F = '02 Metas'
m('Qtd Linha Leve', '''
CALCULATE ( [Quantidade], KEEPFILTERS ( Dim_Produto[Familia] = "Linha Leve" ) )''', INT, F)
m('% Linha Leve no Volume', 'DIVIDE ( [Qtd Linha Leve], [Quantidade] )', PCT, F)
m('Meta Linha Leve', f'''
-- Meta mora no grão vendedor × mês, só para a Linha Leve (40–72Ah).
-- Fica em branco com filtro fora desse grão (produto, cliente, município) ou abaixo do mês.
VAR _ForaDoGrao =
    ISFILTERED ( Dim_Produto ) || ISFILTERED ( Dim_Cliente ) || ISFILTERED ( Dim_Municipio )
VAR _AbaixoDoMes = ISINSCOPE ( Dim_Calendario[Data] )
VAR _Meses = VALUES ( Dim_Calendario[Inicio_Mes] )
{VEND_CTX}
RETURN
    IF (
        NOT _ForaDoGrao && NOT _AbaixoDoMes,
        CALCULATE (
            SUM ( Fato_Metas[Meta_Quantidade] ),
            REMOVEFILTERS ( Dim_Calendario ),
            TREATAS ( _Meses, Fato_Metas[Data_Mes] ),
            TREATAS ( _VendCtx, Fato_Metas[ID_Vendedor] )
        )
    )''', INT, F)
m('% Atingimento Meta', 'DIVIDE ( [Qtd Linha Leve], [Meta Linha Leve] )', PCT, F)
m('Gap Meta', '''
VAR _g = [Meta Linha Leve] - [Qtd Linha Leve]
RETURN IF ( NOT ISBLANK ( [Meta Linha Leve] ), MAX ( _g, 0 ) )''', INT, F)
m('Projeção Linha Leve', '''
-- Realizado + extrapolação linear do mês corrente (parcial) até o fim do mês
VAR _Corte = [Data Corte]
VAR _IniMes = DATE ( YEAR ( _Corte ), MONTH ( _Corte ), 1 )
VAR _Fator = DIVIDE ( DAY ( EOMONTH ( _Corte, 0 ) ), DAY ( _Corte ) ) - 1
VAR _MesAtual =
    CALCULATE ( [Qtd Linha Leve], KEEPFILTERS ( Dim_Calendario[Inicio_Mes] = _IniMes ) )
RETURN
    IF ( NOT ISBLANK ( [Qtd Linha Leve] ), [Qtd Linha Leve] + COALESCE ( _MesAtual, 0 ) * _Fator )''', INT, F)
m('% Tendência Meta', 'DIVIDE ( [Projeção Linha Leve], [Meta Linha Leve] )', PCT, F)
m('Vendedores Abaixo 80%', '''
COUNTROWS (
    FILTER ( VALUES ( Dim_Vendedor[ID_Vendedor] ), [% Atingimento Meta] < 0.8 )
) + 0''', INT, F)
m('Vendedores com Meta', '''
COUNTROWS (
    FILTER ( VALUES ( Dim_Vendedor[ID_Vendedor] ), NOT ISBLANK ( [Meta Linha Leve] ) )
) + 0''', INT, F)

# ---------------------------------------------------------------- 03 Carteira
F = '03 Carteira e Cobertura'
m('Carteira Ativa', f'''
-- Clientes com situação "Ativo" na carteira dos vendedores do contexto
{VEND_CTX}
RETURN
    CALCULATE (
        COUNTROWS ( Dim_Cliente ),
        KEEPFILTERS ( Dim_Cliente[Situacao] = "Ativo" ),
        TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] )
    )''', INT, F)
m('Clientes Positivados', '''
-- Clientes ativos com pelo menos uma venda no período
CALCULATE (
    DISTINCTCOUNT ( Fato_Vendas[ID_Cliente] ),
    KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Venda" ),
    KEEPFILTERS ( Dim_Cliente[Situacao] = "Ativo" )
)''', INT, F)
m('% Cobertura', '''
-- Positivação: ativos que compraram ÷ carteira ativa
DIVIDE ( [Clientes Positivados], [Carteira Ativa] )''', PCT, F)
m('% Cobertura AA', AA('[% Cobertura]'), PCT, F)
m('Clientes Compradores', '''
CALCULATE ( DISTINCTCOUNT ( Fato_Vendas[ID_Cliente] ), KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Venda" ) )''', INT, F)
m('Ticket por Cliente', 'DIVIDE ( [Faturamento], [Clientes Compradores] )', BRL, F)
m('Ticket por Cliente AA', AA('[Ticket por Cliente]'), BRL, F)
m('Qtd Clientes Não Ativos', '''
-- Governança: volume faturado para cliente inativo ou bloqueado
CALCULATE ( [Quantidade], KEEPFILTERS ( Dim_Cliente[Situacao] <> "Ativo" ) ) + 0''', INT, F)
m('Clientes Não Ativos Comprando', '''
CALCULATE (
    DISTINCTCOUNT ( Fato_Vendas[ID_Cliente] ),
    KEEPFILTERS ( Fato_Vendas[Tipo_Operacao] = "Venda" ),
    KEEPFILTERS ( Dim_Cliente[Situacao] <> "Ativo" )
) + 0''', INT, F)
m('Clientes Sem Compra 90d', f'''
-- Ativos da carteira sem venda nos 90 dias até o fim do período
VAR _Fim = MAX ( Dim_Calendario[Data] )
{VEND_CTX}
VAR _Carteira =
    CALCULATETABLE (
        VALUES ( Dim_Cliente[ID_Cliente] ),
        KEEPFILTERS ( Dim_Cliente[Situacao] = "Ativo" ),
        TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] )
    )
VAR _Compraram =
    CALCULATETABLE (
        VALUES ( Fato_Vendas[ID_Cliente] ),
        DATESBETWEEN ( Dim_Calendario[Data], _Fim - 89, _Fim ),
        Fato_Vendas[Tipo_Operacao] = "Venda"
    )
RETURN COUNTROWS ( EXCEPT ( _Carteira, _Compraram ) ) + 0''', INT, F)

# ---------------------------------------------------------------- 04 RFQ
F = '04 RFQ'
# Tabela de clientes com Recência, Frequência e Quantidade 12M até o fim do período.
# A média de referência é a da base inteira (independe de slicer de cliente/vendedor),
# para o segmento de um cliente não mudar quando o usuário filtra a carteira.
RFQ_BASE = f'''VAR _Fim = MAX ( Dim_Calendario[Data] )
VAR _Ini = EDATE ( _Fim, -12 ) + 1
{VEND_CTX}
VAR _Clientes =
    CALCULATETABLE ( VALUES ( Dim_Cliente[ID_Cliente] ), TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] ) )
VAR _Media =
    CALCULATE (
        AVERAGEX (
            FILTER (
                ADDCOLUMNS ( VALUES ( Dim_Cliente[ID_Cliente] ), "@q", [Quantidade] ),
                [@q] > 0
            ),
            [@q]
        ),
        DATESBETWEEN ( Dim_Calendario[Data], _Ini, _Fim ),
        REMOVEFILTERS ( Dim_Cliente ),
        REMOVEFILTERS ( Dim_Municipio ),
        REMOVEFILTERS ( Dim_Vendedor ),
        REMOVEFILTERS ( Dim_Filial )
    )
VAR _T =
    ADDCOLUMNS (
        _Clientes,
        "@q", CALCULATE ( [Quantidade], DATESBETWEEN ( Dim_Calendario[Data], _Ini, _Fim ) ),
        "@v", CALCULATE ( [Faturamento], DATESBETWEEN ( Dim_Calendario[Data], _Ini, _Fim ) ),
        "@f", CALCULATE (
            DISTINCTCOUNT ( Fato_Vendas[Mes_Ref] ),
            DATESBETWEEN ( Dim_Calendario[Data], _Ini, _Fim ),
            Fato_Vendas[Tipo_Operacao] = "Venda"
        ),
        "@u", CALCULATE (
            MAX ( Fato_Vendas[Data_Emissao] ),
            REMOVEFILTERS ( Dim_Calendario ),
            Dim_Calendario[Data] <= _Fim,
            Fato_Vendas[Tipo_Operacao] = "Venda"
        )
    )
VAR _S =
    ADDCOLUMNS (
        _T,
        "@seg",
            SWITCH (
                TRUE (),
                COALESCE ( [@q], 0 ) = 0, "Sem compra 12M",
                _Fim - [@u] > 60, "Em risco",
                [@f] >= 10 && [@q] >= 1.2 * _Media, "Campeões",
                [@f] >= 8 && [@q] >= 0.8 * _Media, "Leais",
                "Ocasionais"
            )
    )
VAR _Seg = SELECTEDVALUE ( Seg_RFQ[Segmento] )
VAR _Sel = FILTER ( _S, ISBLANK ( _Seg ) || [@seg] = _Seg )'''

m('RFQ Clientes', RFQ_BASE + '\nRETURN COUNTROWS ( _Sel ) + 0', INT, F)
m('RFQ Qtd 12M', RFQ_BASE + '\nRETURN SUMX ( _Sel, [@q] ) + 0', INT, F)
m('RFQ Fat 12M', RFQ_BASE + '\nRETURN SUMX ( _Sel, [@v] ) + 0', BRL, F)
m('RFQ % Qtd 12M', RFQ_BASE + '\nRETURN DIVIDE ( SUMX ( _Sel, [@q] ), SUMX ( _S, [@q] ) ) + 0', PCT, F)
m('RFQ % Clientes', RFQ_BASE + '\nRETURN DIVIDE ( COUNTROWS ( _Sel ), COUNTROWS ( _S ) ) + 0', PCT, F)
m('RFQ Ordem Segmento', 'MIN ( Seg_RFQ[Ordem] )', '0', F)

# ---------------------------------------------------------------- 05 Potencial e Share
F = '05 Potencial e Share'
POT_GUARD = '''ISFILTERED ( Dim_Vendedor ) || ISFILTERED ( Dim_Filial )
    || ISFILTERED ( Dim_Produto ) || ISFILTERED ( Dim_Cliente )'''
m('Meses Equivalentes', '''
-- Fração de mês coberta pelo contexto (o mês corrente parcial conta pelos dias decorridos)
SUMX (
    VALUES ( Dim_Calendario[Inicio_Mes] ),
    DIVIDE (
        CALCULATE ( COUNTROWS ( Dim_Calendario ) ),
        DAY ( EOMONTH ( Dim_Calendario[Inicio_Mes], 0 ) )
    )
)''', '0.00', F)
m('Potencial Mensal', f'''
-- Potencial é de mercado (município). Não se reparte por vendedor, filial, produto ou cliente.
IF ( NOT ( {POT_GUARD} ), SUM ( Dim_Municipio[Potencial_Baterias_Mes] ) )''', INT, F)
m('Potencial Período', 'IF ( NOT ISBLANK ( [Potencial Mensal] ), [Potencial Mensal] * [Meses Equivalentes] )', INT, F)
m('Share Potencial', 'DIVIDE ( [Quantidade], [Potencial Período] )', PCT, F)
m('Share Potencial AA', AA('[Share Potencial]'), PCT, F)
m('Var Share p.p.', '''
VAR _aa = [Share Potencial AA]
RETURN IF ( NOT ISBLANK ( _aa ) && NOT ISBLANK ( [Share Potencial] ), ( [Share Potencial] - _aa ) * 100 )''', '+0.0;-0.0;0.0', F)
m('Gap Potencial', '''
VAR _p = [Potencial Período]
RETURN IF ( NOT ISBLANK ( _p ), MAX ( _p - [Quantidade], 0 ) )''', INT, F)
m('Prospects Total', 'COUNTROWS ( Fato_Prospects ) + 0', INT, F)
m('Prospects Liberados', '''
CALCULATE ( COUNTROWS ( Fato_Prospects ), KEEPFILTERS ( Fato_Prospects[Status_Prospect] = "Liberado" ) ) + 0''', INT, F)
m('Prospects Contatáveis', '''
-- Liberados para abordagem e com telefone cadastrado
CALCULATE (
    COUNTROWS ( Fato_Prospects ),
    KEEPFILTERS ( Fato_Prospects[Status_Prospect] = "Liberado" ),
    KEEPFILTERS ( Fato_Prospects[Possui_Telefone] = "Sim" )
) + 0''', INT, F)
m('Prospects Pendentes', '''
CALCULATE ( COUNTROWS ( Fato_Prospects ), KEEPFILTERS ( Fato_Prospects[Status_Prospect] = "Pendente Revisão" ) ) + 0''', INT, F)

# ---------------------------------------------------------------- 06 SWOT
F = '06 SWOT'
# SWOT do cliente: porte (quantidade no período vs média da base) × tendência (vs mesmo período AA)
SWOT_BASE = f'''{VEND_CTX}
VAR _Media =
    CALCULATE (
        AVERAGEX (
            FILTER ( ADDCOLUMNS ( VALUES ( Dim_Cliente[ID_Cliente] ), "@q", [Quantidade] ), [@q] > 0 ),
            [@q]
        ),
        REMOVEFILTERS ( Dim_Cliente ),
        REMOVEFILTERS ( Dim_Municipio ),
        REMOVEFILTERS ( Dim_Vendedor ),
        REMOVEFILTERS ( Dim_Filial )
    )
VAR _T =
    FILTER (
        ADDCOLUMNS (
            CALCULATETABLE ( VALUES ( Dim_Cliente[ID_Cliente] ), TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] ) ),
            "@q", [Quantidade],
            "@aa", [Quantidade AA]
        ),
        [@q] > 0
    )
VAR _S =
    ADDCOLUMNS (
        _T,
        "@quad",
            VAR _grande = [@q] >= _Media
            VAR _cresce = [@q] >= COALESCE ( [@aa], 0 )
            RETURN
                SWITCH (
                    TRUE (),
                    _grande && _cresce, "Fortalezas",
                    NOT _grande && _cresce, "Oportunidades",
                    NOT _grande && NOT _cresce, "Fraquezas",
                    "Atenção"
                )
    )
VAR _Quad = SELECTEDVALUE ( Seg_SWOT[Quadrante] )
VAR _Sel = FILTER ( _S, ISBLANK ( _Quad ) || [@quad] = _Quad )'''
m('SWOT Clientes', SWOT_BASE + '\nRETURN COUNTROWS ( _Sel ) + 0', INT, F)
m('SWOT Qtd', SWOT_BASE + '\nRETURN SUMX ( _Sel, [@q] ) + 0', INT, F)
m('SWOT % Qtd', SWOT_BASE + '\nRETURN DIVIDE ( SUMX ( _Sel, [@q] ), SUMX ( _S, [@q] ) ) + 0', PCT, F)
m('SWOT Var Qtd', SWOT_BASE + '''
VAR _aa = SUMX ( _Sel, [@aa] )
RETURN IF ( _aa > 0, DIVIDE ( SUMX ( _Sel, [@q] ) - _aa, _aa ) )''', VAR_PCT, F)
m('Média Qtd por Cliente', '''
-- Linha de corte do porte no SWOT: média da base inteira no período
CALCULATE (
    AVERAGEX (
        FILTER ( ADDCOLUMNS ( VALUES ( Dim_Cliente[ID_Cliente] ), "@q", [Quantidade] ), [@q] > 0 ),
        [@q]
    ),
    REMOVEFILTERS ( Dim_Cliente ),
    REMOVEFILTERS ( Dim_Municipio ),
    REMOVEFILTERS ( Dim_Vendedor ),
    REMOVEFILTERS ( Dim_Filial )
)''', DEC1, F)

# ---------------------------------------------------------------- 07 Sucata
F = '07 Sucata e EcoCiclo'
def suc(name, inner, fmt, comment=''):
    m(name, f'''{comment}{VEND_CTX}
RETURN
    CALCULATE ( {inner}, TREATAS ( _VendCtx, Dim_Cliente[ID_Vendedor] ) )''', fmt, F)
suc('Sucata em Aberto kg', 'SUM ( Fato_Sucata[Sucata_Em_Aberto_KG] )', INT,
    '-- Posição na data de corte: Fato_Sucata não se liga ao calendário\n')
suc('Sucata Devida kg', 'SUM ( Fato_Sucata[Sucata_Devida_KG] )', INT)
suc('Sucata Entregue kg', 'SUM ( Fato_Sucata[Sucata_Entregue_KG] )', INT)
suc('Lançamentos em Aberto', 'COUNTROWS ( Fato_Sucata )', INT)
suc('Clientes com Sucata', 'DISTINCTCOUNT ( Fato_Sucata[ID_Cliente] )', INT)
suc('Sucata > 60 dias kg', 'SUM ( Fato_Sucata[Sucata_Em_Aberto_KG] ), Fato_Sucata[Dias_Atraso] > 60', INT)
m('% Sucata > 60 dias', 'DIVIDE ( [Sucata > 60 dias kg], [Sucata em Aberto kg] )', PCT, F)
m('% Sucata Recuperada', '''
-- Dos lançamentos ainda abertos, quanto do devido já voltou
DIVIDE ( [Sucata Entregue kg], [Sucata Devida kg] )''', PCT, F)
suc('Atraso Médio Ponderado', '''DIVIDE (
            SUMX ( Fato_Sucata, Fato_Sucata[Sucata_Em_Aberto_KG] * Fato_Sucata[Dias_Atraso] ),
            SUM ( Fato_Sucata[Sucata_Em_Aberto_KG] )
        )''', '0', '-- Dias de atraso ponderados pelos kg em aberto\n')
m('% Vendas com Troca de Casco', '''
DIVIDE (
    CALCULATE ( [Qtd Venda], KEEPFILTERS ( Fato_Vendas[Com_Troca_Casco] = "Sim" ) ),
    [Qtd Venda]
)''', PCT, F)
m('Baterias sem Casco', '''
-- Vendas sem devolução do casco no ato: geram débito de sucata
CALCULATE ( [Qtd Venda], KEEPFILTERS ( Fato_Vendas[Com_Troca_Casco] = "Não" ) ) + 0''', INT, F)
