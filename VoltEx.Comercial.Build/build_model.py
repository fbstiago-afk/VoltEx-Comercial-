# -*- coding: utf-8 -*-
"""Gera VoltEx.Comercial.SemanticModel (TMDL)."""
import os, json, uuid, shutil, sys
import model_measures as MM
import model_html  # registra medidas HTML em MM.M

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/out/VoltEx.Comercial.SemanticModel'
HERE = os.path.dirname(os.path.abspath(__file__))
NS = uuid.UUID('9c3e2a71-4b8d-4f0e-a1c6-2d7e5f3b8a90')
def lt(*k):
    return str(uuid.uuid5(NS, '|'.join(map(str, k))))

IMG = json.load(open(os.path.join(HERE, 'img_b64.json')))
# Fotos reais do catálogo VoltEx (1 Moto 7Ah, 2 Moto 9Ah AGM, 3 Carro 60Ah, 4 Carro 72Ah SS, 5 Caminhão 150Ah, 6 Trator 220Ah)

def col(table, name, dtype, fmt=None, hidden=False, sort=None, cat=None, key=False, summ='none', datecol=False):
    s = f'\tcolumn {name}\n\t\tdataType: {dtype}\n'
    if key: s += '\t\tisKey\n'
    if hidden: s += '\t\tisHidden\n'
    if fmt: s += f'\t\tformatString: {fmt}\n'
    s += f'\t\tlineageTag: {lt(table, name)}\n'
    if cat: s += f'\t\tdataCategory: {cat}\n'
    s += f'\t\tsummarizeBy: {summ}\n\t\tsourceColumn: {name}\n'
    if sort: s += f'\t\tsortByColumn: {sort}\n'
    s += '\n\t\tannotation SummarizationSetBy = Automatic\n'
    if datecol: s += '\n\t\tannotation UnderlyingDateTimeDataType = Date\n'
    return s + '\n'

def indent_m(code, n=4):
    return '\n'.join(('\t' * n + l) if l.strip() else '' for l in code.strip('\n').split('\n'))

def table(name, cols, mcode, extra_attrs=''):
    s = f'table {name}\n\tlineageTag: {lt(name)}\n{extra_attrs}\n'
    s += ''.join(cols)
    s += f'\tpartition {name} = m\n\t\tmode: import\n\t\tsource =\n{indent_m(mcode)}\n\n'
    s += '\tannotation PBI_ResultType = Table\n'
    return s

def excel(sheet, types, steps=''):
    t = ',\n'.join(f'        {{"{c}", {ty}}}' for c, ty in types)
    return f'''let
    Fonte = Excel.Workbook ( File.Contents ( CaminhoBaseCom ), null, true ),
    Planilha = Fonte{{[Item = "{sheet}", Kind = "Sheet"]}}[Data],
    Cabecalho = Table.PromoteHeaders ( Planilha, [PromoteAllScalars = true] ),
    Tipos = Table.TransformColumnTypes ( Cabecalho, {{
{t}
    }} ){steps}
in
    Resultado'''

T = {}

# ---------------- Dim_Calendario (termina na data de corte)
T['Dim_Calendario'] = table('Dim_Calendario', [
    col('Dim_Calendario', 'Data', 'dateTime', 'dd/mm/yyyy', key=True, datecol=True),
    col('Dim_Calendario', 'Ano', 'int64', '0'),
    col('Dim_Calendario', 'Mes_Num', 'int64', hidden=True),
    col('Dim_Calendario', 'Mes', 'string', sort='Mes_Num'),
    col('Dim_Calendario', 'AnoMes', 'int64', hidden=True),
    col('Dim_Calendario', 'Ano_Mes', 'string', sort='AnoMes'),
    col('Dim_Calendario', 'Inicio_Mes', 'dateTime', 'mmm/yy', datecol=True),
    col('Dim_Calendario', 'Trimestre', 'string'),
    col('Dim_Calendario', 'Status_Mes', 'string'),
], '''let
    // Termina na data de corte: a base traz vendas com data futura (até 31/12/2026)
    // e o ano corrente vira YTD automaticamente, o que alinha o SAMEPERIODLASTYEAR.
    DataMin = #date ( 2025, 1, 1 ),
    DataMax = DataCorte,
    Lista = List.Dates ( DataMin, Duration.Days ( DataMax - DataMin ) + 1, #duration ( 1, 0, 0, 0 ) ),
    Tabela = Table.FromList ( Lista, Splitter.SplitByNothing (), {"Data"} ),
    Tipada = Table.TransformColumnTypes ( Tabela, {{"Data", type date}} ),
    Ano = Table.AddColumn ( Tipada, "Ano", each Date.Year ( [Data] ), Int64.Type ),
    MesNum = Table.AddColumn ( Ano, "Mes_Num", each Date.Month ( [Data] ), Int64.Type ),
    Mes = Table.AddColumn ( MesNum, "Mes", each Text.Proper ( Date.ToText ( [Data], "MMM", "pt-BR" ) ), type text ),
    AnoMes = Table.AddColumn ( Mes, "AnoMes", each [Ano] * 100 + [Mes_Num], Int64.Type ),
    AnoMesTxt = Table.AddColumn ( AnoMes, "Ano_Mes", each Date.ToText ( [Data], "MMM/yy", "pt-BR" ), type text ),
    MesIni = Table.AddColumn ( AnoMesTxt, "Inicio_Mes", each Date.StartOfMonth ( [Data] ), type date ),
    Trim = Table.AddColumn ( MesIni, "Trimestre", each "T" & Text.From ( Date.QuarterOfYear ( [Data] ) ), type text ),
    Resultado = Table.AddColumn ( Trim, "Status_Mes", each
        if [Inicio_Mes] = Date.StartOfMonth ( DataCorte ) and DataCorte < Date.EndOfMonth ( DataCorte )
        then "Parcial" else "Fechado", type text )
in
    Resultado''', '\tdataCategory: Time\n')

# ---------------- Dim_Produto (SKU comercial) -> Dim_Catalogo (produto oficial da fábrica)
# SKU comercial -> ID do produto oficial na Base_VoltEx_Dashboard_Completo (Dim_Produto da fábrica).
# 40-50Ah não existem no catálogo oficial: ficam no 60Ah convencional (aproximação documentada no README).
OFICIAL = {501: 3, 502: 3, 503: 3, 504: 3, 505: 4, 506: 4, 507: 5, 508: 5, 509: 1, 510: 1}
FOTO_LINHA = {'SLI': 3, 'EFB': 4, 'AGM': 4, 'Pesada': 5, 'Moto': 1}
irow = ',\n'.join(f'        {{ {k}, "{IMG[str(k)]}" }}' for k in range(1, 7))
omap = ', '.join(f'{{ {pid}, {k} }}' for pid, k in OFICIAL.items())
lmap = ', '.join(f'{{ "{ln}", {k} }}' for ln, k in FOTO_LINHA.items())
FOTOS_M = ('    // Fotos reais do catálogo VoltEx, indexadas pelo ID do produto oficial (WebP base64)\n'
           '    Fotos = #table ( type table [Foto = Int64.Type, B64 = text], {\n' + irow + '\n    } ),')

T['Dim_Produto'] = table('Dim_Produto', [
    col('Dim_Produto', 'ID_Produto', 'int64', hidden=True),
    col('Dim_Produto', 'ID_Produto_Oficial', 'int64', hidden=True),
    col('Dim_Produto', 'Codigo_Original', 'string'),
    col('Dim_Produto', 'Produto', 'string', sort='ID_Produto'),
    col('Dim_Produto', 'Nome_Curto', 'string', sort='ID_Produto'),
    col('Dim_Produto', 'Grupo', 'string'),
    col('Dim_Produto', 'Familia', 'string', sort='Ordem_Familia'),
    col('Dim_Produto', 'Ordem_Familia', 'int64', hidden=True),
    col('Dim_Produto', 'Linha', 'string', sort='Ordem_Linha'),
    col('Dim_Produto', 'Ordem_Linha', 'int64', hidden=True),
    col('Dim_Produto', 'Imagem_Base64', 'string', cat='ImageUrl'),
    col('Dim_Produto', 'Imagem_Linha', 'string', hidden=True, cat='ImageUrl'),
], excel('Dim_Produto', [('ID_Produto', 'Int64.Type'), ('Codigo_Original', 'type text'), ('Produto', 'type text'),
                         ('Grupo', 'type text'), ('Linha', 'type text')],
    ''',
    // Família VoltEx derivada da linha técnica. Qualquer coluna de marca da origem é descartada:
    // o relatório só exibe a marca VoltEx, mesmo se a base vier com marcas de terceiros.
    SemMarca = Table.RemoveColumns ( Tipos, { "Subgrupo_Marca", "Familia" }, MissingField.Ignore ),
    Familia = Table.AddColumn ( SemMarca, "Familia", each
        if List.Contains ( { "SLI", "EFB", "AGM" }, [Linha] ) then "Linha Leve"
        else if [Linha] = "Pesada" then "Linha Pesada" else "Linha Moto", type text ),
    OrdFam = Table.AddColumn ( Familia, "Ordem_Familia", each
        List.PositionOf ( { "Linha Leve", "Linha Pesada", "Linha Moto" }, [Familia] ) + 1, Int64.Type ),
    Curto = Table.AddColumn ( OrdFam, "Nome_Curto", each Text.Trim ( Text.Replace ( [Produto], "Bat ", "" ) ), type text ),
    Ordem = Table.AddColumn ( Curto, "Ordem_Linha", each
        List.PositionOf ( { "SLI", "EFB", "AGM", "Pesada", "Moto" }, [Linha] ) + 1, Int64.Type ),
    // De-para SKU comercial -> produto oficial do catálogo da fábrica (Dim_Catalogo)
    Mapa = #table ( type table [ID_Produto = Int64.Type, ID_Produto_Oficial = Int64.Type], { ''' + omap + ''' } ),
    FotoLinha = #table ( type table [Linha = text, FotoL = Int64.Type], { ''' + lmap + ''' } ),
''' + FOTOS_M + '''
    J1 = Table.ExpandTableColumn ( Table.NestedJoin ( Ordem, {"ID_Produto"}, Mapa, {"ID_Produto"}, "P", JoinKind.LeftOuter ), "P", {"ID_Produto_Oficial"} ),
    J2 = Table.ExpandTableColumn ( Table.NestedJoin ( J1, {"Linha"}, FotoLinha, {"Linha"}, "L", JoinKind.LeftOuter ), "L", {"FotoL"} ),
    Img = Table.AddColumn ( J2, "Imagem_Base64", each Fotos{[Foto = [ID_Produto_Oficial]]}[B64], type text ),
    ImgL = Table.AddColumn ( Img, "Imagem_Linha", each Fotos{[Foto = [FotoL]]}[B64], type text ),
    Resultado = Table.RemoveColumns ( ImgL, { "FotoL" } )'''))

# ---------------- Dim_Catalogo: catálogo oficial da fábrica (Base_VoltEx_Dashboard_Completo)
T['Dim_Catalogo'] = table('Dim_Catalogo', [
    col('Dim_Catalogo', 'ID_Produto_Oficial', 'int64', hidden=True),
    col('Dim_Catalogo', 'Produto_Oficial', 'string', sort='ID_Produto_Oficial'),
    col('Dim_Catalogo', 'Categoria_Oficial', 'string'),
    col('Dim_Catalogo', 'Preco_Tabela', 'double', 'R$ #,0', hidden=True),
    col('Dim_Catalogo', 'Imagem_Oficial', 'string', cat='ImageUrl'),
], '''let
    // Catálogo oficial: os 6 produtos VoltEx da base da fábrica. Só a dimensão de produto é usada
    // (vendas, clientes e período da fábrica não conversam com a base comercial).
    Fonte = Excel.Workbook ( File.Contents ( CaminhoBaseFab ), null, true ),
    Planilha = Fonte{[Item = "Dim_Produto", Kind = "Sheet"]}[Data],
    Cabecalho = Table.PromoteHeaders ( Planilha, [PromoteAllScalars = true] ),
    Colunas = Table.SelectColumns ( Cabecalho, { "ID_Produto", "Nome_Produto", "Categoria", "Preco_Venda" } ),
    Tipos = Table.TransformColumnTypes ( Colunas, {
        {"ID_Produto", Int64.Type}, {"Nome_Produto", type text}, {"Categoria", type text}, {"Preco_Venda", type number}
    } ),
    Nomes = Table.RenameColumns ( Tipos, {
        {"ID_Produto", "ID_Produto_Oficial"}, {"Nome_Produto", "Produto_Oficial"},
        {"Categoria", "Categoria_Oficial"}, {"Preco_Venda", "Preco_Tabela"}
    } ),
    // "Caminhao" e "Onibus" chegam sem acento da origem
    Acentos = Table.TransformColumns ( Nomes, { "Produto_Oficial", each
        Text.Replace ( Text.Replace ( _, "Caminhao", "Caminhão" ), "Onibus", "Ônibus" ), type text } ),
    Categoria = Table.TransformColumns ( Acentos, { "Categoria_Oficial", each if _ = "Motos" then "Linha Moto" else _, type text } ),
''' + FOTOS_M + '''
    Resultado = Table.AddColumn ( Categoria, "Imagem_Oficial", each Fotos{[Foto = [ID_Produto_Oficial]]}[B64], type text )
in
    Resultado''')

# ---------------- Dim_Filial
T['Dim_Filial'] = table('Dim_Filial', [
    col('Dim_Filial', 'ID_Filial', 'int64', hidden=True),
    col('Dim_Filial', 'Nome_Filial', 'string'),
    col('Dim_Filial', 'Filial_Curta', 'string', sort='ID_Filial'),
    col('Dim_Filial', 'UF_Filial', 'string'),
], excel('Dim_Filial', [('ID_Filial', 'Int64.Type'), ('Nome_Filial', 'type text')],
    ''',
    // "Matriz - SP" -> "Matriz · SP"
    Curta = Table.AddColumn ( Tipos, "Filial_Curta", each Text.Replace ( [Nome_Filial], " - ", " · " ), type text ),
    Resultado = Table.AddColumn ( Curta, "UF_Filial", each Text.End ( Text.Trim ( [Nome_Filial] ), 2 ), type text )'''))

# ---------------- Dim_Vendedor
T['Dim_Vendedor'] = table('Dim_Vendedor', [
    col('Dim_Vendedor', 'ID_Vendedor', 'int64', hidden=True),
    col('Dim_Vendedor', 'Nome_Vendedor', 'string', sort='ID_Vendedor'),
    col('Dim_Vendedor', 'ID_Filial', 'int64', hidden=True),
    col('Dim_Vendedor', 'Area_Rota', 'string'),
    col('Dim_Vendedor', 'Filial_Vendedor', 'string'),
], excel('Dim_Vendedor', [('ID_Vendedor', 'Int64.Type'), ('Nome_Vendedor', 'type text'), ('ID_Filial', 'Int64.Type'),
                          ('Area_Rota', 'type text')],
    ''',
    // Rótulo da filial como atributo; o vínculo vendedor -> filial nas medidas é por TREATAS
    Filial = Table.AddColumn ( Tipos, "Filial_Vendedor", each if [ID_Filial] = 1 then "Matriz · SP" else "Filial · RJ", type text ),
    Resultado = Filial'''))

# ---------------- Dim_Municipio (Potencial_Mercado)
T['Dim_Municipio'] = table('Dim_Municipio', [
    col('Dim_Municipio', 'Cod_IBGE', 'int64', hidden=True),
    col('Dim_Municipio', 'Municipio', 'string'),
    col('Dim_Municipio', 'UF', 'string'),
    col('Dim_Municipio', 'Potencial_Baterias_Mes', 'int64', '#,0', hidden=True),
], excel('Potencial_Mercado', [('Municipio', 'type text'), ('UF', 'type text'), ('Cod_IBGE', 'Int64.Type'),
                               ('Potencial_Baterias_Mes', 'Int64.Type')], ',\n    Resultado = Tipos'))

# ---------------- Dim_Cliente
T['Dim_Cliente'] = table('Dim_Cliente', [
    col('Dim_Cliente', 'ID_Cliente', 'int64', hidden=True),
    col('Dim_Cliente', 'CNPJ', 'string'),
    col('Dim_Cliente', 'Razao_Social', 'string'),
    col('Dim_Cliente', 'Nome_Fantasia', 'string'),
    col('Dim_Cliente', 'Cliente_Rotulo', 'string', sort='ID_Cliente'),
    col('Dim_Cliente', 'Ramo_Atividade', 'string'),
    col('Dim_Cliente', 'Cod_IBGE', 'int64', hidden=True),
    col('Dim_Cliente', 'Data_Cadastro', 'dateTime', 'dd/mm/yyyy', datecol=True),
    col('Dim_Cliente', 'Situacao', 'string'),
    col('Dim_Cliente', 'ID_Vendedor', 'int64', hidden=True),
], excel('Dim_Cliente', [('ID_Cliente', 'Int64.Type'), ('CNPJ', 'type text'), ('Razao_Social', 'type text'),
                         ('Nome_Fantasia', 'type text'), ('Ramo_Atividade', 'type text'), ('Cod_IBGE', 'Int64.Type'),
                         ('Data_Cadastro', 'type date'), ('Situacao', 'type text'), ('ID_Vendedor', 'Int64.Type')],
    ''',
    // Município/UF ficam só na Dim_Municipio (fonte única da geografia e do potencial)
    SemGeo = Table.RemoveColumns ( Tipos, { "Municipio", "UF" }, MissingField.Ignore ),
    Resultado = Table.AddColumn ( SemGeo, "Cliente_Rotulo", each [Nome_Fantasia] & " · " & [Ramo_Atividade], type text )'''))

# ---------------- Fatos
T['Fato_Vendas'] = table('Fato_Vendas', [
    col('Fato_Vendas', 'ID_Nota_Item', 'int64', hidden=True),
    col('Fato_Vendas', 'Numero_Nota', 'int64', hidden=True),
    col('Fato_Vendas', 'Data_Emissao', 'dateTime', 'dd/mm/yyyy', hidden=True, datecol=True),
    col('Fato_Vendas', 'Mes_Ref', 'dateTime', 'mmm/yy', hidden=True, datecol=True),
    col('Fato_Vendas', 'ID_Cliente', 'int64', hidden=True),
    col('Fato_Vendas', 'ID_Produto', 'int64', hidden=True),
    col('Fato_Vendas', 'Tipo_Operacao', 'string', hidden=True),
    col('Fato_Vendas', 'Com_Troca_Casco', 'string', hidden=True),
    col('Fato_Vendas', 'Quantidade', 'int64', '#,0', hidden=True),
    col('Fato_Vendas', 'ID_Vendedor', 'int64', hidden=True),
    col('Fato_Vendas', 'ID_Filial', 'int64', hidden=True),
    col('Fato_Vendas', 'Valor_Unitario', 'double', 'R$ #,0.00', hidden=True),
    col('Fato_Vendas', 'Faturamento_RS', 'double', 'R$ #,0.00', hidden=True),
], excel('Fato_Vendas', [('ID_Nota_Item', 'Int64.Type'), ('Numero_Nota', 'Int64.Type'), ('Data_Emissao', 'type date'),
                         ('ID_Cliente', 'Int64.Type'), ('ID_Produto', 'Int64.Type'), ('Tipo_Operacao', 'type text'),
                         ('Com_Troca_Casco', 'type text'), ('Quantidade', 'Int64.Type'), ('ID_Vendedor', 'Int64.Type'),
                         ('ID_Filial', 'Int64.Type'), ('Valor_Unitario', 'type number'), ('Faturamento_RS', 'type number')],
    ''',
    // Corta lançamentos com data futura (a base vai até 31/12/2026)
    AteCorte = Table.SelectRows ( Tipos, each [Data_Emissao] <= DataCorte ),
    Resultado = Table.AddColumn ( AteCorte, "Mes_Ref", each Date.StartOfMonth ( [Data_Emissao] ), type date )'''))

T['Fato_Metas'] = table('Fato_Metas', [
    col('Fato_Metas', 'Data_Mes', 'dateTime', 'mmm/yy', hidden=True, datecol=True),
    col('Fato_Metas', 'ID_Vendedor', 'int64', hidden=True),
    col('Fato_Metas', 'Meta_Quantidade', 'int64', '#,0', hidden=True),
], excel('Fato_Metas', [('Data_Mes', 'type date'), ('ID_Vendedor', 'Int64.Type'),
                        ('Meta_Quantidade', 'Int64.Type')],
    ''',
    // Metas valem para a Linha Leve (40–72Ah). A coluna de marca da origem é descartada.
    // Metas de meses ainda não iniciados ficam fora (não há calendário para elas)
    SemMarca = Table.RemoveColumns ( Tipos, { "Marca_Meta", "Familia_Meta" }, MissingField.Ignore ),
    Resultado = Table.SelectRows ( SemMarca, each [Data_Mes] <= DataCorte )'''))

T['Fato_Sucata'] = table('Fato_Sucata', [
    col('Fato_Sucata', 'ID_Lancamento', 'int64', hidden=True),
    col('Fato_Sucata', 'Data_Emissao_Origem', 'dateTime', 'dd/mm/yyyy', hidden=True, datecol=True),
    col('Fato_Sucata', 'ID_Cliente', 'int64', hidden=True),
    col('Fato_Sucata', 'Sucata_Devida_KG', 'double', '#,0', hidden=True),
    col('Fato_Sucata', 'Sucata_Entregue_KG', 'double', '#,0', hidden=True),
    col('Fato_Sucata', 'Sucata_Em_Aberto_KG', 'double', '#,0', hidden=True),
    col('Fato_Sucata', 'Dias_Atraso', 'int64', '0', hidden=True),
    col('Fato_Sucata', 'Faixa_Atraso', 'string', sort='Ordem_Faixa'),
    col('Fato_Sucata', 'Ordem_Faixa', 'int64', hidden=True),
], excel('Fato_Sucata', [('ID_Lancamento', 'Int64.Type'), ('Data_Emissao_Origem', 'type date'), ('ID_Cliente', 'Int64.Type'),
                         ('Sucata_Devida_KG', 'type number'), ('Sucata_Entregue_KG', 'type number'),
                         ('Sucata_Em_Aberto_KG', 'type number')],
    ''',
    // Dias_Atraso da origem foi congelado na data em que o Excel foi gerado: recalculado aqui
    SemDias = Table.RemoveColumns ( Tipos, { "Dias_Atraso" }, MissingField.Ignore ),
    AteCorte = Table.SelectRows ( SemDias, each [Data_Emissao_Origem] <= DataCorte and [Sucata_Em_Aberto_KG] > 0 ),
    Dias = Table.AddColumn ( AteCorte, "Dias_Atraso", each Duration.Days ( DataCorte - [Data_Emissao_Origem] ), Int64.Type ),
    Ordem = Table.AddColumn ( Dias, "Ordem_Faixa", each
        if [Dias_Atraso] <= 30 then 1 else if [Dias_Atraso] <= 60 then 2 else if [Dias_Atraso] <= 90 then 3 else 4, Int64.Type ),
    Resultado = Table.AddColumn ( Ordem, "Faixa_Atraso", each
        { "0–30 dias", "31–60 dias", "61–90 dias", "90+ dias" }{[Ordem_Faixa] - 1}, type text )'''))

T['Fato_Prospects'] = table('Fato_Prospects', [
    col('Fato_Prospects', 'CNPJ_Prospect', 'string', hidden=True),
    col('Fato_Prospects', 'Razao_Social_Prospect', 'string'),
    col('Fato_Prospects', 'Cod_IBGE', 'int64', hidden=True),
    col('Fato_Prospects', 'Status_Prospect', 'string', sort='Ordem_Status'),
    col('Fato_Prospects', 'Ordem_Status', 'int64', hidden=True),
    col('Fato_Prospects', 'Possui_Telefone', 'string'),
], excel('Base_Mercado_Prospects', [('CNPJ_Prospect', 'type text'), ('Razao_Social_Prospect', 'type text'),
                                    ('Cod_IBGE', 'Int64.Type'), ('Status_Prospect', 'type text'), ('Possui_Telefone', 'type text')],
    ''',
    Resultado = Table.AddColumn ( Tipos, "Ordem_Status", each
        List.PositionOf ( { "Liberado", "Pendente Revisão", "Já é Cliente" }, [Status_Prospect] ) + 1, Int64.Type )'''))

# ---------------- Desconectadas
T['Seg_RFQ'] = table('Seg_RFQ', [
    col('Seg_RFQ', 'Ordem', 'int64', hidden=True),
    col('Seg_RFQ', 'Segmento', 'string', sort='Ordem'),
    col('Seg_RFQ', 'Regra', 'string'),
], '''let
    // Segmentos RFQ (Recência, Frequência, Quantidade 12M). A regra mora na medida RFQ.
    Resultado = #table (
        type table [Ordem = Int64.Type, Segmento = text, Regra = text],
        {
            { 1, "Campeões", "10+ meses comprando e volume ≥ 1,2× a média" },
            { 2, "Leais", "8+ meses comprando e volume ≥ 0,8× a média" },
            { 3, "Ocasionais", "compra recente, frequência ou volume baixos" },
            { 4, "Em risco", "sem compra há mais de 60 dias" },
            { 5, "Sem compra 12M", "nenhuma compra nos últimos 12 meses" }
        }
    )
in
    Resultado''')

T['Seg_SWOT'] = table('Seg_SWOT', [
    col('Seg_SWOT', 'Ordem', 'int64', hidden=True),
    col('Seg_SWOT', 'Quadrante', 'string', sort='Ordem'),
], '''let
    // Porte (quantidade vs média da base) × tendência (vs mesmo período do ano anterior)
    Resultado = #table (
        type table [Ordem = Int64.Type, Quadrante = text],
        { { 1, "Fortalezas" }, { 2, "Atenção" }, { 3, "Oportunidades" }, { 4, "Fraquezas" } }
    )
in
    Resultado''')

# ---------------- _Medidas
def measure_block(name, expr, fmt, folder):
    q = name if all(c.isalnum() or c == '_' for c in name) else "'" + name.replace("'", "''") + "'"
    lines = expr.split('\n')
    if len(lines) == 1:
        s = f'\tmeasure {q} = {expr}\n'
    else:
        body = '\n'.join(('\t\t\t' + l) if l.strip() else '' for l in lines)
        s = f'\tmeasure {q} =\n{body}\n'
    if fmt:
        s += f'\t\tformatString: {fmt}\n'
    if folder:
        s += f'\t\tdisplayFolder: {folder}\n'
    s += f'\t\tlineageTag: {lt("_Medidas", name)}\n\n'
    return s

names = [x[0] for x in MM.M]
assert len(names) == len(set(names)), [n for n in names if names.count(n) > 1]
med = f'table _Medidas\n\tlineageTag: {lt("_Medidas")}\n\n'
med += ''.join(measure_block(*x) for x in MM.M)
med += col('_Medidas', 'Coluna', 'string', hidden=True)
med += '\tpartition _Medidas = m\n\t\tmode: import\n\t\tsource =\n\t\t\t\tlet\n\t\t\t\t    Resultado = #table ( type table [Coluna = text], {} )\n\t\t\t\tin\n\t\t\t\t    Resultado\n\n\tannotation PBI_ResultType = Table\n'
T['_Medidas'] = med

ORDER = ['Dim_Calendario', 'Dim_Catalogo', 'Dim_Produto', 'Dim_Filial', 'Dim_Vendedor', 'Dim_Municipio', 'Dim_Cliente',
         'Fato_Vendas', 'Fato_Metas', 'Fato_Sucata', 'Fato_Prospects', 'Seg_RFQ', 'Seg_SWOT', '_Medidas']

RELS = [
    ('Dim_Produto.ID_Produto_Oficial', 'Dim_Catalogo.ID_Produto_Oficial'),
    ('Fato_Vendas.Data_Emissao', 'Dim_Calendario.Data'),
    ('Fato_Metas.Data_Mes', 'Dim_Calendario.Data'),
    ('Fato_Vendas.ID_Produto', 'Dim_Produto.ID_Produto'),
    ('Fato_Vendas.ID_Cliente', 'Dim_Cliente.ID_Cliente'),
    ('Fato_Vendas.ID_Vendedor', 'Dim_Vendedor.ID_Vendedor'),
    ('Fato_Vendas.ID_Filial', 'Dim_Filial.ID_Filial'),
    ('Fato_Metas.ID_Vendedor', 'Dim_Vendedor.ID_Vendedor'),
    ('Dim_Cliente.Cod_IBGE', 'Dim_Municipio.Cod_IBGE'),
    ('Fato_Sucata.ID_Cliente', 'Dim_Cliente.ID_Cliente'),
    ('Fato_Prospects.Cod_IBGE', 'Dim_Municipio.Cod_IBGE'),
]

def write(path, txt):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(txt)

if os.path.exists(OUT):
    shutil.rmtree(OUT)
D = OUT + '/definition'
write(OUT + '/definition.pbism', json.dumps({
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "4.2", "settings": {}}, indent=2))
write(OUT + '/.platform', json.dumps({
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": "VoltEx.Comercial"},
    "config": {"version": "2.0", "logicalId": lt('logical', 'model')}}, indent=2))
write(D + '/database.tmdl', 'database\n\tcompatibilityLevel: 1606\n\n')
qo = json.dumps(['CaminhoBaseCom', 'CaminhoBaseFab', 'DataCorte'] + ORDER, ensure_ascii=False).replace(' ', '')
write(D + '/model.tmdl', f'''model Model
\tculture: pt-BR
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tdiscourageImplicitMeasures
\tsourceQueryCulture: pt-BR
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_QueryOrder = {qo}

annotation PBI_ProTooling = ["DevMode"]

''' + ''.join(f'ref table {t}\n' for t in ORDER) + '\nref cultureInfo pt-BR\n\n')
# Cultura sem metadados linguísticos gerados: o Desktop recria os termos a partir dos nomes atuais
write(D + '/cultures/pt-BR.tmdl', 'cultureInfo pt-BR\n\n')
write(D + '/expressions.tmdl', f'''/// Caminho completo do Excel comercial. Altere em Transformar dados › Gerenciar parâmetros.
expression CaminhoBaseCom = "E:\\Projetos BI\\14 - Voltex baterias\\Base_VoltEx_Comercial.xlsx" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
\tlineageTag: {lt('expr', 'CaminhoBaseCom')}

\tannotation PBI_ResultType = Text

/// Base da fábrica: usada só para o catálogo oficial de produtos (Dim_Catalogo).
expression CaminhoBaseFab = "E:\\Projetos BI\\14 - Voltex baterias\\Base_VoltEx_Dashboard_Completo.xlsx" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
\tlineageTag: {lt('expr', 'CaminhoBaseFab')}

\tannotation PBI_ResultType = Text

/// Data de corte: hoje. Corta vendas, metas e sucata com data futura e fecha o calendário.
/// Para congelar um fechamento, troque por #date ( 2026, 9, 30 ), por exemplo.
expression DataCorte =
\t\tlet
\t\t    Resultado = Date.From ( DateTime.LocalNow () )
\t\tin
\t\t    Resultado
\tlineageTag: {lt('expr', 'DataCorte')}

\tannotation PBI_ResultType = Date

''')
write(D + '/relationships.tmdl', ''.join(
    f'relationship {lt("rel", a, b)}\n\tfromColumn: {a}\n\ttoColumn: {b}\n\n' for a, b in RELS))
for t in ORDER:
    write(f'{D}/tables/{t}.tmdl', T[t])
print('tabelas', len(ORDER), 'medidas', len(MM.M))
