# -*- coding: utf-8 -*-
"""Specs Vega-Lite (Deneb) da VoltEx Comercial. Campos = displayName das projeções."""

SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"
CFG = {"background": "transparent", "view": {"stroke": None}, "font": "Segoe UI",
       "axis": {"labelColor": "#9AA6B0", "labelFont": "Segoe UI", "labelFontSize": 10, "titleColor": "#9AA6B0",
                "titleFont": "Segoe UI", "titleFontWeight": "normal", "titleFontSize": 10,
                "domain": False, "ticks": False, "gridColor": "#2C363E"},
       "legend": {"labelColor": "#9AA6B0", "titleColor": "#9AA6B0", "labelFont": "Segoe UI"},
       "title": {"color": "#C9D3DB", "font": "Segoe UI Semibold", "fontSize": 12, "fontWeight": "normal",
                 "anchor": "start", "offset": 12},
       "locale": {"number": {"decimal": ",", "thousands": ".", "grouping": [3], "currency": ["R$ ", ""]},
                  "time": {"dateTime": "%A, %e de %B de %Y. %X", "date": "%d/%m/%Y", "time": "%H:%M:%S",
                           "periods": ["AM", "PM"],
                           "days": ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"],
                           "shortDays": ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"],
                           "months": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
                                      "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
                           "shortMonths": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set",
                                           "Out", "Nov", "Dez"]}}}

def base(title, **kw):
    s = {"$schema": SCHEMA, "data": {"name": "dataset"}, "config": CFG,
         "title": {"text": title}, "width": "container", "height": "container"}
    s.update(kw)
    return s

ROW_AXIS = {"title": None, "labelColor": "#F2F4F5", "labelFontSize": 12, "labelPadding": 12}

# ---------------------------------------------------------------- 1. Evolução mensal
def evolucao():
    X = {"field": "Mes", "type": "ordinal", "timeUnit": "yearmonth",
         "axis": {"format": "%b/%y", "title": None, "labelAngle": 0, "labelOverlap": "greedy"}}
    return base(
        "Baterias por mês · barra = período, traço = mesmo mês do ano anterior",
        transform=[{"calculate": "datum['Status'] == 'Parcial'", "as": "parcial"}],
        encoding={"x": X},
        layer=[
            {"mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3, "width": {"band": 0.62}},
             "encoding": {
                 "y": {"field": "Qtd", "type": "quantitative",
                       "axis": {"title": None, "format": "~s", "grid": True, "gridDash": [2, 3], "tickCount": 4}},
                 "color": {"condition": {"test": "datum.parcial", "value": "#3A2A16"}, "value": "#FF8C00"},
                 "stroke": {"condition": {"test": "datum.parcial", "value": "#FF8C00"}, "value": None},
                 "strokeDash": {"value": [3, 2]},
                 "tooltip": [{"field": "Mes", "type": "ordinal", "timeUnit": "yearmonth", "format": "%B/%Y", "title": "Mês"},
                             {"field": "Status", "title": "Situação"},
                             {"field": "Qtd", "format": ",.0f", "title": "Baterias"},
                             {"field": "QtdAA", "format": ",.0f", "title": "Ano anterior"},
                             {"field": "Var", "format": "+.1%", "title": "Variação"},
                             {"field": "Fat", "format": ",.0f", "title": "Faturamento (R$)"},
                             {"field": "Cob", "format": ".1%", "title": "Cobertura"}]}},
            {"mark": {"type": "tick", "color": "#F2F4F5", "thickness": 2, "size": 22, "opacity": 0.9},
             "encoding": {"y": {"field": "QtdAA", "type": "quantitative"}}},
            {"transform": [{"filter": "isValid(datum['Var']) && !datum.parcial"}],
             "mark": {"type": "text", "dy": -10, "fontSize": 10, "fontWeight": 600},
             "encoding": {"y": {"field": "Qtd", "type": "quantitative"},
                          "text": {"field": "Var", "format": "+.0%"},
                          "color": {"condition": {"test": "datum['Var'] < 0", "value": "#FF6B6F"}, "value": "#3FB68B"}}},
            {"transform": [{"filter": "datum.parcial"}],
             "mark": {"type": "text", "dy": -10, "fontSize": 10, "color": "#FFB45C", "text": "parcial"},
             "encoding": {"y": {"field": "Qtd", "type": "quantitative"}}}
        ])

# ---------------------------------------------------------------- 2. Bullet de metas
def bullet():
    return base(
        "Atingimento da meta da Linha Leve por vendedor · ◆ = tendência com o mês corrente projetado",
        transform=[
            {"calculate": "datum['Ating']", "as": "ating"},
            {"calculate": "min(datum.ating, 1.5)", "as": "plot"},
            {"calculate": "min(datum['Tend'], 1.5)", "as": "tend"},
            {"calculate": "datum['Gap'] > 0 ? 'faltam ' + format(datum['Gap'], ',.0f') + ' un' : 'meta batida'", "as": "gaptxt"}],
        encoding={"y": {"field": "Vendedor", "type": "nominal", "sort": {"field": "ating", "op": "min", "order": "ascending"},
                        "axis": ROW_AXIS}},
        layer=[
            {"mark": {"type": "bar", "color": "#252E36", "height": {"band": 0.62}},
             "encoding": {"x": {"datum": 0}, "x2": {"datum": 1.5}}},
            {"mark": {"type": "bar", "color": "#2F3A44", "height": {"band": 0.62}},
             "encoding": {"x": {"datum": 0}, "x2": {"datum": 1.0}}},
            {"mark": {"type": "bar", "color": "#38454F", "height": {"band": 0.62}},
             "encoding": {"x": {"datum": 0}, "x2": {"datum": 0.8}}},
            {"mark": {"type": "bar", "height": {"band": 0.22}, "cornerRadiusEnd": 2},
             "encoding": {
                 "x": {"field": "plot", "type": "quantitative", "scale": {"domain": [0, 1.5], "clamp": True},
                       "axis": {"format": ".0%", "title": None, "values": [0, 0.5, 0.8, 1, 1.25, 1.5],
                                "grid": True, "gridDash": [2, 3]}},
                 "color": {"condition": {"test": "datum.ating < 0.8", "value": "#E5484D"}, "value": "#FF8C00"},
                 "tooltip": [{"field": "Vendedor"},
                             {"field": "Realizado", "format": ",.0f", "title": "Vendas Linha Leve (un)"},
                             {"field": "Meta", "format": ",.0f", "title": "Meta (un)"},
                             {"field": "ating", "format": ".1%", "title": "Atingimento"},
                             {"field": "Tend", "format": ".1%", "title": "Tendência"},
                             {"field": "Cob", "format": ".1%", "title": "Cobertura da carteira"}]}},
            {"mark": {"type": "tick", "color": "#F2F4F5", "thickness": 2, "size": 30},
             "encoding": {"x": {"datum": 1}}},
            {"transform": [{"filter": "isValid(datum.tend) && abs(datum.tend - datum.plot) > 0.005"}],
             "mark": {"type": "point", "shape": "diamond", "size": 70, "filled": True, "color": "#F2F4F5", "stroke": "#1A2026"},
             "encoding": {"x": {"field": "tend", "type": "quantitative"}}},
            {"mark": {"type": "text", "align": "left", "dx": 10, "fontSize": 11, "color": "#F2F4F5"},
             "encoding": {"x": {"field": "plot", "type": "quantitative"},
                          "text": {"field": "ating", "format": ".0%"}}},
            {"mark": {"type": "text", "align": "right", "baseline": "bottom", "dy": -9, "fontSize": 9, "color": "#7D8A95"},
             "encoding": {"x": {"datum": 1.5}, "text": {"field": "gaptxt"}}}
        ])

# ---------------------------------------------------------------- 3. RFQ
SEG = ["Campeões", "Leais", "Ocasionais", "Em risco", "Sem compra 12M"]
SEG_COR = ["#FF8C00", "#FFB45C", "#8A98A4", "#E5484D", "#4A5862"]
def rfq():
    return base(
        "Segmentos RFQ · barra = % do volume 12M, traço = % dos clientes",
        transform=[{"calculate": "format(datum['Clientes'], ',.0f') + ' clientes · R$ ' + format(datum['Fat'] / 1000000, ',.1f') + ' mi'",
                    "as": "txt"}],
        encoding={"y": {"field": "Segmento", "type": "nominal", "sort": SEG,
                        "axis": {**ROW_AXIS, "labelFontSize": 13}}},
        layer=[
            {"mark": {"type": "bar", "color": "#252E36", "height": {"band": 0.56}},
             "encoding": {"x": {"datum": 0}, "x2": {"datum": 1}}},
            {"mark": {"type": "bar", "height": {"band": 0.56}, "cornerRadiusEnd": 3},
             "encoding": {
                 "x": {"field": "PctQtd", "type": "quantitative", "scale": {"domain": [0, 1]},
                       "axis": {"format": ".0%", "title": None, "grid": True, "gridDash": [2, 3], "values": [0, 0.25, 0.5, 0.75, 1]}},
                 "color": {"field": "Segmento", "type": "nominal", "scale": {"domain": SEG, "range": SEG_COR}, "legend": None},
                 "tooltip": [{"field": "Segmento"}, {"field": "Regra", "title": "Regra"},
                             {"field": "Clientes", "format": ",.0f"},
                             {"field": "PctCli", "format": ".1%", "title": "% dos clientes"},
                             {"field": "Qtd", "format": ",.0f", "title": "Baterias 12M"},
                             {"field": "PctQtd", "format": ".1%", "title": "% do volume 12M"},
                             {"field": "Fat", "format": ",.0f", "title": "Faturamento 12M (R$)"}]}},
            {"mark": {"type": "tick", "color": "#F2F4F5", "thickness": 2.5, "bandSize": 30},
             "encoding": {"x": {"field": "PctCli", "type": "quantitative"}}},
            {"mark": {"type": "text", "align": "left", "dx": 8, "fontSize": 13, "fontWeight": 600, "color": "#F2F4F5"},
             "encoding": {"x": {"field": "PctQtd", "type": "quantitative"}, "text": {"field": "PctQtd", "format": ".0%"}}},
            {"mark": {"type": "text", "align": "right", "baseline": "bottom", "dy": -16, "fontSize": 10, "color": "#9AA6B0"},
             "encoding": {"x": {"datum": 1}, "text": {"field": "txt"}}}
        ])

# ---------------------------------------------------------------- 4. Share por praça
def share():
    return base(
        "Potencial × vendido por praça · ordenado pelo potencial, onde está a oportunidade",
        transform=[
            {"calculate": "datum['Municipio'] + ' · ' + datum['UF']", "as": "praca"},
            {"calculate": "isValid(datum['ShareAA']) ? format((datum['Share'] - datum['ShareAA']) * 100, '+.1f') + ' p.p.' : ''", "as": "dpp"},
            {"calculate": "format(datum['Share'], '.1%') + '  ' + datum.dpp", "as": "lbl"},
            {"calculate": "format(datum['Prospects'], ',.0f') + ' prospects'", "as": "prs"}],
        encoding={"y": {"field": "praca", "type": "nominal", "sort": {"field": "Potencial", "op": "max", "order": "descending"},
                        "axis": {**ROW_AXIS, "labelLimit": 220}}},
        layer=[
            {"mark": {"type": "bar", "color": "#2F3A44", "height": {"band": 0.6}, "cornerRadiusEnd": 3},
             "encoding": {"x": {"field": "Potencial", "type": "quantitative",
                                "axis": {"format": "~s", "title": None, "grid": True, "gridDash": [2, 3], "tickCount": 5}},
                          "tooltip": [{"field": "praca", "title": "Praça"},
                                      {"field": "Potencial", "format": ",.0f", "title": "Potencial no período"},
                                      {"field": "Vendido", "format": ",.0f", "title": "Vendido"},
                                      {"field": "Share", "format": ".1%"},
                                      {"field": "ShareAA", "format": ".1%", "title": "Share AA"},
                                      {"field": "Prospects", "format": ",.0f", "title": "Prospects contatáveis"}]}},
            {"mark": {"type": "bar", "color": "#FF8C00", "height": {"band": 0.26}, "cornerRadiusEnd": 2},
             "encoding": {"x": {"field": "Vendido", "type": "quantitative"}}},
            {"mark": {"type": "text", "align": "left", "dx": 8, "fontSize": 12, "fontWeight": 600, "color": "#F2F4F5"},
             "encoding": {"x": {"field": "Vendido", "type": "quantitative"}, "text": {"field": "lbl"}}},
            {"mark": {"type": "text", "align": "left", "dx": 8, "dy": 15, "fontSize": 10, "color": "#9AA6B0"},
             "encoding": {"x": {"field": "Vendido", "type": "quantitative"}, "text": {"field": "prs"}}}
        ])

# ---------------------------------------------------------------- 5. SWOT (quadrantes)
QUAD = ["Fortalezas", "Atenção", "Oportunidades", "Fraquezas"]
QUAD_COR = ["#3FB68B", "#F2B84B", "#5B8DB8", "#E5484D"]
def swot():
    def lab(t, cor, x, y, al, bl):
        return {"data": {"values": [{}]},
                "mark": {"type": "text", "text": t, "x": x, "y": y, "align": al, "baseline": bl, "fontSize": 10,
                         "fontWeight": 600, "color": cor, "opacity": 0.9}}
    return base(
        "Clientes por porte e tendência · cada ponto é um cliente",
        transform=[
            {"filter": "datum['Qtd'] > 0"},
            {"calculate": "isValid(datum['QtdAA']) && datum['QtdAA'] > 0 ? datum['Qtd'] / datum['QtdAA'] - 1 : 0", "as": "var"},
            {"calculate": "max(min(datum.var, 1), -0.6)", "as": "vplot"},
            {"calculate": "datum['Qtd'] >= datum['Media']", "as": "grande"},
            {"calculate": "datum['Qtd'] >= (isValid(datum['QtdAA']) ? datum['QtdAA'] : 0)", "as": "cresce"},
            {"calculate": "datum.grande ? (datum.cresce ? 'Fortalezas' : 'Atenção') : (datum.cresce ? 'Oportunidades' : 'Fraquezas')",
             "as": "quad"}],
        layer=[
            {"mark": {"type": "point", "filled": True, "size": 54, "opacity": 0.85, "stroke": "#1A2026", "strokeWidth": 0.6},
             "encoding": {
                 "x": {"field": "Qtd", "type": "quantitative", "scale": {"zero": False, "nice": True},
                       "axis": {"title": "Baterias no período →", "format": ",.0f", "grid": True, "gridDash": [2, 3], "tickCount": 5}},
                 "y": {"field": "vplot", "type": "quantitative", "scale": {"domain": [-0.6, 1]},
                       "axis": {"title": "vs mesmo período AA →", "format": "+.0%", "grid": True, "gridDash": [2, 3],
                                "values": [-0.5, -0.25, 0, 0.25, 0.5, 0.75, 1]}},
                 "color": {"field": "quad", "type": "nominal", "scale": {"domain": QUAD, "range": QUAD_COR}, "legend": None},
                 "tooltip": [{"field": "Cliente"}, {"field": "Ramo"}, {"field": "Municipio", "title": "Município"},
                             {"field": "quad", "title": "Quadrante"},
                             {"field": "Qtd", "format": ",.0f", "title": "Baterias"},
                             {"field": "QtdAA", "format": ",.0f", "title": "Ano anterior"},
                             {"field": "var", "format": "+.1%", "title": "Variação"}]}},
            {"mark": {"type": "rule", "color": "#9AA6B0", "strokeDash": [4, 4], "opacity": 0.7},
             "encoding": {"x": {"aggregate": "max", "field": "Media", "type": "quantitative"}}},
            {"mark": {"type": "rule", "color": "#9AA6B0", "strokeDash": [4, 4], "opacity": 0.7},
             "encoding": {"y": {"datum": 0}}},
            lab("FORTALEZAS", QUAD_COR[0], {"expr": "width - 6"}, 4, "right", "top"),
            lab("ATENÇÃO", QUAD_COR[1], {"expr": "width - 6"}, {"expr": "height - 6"}, "right", "bottom"),
            lab("OPORTUNIDADES", QUAD_COR[2], 6, 4, "left", "top"),
            lab("FRAQUEZAS", QUAD_COR[3], 6, {"expr": "height - 6"}, "left", "bottom"),
        ])

# ---------------------------------------------------------------- 6. Dumbbell
def dumbbell():
    return base(
        "Peso no volume × peso no faturamento, por produto",
        transform=[{"fold": ["Volume", "Faturamento"], "as": ["medida", "valor"]}],
        encoding={"y": {"field": "Produto", "type": "nominal", "sort": None, "axis": ROW_AXIS}},
        layer=[
            {"mark": {"type": "rule", "color": "#4A5862", "strokeWidth": 3},
             "encoding": {"x": {"aggregate": "min", "field": "valor", "type": "quantitative"},
                          "x2": {"aggregate": "max", "field": "valor"}}},
            {"mark": {"type": "circle", "size": 200, "opacity": 1, "stroke": "#1A2026", "strokeWidth": 2},
             "encoding": {
                 "x": {"field": "valor", "type": "quantitative",
                       "axis": {"format": ".0%", "title": None, "grid": True, "gridDash": [2, 3], "tickCount": 5}},
                 "color": {"field": "medida", "type": "nominal",
                           "scale": {"domain": ["Volume", "Faturamento"], "range": ["#8A98A4", "#FF8C00"]},
                           "legend": {"orient": "top", "title": None, "direction": "horizontal", "symbolType": "circle"}},
                 "tooltip": [{"field": "Produto"}, {"field": "Linha"}, {"field": "Familia", "title": "Família"}, {"field": "Oficial", "title": "Produto oficial"},
                             {"field": "medida", "title": "Medida"},
                             {"field": "valor", "format": ".1%", "title": "% do total"}]}},
            {"mark": {"type": "text", "dy": -14, "fontSize": 10},
             "encoding": {"x": {"field": "valor", "type": "quantitative"},
                          "text": {"field": "valor", "format": ".0%"},
                          "color": {"field": "medida", "type": "nominal",
                                    "scale": {"domain": ["Volume", "Faturamento"], "range": ["#9AA6B0", "#FFB45C"]},
                                    "legend": None}}}
        ],
        resolve={"scale": {"color": "independent"}})

# ---------------------------------------------------------------- 7. Aging da sucata
def aging():
    return base(
        "Onde a sucata está parada · kg em aberto por praça e faixa de atraso",
        transform=[{"joinaggregate": [{"op": "sum", "field": "Kg", "as": "tot"}], "groupby": ["Municipio"]},
                   {"calculate": "datum['Municipio'] + '  ' + format(datum.tot / 1000, ',.1f') + ' t'", "as": "praca"},
                   {"calculate": "format(datum['Lanc'], ',.0f') + ' lanç.'", "as": "lanctxt"}],
        encoding={
            "x": {"field": "Faixa", "type": "ordinal", "sort": {"field": "Ordem", "op": "min", "order": "ascending"},
                  "axis": {"orient": "top", "title": None, "labelColor": "#F2F4F5", "labelAngle": 0, "labelFontSize": 11}},
            "y": {"field": "praca", "type": "nominal", "sort": {"field": "tot", "op": "max", "order": "descending"},
                  "axis": {"title": None, "labelColor": "#F2F4F5", "labelFontSize": 11, "labelPadding": 10}}},
        layer=[
            {"mark": {"type": "rect", "cornerRadius": 4, "stroke": "#1A2026", "strokeWidth": 4},
             "encoding": {
                 "color": {"field": "Kg", "type": "quantitative",
                           "scale": {"range": ["#252E36", "#6B4416", "#FF8C00"], "interpolate": "rgb"}, "legend": None},
                 "tooltip": [{"field": "Municipio", "title": "Praça"}, {"field": "Faixa", "title": "Atraso"},
                             {"field": "Kg", "format": ",.0f", "title": "kg em aberto"},
                             {"field": "Lanc", "format": ",.0f", "title": "Lançamentos"},
                             {"field": "Clientes", "format": ",.0f"}]}},
            {"transform": [{"filter": "datum['Ordem'] == 4 && datum['Kg'] > 0"}],
             "mark": {"type": "rect", "cornerRadius": 4, "fill": None, "stroke": "#E5484D", "strokeWidth": 1.5}},
            {"mark": {"type": "text", "fontSize": 14, "fontWeight": 600, "dy": -6},
             "encoding": {"text": {"field": "Kg", "format": ",.0f"},
                          "color": {"condition": {"test": "datum['Kg'] > 2200", "value": "#1A2026"}, "value": "#F2F4F5"}}},
            {"mark": {"type": "text", "fontSize": 9, "dy": 10},
             "encoding": {"text": {"field": "lanctxt"},
                          "color": {"condition": {"test": "datum['Kg'] > 2200", "value": "#3A2A16"}, "value": "#9AA6B0"}}}
        ])
