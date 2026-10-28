# -*- coding: utf-8 -*-
"""Gera VoltEx.Comercial.Report (PBIR) + .pbip."""
import os, json, shutil, sys
from pbir import *
from css import CSS
import deneb_specs as DS

ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/out'
REF = sys.argv[2] if len(sys.argv) > 2 else '/mnt/user-data/uploads/14 - Voltex baterias/VoltEx.Distribuidora.Report'
REP = ROOT + '/VoltEx.Comercial.Report'
DEF = REP + '/definition'

def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        if isinstance(obj, str): f.write(obj)
        else: json.dump(obj, f, ensure_ascii=False, indent=2)

if os.path.exists(REP): shutil.rmtree(REP)

# ------------------------------------------------------------------ páginas
PG = {k: hid('vxcom', 'page', k) for k in
      ['capa', 'visao', 'metas', 'cart', 'merc', 'swot', 'mix', 'suc', 'tt_mes', 'tt_vend', 'tt_prod']}
ABAS = [  # chave, rótulo nav, nome da página, header, faixa de KPI, insight
    ('visao', 'Visão', '1 · Visão Comercial', 'Header Visao', 'KPI Visao', 'Insight Visao'),
    ('metas', 'Metas', '2 · Metas de Vendas', 'Header Metas', 'KPI Metas', 'Insight Metas'),
    ('cart', 'Carteira', '3 · Carteira e Cobertura', 'Header Carteira', 'KPI Carteira', 'Insight Carteira'),
    ('merc', 'Mercado', '4 · Potencial e Share', 'Header Mercado', 'KPI Mercado', 'Insight Mercado'),
    ('swot', 'SWOT', '5 · SWOT da Carteira', 'Header SWOT', 'KPI SWOT', 'Insight SWOT'),
    ('mix', 'Mix', '6 · Mix de Produtos', 'Header Mix', 'Catalogo Linhas HTML', 'Insight Mix'),
    ('suc', 'Sucata', '7 · Sucata EcoCiclo', 'Header Sucata', 'KPI Sucata', 'Insight Sucata'),
]

# ------------------------------------------------------------------ ícones (24×24, traço)
ICON = {
    'visao': '<path d="M4 20V11M10 20V5M16 20v-6M2 20h20"/>',
    'metas': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
    'cart': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.3c2 .8 3.5 2.8 3.5 5.7"/>',
    'merc': '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'swot': '<rect x="3" y="3" width="8" height="8" rx="1.5"/><rect x="13" y="3" width="8" height="8" rx="1.5"/><rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/>',
    'mix': '<rect x="3" y="8" width="16" height="11" rx="1.5"/><path d="M19 11.5h2v4h-2M7 5.5v2.5M15 5.5v2.5M7.5 13.5h3M13 13.5h3M14.5 12v3"/>',
    'suc': '<path d="M20 12a8 8 0 1 1-2.3-5.7"/><path d="M20 3.5V8h-4.5"/><path d="M10 9.5h4v6.5h-4zM11.2 8.5h1.6"/>',
}

def nav_svg(key, label, active):
    stroke = '#FF8C00' if active else '#9AA6B0'
    txt = '#F2F4F5' if active else '#9AA6B0'
    bg = '<rect x="6" y="2" width="60" height="56" rx="10" fill="#FF8C00" fill-opacity="0.10"/><rect x="0" y="14" width="3" height="32" rx="1.5" fill="#FF8C00"/>' if active else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="72" height="60" viewBox="0 0 72 60">{bg}'
            f'<g transform="translate(24 8)" fill="none" stroke="{stroke}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICON[key]}</g>'
            f'<text x="36" y="49" text-anchor="middle" font-family="Segoe UI, Arial" font-size="10" font-weight="600" fill="{txt}">{label}</text></svg>')

LOGO_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">'
            '<rect x="2" y="2" width="44" height="44" rx="12" fill="#FF8C00" fill-opacity="0.14"/>'
            '<path d="M26.5 9 14 27h9l-2 12 13-19h-9z" fill="#FF8C00"/></svg>')
FILTER_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="72" height="60" viewBox="0 0 72 60">'
              '<g transform="translate(24 8)" fill="none" stroke="#F2F4F5" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
              '<path d="M3 5h18l-7 8.5V19l-4 2v-7.5z"/></g>'
              '<text x="36" y="49" text-anchor="middle" font-family="Segoe UI, Arial" font-size="10" font-weight="600" fill="#F2F4F5">Filtros</text></svg>')
CLOSE_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">'
             '<rect x="1" y="1" width="34" height="34" rx="9" fill="#1A2026"/>'
             '<path d="M12 12l12 12M24 12 12 24" stroke="#F2F4F5" stroke-width="1.8" stroke-linecap="round"/></svg>')
SCRIM_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10" preserveAspectRatio="none"><rect width="10" height="10" fill="#0B0E11" fill-opacity="0.62"/></svg>'
PANEL_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="344" height="720" viewBox="0 0 344 720">'
             '<rect width="344" height="720" fill="#232B32"/><rect width="1" height="720" fill="#34404A"/>'
             '<rect x="0" y="0" width="344" height="3" fill="#FF8C00"/></svg>')

def btn_svg(text, primary):
    fill = '#FF8C00' if primary else 'none'
    stroke = 'none' if primary else '#4A5862'
    color = '#1A2026' if primary else '#F2F4F5'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="140" height="40" viewBox="0 0 140 40">'
            f'<rect x="1" y="1" width="138" height="38" rx="8" fill="{fill}" stroke="{stroke}"/>'
            f'<text x="70" y="25" text-anchor="middle" font-family="Segoe UI, Arial" font-size="12" font-weight="600" fill="{color}">{text}</text></svg>')

START_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" width="200" height="52" viewBox="0 0 200 52">'
             '<rect x="1" y="1" width="198" height="50" rx="10" fill="#FF8C00"/>'
             '<text x="86" y="32" text-anchor="middle" font-family="Segoe UI, Arial" font-size="15" font-weight="700" letter-spacing="2" fill="#1A2026">INICIAR</text>'
             '<path d="M140 19l7 7-7 7M149 19l7 7-7 7" fill="none" stroke="#1A2026" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def bg_page(item, transparency=0):
    return {"background": [{"properties": {"image": {"image": {
        "name": S(item), "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": item}}},
        "scaling": S('Fit')}}, "transparency": D(transparency)}}],
        "outspace": [{"properties": {"color": C('#1A2026'), "transparency": D(0)}}]}

def page_json(key, name, w=1280, h=720, bg='bg_com_page.png', tooltip=False):
    p = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json",
         "name": PG[key], "displayName": name, "displayOption": "FitToPage" if not tooltip else "ActualSize",
         "height": h, "width": w}
    if tooltip:
        p.update({"type": "Tooltip", "visibility": "HiddenInViewMode",
                  "pageBinding": {"name": hid('vxcom', 'binding', key), "type": "Tooltip", "parameters": []}})
    p["objects"] = bg_page(bg)
    return p

BOOKMARKS = []
VIS = {}

def add(page, c):
    VIS.setdefault(page, []).append(c)
    return c['name']

def z_of(page):
    return 1000 + 10 * len(VIS.get(page, []))

def V(page, tag, x, y, w, h, visual, **kw):
    n = hid('vxcom', page, tag)
    return add(page, container(n, x, y, w, h, kw.pop('z', z_of(page)), visual, **kw))

# ------------------------------------------------------------------ elementos comuns
def chrome(key, header, kpi, insight):
    V(key, 'logo', 12, 14, 48, 48, image(LOGO_SVG, link=nav(PG['capa'])))
    for i, (k, lab, *_r) in enumerate(ABAS):
        V(key, f'nav_{k}', 0, 92 + i * 64, 72, 60, image(nav_svg(k, lab, k == key), link=nav(PG[k])))
    V(key, 'header', 96, 6, 1160, 60, html(header, CSS))
    V(key, 'kpi', 96, 76, 1160, 92, html(kpi, CSS))
    V(key, 'insight', 96, 624, 1160, 60, html(insight, CSS))

SLICERS = [('Dim_Calendario', 'Ano', 'Ano', 'sync_ano', '2026L'),
           ('Dim_Filial', 'Filial_Curta', 'Filial', 'sync_fil', None),
           ('Dim_Vendedor', 'Nome_Vendedor', 'Vendedor', 'sync_vend', None),
           ('Dim_Produto', 'Linha', 'Linha de produto', 'sync_lin', None),
           ('Dim_Cliente', 'Ramo_Atividade', 'Ramo de atividade', 'sync_ramo', None),
           ('Dim_Municipio', 'Municipio', 'Município', 'sync_mun', None)]

def drawer(key):
    g = hid('vxcom', key, 'drawer_grp')
    open_bm, close_bm = hid('vxcom', key, 'bm_open'), hid('vxcom', key, 'bm_close')
    V(key, 'btn_filtros', 0, 640, 72, 60, image(FILTER_SVG, link=bmk(open_bm)))
    members = []
    add(key, container(g, 0, 0, 1280, 720, 30000, group='GRP_Drawer', hidden=True))
    def child(tag, x, y, w, h, visual, z):
        n = hid('vxcom', key, tag)
        add(key, container(n, x, y, w, h, z, visual, parent=g, hidden=False))
        members.append((n, visual['visualType']))
    child('scrim', 0, 0, 936, 720, image(SCRIM_SVG, link=bmk(close_bm), scaling='Fill'), 30001)
    child('panel', 936, 0, 344, 720, image(PANEL_SVG, scaling='Fill'), 30002)
    child('dr_head', 960, 22, 256, 140, html('Drawer Header HTML', CSS), 30003)
    child('dr_close', 1224, 18, 36, 36, image(CLOSE_SVG, link=bmk(close_bm)), 30004)
    for i, (e, p, hd, sg, dflt) in enumerate(SLICERS):
        child(f'sl_{p}', 960, 168 + i * 72, 296, 60, slicer(e, p, hd, sg, default=dflt), 30010 + i)
    child('dr_clear', 960, 648, 140, 40, image(btn_svg('Limpar filtros', False), link=clear_all()), 30030)
    child('dr_apply', 1116, 648, 140, 40, image(btn_svg('Aplicar e fechar', True), link=bmk(close_bm)), 30031)
    names = [g] + [n for n, _ in members]
    page = PG[key]
    for bm, label, hidden in ((open_bm, 'Filtros abertos', False), (close_bm, 'Filtros fechados', True)):
        vc = {n: ({"singleVisual": {"visualType": t, "display": {"mode": "hidden"}}} if hidden else {}) for n, t in members}
        BOOKMARKS.append({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json",
                          "displayName": f"{key} · {label}", "name": bm,
                          "options": {"applyOnlyToTargetVisuals": True, "targetVisualNames": names, "suppressData": True},
                          "explorationState": {"version": "1.0", "activeSection": page, "sections": {page: {
                              "visualContainers": vc, "visualContainerGroups": {g: {"isHidden": hidden}}}}}})

HERO = (96, 180, 712, 424)
SUP = (836, 180, 420, 424)
GRID = C('#2C363E')

def native(vtype, query, objects, title, tooltip_page=None, sort=None):
    v = {"visualType": vtype, "query": {"queryState": query}, "objects": objects,
         "visualContainerObjects": vco(title=title, pad=(4, 4, 4, 4), tooltip_page=tooltip_page)}
    if sort:
        v["query"]["sortDefinition"] = {"sort": sort, "isDefaultSort": True}
    return v

# ================================================================== CAPA
VIS['capa'] = []
V('capa', 'capa_txt', 72, 150, 560, 330, html('Capa HTML', CSS))
V('capa', 'capa_btn', 72, 500, 200, 52, image(START_SVG, link=nav(PG['visao'])))
V('capa', 'capa_logo', 72, 640, 150, 52, image_resource('Logo_Bocardi_Data+Insights16179233929570047.png',
                                                       link=dict(show=B(True), type=S('WebUrl'), webUrl=S('https://bocardidata.com.br'))))

# ================================================================== 1 · Visão Comercial
k = 'visao'; chrome(k, 'Header Visao', 'KPI Visao', 'Insight Visao')
V(k, 'hero', *HERO, deneb([Col('Dim_Calendario', 'Inicio_Mes', 'Mes'), Col('Dim_Calendario', 'Status_Mes', 'Status'),
                           M('Quantidade', 'Qtd'), M('Quantidade AA', 'QtdAA'), M('Var % Qtd AA', 'Var'),
                           M('Faturamento', 'Fat'), M('% Cobertura', 'Cob')], DS.evolucao(), w=700, h=412))
V(k, 'sup', *SUP, native('clusteredBarChart',
    {"Category": {"projections": [Col('Dim_Produto', 'Linha', 'Linha', active=True)]},
     "Y": {"projections": [M('Quantidade', 'Período'), M('Quantidade AA', 'Ano anterior')]}},
    {"categoryAxis": axis(fontSize=D(11), labelColor=C('#F2F4F5'), maxMarginFactor=L('30L')),
     "valueAxis": axis(show=B(False)),
     "labels": labels(True, '#C9D3DB', units=1000, precision=1, size=9),
     "legend": legend(True),
     "dataPoint": measure_colors({'Quantidade': '#FF8C00', 'Quantidade AA': '#4A5862'})},
    'Baterias por linha vs ano anterior (mil)', tooltip_page=PG['tt_prod'],
    sort=[{"field": colm('Dim_Produto', 'Linha'), "direction": "Ascending"}]))
drawer(k)

# ================================================================== 2 · Metas de Vendas
k = 'metas'; chrome(k, 'Header Metas', 'KPI Metas', 'Insight Metas')
V(k, 'hero', *HERO, deneb([Col('Dim_Vendedor', 'Nome_Vendedor', 'Vendedor'), M('Qtd Linha Leve', 'Realizado'),
                           M('Meta Linha Leve', 'Meta'), M('% Atingimento Meta', 'Ating'), M('% Tendência Meta', 'Tend'),
                           M('Gap Meta', 'Gap'), M('% Cobertura', 'Cob')], DS.bullet(), w=700, h=412))
V(k, 'sup', *SUP, native('scatterChart',
    {"Category": {"projections": [Col('Dim_Vendedor', 'Nome_Vendedor', 'Vendedor', active=True)]},
     "X": {"projections": [M('% Linha Leve no Volume', 'Linha Leve no volume')]},
     "Y": {"projections": [M('% Atingimento Meta', 'Atingimento da meta')]},
     "Size": {"projections": [M('Quantidade', 'Baterias')]}},
    {"categoryAxis": axis(showAxisTitle=B(True), gridlineShow=B(True), gridlineColor=GRID),
     "valueAxis": axis(showAxisTitle=B(True), gridlineShow=B(True), gridlineColor=GRID),
     "categoryLabels": props(show=B(True), color=C('#C9D3DB'), fontSize=D(9)),
     "dataPoint": props(fill=C('#FF8C00')),
     "legend": legend(False)},
    'Peso da Linha Leve no volume × atingimento, por vendedor', tooltip_page=PG['tt_vend']))
drawer(k)

# ================================================================== 3 · Carteira e Cobertura
k = 'cart'; chrome(k, 'Header Carteira', 'KPI Carteira', 'Insight Carteira')
V(k, 'hero', *HERO, deneb([Col('Seg_RFQ', 'Segmento', 'Segmento'), Col('Seg_RFQ', 'Regra', 'Regra'),
                           M('RFQ Clientes', 'Clientes'), M('RFQ % Clientes', 'PctCli'), M('RFQ Qtd 12M', 'Qtd'),
                           M('RFQ % Qtd 12M', 'PctQtd'), M('RFQ Fat 12M', 'Fat')], DS.rfq(), w=700, h=412))
V(k, 'sup', *SUP, native('lineChart',
    {"Category": {"projections": [Col('Dim_Calendario', 'Inicio_Mes', 'Mês', active=True)]},
     "Y": {"projections": [M('% Cobertura', 'Período'), M('% Cobertura AA', 'Ano anterior')]}},
    {"categoryAxis": axis(), "valueAxis": axis(gridlineShow=B(True), gridlineColor=GRID),
     "legend": legend(True), "labels": labels(False),
     "dataPoint": measure_colors({'% Cobertura': '#FF8C00', '% Cobertura AA': '#5E6B75'}),
     "lineStyles": props(strokeWidth=L('2L'), showMarker=B(True))},
    'Cobertura mensal da carteira ativa', tooltip_page=PG['tt_mes']))
drawer(k)

# ================================================================== 4 · Potencial e Share
k = 'merc'; chrome(k, 'Header Mercado', 'KPI Mercado', 'Insight Mercado')
V(k, 'hero', *HERO, deneb([Col('Dim_Municipio', 'Municipio', 'Municipio'), Col('Dim_Municipio', 'UF', 'UF'),
                           M('Potencial Período', 'Potencial'), M('Quantidade', 'Vendido'), M('Share Potencial', 'Share'),
                           M('Share Potencial AA', 'ShareAA'), M('Prospects Contatáveis', 'Prospects')], DS.share(), w=700, h=412))
V(k, 'sup', *SUP, native('barChart',
    {"Category": {"projections": [Col('Dim_Municipio', 'Municipio', 'Praça', active=True)]},
     "Series": {"projections": [Col('Fato_Prospects', 'Status_Prospect', 'Status')]},
     "Y": {"projections": [M('Prospects Total', 'Prospects')]}},
    {"categoryAxis": axis(fontSize=D(10), labelColor=C('#F2F4F5'), maxMarginFactor=L('35L')),
     "valueAxis": axis(show=B(False)),
     "legend": legend(True), "labels": labels(True, '#1A2026', precision=0, size=9),
     "dataPoint": series_colors('Fato_Prospects', 'Status_Prospect',
                                {'Liberado': '#FF8C00', 'Pendente Revisão': '#5B8DB8', 'Já é Cliente': '#5B6B78'})},
    'Base de prospects por praça e status',
    sort=[{"field": meas('_Medidas', 'Prospects Total'), "direction": "Descending"}]))
drawer(k)

# ================================================================== 5 · SWOT
k = 'swot'; chrome(k, 'Header SWOT', 'KPI SWOT', 'Insight SWOT')
V(k, 'hero', *HERO, deneb([Col('Dim_Cliente', 'Cliente_Rotulo', 'Cliente'), Col('Dim_Cliente', 'Ramo_Atividade', 'Ramo'),
                           Col('Dim_Municipio', 'Municipio', 'Municipio'), M('Quantidade', 'Qtd'),
                           M('Quantidade AA', 'QtdAA'), M('Média Qtd por Cliente', 'Media')], DS.swot(), w=700, h=412))
mat_obj = {
    "grid": props(gridVertical=B(False), gridHorizontal=B(True), gridHorizontalColor=GRID,
                  outlineColor=C('#34404A'), rowPadding=L('7L'), textSize=D(11)),
    "columnHeaders": props(fontColor=C('#9AA6B0'), backColor=C('#1A2026'), fontFamily=S('Segoe UI Semibold'),
                           fontSize=D(10), alignment=S('Center'), wordWrap=B(True)),
    "rowHeaders": props(fontColor=C('#F2F4F5'), backColor=C('#1A2026'), fontSize=D(11)),
    "values": props(fontColorPrimary=C('#F2F4F5'), backColorPrimary=C('#1A2026'),
                    fontColorSecondary=C('#F2F4F5'), backColorSecondary=C('#1A2026'), fontSize=D(12)),
    "total": props(fontColor=C('#FF8C00'), backColor=C('#1A2026'), fontFamily=S('Segoe UI Semibold'), fontSize=D(12)),
    "subTotals": props(rowSubtotals=B(True), columnSubtotals=B(False)),
    "columnFormatting": props(alignment=S('Center')),
}
V(k, 'sup', *SUP, native('pivotTable',
    {"Rows": {"projections": [Col('Dim_Municipio', 'Municipio', 'Praça', active=True)]},
     "Columns": {"projections": [Col('Seg_SWOT', 'Quadrante', 'Quadrante', active=True)]},
     "Values": {"projections": [M('SWOT Clientes', 'Clientes')]}},
    mat_obj, 'Clientes por quadrante e praça'))
drawer(k)

# ================================================================== 6 · Mix
k = 'mix'; chrome(k, 'Header Mix', 'Catalogo Linhas HTML', 'Insight Mix')
V(k, 'hero', *HERO, deneb([Col('Dim_Produto', 'Nome_Curto', 'Produto'), Col('Dim_Produto', 'Linha', 'Linha'),
                           Col('Dim_Produto', 'Familia', 'Familia'), Col('Dim_Catalogo', 'Produto_Oficial', 'Oficial'),
                           M('% Qtd s/ Total Produto', 'Volume'), M('% Fat s/ Total Produto', 'Faturamento')],
                          DS.dumbbell(), w=700, h=412))
V(k, 'sup', *SUP, native('clusteredBarChart',
    {"Category": {"projections": [Col('Dim_Produto', 'Nome_Curto', 'Produto', active=True)]},
     "Y": {"projections": [M('Preço Médio', 'Preço médio')]}},
    {"categoryAxis": axis(fontSize=D(10), labelColor=C('#F2F4F5'), maxMarginFactor=L('30L')),
     "valueAxis": axis(show=B(False)),
     "labels": labels(True, '#F2F4F5', units=1, precision=0, size=10),
     "dataPoint": props(fill=C('#FF8C00')), "legend": legend(False)},
    'Preço médio por produto (R$/un)', tooltip_page=PG['tt_prod'],
    sort=[{"field": meas('_Medidas', 'Preço Médio'), "direction": "Descending"}]))
drawer(k)

# ================================================================== 7 · Sucata
k = 'suc'; chrome(k, 'Header Sucata', 'KPI Sucata', 'Insight Sucata')
V(k, 'hero', *HERO, deneb([Col('Dim_Municipio', 'Municipio', 'Municipio'), Col('Fato_Sucata', 'Faixa_Atraso', 'Faixa'),
                           Col('Fato_Sucata', 'Ordem_Faixa', 'Ordem'), M('Sucata em Aberto kg', 'Kg'),
                           M('Lançamentos em Aberto', 'Lanc'), M('Clientes com Sucata', 'Clientes')], DS.aging(), w=700, h=412))
V(k, 'sup', 852, 188, 396, 416, html('Ranking Sucata HTML', CSS))
drawer(k)

# ================================================================== TOOLTIPS
VIS['tt_mes'] = []; V('tt_mes', 'tt', 0, 0, 360, 300, html('TT Mes HTML', CSS))
VIS['tt_vend'] = []; V('tt_vend', 'tt', 0, 0, 360, 230, html('TT Vendedor HTML', CSS))
VIS['tt_prod'] = []; V('tt_prod', 'tt', 0, 0, 360, 290, html('TT Produto HTML', CSS))

# ------------------------------------------------------------------ escrita
PAGES = [('capa', 'Capa', dict(bg='bg_com_capa.jpg'))] + [(a[0], a[2], {}) for a in ABAS] + [
    ('tt_mes', 'TT Mês', dict(w=360, h=300, bg='bg_com_tooltip.png', tooltip=True)),
    ('tt_vend', 'TT Vendedor', dict(w=360, h=230, bg='bg_com_tooltip.png', tooltip=True)),
    ('tt_prod', 'TT Produto', dict(w=360, h=290, bg='bg_com_tooltip.png', tooltip=True))]

for key, name, kw in PAGES:
    write(f'{DEF}/pages/{PG[key]}/page.json', page_json(key, name, **kw))
    for c in VIS[key]:
        write(f'{DEF}/pages/{PG[key]}/visuals/{c["name"]}/visual.json', c)
write(f'{DEF}/pages/pages.json', {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
    "pageOrder": [PG[k] for k, _, _ in PAGES], "activePageName": PG['capa']})
for b in BOOKMARKS:
    write(f'{DEF}/bookmarks/{b["name"]}.bookmark.json', b)
write(f'{DEF}/bookmarks/bookmarks.json', {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json",
    "items": [{"name": b["name"]} for b in BOOKMARKS]})

# report.json: mesmo cabeçalho salvo pelo Desktop no projeto Distribuidora, recursos próprios
rep = json.load(open(f'{REF}/definition/report.json', encoding='utf-8'))
rep['themeCollection']['customTheme']['name'] = 'VoltEx_Com_Theme.json'
res = ['bg_com_page.png', 'bg_com_capa.jpg', 'bg_com_tooltip.png', 'Logo_Bocardi_Data+Insights16179233929570047.png']
for pkg in rep['resourcePackages']:
    if pkg['name'] == 'RegisteredResources':
        pkg['items'] = [{"name": r, "path": r, "type": "Image"} for r in res] + \
            [{"name": "VoltEx_Com_Theme.json", "path": "VoltEx_Com_Theme.json", "type": "CustomTheme"}]
write(f'{DEF}/report.json', rep)
shutil.copyfile(f'{REF}/definition/version.json', f'{DEF}/version.json')
write(f'{REP}/definition.pbir', {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
    "version": "4.0", "datasetReference": {"byPath": {"path": "../VoltEx.Comercial.SemanticModel"}}})
write(f'{REP}/.platform', {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "Report", "displayName": "VoltEx.Comercial"},
    "config": {"version": "2.0", "logicalId": "4c8e2b1a-6d3f-5a7e-9b10-c2d3e4f5a6b7"}})
RR = f'{REP}/StaticResources/RegisteredResources'
SRC = f'{REF}/StaticResources/RegisteredResources'
os.makedirs(RR, exist_ok=True)
# Fundos: mesmo desenho da Distribuidora (rail, divisórias de zona e capa com o portfólio)
for a, b in (('bg_dist_page.png', 'bg_com_page.png'), ('bg_dist_capa.jpg', 'bg_com_capa.jpg'), ('bg_dist_tooltip.png', 'bg_com_tooltip.png')):
    shutil.copyfile(f'{SRC}/{a}', f'{RR}/{b}')
shutil.copyfile(f'{SRC}/Logo_Bocardi_Data+Insights16179233929570047.png', f'{RR}/Logo_Bocardi_Data+Insights16179233929570047.png')
os.makedirs(f'{REP}/StaticResources/SharedResources/BaseThemes', exist_ok=True)
shutil.copyfile(f'{REF}/StaticResources/SharedResources/BaseThemes/CY24SU10.json',
            f'{REP}/StaticResources/SharedResources/BaseThemes/CY24SU10.json')
theme = json.load(open(f'{SRC}/VoltEx_Dist_Theme.json', encoding='utf-8'))
theme['name'] = 'VoltEx Comercial Dark'
write(f'{RR}/VoltEx_Com_Theme.json', theme)
write(f'{ROOT}/VoltEx.Comercial.pbip', {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0", "artifacts": [{"report": {"path": "VoltEx.Comercial.Report"}}],
    "settings": {"enableAutoRecovery": True}})
n = sum(len(v) for v in VIS.values())
print('páginas', len(PAGES), 'visuais', n, 'bookmarks', len(BOOKMARKS))
