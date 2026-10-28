# -*- coding: utf-8 -*-
"""Helpers PBIR (formato salvo pelo Power BI Desktop do usuário)."""
import json, hashlib, base64

VC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.4.0/schema.json"
HTML_T = "htmlContent443BE3AD55E043BF878BED274D3A6865"
DENEB_T = "deneb7E15AEF80B9E4D4F8E12924291ECE89A"

def hid(*k):
    return hashlib.sha1('|'.join(map(str, k)).encode()).hexdigest()[:20]

def L(v):
    return {"expr": {"Literal": {"Value": v}}}

def S(s):
    return L("'" + s.replace("'", "''") + "'")

def B(b):
    return L('true' if b else 'false')

def D(n):
    return L(f'{n}D')

def C(hexc):
    return {"solid": {"color": L(f"'{hexc}'")}}

def props(**kw):
    return [{"properties": kw}]

def meas(entity, prop):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}

def colm(entity, prop):
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}

def proj(field_kind, entity, prop, display=None, active=None):
    f = meas(entity, prop) if field_kind == 'm' else colm(entity, prop)
    p = {"field": f, "queryRef": f"{entity}.{prop}", "nativeQueryRef": prop}
    if display:
        p["displayName"] = display
    if active is not None:
        p["active"] = active
    return p

def M(prop, display=None):
    return proj('m', '_Medidas', prop, display)

def Col(entity, prop, display=None, active=None):
    return proj('c', entity, prop, display, active)

def vco(title=None, bg=None, transparency=0, pad=None, link=None, tooltip_page=None):
    o = {
        "background": props(show=B(False)) if not bg else props(show=B(True), color=C(bg), transparency=D(transparency)),
        "border": props(show=B(False)),
        "dropShadow": props(show=B(False)),
        "visualHeader": props(show=B(False)),
        "title": props(show=B(False)) if not title else props(
            show=B(True), text=S(title), fontColor=C('#C9D3DB'), fontSize=D(11),
            fontFamily=S('Segoe UI Semibold'), bold=B(False)),
    }
    if pad is not None:
        o["padding"] = props(top=D(pad[0]), bottom=D(pad[1]), left=D(pad[2]), right=D(pad[3]))
    if link:
        o["visualLink"] = props(**link)
    if tooltip_page:
        o["visualTooltip"] = props(show=B(True), type=S('Canvas'), section=S(tooltip_page))
    return o

def container(name, x, y, w, h, z, visual=None, parent=None, hidden=False, group=None):
    c = {"$schema": VC_SCHEMA, "name": name,
         "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z}}
    if group:
        c["visualGroup"] = {"displayName": group, "groupMode": "ScaleMode"}
    if visual:
        visual.setdefault("drillFilterOtherVisuals", True)
        c["visual"] = visual
    if parent:
        c["parentGroupName"] = parent
    if hidden:
        c["isHidden"] = True
    return c

# ------------------------------------------------------------------ links
def nav(page):
    return dict(show=B(True), type=S('PageNavigation'), navigationSection=S(page))

def bmk(bm):
    return dict(show=B(True), type=S('Bookmark'), bookmark=S(bm))

def clear_all():
    return dict(show=B(True), type=S('ClearAllSlicers'))

# ------------------------------------------------------------------ visuais
def image(svg_or_uri, link=None, scaling='Fit'):
    uri = svg_or_uri if svg_or_uri.startswith('data:') else \
        'data:image/svg+xml;base64,' + base64.b64encode(svg_or_uri.encode('utf-8')).decode()
    return {"visualType": "image",
            "objects": {"general": props(imageUrl=S(uri)),
                        "imageScaling": props(imageScalingType=S(scaling))},
            "visualContainerObjects": vco(link=link)}

def image_resource(item, link=None, title=None):
    return {"visualType": "image",
            "objects": {"image": props(sourceFile={"image": {
                "name": S(item), "url": {"expr": {"ResourcePackageItem": {
                    "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": item}}},
                "scaling": S('Normal')}}),
                "imageScaling": props(imageScalingType=S('Fit'))},
            "visualContainerObjects": vco(link=link)}

def html(measure, css, link=None):
    return {"visualType": HTML_T,
            "query": {"queryState": {"content": {"projections": [M(measure)]}}},
            "objects": {
                "contentFormatting": props(showRawHtml=B(False), fontFamily=S('Segoe UI'), fontSize=D(11),
                                           fontColour=C('#F2F4F5'), align=S('left'), noDataMessage=S(' ')),
                "stylesheet": props(stylesheet=S(css)),
                "compatibility": props(legacyRedirects=B(False)) if False else props(legacyRendering=B(True))},
            "visualContainerObjects": vco(link=link)}

def deneb(fields, spec, title=None, w=600, h=400):
    """fields: lista de projeções (com displayName = nome do campo na spec)."""
    cfg = {}
    for p in fields:
        n = p.get("displayName", p["nativeQueryRef"])
        is_m = "Measure" in p["field"]
        cfg[n] = {"highlight": False, "highlightStatus": False, "highlightComparator": False,
                  "format": is_m, "formatted": is_m, "names": False}
    return {"visualType": DENEB_T,
            "query": {"queryState": {"dataset": {"projections": fields}}},
            "objects": {
                "vega": props(jsonSpec=S(json.dumps(spec, ensure_ascii=False, indent=2)), jsonConfig=S('{}'),
                              provider=S('vegaLite'), renderMode=S('svg'), enableTooltips=B(True),
                              enableContextMenu=B(True), enableSelection=B(False), version=S('6.4.3')),
                "developer": props(locale=S('pt-BR'), version=S('2.0.0.0')),
                "stateManagement": props(viewportHeight=D(h), viewportWidth=D(w),
                                         supportFieldConfiguration=S(json.dumps(cfg)),
                                         denebMetaVersion=S('2'), consolidateFieldParameters=B(False))},
            "visualContainerObjects": vco(title=title, pad=(4, 4, 6, 6))}

AX = dict(show=B(True), showAxisTitle=B(False), gridlineShow=B(False), labelColor=C('#9AA6B0'),
          fontSize=D(9), fontFamily=S('Segoe UI'))

def axis(**over):
    d = dict(AX); d.update(over); return props(**d)

def legend(show=True, pos='Top'):
    return props(show=B(show), position=S(pos), showTitle=B(False), labelColor=C('#9AA6B0'), fontSize=D(9))

def labels(show=True, color='#C9D3DB', units=None, precision=None, size=9):
    p = dict(show=B(show), color=C(color), fontSize=D(size))
    if units is not None: p['labelDisplayUnits'] = D(units)
    if precision is not None: p['labelPrecision'] = L(f'{precision}L')
    return props(**p)

def series_colors(entity, prop, mapping):
    out = []
    for val, colr in mapping.items():
        out.append({"properties": {"fill": C(colr)},
                    "selector": {"data": [{"scopeId": {"Comparison": {
                        "ComparisonKind": 0, "Left": colm(entity, prop), "Right": {"Literal": {"Value": f"'{val}'"}}}}}]}})
    return out

def measure_colors(mapping):
    return [{"properties": {"fill": C(c)}, "selector": {"metadata": f"_Medidas.{m}"}} for m, c in mapping.items()]

def slicer(entity, prop, header, sync, mode='Dropdown', single=False, default=None, default_kind='L'):
    v = {"visualType": "slicer",
         "query": {"queryState": {"Values": {"projections": [Col(entity, prop, active=True)]}}},
         "objects": {
             "data": props(mode=S(mode)),
             "selection": props(singleSelect=B(single), selectAllCheckboxEnabled=B(not single)),
             "header": props(show=B(True), text=S(header), fontColor=C('#9AA6B0'), textSize=D(9),
                             fontFamily=S('Segoe UI Semibold')),
             "items": props(fontColor=C('#F2F4F5'), background=C('#1A2026'), textSize=D(10),
                            fontFamily=S('Segoe UI'))},
         "visualContainerObjects": vco(bg='#1A2026', pad=(4, 4, 8, 8)),
         "syncGroup": {"groupName": sync, "fieldChanges": True, "filterChanges": True}}
    if default is not None:
        v["objects"]["general"] = props(filter={"filter": {
            "Version": 2, "From": [{"Name": "d", "Entity": entity, "Type": 0}],
            "Where": [{"Condition": {"In": {
                "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}],
                "Values": [[{"Literal": {"Value": default}}]]}}}]}})
    return v
