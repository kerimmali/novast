#!/usr/bin/env python3
"""Kaynak dikişi + Smith diyagramı çalışma PDF'inin HTML kaynağını üretir.

St37 eğilme Smith diyagramı, hocanın PDF'indeki diyagramdan okunan üç sayıyla
çizilir: sigma_eD = 170, titreşimli 290 (sigma_m = 145), akma sigma_Ak = 330.

Kullanım:  python3 build.py && node render.js
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- St37 verisi
S_ED = 170.0           # tam değişken eğilme dayanımı (sigma_m = 0)
S_SCH = 290.0          # titreşimli: 0 ile 290 arasında, sigma_m = 145
S_AK = 330.0           # eğilme akma sınırı
K_SLOPE = (S_SCH - S_ED) / (S_SCH / 2)   # üst eğrinin eğimi = 120/145
M_KNEE = (S_AK - S_ED) / K_SLOPE          # üst eğrinin akmaya değdiği yer ~193


def ust(m):
    return min(S_ED + K_SLOPE * m, S_AK)


def alt(m):
    return 2 * m - ust(m)


def sed(m):
    return ust(m) - m


# Faktörler (örnek değerler, sınavda hocanınkiler konur)
B0, B1, BK, S_GER = 0.9, 0.9, 2.0, 1.5
KF = B0 * B1 / BK      # 0,405


def tr(x, d=1):
    """Türkçe ondalık, yukarı yuvarlama: 73.25 -> '73,3'; tam sayıysa ',0' yazmaz."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(repr(x)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    t = format(q, "f")
    if "." in t and d >= 2:          # 51,90 -> 51,9 ; 100,00 -> 100 (1 haneliler aynen kalır: 5,0)
        t = t.rstrip("0").rstrip(".")
    if t == "-0":
        t = "0"
    return t.replace("-", "−").replace(".", ",")


def trg(x):
    """En az bir ondalık: 13 -> '13,0', 2.08 -> '2,08'."""
    t = tr(x, 2)
    return t if "," in t else t + ",0"


def reading(m0):
    """Diyagramdan okunanlar: üst ve alt tam sayıya yuvarlanır (göz kararı),
    sigma_ed' bu okumalardan hesaplanır."""
    su_r = round(ust(m0))
    sl_r = round(alt(m0))
    se_r = round(su_r - m0, 1)
    return su_r, sl_r, se_r


# ---------------------------------------------------------------- SVG çizimi
RED, GREEN, BLUE, INK, MUTED = "#c0392b", "#1e8a4c", "#2563eb", "#1d232a", "#6b7480"


def smith_svg(m0=None, g=None, anatomy=False, width=640, height=420):
    L, R, T, B = 58, 132, 16, 34
    pw, ph = width - L - R, height - T - B
    m_max, s_min, s_max = 360.0, -200.0, 360.0

    def X(m):
        return L + m / m_max * pw

    def Y(s):
        return T + (s_max - s) / (s_max - s_min) * ph

    o = []
    add = o.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="Inter, sans-serif">')
    add('<defs>'
        f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>'
        f'<marker id="ag" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{GREEN}"/></marker>'
        '</defs>')

    # ızgara
    for m in range(50, 351, 50):
        add(f'<line x1="{X(m):.1f}" y1="{Y(s_max):.1f}" x2="{X(m):.1f}" y2="{Y(s_min):.1f}" stroke="#e7e9ec" stroke-width="1"/>')
    for s in range(-200, 351, 50):
        add(f'<line x1="{X(0):.1f}" y1="{Y(s):.1f}" x2="{X(m_max):.1f}" y2="{Y(s):.1f}" stroke="#e7e9ec" stroke-width="1"/>')

    # güvenli bant
    up = [(0, S_ED), (M_KNEE, S_AK), (S_AK, S_AK)]
    lo = [(S_AK, S_AK), (M_KNEE, alt(M_KNEE)), (0, -S_ED)]
    pts = " ".join(f"{X(m):.1f},{Y(s):.1f}" for m, s in up + lo)
    add(f'<polygon points="{pts}" fill="#eef2f7"/>')

    # eksenler
    add(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(m_max):.1f}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.3"/>')
    add(f'<line x1="{X(0):.1f}" y1="{Y(s_min):.1f}" x2="{X(0):.1f}" y2="{Y(s_max):.1f}" stroke="{INK}" stroke-width="1.3"/>')

    # eksen yazıları
    halo = 'paint-order="stroke" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"'
    for m in (100, 200, 300):
        add(f'<text x="{X(m):.1f}" y="{Y(0) + 14:.1f}" font-size="11" fill="{MUTED}" text-anchor="middle" {halo}>{m}</text>')
    add(f'<text x="{X(m_max):.1f}" y="{Y(0) + 29:.1f}" font-size="12" fill="{INK}" text-anchor="end" {halo}>σ<tspan font-size="9" dy="3">m</tspan><tspan dy="-3"> (N/mm²)</tspan></text>')
    special = {170: "170", -170: "−170", 330: "330"}
    for s in range(-200, 351, 100):
        if any(abs(s - k) < 25 for k in special):
            continue
        add(f'<text x="{X(0) - 7:.1f}" y="{Y(s) + 4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">{str(s).replace("-", "−")}</text>')
    for s, lab in special.items():
        add(f'<text x="{X(0) - 7:.1f}" y="{Y(s) + 4:.1f}" font-size="11.5" font-weight="600" fill="{INK}" text-anchor="end">{lab}</text>')
    add(f'<text x="{X(0) - 7:.1f}" y="{Y(0) + 4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">0</text>')
    add(f'<text transform="translate(14,{Y(80):.1f}) rotate(-90)" font-size="12" fill="{INK}" text-anchor="middle">gerilme σ (N/mm²)</text>')

    # orta çizgi 45°
    add(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(350):.1f}" y2="{Y(350):.1f}" stroke="#7a828c" stroke-width="1.3" stroke-dasharray="7 3 1.5 3"/>')

    # x = 0 ışını (titreşimli)
    if anatomy:
        add(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(175):.1f}" y2="{Y(350):.1f}" stroke="#9aa3ad" stroke-width="1" stroke-dasharray="3 3"/>')
        add(f'<text x="{X(176) + 3:.1f}" y="{Y(352):.1f}" font-size="11" fill="{MUTED}">x = 0</text>')

    # üst ve alt eğriler
    add(f'<polyline points="{" ".join(f"{X(m):.1f},{Y(s):.1f}" for m, s in up)}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    add(f'<polyline points="{" ".join(f"{X(m):.1f},{Y(s):.1f}" for m, s in lo)}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')

    # karakteristik noktalar
    add(f'<circle cx="{X(0):.1f}" cy="{Y(S_ED):.1f}" r="3.2" fill="{INK}"/>')
    add(f'<circle cx="{X(0):.1f}" cy="{Y(-S_ED):.1f}" r="3.2" fill="{INK}"/>')
    add(f'<circle cx="{X(145):.1f}" cy="{Y(290):.1f}" r="3.2" fill="{INK}"/>')
    add(f'<circle cx="{X(S_AK):.1f}" cy="{Y(S_AK):.1f}" r="3.2" fill="{INK}"/>')
    add(f'<text x="{X(145) - 8:.1f}" y="{Y(290) - 7:.1f}" font-size="11.5" fill="{INK}" text-anchor="end" {halo}>290</text>')
    add(f'<text x="{X(S_AK) + 6:.1f}" y="{Y(S_AK) + 15:.1f}" font-size="11.5" fill="{INK}" {halo}>330</text>')

    def along(m1, m2, f, text, off, size=11.5, color=INK, weight="500"):
        import math
        x1, y1, x2, y2 = X(m1), Y(f(m1)), X(m2), Y(f(m2))
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        add(f'<text transform="translate({cx:.1f},{cy:.1f}) rotate({ang:.1f})" y="{off}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="middle">{text}</text>')

    if anatomy:
        along(15, 120, ust, "üst sınır eğrisi", -7)
        along(25, 125, alt, "alt sınır eğrisi", 15)
        along(225, 315, lambda m: m, "orta çizgi (σ = σ<tspan font-size='8.5' dy='2'>m</tspan><tspan dy='-2'>)</tspan>", -6, color="#4a525c")
        add(f'<text x="{X(132):.1f}" y="{Y(55):.1f}" font-size="12" font-style="italic" fill="#5b6b80" text-anchor="middle">güvenli bölge (bant)</text>')
        # açıklama okları
        add(f'<text x="{X(200) + 2:.1f}" y="{Y(338) - 2:.1f}" font-size="11" fill="{INK}">akmada kesilir (330)</text>')
        add(f'<text x="{X(150) + 12:.1f}" y="{Y(282) + 4:.1f}" font-size="11" fill="{MUTED}">titreşimli</text>')
        add(f'<text x="{X(0) + 8:.1f}" y="{Y(S_ED) + 15:.1f}" font-size="11" fill="{MUTED}">σ<tspan font-size="8.5" dy="2">eD</tspan><tspan dy="-2"> = 170</tspan></text>')
        add(f'<text x="{X(0) + 8:.1f}" y="{Y(-S_ED) + 16:.1f}" font-size="11" fill="{MUTED}" {halo}>−σ<tspan font-size="8.5" dy="2">eD</tspan><tspan dy="-2"> = −170</tspan></text>')
        # sağ kenar açıklaması
        add(f'<text x="{X(m_max) + 10:.1f}" y="{Y(S_AK) + 4:.1f}" font-size="11" fill="{MUTED}">bant burada</text>')
        add(f'<text x="{X(m_max) + 10:.1f}" y="{Y(S_AK) + 18:.1f}" font-size="11" fill="{MUTED}">kapanıyor</text>')
        add(f'<text x="{X(m_max) + 10:.1f}" y="{Y(S_AK) + 32:.1f}" font-size="11" fill="{MUTED}">(σ<tspan font-size="8.5" dy="2">ed</tspan><tspan dy="-2">\' = 0)</tspan></text>')

    if m0 is not None:
        su, sl = ust(m0), alt(m0)
        xm = X(m0)
        # 1) sağa git
        add(f'<line x1="{X(0) + 1:.1f}" y1="{Y(0):.1f}" x2="{xm:.1f}" y2="{Y(0):.1f}" stroke="{RED}" stroke-width="3.2" marker-end="url(#ar)"/>')
        # dikey okuma çizgisi
        add(f'<line x1="{xm:.1f}" y1="{Y(sl):.1f}" x2="{xm:.1f}" y2="{Y(su):.1f}" stroke="{RED}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        # yeşil yatay çizgiler + parantez
        xr = X(m_max)
        for s in (m0, su):
            add(f'<line x1="{xm:.1f}" y1="{Y(s):.1f}" x2="{xr + 8:.1f}" y2="{Y(s):.1f}" stroke="{GREEN}" stroke-width="1.4"/>')
        add(f'<line x1="{xr + 16:.1f}" y1="{Y(m0) - 2:.1f}" x2="{xr + 16:.1f}" y2="{Y(su) + 2:.1f}" stroke="{GREEN}" stroke-width="1.6" marker-start="url(#ag)" marker-end="url(#ag)"/>')
        ymid = (Y(m0) + Y(su)) / 2
        add(f'<text x="{xr + 24:.1f}" y="{ymid + 5:.1f}" font-size="14" font-weight="700" fill="{GREEN}">σ<tspan font-size="10" dy="3">ed</tspan><tspan dy="-3">\' ≈ {tr(reading(m0)[2], 2)}</tspan></text>')
        add(f'<text x="{xr + 24:.1f}" y="{Y(su) - 6:.1f}" font-size="12" font-weight="600" fill="{RED}">③ üst ≈ {tr(su, 0)}</text>')
        add(f'<text x="{xr + 24:.1f}" y="{Y(m0) + 16:.1f}" font-size="12" font-weight="600" fill="{INK}">② orta = {tr(m0, 2)}</text>')
        # çalışma aralığı (mavi)
        if g:
            add(f'<line x1="{xm:.1f}" y1="{Y(m0 - g):.1f}" x2="{xm:.1f}" y2="{Y(m0 + g):.1f}" stroke="{BLUE}" stroke-width="7" stroke-linecap="butt" opacity="0.9"/>')
        # noktalar
        add(f'<circle cx="{xm:.1f}" cy="{Y(m0):.1f}" r="4" fill="#ffffff" stroke="{INK}" stroke-width="2"/>')
        add(f'<circle cx="{xm:.1f}" cy="{Y(su):.1f}" r="4.3" fill="{RED}"/>')
        add(f'<circle cx="{xm:.1f}" cy="{Y(sl):.1f}" r="4.3" fill="{RED}"/>')
        add(f'<text x="{xm + 9:.1f}" y="{Y(sl) + 16:.1f}" font-size="12" font-weight="600" fill="{RED}" {halo}>④ alt ≈ {tr(sl, 0)}</text>')
        add(f'<text x="{X(0) + 5:.1f}" y="{Y(0) + 30:.1f}" font-size="12" font-weight="600" fill="{RED}" {halo}>① sağa git: σ<tspan font-size="9" dy="3">m</tspan><tspan dy="-3"> = {tr(m0, 2)}</tspan></text>')

    add('</svg>')
    return "\n".join(o)


def legend(g=True):
    items = [
        (f'<span class="lg-line" style="background:{RED}"></span>', "okuma yolu (sağa → yukarı)"),
        (f'<span class="lg-line" style="background:{GREEN}"></span>', "σ<sub>ed</sub>' (orta ile üst arası)"),
    ]
    if g:
        items.append((f'<span class="lg-bar" style="background:{BLUE}"></span>',
                      "senin gerilmen: σ<sub>vm</sub> ± σ<sub>vg</sub>"))
    items.append(('<span class="lg-box"></span>', "güvenli bant"))
    return '<div class="legend">' + "".join(f"<span>{a}<span>{b}</span></span>" for a, b in items) + "</div>"


# ---------------------------------------------------------------- örnekler
def example_block(num_title, soru, onceki, m0, g, extra_before="", extra_after="", fig=True, crit=""):
    su, sl, se = reading(m0)
    num = se * B0 * B1
    den = BK * g
    S = num / den
    fig_html = ""
    if fig:
        fig_html = f'<figure class="fig">{smith_svg(m0, g)}{legend()}</figure>'
    return f"""
<section class="ex">
<h2>{num_title}</h2>
<div class="q"><b>Soru:</b> {soru}</div>
<p class="prev"><b>Önceki PDF'ten (gerilmeler):</b> {onceki}</p>
{extra_before}
{fig_html}
<div class="steps">
<p><b>Adım 8, ortalama gerilme:</b> σ<sub>vm</sub> = {tr(m0, 2)} N/mm²{crit}. Diyagrama bu sayıyla gireceğiz.</p>
<p><b>Adım 9, diyagramdan oku:</b></p>
<ol class="moves">
<li><span class="mv r">① sağa</span> Yatay eksende σ<sub>m</sub> = <b>{tr(m0, 2)}</b> noktasına git.</li>
<li><span class="mv k">② orta</span> Yukarı çık, kesik 45° çizgisine değ: orta = <b>{tr(m0, 2)}</b>.</li>
<li><span class="mv r">③ üst</span> Devam et, üst eğriye değ: üst ≈ <b>{tr(su, 0)}</b>.</li>
<li><span class="mv r">④ alt</span> Aşağı in, alt eğriye değ: alt ≈ <b>{tr(sl, 0)}</b>.</li>
</ol>
<p class="calc">σ<sub>ed</sub>' = üst − orta = {tr(su, 0)} − {tr(m0, 2)} = <b>{tr(se)} N/mm²</b>
<span class="chk">kontrol: orta − alt = {tr(m0, 2)} − ({tr(sl, 0)}) = {tr(m0 - sl, 1)} ✓ (±1 göz kararı farkı normal) &nbsp;·&nbsp; formülle: 170 − 0,17·{tr(m0, 2)} = {tr(170 - 0.17 * m0)}</span></p>
<p><b>Adım 10, emniyet katsayısı:</b></p>
<p class="calc">S = σ<sub>ed</sub>'·b<sub>0</sub>·b<sub>1</sub> / (β<sub>k</sub>·σ<sub>vg</sub>) = {tr(se)}·0,9·0,9 / (2,0·{trg(g)}) = {tr(num)} / {trg(den)} = <b>{tr(S)}</b>
</p>
{extra_after}
<div class="verdict"><b>Karar:</b> S = {tr(S)} ≥ 1,5 ve statik {tr(m0, 2)} &lt; 136 → dikiş <b>emniyetli</b>.</div>
</div>
</section>
"""


def main():
    ex1 = dict(m0=51.9, g=13.0)
    ex2 = dict(m0=8.33, g=2.08)
    ex3 = dict(m0=20.4, g=5.1)
    p78 = dict(m0=73.3, g=24.4)

    def S_of(d):
        return reading(d["m0"])[2] * B0 * B1 / (BK * d["g"])

    def U(d):
        return tr(reading(d["m0"])[0], 0)

    def E(d):
        return tr(reading(d["m0"])[2])

    css = (HERE / "style.css").read_text(encoding="utf-8")

    html = f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8">
<title>Kaynak Dikişi ve Smith Diyagramı</title>
<style>{css}</style></head>
<body>

<header class="cover">
<h1>Kaynak Dikişi ve Smith Diyagramı: Adım Adım</h1>
<p class="sub">Makina Elemanları I · Sınav hazırlığı · “4 Örnek (Statik + Dinamik)” PDF'inin devamı</p>
</header>

<h2>1. Ne değişiyor?</h2>
<p>Önceki PDF'te her soruyu iki kere hesapladık: bir kere statik kuvvetle, bir kere dinamik (±) kuvvetle. Statiği 136 ile, dinamiği ≈62 ile karşılaştırdık.</p>
<p>Hoca <b>dinamik kısmı Smith diyagramıyla</b> kontrol etmemizi istiyor. Sebebi şu: bir parçanın ne kadar salınıma (± kısmına) dayanabileceği, üstüne ne kadar sabit yük bindiğine bağlıdır. Sabit yük ne kadar çoksa salınım payı o kadar azalır. Tek bir “62” sayısı bunu göstermez, Smith diyagramı gösterir.</p>
<div class="key">
<p><b>F = 12 000 ± 4000 N</b> gibi bir yükte iki parça var:</p>
<ul>
<li><b>12 000 (statik kısım)</b> → <b>ortalama gerilme σ<sub>vm</sub></b>. Diyagrama bununla girilir.</li>
<li><b>± 4000 (dinamik kısım)</b> → <b>genlik σ<sub>vg</sub></b>. Formülün paydasına bu girer.</li>
</ul>
<p>Önceki PDF'teki hesapların hiçbiri boşa gitmiyor: σ<sub>vm</sub> eski “σ<sub>v</sub> statik”in, σ<sub>vg</sub> eski “σ<sub>v</sub> dinamik”in ta kendisi. Yeni olan sadece <b>diyagramdan okumak</b> ve <b>S formülü</b>.</p>
</div>
<p class="small">İsimler: <b>m</b> = ortalama (statik), <b>g</b> = genlik (dinamik), <b>v</b> = eşdeğer, yani σ<sub>v</sub> = √(σ² + 3τ²). Statik kontrol aynen kalıyor: σ<sub>vm</sub> &lt; 136.</p>

<h2>2. Gerçek diyagram: hocanın PDF'indeki Smith diyagramı</h2>
<figure class="photo"><img src="hoca_slayt_smith.png" alt="Hocanın PDF'indeki Smith diyagramı ve hesap sırası">
<figcaption>Hocanın PDF'inden (İTÜ Makina Elemanları I sunumu, “Hesap sırası” sayfası; gönderdiğin ekran görüntüsü). St37'den St70'e kadar çelikler için eğilme Smith diyagramı. Kırmızı çizgi σ<sub>vm</sub>'nin yeri, yeşil ok okunan σ<sub>ed</sub>'.</figcaption></figure>
<p>Her çelik için iki eğri var: biri yukarıda (üst sınır), biri aşağıda (alt sınır). Malzememiz <b>St37</b> olduğu için en içteki, en küçük eğri çiftini kullanıyoruz. Diyagramdan St37 için şu üç sayı okunuyor:</p>
<table class="t">
<tr><th>Diyagramda nerede?</th><th>Değer</th><th>Anlamı</th></tr>
<tr><td>Sol eksen, σ<sub>m</sub> = 0</td><td><b>+170 ve −170</b></td><td>σ<sub>eD</sub>: ortalama sıfırken (tam değişken yük) taşınan genlik</td></tr>
<tr><td>x = 0 çizgisi üstündeki nokta</td><td><b>290</b> (σ<sub>m</sub> = 145)</td><td>Titreşimli yük: gerilme 0 ile 290 arasında gidip geliyor</td></tr>
<tr><td>Sağ üstteki nokta</td><td><b>330</b></td><td>σ<sub>Ak</sub>: akma sınırı, gerilme bunun üstüne çıkamaz</td></tr>
</table>
<p>Bir sonraki bölümdeki diyagram, bu üç sayıyla St37 eğrilerinin temiz çizilmiş hâlidir. Bundan sonra hep onu kullanacağız.</p>
<p class="small"><b>Not:</b> σ<sub>eD</sub>'deki <b>e</b> eğilme demek, yani bu bir eğilme diyagramı. Bizim kaynak sorularında gerilmenin büyük kısmı eğilmeden geliyor ve hocanın PDF'inde bu diyagram var, o yüzden bunu kullanıyoruz.</p>

<section>
<h2>3. Diyagramın parçaları (St37)</h2>
<figure class="fig">{smith_svg(anatomy=True)}</figure>
<ul class="parts">
<li><b>Yatay eksen σ<sub>m</sub>:</b> ortalama (statik) gerilme. Okumaya hep buradan başlarsın.</li>
<li><b>Orta çizgi (kesik 45° çizgi):</b> σ = σ<sub>m</sub>. Yük hiç salınmasaydı gerilme burada dururdu.</li>
<li><b>Üst eğri:</b> gerilmenin en fazla çıkabileceği yer. σ<sub>üst</sub> = σ<sub>m</sub> + σ<sub>ed</sub>'.</li>
<li><b>Alt eğri:</b> gerilmenin en fazla inebileceği yer. σ<sub>alt</sub> = σ<sub>m</sub> − σ<sub>ed</sub>'.</li>
<li><b>Bant (iki eğrinin arası):</b> güvenli bölge. Gerilme bu bandın içinde gidip geliyorsa parça yorulmadan dayanır.</li>
<li><b>σ<sub>ed</sub>':</b> orta çizgi ile üst eğri arasındaki yükseklik, yani bandın yarısı. Aradığımız sayı bu.</li>
<li><b>x çizgileri</b> (hocanın diyagramında üstte −1, −0,5, 0, 0,5, 1): alt gerilme / üst gerilme oranı. x = −1 tam değişken (dikey eksen), x = 0 titreşimli (alt gerilme 0), x = 1 statik (orta çizginin kendisi).</li>
</ul>
<p>Bant sağa doğru daralıyor: ortalama gerilme arttıkça salınım payı azalıyor. σ<sub>m</sub> = 330'da bant tamamen kapanıyor.</p>
</section>

<div class="key">
<p><b>Kontrol formülü</b> (göz kararı okumayı kontrol etmek için): Üst eğri 170'ten başlayıp 290 noktasından geçen düz bir çizgi. Eğimi (290 − 170) / 145 = <b>0,83</b>.</p>
<ul>
<li>σ<sub>m</sub> ≤ 193 iken: σ<sub>üst</sub> = 170 + 0,83·σ<sub>m</sub> &nbsp;ve&nbsp; <b>σ<sub>ed</sub>' = 170 − 0,17·σ<sub>m</sub></b></li>
<li>σ<sub>m</sub> &gt; 193 iken: üst eğri akmada kesilir, σ<sub>üst</sub> = 330 &nbsp;ve&nbsp; <b>σ<sub>ed</sub>' = 330 − σ<sub>m</sub></b></li>
</ul>
</div>

<section>
<h2>4. Diyagramı okumak: 4 hareket</h2>
<p>Deneme: σ<sub>m</sub> = 100 N/mm² için diyagramı okuyalım.</p>
<figure class="fig">{smith_svg(100)}{legend(g=False)}</figure>
<ol class="moves big">
<li><span class="mv r">① sağa</span> Yatay eksende 0'dan σ<sub>m</sub> = 100'e kadar sağa git.</li>
<li><span class="mv k">② orta</span> Yukarı çık, kesik 45° çizgisine değ. Orta = 100 (hep σ<sub>m</sub>'ye eşit, bu senin kontrol noktan).</li>
<li><span class="mv r">③ üst</span> Yukarı devam et, üst eğriye değ. Okunan: üst ≈ 253.</li>
<li><span class="mv r">④ alt</span> Aşağı in, alt eğriye değ. Okunan: alt ≈ −53.</li>
</ol>
<p class="calc">σ<sub>ed</sub>' = üst − orta = 253 − 100 = <b>153</b> <span class="chk">kontrol: orta − alt = 100 − (−53) = 153. İkisi aynı çıktıysa doğru okudun.</span></p>
<div class="warn"><b>En çok yapılan hata:</b> σ<sub>ed</sub>' yerine üst değeri (253) yazmak. σ<sub>ed</sub>' her zaman <b>orta çizgiden</b> ölçülür, sıfırdan değil.</div>
</section>

<h3>Hoca tarzı kısa okuma soruları</h3>
<p>Önce kendin oku, sonra tabloya bak.</p>
<ol class="quiz">
<li>Ortalama gerilme sıfır (tam değişken yük). Üst, alt ve σ<sub>ed</sub>' kaç?</li>
<li>σ<sub>m</sub> = 100 için üst, alt ve σ<sub>ed</sub>' kaç?</li>
<li>Titreşimli yük (alt gerilme 0). σ<sub>m</sub> ve üst kaç?</li>
<li>σ<sub>m</sub> = 250 için üst, alt ve σ<sub>ed</sub>' kaç?</li>
<li>σ<sub>m</sub> = 330 olursa ne olur?</li>
</ol>
<table class="t ans">
<tr><th>Soru</th><th>① sağa (σ<sub>m</sub>)</th><th>③ üst</th><th>④ alt</th><th>σ<sub>ed</sub>'</th><th>Not</th></tr>
<tr><td>1</td><td>0</td><td>170</td><td>−170</td><td>170</td><td>sol eksenden direkt okunur</td></tr>
<tr><td>2</td><td>100</td><td>≈ 253</td><td>≈ −53</td><td>≈ 153</td><td>yukarıdaki şekil</td></tr>
<tr><td>3</td><td>145</td><td>290</td><td>0</td><td>145</td><td>x = 0 çizgisiyle kesişen nokta</td></tr>
<tr><td>4</td><td>250</td><td>330</td><td>170</td><td>80</td><td>193'ü geçti, üst eğri akmada yatay</td></tr>
<tr><td>5</td><td>330</td><td>330</td><td>330</td><td>0</td><td>bant kapandı, hiç salınım taşınmaz</td></tr>
</table>

<section>
<h2>5. Hesap sırası (hocanın PDF'indeki gibi)</h2>
<p><b>Önce gerilmeler</b> (önceki PDF'te yaptığımız kısım):</p>
<ul>
<li>Kuvveti statik ve dinamik diye ayır. Eğikse cos/sin ile böl.</li>
<li>Alanlar ve W: çekme alanı 960, kayma alanı 720, W = 13 280 mm³.</li>
<li>Statik kuvvetle gerilmeleri bul → <b>σ<sub>vm</sub></b> = √(σ² + 3τ²).</li>
<li>Dinamik kuvvetle aynısını yap → <b>σ<sub>vg</sub></b>.</li>
</ul>
<p><b>Sonra hocanın PDF'indeki 8, 9 ve 10. adımlar:</b></p>
<ol class="hoca" start="8">
<li>Söz konusu kesitte bulunan <b>ortalama gerilme</b> hesaplanır: <b>σ<sub>vm</sub></b>.</li>
<li>Bu ortalamaya karşılık gelen <b>yorulma dayanımı</b> diyagramdan okunur: <b>σ<sub>ed</sub>'</b> (4 hareket: sağa, orta, üst, alt).</li>
<li>Kesit için <b>emniyet katsayısı</b> bulunur:</li>
</ol>
<div class="formula">S = <span class="frac"><span>σ<sub>ed</sub>' · b<sub>0</sub> · b<sub>1</sub></span><span>β<sub>k</sub> · σ<sub>vg</sub></span></span></div>
<p>S, istenen emniyet katsayısından büyükse dikiş emniyetlidir.</p>
<table class="t">
<tr><th>Sembol</th><th>Ne demek?</th><th>Nereden gelir?</th></tr>
<tr><td>σ<sub>vm</sub></td><td>ortalama (statik) eşdeğer gerilme</td><td>statik kuvvetten hesap</td></tr>
<tr><td>σ<sub>vg</sub></td><td>genlik (dinamik) eşdeğer gerilme, ± kısmı</td><td>dinamik kuvvetten hesap</td></tr>
<tr><td>σ<sub>ed</sub>'</td><td>o ortalamada taşınabilen genlik</td><td>Smith diyagramı</td></tr>
<tr><td>b<sub>0</sub>, b<sub>1</sub></td><td>boyut ve yüzey faktörleri (1'den küçük)</td><td>hocanın tablosu / soru</td></tr>
<tr><td>β<sub>k</sub></td><td>çentik faktörü: kaynak dikişinin çentik etkisi (1'den büyük)</td><td>hocanın tablosu / soru</td></tr>
<tr><td>S</td><td>emniyet katsayısı</td><td>sonuç</td></tr>
</table>
<div class="key">
<p><b>Bu PDF'te kullandığım değerler:</b> b<sub>0</sub> = 0,9 · b<sub>1</sub> = 0,9 · β<sub>k</sub> = 2,0 → b<sub>0</sub>·b<sub>1</sub>/β<sub>k</sub> = 0,81 / 2 = <b>0,405</b>. İstenen emniyet <b>S ≥ 1,5</b>.</p>
<p>Bu dört sayı hocanın tablolarından gelir ya da soruda verilir. Ben örnek olsun diye seçtim; sınavda hocanın değerlerini koy. Yöntem aynen aynı kalır, sadece S'nin sayısı değişir.</p>
<p><b>Kısayol:</b> 0,405 her soruda aynı olduğu için S = 0,405 · σ<sub>ed</sub>' / σ<sub>vg</sub>.</p>
</div>
</section>

{example_block("6. Örnek 1: Aşağı doğru kuvvet (kol 80 mm)",
    "Parçaya, dikişten 80 mm uzakta, dikey olarak aşağı doğru F = 8000 ± 2000 N etki ediyor. St37, a = 6 mm, 1. kalite. Dinamik kontrolü Smith diyagramıyla yap.",
    "kayma + eğilme var, çekme yok. Statik (8000 N): σ<sub>vm</sub> = <b>51,9</b>. Dinamik (±2000 N): σ<sub>vg</sub> = <b>13,0</b> N/mm².",
    **ex1,
    extra_after="<p class='small'>Mavi çubuk, gerilmenin gerçekte gidip geldiği aralık: 51,9 ± 13,0, yani 38,9 ile 64,9 arası. Bandın çok içinde kaldığı için S büyük çıktı.</p>")}

{example_block("7. Örnek 2: Tam ortadan, sağa çeken kuvvet",
    "Kuvvet tam eksenden geçiyor, yatay, duvardan uzağa: F = 8000 ± 2000 N. Dikiş emniyetli midir?",
    "sadece çekme var. Statik: σ<sub>vm</sub> = 8000 / 960 = <b>8,33</b>. Dinamik: σ<sub>vg</sub> = 2000 / 960 = <b>2,08</b> N/mm².",
    **ex2,
    extra_after="<p class='small'>σ<sub>m</sub> sıfıra çok yakın olduğu için σ<sub>ed</sub>' neredeyse 170 çıktı. Ortalama küçükse diyagramı sol eksenden okumak yeter. (Saf çekmede normalde çekme diyagramı kullanılır, sayıları biraz daha düşüktür. Hoca tek diyagram verdiyse bunu kullan; S çok büyük olduğu için sonuç değişmez.)</p>")}

{example_block("8. Örnek 3: Eksenin 20 mm üstünden çeken kuvvet",
    "Yatay F = 8000 ± 2000 N, duvardan uzağa, kuvvet çizgisi eksenin 20 mm üstünde (e = 20 mm). Dikiş emniyetli midir?",
    "çekme + eğilme, kayma yok. Kritik nokta üst lif. Statik: σ<sub>vm</sub> = 8,33 + 12,05 = <b>20,4</b>. Dinamik: σ<sub>vg</sub> = 2,08 + 3,01 = <b>5,1</b> N/mm².",
    **ex3, crit=" (üst lif)")}

<section class="ex">
<h2>9. Örnek 4: Eksenin 20 mm altından çeken kuvvet</h2>
<div class="q"><b>Soru:</b> Örnek 3'ün aynısı, ama kuvvet çizgisi eksenin 20 mm altında. F = 8000 ± 2000 N. Dikiş emniyetli midir?</div>
<p class="prev"><b>Önceki PDF'ten:</b> sayılar Örnek 3'le birebir aynı, sadece kritik nokta <b>alt lif</b>. σ<sub>vm</sub> = <b>20,4</b>, σ<sub>vg</sub> = <b>5,1</b> N/mm².</p>
<div class="steps">
<p><b>Diyagram okuması da Örnek 3'le aynı</b>, çünkü diyagram hangi lif olduğunu bilmez, sadece sayıyı bilir. Şekil için Örnek 3'e bak.</p>
<p class="calc">① sağa 20,4 → ② orta 20,4 → ③ üst ≈ {U(ex3)} → ④ alt ≈ {tr(reading(20.4)[1], 0)} &nbsp;⇒&nbsp; σ<sub>ed</sub>' = {U(ex3)} − 20,4 = <b>{E(ex3)}</b></p>
<p class="calc">S = {E(ex3)}·0,9·0,9 / (2,0·5,1) = <b>{tr(S_of(ex3))}</b></p>
<div class="verdict"><b>Karar:</b> S = {tr(S_of(ex3))} ≥ 1,5 ve statik 20,4 &lt; 136 → dikiş <b>emniyetli</b>.</div>
</div>
</section>

{example_block("10. Asıl soru: Problem 7.8 (60° eğik kuvvet)",
    "Dikdörtgen kesitli (20×60), St37 parça çepeçevre a = 6 mm, 1. kalite dikişle gövdeye kaynaklı. Kuvvet F = 12 000 ± 4000 N, x eksenine 60° açıyla, dikişten 80 mm uzakta. Dikiş emniyetli midir?",
    "kuvvet bölündü (Fx = F·cos60°, Fy = F·sin60°). Statik: σ = 6,25 + 62,6 = 68,9, τ = 14,4 → σ<sub>vm</sub> = √(68,9² + 3·14,4²) = <b>73,3</b>. Dinamik: σ = ±22,95, τ = ±4,81 → σ<sub>vg</sub> = <b>24,4</b> N/mm² (yuvarlanmış 23,0 ve 4,8 ile 24,5 çıkar, fark önemsiz).",
    **p78, crit=" (üst dikiş, en zorlanan nokta)",
    extra_after=f"""<p><b>İkinci yol (aynı sonuç):</b> İzin verilen genliği bul, sonra σ<sub>vg</sub> ile karşılaştır. σ<sub>g,em</sub> = σ<sub>ed</sub>'·b<sub>0</sub>·b<sub>1</sub> / (β<sub>k</sub>·S<sub>gerekli</sub>) = {E(p78)}·0,81 / (2,0·1,5) = <b>{tr(reading(73.3)[2] * 0.81 / 3.0)}</b> N/mm². σ<sub>vg</sub> = 24,4 &lt; {tr(reading(73.3)[2] * 0.81 / 3.0)} ✓. Bu, önceki PDF'teki “dinamik &lt; 62” karşılaştırmasının Smith diyagramlı hâli.</p>
""")}

<section class="pb">
<h2>11. Hepsi yan yana</h2>
<table class="t sum">
<tr><th>Örnek</th><th>σ<sub>vm</sub><br>(sağa)</th><th>σ<sub>vg</sub></th><th>üst</th><th>σ<sub>ed</sub>'</th><th>S</th><th>Sonuç</th></tr>
<tr><td>1. Aşağı, kol 80</td><td>51,9</td><td>13,0</td><td>{U(ex1)}</td><td>{E(ex1)}</td><td>{tr(S_of(ex1))}</td><td>emniyetli</td></tr>
<tr><td>2. Ortadan sağa</td><td>8,3</td><td>2,1</td><td>{U(ex2)}</td><td>{E(ex2)}</td><td>{tr(S_of(ex2))}</td><td>emniyetli</td></tr>
<tr><td>3. 20 mm üstte</td><td>20,4</td><td>5,1</td><td>{U(ex3)}</td><td>{E(ex3)}</td><td>{tr(S_of(ex3))}</td><td>emniyetli</td></tr>
<tr><td>4. 20 mm altta</td><td>20,4</td><td>5,1</td><td>{U(ex3)}</td><td>{E(ex3)}</td><td>{tr(S_of(ex3))}</td><td>emniyetli</td></tr>
<tr class="hl"><td>Problem 7.8 (60°)</td><td>73,3</td><td>24,4</td><td>{U(p78)}</td><td>{E(p78)}</td><td>{tr(S_of(p78))}</td><td>emniyetli</td></tr>
</table>
<p>σ<sub>ed</sub>' hep 157 ile 169 arasında, çok az değişiyor, çünkü bütün σ<sub>m</sub> değerleri küçük (bandın geniş olduğu sol tarafta). S'yi asıl belirleyen σ<sub>vg</sub>, yani salınımın büyüklüğü: 60° sorusunda salınım en büyük olduğu için S en küçük çıktı.</p>
<p class='small'><b>Bonus (Problem 7.8):</b> Bu yükte alt/üst oranı x = (12 000 − 4000)/(12 000 + 4000) = 0,5. Mavi çubuğun tepesi (73,3 + 24,4 = 97,7) hocanın diyagramındaki x = 0,5 çizgisinin üstüne düşer.</p>

<h2>12. Sınavda dikkat</h2>
<ul class="tips">
<li>Diyagrama <b>σ<sub>vm</sub></b> ile (statik kısım) girilir, σ<sub>vg</sub> ile değil. σ<sub>vg</sub> formülün paydasına gider.</li>
<li><b>σ<sub>ed</sub>' = üst − orta.</b> Üst değerin kendisini yazma.</li>
<li>Kontrol: orta − alt da aynı sayıyı vermeli. Vermiyorsa yanlış eğriden okumuşsundur.</li>
<li>σ<sub>m</sub> 193'ü geçerse üst eğri 330'da yataydır: σ<sub>ed</sub>' = 330 − σ<sub>m</sub>.</li>
<li>Göz kararı okuma birkaç N/mm² farklı çıkabilir, sorun değil. Önemli olan doğru eğriden ve orta çizgiden ölçmek.</li>
<li>Malzeme St37 değilse (St44, St50 …) hocanın diyagramında o çeliğin eğri çiftini kullan. 4 hareket aynı.</li>
<li>b<sub>0</sub>, b<sub>1</sub>, β<sub>k</sub> ve istenen S: hocanın verdiği değerleri koy. Statik kontrol (σ<sub>vm</sub> &lt; 136) aynen kalır.</li>
</ul>
</section>

</body></html>
"""
    (HERE / "kaynak_smith.html").write_text(html, encoding="utf-8")
    print("HTML yazıldı.")
    for name, d in [("ex1", ex1), ("ex2", ex2), ("ex3", ex3), ("p78", p78)]:
        print(name, "okuma", reading(d["m0"]), "tam sed", round(sed(d["m0"]), 2), "S", round(S_of(d), 3))


if __name__ == "__main__":
    main()
