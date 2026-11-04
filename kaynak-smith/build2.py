#!/usr/bin/env python3
"""4 basit kaynak örneği: gerilmeler + Smith diyagramı + dikiş faktörleri (v1, v2, v3).

Kullanım:  python3 build2.py && node render.js ornekler
"""
import math
from pathlib import Path

from build import smith_svg, legend, reading, tr, trg, ust, alt  # aynı St37 diyagramı

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- sabitler
A_C, A_K, I_X, Y_MAX = 960.0, 720.0, 478080.0, 36.0
W = I_X / Y_MAX                       # 13 280
SIG_EM = 170.0                        # parçanın statik emniyet gerilmesi (136 / 0,8)
V1_DIN, V2, V3 = 0.42, 1.0, 0.8       # iki taraflı düz köşe · 1. kalite · köşe (boğaz) kaynağı
K_DIN = V1_DIN * V2 * V3              # 0,336
SKEM_ST = 1.0 * V2 * V3 * SIG_EM      # 136

RED, GREEN, BLUE, INK, MUTED, ORANGE = "#c0392b", "#1e8a4c", "#2563eb", "#1d232a", "#6b7480", "#d9822b"


# ---------------------------------------------------------------- çizimler
def section_svg():
    """20×60 kesit, çepeçevre a = 6 dikiş."""
    s = 2.3
    w, h, a = 20 * s, 60 * s, 6 * s
    cx, cy = 150, 130
    x0, y0 = cx - w / 2, cy - h / 2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 260" width="330" height="260" font-family="Inter, sans-serif">']
    o.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#e9ecef" stroke="{INK}" stroke-width="1.2"/>')
    # dikey dikişler (turuncu), yatay dikişler (yeşil)
    o.append(f'<rect x="{x0 - a:.1f}" y="{y0:.1f}" width="{a:.1f}" height="{h:.1f}" fill="{ORANGE}" opacity="0.85"/>')
    o.append(f'<rect x="{x0 + w:.1f}" y="{y0:.1f}" width="{a:.1f}" height="{h:.1f}" fill="{ORANGE}" opacity="0.85"/>')
    o.append(f'<rect x="{x0:.1f}" y="{y0 - a:.1f}" width="{w:.1f}" height="{a:.1f}" fill="{GREEN}" opacity="0.85"/>')
    o.append(f'<rect x="{x0:.1f}" y="{y0 + h:.1f}" width="{w:.1f}" height="{a:.1f}" fill="{GREEN}" opacity="0.85"/>')
    # nötr eksen
    o.append(f'<line x1="{x0 - a - 18:.1f}" y1="{cy}" x2="{x0 + w + a + 18:.1f}" y2="{cy}" stroke="{MUTED}" stroke-dasharray="6 3 1.5 3"/>')
    o.append(f'<text x="{x0 - a - 20:.1f}" y="{cy + 4}" font-size="11" fill="{MUTED}" text-anchor="end">eksen</text>')
    # ölçüler
    o.append(f'<line x1="{x0:.1f}" y1="{y0 + h + a + 16:.1f}" x2="{x0 + w:.1f}" y2="{y0 + h + a + 16:.1f}" stroke="{INK}" stroke-width="0.8"/>')
    o.append(f'<text x="{cx}" y="{y0 + h + a + 30:.1f}" font-size="11.5" fill="{INK}" text-anchor="middle">20</text>')
    xd = x0 + w + a + 30
    o.append(f'<line x1="{xd:.1f}" y1="{y0:.1f}" x2="{xd:.1f}" y2="{y0 + h:.1f}" stroke="{INK}" stroke-width="0.8"/>')
    o.append(f'<text x="{xd + 6:.1f}" y="{cy + 22:.1f}" font-size="11.5" fill="{INK}">60</text>')
    xy = xd + 34
    o.append(f'<line x1="{xy:.1f}" y1="{y0 - a:.1f}" x2="{xy:.1f}" y2="{cy:.1f}" stroke="{RED}" stroke-width="1"/>')
    o.append(f'<line x1="{xy - 4:.1f}" y1="{y0 - a:.1f}" x2="{xy + 4:.1f}" y2="{y0 - a:.1f}" stroke="{RED}"/>')
    o.append(f'<text x="{xy + 6:.1f}" y="{(y0 - a + cy) / 2 + 4:.1f}" font-size="11.5" fill="{RED}">y = 36</text>')
    o.append(f'<text x="{cx}" y="{y0 - a - 8:.1f}" font-size="11.5" fill="{INK}" text-anchor="middle">a = 6</text>')
    o.append('</svg>')
    return "\n".join(o)


def side_svg(kind):
    """Yan görünüş: duvar + dikiş + parça + kuvvet. kind: asagi | orta | ust | alt"""
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 170" width="330" height="170" font-family="Inter, sans-serif">',
         f'<defs><marker id="fa{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="10" markerHeight="10" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>'
         '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#9aa3ad" stroke-width="1.2"/></pattern></defs>']
    top, bot = 45, 115
    mid = (top + bot) / 2
    o.append(f'<rect x="12" y="20" width="16" height="130" fill="url(#hatch)" stroke="#9aa3ad"/>')
    o.append(f'<rect x="28" y="{top}" width="7" height="{bot - top}" fill="{GREEN}"/>')
    o.append(f'<rect x="35" y="{top}" width="200" height="{bot - top}" fill="#f3f4f6" stroke="{INK}" stroke-width="1.2"/>')
    o.append(f'<line x1="20" y1="{mid}" x2="318" y2="{mid}" stroke="{MUTED}" stroke-dasharray="6 3 1.5 3"/>')
    o.append(f'<text x="44" y="{mid - 5}" font-size="10.5" fill="{MUTED}">eksen</text>')
    o.append(f'<text x="20" y="163" font-size="10.5" fill="{MUTED}" text-anchor="middle">duvar</text>')
    o.append(f'<text x="42" y="163" font-size="10.5" fill="{GREEN}">dikiş</text>')
    lab = "F = 8000 ± 2000 N"
    hot = None
    if kind == "asagi":
        x = 225
        o.append(f'<line x1="{x}" y1="{bot}" x2="{x}" y2="{bot + 42}" stroke="{RED}" stroke-width="2.6" marker-end="url(#fa{kind})"/>')
        o.append(f'<text x="{x - 6}" y="{bot + 36}" font-size="11.5" font-weight="600" fill="{RED}" text-anchor="end">{lab}</text>')
        o.append(f'<line x1="35" y1="30" x2="{x}" y2="30" stroke="{INK}" stroke-width="0.8"/>')
        o.append(f'<line x1="35" y1="25" x2="35" y2="35" stroke="{INK}" stroke-width="0.8"/><line x1="{x}" y1="25" x2="{x}" y2="35" stroke="{INK}" stroke-width="0.8"/>')
        o.append(f'<text x="{(35 + x) / 2}" y="24" font-size="11.5" fill="{INK}" text-anchor="middle">kol = 80 mm</text>')
        hot = top
    else:
        e_px = {"orta": 0, "ust": -24, "alt": 24}[kind]
        y = mid + e_px
        o.append(f'<line x1="235" y1="{y}" x2="300" y2="{y}" stroke="{RED}" stroke-width="2.6" marker-end="url(#fa{kind})"/>')
        ty = {"orta": top - 8, "ust": top - 8, "alt": bot + 20}[kind]
        o.append(f'<text x="318" y="{ty}" font-size="11.5" font-weight="600" fill="{RED}" text-anchor="end">{lab}</text>')
        if kind == "orta":
            o.append(f'<text x="318" y="{y + 18}" font-size="10.5" fill="{MUTED}" text-anchor="end">e = 0</text>')
        else:
            xe = 250
            o.append(f'<line x1="{xe}" y1="{mid}" x2="{xe}" y2="{y}" stroke="{INK}" stroke-width="0.8"/>')
            o.append(f'<text x="{xe + 6}" y="{(mid + y) / 2 + 4}" font-size="11" fill="{INK}">e = 20 mm</text>')
            hot = top if kind == "ust" else bot
    if hot is not None:
        o.append(f'<circle cx="31.5" cy="{hot}" r="6" fill="none" stroke="{RED}" stroke-width="2"/>')
    elif kind == "orta":
        o.append(f'<rect x="25" y="{top - 3}" width="13" height="{bot - top + 6}" fill="none" stroke="{RED}" stroke-width="1.6" rx="3"/>')
    o.append('</svg>')
    return "\n".join(o)


# ---------------------------------------------------------------- örnek
def solve(kind):
    """Gerilmeleri baştan hesapla (statik 8000 N, dinamik 2000 N)."""
    r = {}
    for part, F in (("st", 8000.0), ("din", 2000.0)):
        if kind == "asagi":
            sc, tau, M = 0.0, F / A_K, F * 80
        elif kind == "orta":
            sc, tau, M = F / A_C, 0.0, 0.0
        else:
            sc, tau, M = F / A_C, 0.0, F * 20
        se = M / W
        sig = sc + se
        r[part] = dict(F=F, sc=sc, tau=tau, M=M, se=se, sig=sig, sv=math.sqrt(sig ** 2 + 3 * tau ** 2))
    return r


def n(x, d=2):
    return tr(x, d)


def stress_lines(kind, p, label):
    F = int(p["F"])
    L = []
    if kind == "asagi":
        L.append(f"Kayma: τ = {F} / 720 = <b>{n(p['tau'])}</b> N/mm²")
        L.append(f"Moment: M = {F} · 80 = <b>{p['M']:,.0f}".replace(",", " ") + "</b> Nmm")
        L.append(f"Eğilme: σ<sub>e</sub> = {p['M']:,.0f}".replace(",", " ") + f" / 13 280 = <b>{n(p['se'])}</b>")
        L.append("Çekme yok, o yüzden σ = σ<sub>e</sub>.")
        L.append(f"Eşdeğer: σ<sub>v</sub> = √({n(p['sig'])}² + 3·{n(p['tau'])}²) = <b>{n(p['sv'], 1)}</b> N/mm²")
    elif kind == "orta":
        L.append(f"Çekme: σ = {F} / 960 = <b>{n(p['sc'])}</b> N/mm²")
        L.append(f"Kayma ve eğilme yok, o yüzden σ<sub>v</sub> = σ = <b>{n(p['sv'])}</b> N/mm²")
    else:
        lif = "Üst" if kind == "ust" else "Alt"
        L.append(f"Çekme: σ<sub>ç</sub> = {F} / 960 = <b>{n(p['sc'])}</b>")
        L.append(f"Moment: M = {F} · 20 = <b>{p['M']:,.0f}".replace(",", " ") + "</b> Nmm (kol 20)")
        L.append(f"Eğilme: σ<sub>e</sub> = {p['M']:,.0f}".replace(",", " ") + f" / 13 280 = <b>{n(p['se'])}</b>")
        L.append(f"{lif} lif (ikisi aynı yönde, toplanır): σ = {n(p['sc'])} + {n(p['se'])} = <b>{n(p['sig'], 1)}</b> N/mm²")
        L.append(f"Kayma yok, o yüzden σ<sub>v</sub> = σ = <b>{n(p['sv'], 1)}</b>")
    return f'<p class="lbl"><b>{label}</b></p><ul class="tight">' + "".join(f"<li>{x}</li>" for x in L) + "</ul>"


EXAMPLES = [
    dict(kind="asagi", no=1, title="Aşağı doğru kuvvet (kol 80 mm)",
         soru="Parçaya, dikişten 80 mm uzakta, dikey olarak aşağı doğru F = 8000 ± 2000 N etki ediyor. Dikiş emniyetli midir?",
         var="Kuvvet aşağı, yani dikişe <b>paralel</b>: dikişi keser (<b>kayma var</b>). Duvardan 80 mm uzakta olduğu için dikişi eğer (<b>eğilme var</b>, kol 80). Dikişi çekmiyor (<b>çekme yok</b>). En çok zorlanan yer <b>üst lif</b> (çekilen taraf).",
         m0=51.9, g=13.0, crit="üst lif"),
    dict(kind="orta", no=2, title="Tam ortadan, sağa çeken kuvvet",
         soru="Kuvvet tam eksenden geçiyor, yatay, duvardan uzağa: F = 8000 ± 2000 N. Dikiş emniyetli midir?",
         var="Kuvvet dikişe <b>dik</b>: dikişi çeker (<b>çekme var</b>). Paralel bileşen yok (<b>kayma yok</b>). Tam eksenden geçtiği için kol sıfır (<b>eğilme yok</b>). 80 mm bu soruda hiç kullanılmaz. Bütün dikiş eşit zorlanır.",
         m0=8.33, g=2.08, crit="her yer eşit"),
    dict(kind="ust", no=3, title="Eksenin 20 mm üstünden çeken kuvvet",
         soru="Yatay F = 8000 ± 2000 N, duvardan uzağa. Kuvvet çizgisi eksenin 20 mm üstünden geçiyor (e = 20 mm). Dikiş emniyetli midir?",
         var="Yatay kuvvet: <b>çekme var</b>, <b>kayma yok</b>. Kuvvet eksenden 20 mm kaçık: <b>eğilme var</b>, kol <b>e = 20</b> (80 değil!). Kuvvet yukarıdan çektiği için en çok zorlanan yer <b>üst lif</b>: çekme ile eğilme orada toplanır.",
         m0=20.4, g=5.1, crit="üst lif"),
    dict(kind="alt", no=4, title="Eksenin 20 mm altından çeken kuvvet",
         soru="Örnek 3'ün aynısı, ama kuvvet çizgisi eksenin 20 mm altından geçiyor. F = 8000 ± 2000 N. Dikiş emniyetli midir?",
         var="Örnek 3'ün ayna görüntüsü: <b>çekme var</b>, <b>kayma yok</b>, <b>eğilme var</b> (kol 20). Bu kez en çok zorlanan yer <b>alt lif</b>. Kesit simetrik olduğu için sayılar Örnek 3'le aynı çıkar.",
         m0=20.4, g=5.1, crit="alt lif"),
]


def example_html(ex):
    r = solve(ex["kind"])
    st, dn = r["st"], r["din"]
    m0, g = ex["m0"], ex["g"]
    su, sl, se = reading(m0)
    skd = K_DIN * se
    S = skd / g
    return f"""
<section class="ex">
<h2>{ex['no'] + 4}. Örnek {ex['no']}: {ex['title']}</h2>
<div class="q"><b>Soru:</b> {ex['soru']} (20×60 St37 parça, çepeçevre a = 6 mm köşe dikişi, 1. kalite.)</div>
<div class="row">
<div class="col-fig">{side_svg(ex['kind'])}</div>
<div class="col-txt"><p><span class="st">Adım 1</span> <b>Hangisi var?</b> {ex['var']}</p></div>
</div>
<div class="row two">
<div>{stress_lines(ex['kind'], st, '<span class="st">Adım 2</span> Statik (F = 8000 N) → σ<sub>vm</sub>')}</div>
<div>{stress_lines(ex['kind'], dn, '<span class="st">Adım 3</span> Dinamik (F = ±2000 N) → σ<sub>vg</sub>')}</div>
</div>
<p class="sumline">Sonuç: <b>σ<sub>vm</sub> = {n(m0)}</b> (statik, ortalama) · <b>σ<sub>vg</sub> = {trg(g)}</b> (dinamik, genlik). Kontrol: dinamik = statik / 4.</p>
<p><span class="st">Adım 4</span> <b>Statik kontrol:</b> σ<sub>kem</sub> = v<sub>1</sub>·v<sub>2</sub>·v<sub>3</sub>·σ<sub>em</sub> = 1 · 1 · 0,8 · 170 = 136. &nbsp; {n(m0)} &lt; 136 ✓</p>
<p><span class="st">Adım 5</span> <b>Smith diyagramı</b> (diyagrama σ<sub>vm</sub> = {n(m0)} ile gir):</p>
<figure class="fig sm">{smith_svg(m0, g, height=400)}{legend()}</figure>
<p class="calc">① sağa {n(m0)} → ② orta {n(m0)} → ③ üst ≈ {tr(su, 0)} → ④ alt ≈ {tr(sl, 0)} &nbsp;⇒&nbsp; σ<sub>ed</sub>' = üst − orta = {tr(su, 0)} − {n(m0)} = <b>{tr(se)}</b></p>
<p><span class="st">Adım 6</span> <b>Dinamik kontrol (dikiş faktörleriyle):</b></p>
<p class="calc">σ<sub>kem,D</sub> = v<sub>1</sub>·v<sub>2</sub>·v<sub>3</sub>·σ<sub>ed</sub>' = 0,42 · 1 · 0,8 · {tr(se)} = <b>{tr(skd)}</b> N/mm²
<span class="chk">σ<sub>vg</sub> = {trg(g)} &lt; {tr(skd)} ✓ &nbsp;·&nbsp; kaç kat emniyetli: S = {tr(skd)} / {trg(g)} = {tr(S)}</span></p>
<div class="verdict"><b>Karar:</b> Statik {n(m0)} &lt; 136 ve dinamik {trg(g)} &lt; {tr(skd)} → dikiş <b>emniyetli</b> (S ≈ {tr(S)}).</div>
</section>
"""


def main():
    css = (HERE / "style.css").read_text(encoding="utf-8") + EXTRA_CSS
    rows = []
    for ex in EXAMPLES:
        su, sl, se = reading(ex["m0"])
        skd = K_DIN * se
        rows.append(f"<tr><td>{ex['no']}. {ex['title'].split(' (')[0]}</td><td>{ex['crit']}</td><td>{n(ex['m0'])}</td><td>{trg(ex['g'])}</td>"
                    f"<td>{tr(su, 0)}</td><td>{tr(se)}</td><td>{tr(skd)}</td><td>{tr(skd / ex['g'])}</td><td>emniyetli</td></tr>")
    sum_rows = "\n".join(rows)
    examples = "\n".join(example_html(ex) for ex in EXAMPLES)

    html = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<title>Kaynak Örnekleri: Smith + Dikiş Faktörleri</title>
<style>{css}</style></head>
<body>

<header class="cover">
<h1>Kaynak Örnekleri Baştan Sona: Smith Diyagramı + Dikiş Faktörleri</h1>
<p class="sub">Makina Elemanları I · Sınav hazırlığı · 4 basit örnek: aşağı, ortadan sağa, üstten, alttan</p>
</header>

<p>Bu PDF'te sadece hocanın sorduğu tarzdaki 4 basit örnek var (60° asıl soru yok). Her örneği en baştan, aynı 6 adımla çözüyoruz: gerilmeler → statik kontrol → Smith diyagramı → dikiş faktörleri → karar. İlk Smith PDF'inde örnek olsun diye b<sub>0</sub>, b<sub>1</sub>, β<sub>k</sub> koymuştum; burada onların yerine <b>hocanın kaynak slaytlarındaki v<sub>1</sub>, v<sub>2</sub>, v<sub>3</sub></b> var.</p>

<h2>1. Parça ve bir kere hesaplanan sayılar</h2>
<div class="row">
<div class="col-fig">{section_svg()}
<div class="legend"><span><span class="lg-box" style="background:{ORANGE};border-color:{ORANGE}"></span><span>dikey dikişler: çekme + kayma</span></span><span><span class="lg-box" style="background:{GREEN};border-color:{GREEN}"></span><span>yatay dikişler: sadece çekme</span></span></div></div>
<div class="col-txt">
<p><b>Parça:</b> 20×60 mm, St37, duvara çepeçevre a = 6 mm köşe dikişiyle kaynaklı, 1. kalite. Dört dikiş var: üstte ve altta 20'lik iki yatay, solda ve sağda 60'lık iki dikey.</p>
<ol class="tight">
<li><b>Çekme alanı A = 960 mm²</b>: dört dikişin hepsi. 2·6·20 + 2·6·60 = 240 + 720.</li>
<li><b>Kayma alanı A<sub>k</sub> = 720 mm²</b>: sadece kuvvete paralel (dikey) dikişler. 2·6·60.</li>
<li><b>I = 478 080 mm⁴</b>: dikey 2·6·60³/12 = 216 000, yatay 2·[20·6³/12 + 20·6·33²] = 262 080.</li>
<li><b>W = I / y = 478 080 / 36 = 13 280 mm³</b>. y = 36 = 30 + 6 (en uzak lif, dikişin dış kenarı).</li>
</ol>
</div>
</div>
<div class="key">
<p><b>Formüller:</b> çekme σ<sub>ç</sub> = F<sub>x</sub>/960 · kayma τ = F<sub>y</sub>/720 · eğilme σ<sub>e</sub> = M/13 280 · toplam σ = σ<sub>ç</sub> + σ<sub>e</sub> · eşdeğer σ<sub>v</sub> = √(σ² + 3τ²)</p>
<p><b>F = 8000 ± 2000 N:</b> 8000 statik kısım → <b>σ<sub>vm</sub></b> (ortalama). ±2000 dinamik kısım → <b>σ<sub>vg</sub></b> (genlik). Her şey kuvvetle orantılı, o yüzden dinamik gerilme = statik / 4.</p>
</div>

<section class="pb">
<h2>2. Dikiş faktörleri (hocanın kaynak slaytları)</h2>
<div class="formula"><span>σ<sub>kem</sub> = v<sub>1</sub> · v<sub>2</sub> · v<sub>3</sub> · σ<sub>em</sub></span></div>
<p class="center small">σ<sub>kem</sub>: kaynağın emniyet gerilmesi · σ<sub>em</sub>: yapı elemanının (parçanın) emniyet gerilmesi</p>
<table class="t">
<tr><th>Faktör</th><th>Ne demek?</th><th>Bizim örneklerde</th><th>Neden?</th></tr>
<tr><td><b>v<sub>1</sub></b> dikiş faktörü</td><td>Yorulmada gerilme yığılması (dikişin çentik etkisi). <b>Statikte 1.</b></td><td>statik <b>1</b> · dinamik <b>0,42</b></td><td>tablo: iki taraflı, düz köşe dikişi</td></tr>
<tr><td><b>v<sub>2</sub></b> kalite faktörü</td><td>Kaynağın kalitesi</td><td><b>1</b></td><td>1. kalite</td></tr>
<tr><td><b>v<sub>3</sub></b> gerilme faktörü</td><td>Dikiş türü ve zorlanma türü</td><td><b>0,8</b></td><td>çelik, köşe (boğaz) kaynağı, her zorlanma</td></tr>
<tr><td><b>σ<sub>em</sub></b></td><td>Parçanın emniyet gerilmesi</td><td>statik <b>170</b> · dinamik <b>σ<sub>ed</sub>'</b></td><td>dinamikte Smith diyagramından okunur</td></tr>
</table>

<h3>v<sub>1</sub>: Köşe dikişleri tablosu (hocanın slaytından)</h3>
<table class="t v1">
<tr><th rowspan="2">Köşe dikişler</th><th colspan="3">Tek taraflı (alan a·l)</th><th colspan="3">İki taraflı (alan 2a·l)</th></tr>
<tr><th>Dışbükey</th><th>Düz</th><th>İçbükey</th><th>Dışbükey</th><th class="hl">Düz</th><th>İçbükey</th></tr>
<tr><td>1. satır: σ<sub>⊥</sub> çekme</td><td>0,28</td><td>0,3</td><td>0,33</td><td>0,38</td><td class="hl">0,42</td><td>0,5</td></tr>
<tr><td>2. satır: σ<sub>⊥</sub> basma</td><td>0,5</td><td>0,54</td><td>0,6</td><td>0,54</td><td class="hl">0,6</td><td>0,7</td></tr>
<tr><td>3. satır: τ<sub>∥</sub> kayma</td><td>0,28</td><td>0,3</td><td>0,33</td><td>0,38</td><td class="hl">0,42</td><td>0,5</td></tr>
</table>
<p class="small"><b>Hangi sütun?</b> Parça duvara çepeçevre kaynaklı, yani iki yanında da dikiş var → <b>iki taraflı</b>. Dikiş şekli yazmıyorsa → <b>düz</b>. Bu sütunda çekme ve kayma ikisi de <b>0,42</b>, o yüzden kayma olan Örnek 1'de de aynı sayıyı kullanırız. En çok zorlanan yer hep çekilen lif olduğu için 2. satıra (basma, 0,6) gerek yok. Soruda başka bir dikiş türü yazarsa (ör. “tek taraflı düz”) o sütundan oku. (Slayttaki dipnot numaralarını göremedim; satırları değerlere bakarak çekme, basma, kayma diye okudum. Basma her sütunda en büyük, çünkü basılan dikiş daha az yorulur.)</p>

<div class="row two">
<div>
<h3>v<sub>2</sub>: Kalite faktörü</h3>
<table class="t">
<tr><th>Eski sistem</th><th>v<sub>2</sub></th></tr>
<tr><td>I. kalite</td><td><b>1</b></td></tr>
<tr><td>II. kalite</td><td>0,8</td></tr>
<tr><td>III. kalite</td><td>0,5</td></tr>
</table>
<table class="t">
<tr><th>Yeni sistem</th><th>v<sub>2</sub></th></tr>
<tr><td>Hiç dış denetim yok</td><td>0,5</td></tr>
<tr><td>Sadece gözle kontrol</td><td>0,8</td></tr>
<tr><td>Normal kalite</td><td>0,9</td></tr>
<tr><td>Özel kalite</td><td>1,0</td></tr>
</table>
</div>
<div>
<h3>v<sub>3</sub>: Gerilme faktörü</h3>
<table class="t">
<tr><th>Dikiş</th><th>Zorlanma</th><th>Çelik</th><th>Alüminyum</th></tr>
<tr><td rowspan="4">Alın</td><td>Çekme</td><td>1,0</td><td>1,0</td></tr>
<tr><td>Basma</td><td>1,0</td><td>1,0</td></tr>
<tr><td>Eğilme</td><td>1,0</td><td>1,0</td></tr>
<tr><td>Kesme, burulma</td><td>0,8</td><td>0,65</td></tr>
<tr><td>Boğaz (köşe)</td><td>Herhangi</td><td><b>0,8</b></td><td>0,65</td></tr>
</table>
<p class="small">“Boğaz kaynağı” = köşe kaynağı. Adını a boğaz kalınlığından alır. Bizim dikiş köşe dikişi, çelik → <b>v<sub>3</sub> = 0,8</b>.</p>
</div>
</div>

<div class="key">
<p><b>Bütün örneklerde kullanacağımız iki sayı:</b></p>
<ul class="tight">
<li><b>Statik:</b> σ<sub>kem</sub> = 1 · 1 · 0,8 · 170 = <b>136 N/mm²</b>. Hocanın tahtadaki 136'sı tam bu: 136 / 0,8 = 170, yani parça için σ<sub>em</sub> = 170 alınmış.</li>
<li><b>Dinamik:</b> σ<sub>kem,D</sub> = 0,42 · 1 · 0,8 · σ<sub>ed</sub>' = <b>0,336 · σ<sub>ed</sub>'</b>. Burada σ<sub>em</sub> yerine Smith diyagramından okunan σ<sub>ed</sub>' girer.</li>
</ul>
</div>
</section>

<section>
<h2>3. Smith diyagramı: 30 saniyede hatırlatma</h2>
<figure class="fig sm">{smith_svg(anatomy=True, height=400)}</figure>
<p>Diyagram hocanın PDF'indeki St37 eğilme diyagramı: sol eksende <b>±170</b>, titreşimli noktada <b>290</b> (σ<sub>m</sub> = 145), akma <b>330</b>. Okumak için 4 hareket:</p>
<ol class="moves">
<li><span class="mv r">① sağa</span> Yatay eksende σ<sub>vm</sub>'ye git (statik kısım).</li>
<li><span class="mv k">② orta</span> Yukarı çık, kesik 45° çizgisine değ. Orta = σ<sub>vm</sub>.</li>
<li><span class="mv r">③ üst</span> Devam et, üst eğriye değ.</li>
<li><span class="mv r">④ alt</span> Aşağı in, alt eğriye değ.</li>
</ol>
<p class="calc"><b>σ<sub>ed</sub>' = üst − orta</b> <span class="chk">kontrol: orta − alt de aynı çıkmalı · formülle (σ<sub>m</sub> ≤ 193 iken): σ<sub>ed</sub>' = 170 − 0,17·σ<sub>m</sub></span></p>

<h2>4. Her örnekte aynı 6 adım</h2>
<ol class="recipe">
<li><b>Hangisi var?</b> Çekme, kayma, eğilme: kuvvetin yönüne ve koluna bak.</li>
<li><b>Statik gerilmeler</b> (8000 N) → σ<sub>vm</sub> = √(σ² + 3τ²)</li>
<li><b>Dinamik gerilmeler</b> (±2000 N) → σ<sub>vg</sub> (statiğin dörtte biri)</li>
<li><b>Statik kontrol:</b> σ<sub>vm</sub> ≤ σ<sub>kem</sub> = 136</li>
<li><b>Smith:</b> σ<sub>vm</sub> ile diyagrama gir → σ<sub>ed</sub>' = üst − orta</li>
<li><b>Dinamik kontrol:</b> σ<sub>kem,D</sub> = v<sub>1</sub>·v<sub>2</sub>·v<sub>3</sub>·σ<sub>ed</sub>' = 0,336·σ<sub>ed</sub>' → σ<sub>vg</sub> ≤ σ<sub>kem,D</sub> ise emniyetli. Kaç kat emniyetli: S = σ<sub>kem,D</sub> / σ<sub>vg</sub></li>
</ol>
</section>

{examples}

<section class="pb">
<h2>9. Hoca faktörleri nasıl sorar? Kısa işlem soruları</h2>
<p>Önce cevap sütununu kapat, kendin yap.</p>
<table class="t quiz2">
<tr><th>#</th><th>Soru</th><th>İşlem</th><th>Cevap</th></tr>
<tr><td>1</td><td>1. kalite kaynakta v<sub>2</sub>?</td><td>eski sistem tablosu</td><td><b>1</b></td></tr>
<tr><td>2</td><td>3. kalite kaynakta v<sub>2</sub>?</td><td>eski sistem tablosu</td><td><b>0,5</b></td></tr>
<tr><td>3</td><td>Yeni sistem, sadece gözle kontrol edilmiş kaynak: v<sub>2</sub>?</td><td>yeni sistem tablosu</td><td><b>0,8</b></td></tr>
<tr><td>4</td><td>Çelik, köşe (boğaz) kaynağı: v<sub>3</sub>?</td><td>her zorlanmada aynı</td><td><b>0,8</b></td></tr>
<tr><td>5</td><td>Çelik alın kaynağı, çekme: v<sub>3</sub>? Kesme olsa?</td><td>alın satırları</td><td><b>1,0</b> · <b>0,8</b></td></tr>
<tr><td>6</td><td>Statik yükte v<sub>1</sub>?</td><td>slayt: “statikte 1'dir”</td><td><b>1</b></td></tr>
<tr><td>7</td><td>Tek taraflı düz köşe dikişi, çekme: v<sub>1</sub>?</td><td>tek taraflı · düz · 1. satır</td><td><b>0,3</b></td></tr>
<tr><td>8</td><td>İki taraflı içbükey köşe dikişi, basma: v<sub>1</sub>?</td><td>iki taraflı · içbükey · 2. satır</td><td><b>0,7</b></td></tr>
<tr><td>9</td><td>İki taraflı düz köşe dikişi, a = 6, l = 60: kaynak alanı?</td><td>2a·l = 2·6·60</td><td><b>720 mm²</b></td></tr>
<tr><td>10</td><td>σ<sub>em</sub> = 170, 1. kalite köşe kaynağı, statik: σ<sub>kem</sub>?</td><td>1 · 1 · 0,8 · 170</td><td><b>136</b></td></tr>
<tr><td>11</td><td>Aynı soru, 2. kalite kaynak olsa?</td><td>1 · 0,8 · 0,8 · 170</td><td><b>108,8</b></td></tr>
<tr><td>12</td><td>Aynı soru, 3. kalite kaynak olsa?</td><td>1 · 0,5 · 0,8 · 170</td><td><b>68</b></td></tr>
<tr><td>13</td><td>Dinamik, iki taraflı düz köşe, 1. kalite, σ<sub>ed</sub>' = 160: σ<sub>kem,D</sub>?</td><td>0,42 · 1 · 0,8 · 160</td><td><b>53,8</b></td></tr>
<tr><td>14</td><td>Örnek 1'deki dikiş 2. kalite olsaydı dinamik sınır? Yine emniyetli mi?</td><td>0,42 · 0,8 · 0,8 · 161,1</td><td><b>43,3</b> · 13,0 &lt; 43,3, evet</td></tr>
</table>
<p class="small">Dikkat: kalite düşünce (v<sub>2</sub> küçülünce) hem statik hem dinamik sınır aynı oranda düşer. v<sub>1</sub> ise sadece dinamik sınırı etkiler, çünkü statikte 1'dir.</p>

<h2>10. Dört örnek yan yana</h2>
<table class="t sum2">
<tr><th>Örnek</th><th>Kritik yer</th><th>σ<sub>vm</sub><br>(≤ 136)</th><th>σ<sub>vg</sub></th><th>üst</th><th>σ<sub>ed</sub>'</th><th>σ<sub>kem,D</sub></th><th>S</th><th>Sonuç</th></tr>
{sum_rows}
</table>
<p>Kuvvet hepsinde aynı (8000 ± 2000 N), ama gerilme yönden ve koldan değişiyor: en tehlikelisi aşağı doğru kuvvet (uzun kol 80 mm). σ<sub>ed</sub>' her örnekte 160–170 arası çıkıyor, çünkü σ<sub>vm</sub> küçük ve bandın geniş olduğu sol taraftayız.</p>

<h2>11. Sınavda dikkat</h2>
<ul class="tips">
<li><b>v<sub>1</sub> statikte 1.</b> Tablodaki v<sub>1</sub> sadece dinamik (yorulma) kontrolünde kullanılır.</li>
<li>Köşe (boğaz) kaynağında <b>v<sub>3</sub> = 0,8</b>, zorlanma ne olursa olsun. Alın kaynağında çekme, basma ve eğilme 1,0, kesme 0,8.</li>
<li><b>1. kalite → v<sub>2</sub> = 1.</b> 2. kalite 0,8, 3. kalite 0,5.</li>
<li>Diyagrama <b>σ<sub>vm</sub></b> ile girilir, <b>σ<sub>vg</sub></b> ile karşılaştırılır. Karıştırma.</li>
<li><b>σ<sub>ed</sub>' = üst − orta.</b> Üst değerin kendisini yazma.</li>
<li>Çekmede 960, kaymada 720. Eğilmede y = 36, W = 13 280.</li>
<li>Kol: dikey kuvvette dikişe uzaklık (80), yatay kuvvette eksene uzaklık (e = 20). Ortadan geçen yatay kuvvette kol yok.</li>
<li>Dikiş türü soruda yazar; v<sub>1</sub>'i o sütundan oku. Bu PDF'te iki taraflı düz köşe (0,42) aldım.</li>
</ul>
</section>

</body></html>
"""
    (HERE / "kaynak_ornekler.html").write_text(html, encoding="utf-8")
    print("HTML yazıldı.")
    for ex in EXAMPLES:
        r = solve(ex["kind"])
        su, sl, se = reading(ex["m0"])
        print(ex["no"], "sv st", round(r["st"]["sv"], 3), "sv din", round(r["din"]["sv"], 3),
              "okuma", (su, sl, se), "skd", round(K_DIN * se, 2), "S", round(K_DIN * se / ex["g"], 2))


EXTRA_CSS = """
.row { display: flex; gap: 14px; align-items: flex-start; margin: 6px 0; break-inside: avoid; }
.row .col-fig { flex: 0 0 42%; text-align: center; }
.row .col-fig svg { width: 100%; height: auto; }
.row .col-txt { flex: 1; }
.row.two > div { flex: 1; min-width: 0; }
.st { display: inline-block; background: #1d232a; color: #fff; font-size: 8.6pt; font-weight: 600; padding: 0 6px; border-radius: 3px; margin-right: 4px; }
.lbl { margin: 4px 0 2px; }
ul.tight, ol.tight { margin: 2px 0 4px; }
ul.tight li, ol.tight li { margin: 1px 0; }
.sumline { background: #f3f6f9; padding: 5px 10px; border-radius: 4px; }
.fig.sm svg { max-width: 108mm; }
.center { text-align: center; }
.t.v1 td, .t.v1 th { text-align: center; }
.t.v1 td:first-child { text-align: left; }
.t.v1 .hl { background: #eaf6ee; font-weight: 700; }
.recipe li { margin: 4px 0; }
.t.quiz2 td:last-child { white-space: nowrap; }
.t.sum2 td:nth-child(n+3):nth-child(-n+8) { text-align: right; font-variant-numeric: tabular-nums; }
.ex .calc { margin: 4px 0; }
"""

if __name__ == "__main__":
    main()
