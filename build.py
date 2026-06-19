#!/usr/bin/env python3
# Сборка сайта книги «Путь Ветра» из глав-маркдаунов в один index.html
import re
import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
BOOK = ROOT / "book"
OUT = ROOT / "index.html"
DIST = ROOT / "dist"

# Порядок разделов книги
ORDER = [
    "пролог.md",
    "01-счастье.md",
    "02-действие.md",
    "03-сила-свобода-страх.md",
    "04-любовь-благодарность.md",
    "05-отношения.md",
    "06-забота.md",
    "07-работа-мастерство-деньги.md",
    "08-пиздец-боль-проигрыш.md",
    "09-видеть-реальность.md",
    "10-иррациональность-чудеса.md",
    "11-дети.md",
    "12-душа-характер-бог.md",
    "эпилог.md",
]


def clean(md_text):
    """Снять служебные пометки черновика, вытащить заголовок."""
    lines = md_text.splitlines()
    title = ""
    body = []
    for ln in lines:
        s = ln.strip()
        if not title and s.startswith("# "):
            title = s[2:].strip()
            continue
        if s.startswith("> Черновик"):
            continue
        if s.startswith("*Конец"):
            continue
        body.append(ln)
    # обрезать хвостовые пустые строки и завершающий разделитель ---
    while body and body[-1].strip() in ("", "---"):
        body.pop()
    return title, "\n".join(body).strip()


def clean_keep_title(md_text):
    """Снять служебные пометки черновика, сохранив заголовок главы."""
    out = []
    for ln in md_text.splitlines():
        s = ln.strip()
        if s.startswith("> Черновик") or s.startswith("*Конец"):
            continue
        out.append(ln)
    while out and out[-1].strip() in ("", "---"):
        out.pop()
    return "\n".join(out).strip()


def write_combined():
    """Единый чистый markdown с метаданными для pandoc."""
    DIST.mkdir(exist_ok=True)
    # YAML-шапка: строки плотно, без пустых строк внутри блока
    header = "\n".join([
        "---",
        'title: "Путь Ветра"',
        'subtitle: "Книга наставлений"',
        'author: "Ветер"',
        "lang: ru",
        "---",
    ])
    chapters = [
        clean_keep_title((BOOK / name).read_text(encoding="utf-8"))
        for name in ORDER
    ]
    md = header + "\n\n" + "\n\n".join(chapters) + "\n"
    md_path = DIST / "_book.md"
    md_path.write_text(md, encoding="utf-8")
    return md_path


def render():
    md = markdown.Markdown(extensions=["extra", "sane_lists"])
    toc_items = []
    sections = []
    for i, name in enumerate(ORDER):
        raw = (BOOK / name).read_text(encoding="utf-8")
        title, body = clean(raw)
        md.reset()
        html = md.convert(body)
        sid = f"sec-{i}"
        toc_items.append(
            f'<li><a href="#{sid}" data-target="{sid}">{title}</a></li>'
        )
        sections.append(
            f'<section id="{sid}" class="chapter">\n'
            f"<h1>{title}</h1>\n{html}\n</section>"
        )
    return "\n".join(toc_items), "\n\n".join(sections)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Путь Ветра</title>
<meta name="description" content="Путь Ветра — книга наставлений по мотивам канала @vetermind. Девять лет мыслей о счастье, действии, любви, боли, Душе и характере.">
<meta property="og:title" content="Путь Ветра">
<meta property="og:description" content="Книга наставлений. Не даёт ответы — учит спрашивать.">
<meta property="og:type" content="book">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;0,7..72,700;1,7..72,400;1,7..72,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f7f4ee; --surface:#fffdf9; --surface-2:#f1ece2;
  --text:#221f1a; --muted:#766e62; --faint:#a89e8e;
  --accent:#bd6431; --accent-soft:#bd643118;
  --border:#e7e0d3; --shadow:0 1px 2px #00000008,0 8px 24px #0000000a;
  --maxw:42rem;
}
html[data-theme="dark"]{
  --bg:#14120d; --surface:#1c1914; --surface-2:#241f18;
  --text:#ece6da; --muted:#9c9384; --faint:#6f675a;
  --accent:#e08a4f; --accent-soft:#e08a4f22;
  --border:#2c281f; --shadow:0 1px 2px #00000030,0 12px 32px #00000040;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--bg); color:var(--text);
  font-family:"Literata",Georgia,serif;
  font-size:clamp(1.02rem,0.62rem + 0.6vw,1.18rem);
  line-height:1.78; -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
  transition:background .35s ease,color .35s ease;
}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}

/* прогресс чтения */
#progress{position:fixed; top:0; left:0; height:3px; width:0;
  background:var(--accent); z-index:60; transition:width .1s linear}

/* шапка */
header{
  position:fixed; top:0; left:0; right:0; height:56px; z-index:50;
  display:flex; align-items:center; gap:.75rem;
  padding:0 clamp(.9rem,3vw,1.5rem);
  background:color-mix(in srgb,var(--surface) 86%,transparent);
  backdrop-filter:saturate(1.4) blur(12px);
  border-bottom:1px solid var(--border);
}
.brand{font-family:"Inter",sans-serif; font-weight:600; letter-spacing:.01em;
  color:var(--text); font-size:1rem; cursor:pointer}
.brand b{color:var(--accent)}
header .spacer{flex:1}
.iconbtn{
  display:inline-flex; align-items:center; justify-content:center;
  width:40px; height:40px; border-radius:11px; border:1px solid var(--border);
  background:var(--surface); color:var(--text); cursor:pointer;
  transition:transform .15s ease,border-color .2s,background .2s}
.iconbtn:hover{border-color:var(--accent); transform:translateY(-1px)}
.iconbtn svg{width:19px; height:19px}
#menuBtn{display:none}

/* боковое оглавление */
#overlay{position:fixed; inset:0; background:#0006; opacity:0; visibility:hidden;
  transition:opacity .3s; z-index:40}
#overlay.show{opacity:1; visibility:visible}
nav#toc{
  position:fixed; top:56px; bottom:0; left:0; width:300px; z-index:45;
  overflow-y:auto; padding:1.4rem 1rem 3rem;
  background:var(--surface); border-right:1px solid var(--border);
}
nav#toc .toc-title{font-family:"Inter",sans-serif; font-size:.72rem;
  text-transform:uppercase; letter-spacing:.12em; color:var(--faint);
  padding:0 .6rem .6rem; font-weight:600}
nav#toc ol{list-style:none; margin:0; padding:0; counter-reset:c}
nav#toc li a{
  display:block; padding:.5rem .6rem; margin:.1rem 0; border-radius:9px;
  font-family:"Inter",sans-serif; font-size:.86rem; line-height:1.35;
  color:var(--muted); border-left:2px solid transparent; transition:.18s}
nav#toc li a:hover{background:var(--surface-2); color:var(--text); text-decoration:none}
nav#toc li a.active{color:var(--accent); background:var(--accent-soft);
  border-left-color:var(--accent); font-weight:500}

/* контент */
main{margin-left:300px; padding:0 clamp(1.1rem,5vw,2rem)}
.wrap{max-width:var(--maxw); margin:0 auto}
.chapter{scroll-margin-top:74px; padding:2.4rem 0 1rem}
.chapter + .chapter{border-top:1px solid var(--border)}

/* обложка */
#cover{max-width:var(--maxw); margin:0 auto; text-align:center;
  padding:clamp(4rem,16vh,9rem) 0 2.5rem}
#cover .kicker{font-family:"Inter",sans-serif; text-transform:uppercase;
  letter-spacing:.28em; font-size:.7rem; color:var(--faint); margin-bottom:1.4rem}
#cover h1{font-size:clamp(2.6rem,9vw,4.4rem); line-height:1.02; margin:0;
  font-weight:700; letter-spacing:-.01em}
#cover .by{margin-top:1.6rem; color:var(--muted); font-style:italic}
#cover .by a{color:var(--muted)}
#cover .epi{margin:2.6rem auto 0; max-width:30rem; color:var(--muted);
  font-style:italic; font-size:1.02rem}

/* типографика глав */
.chapter h1{font-size:clamp(1.7rem,4.6vw,2.5rem); line-height:1.12;
  font-weight:700; letter-spacing:-.01em; margin:0 0 1.4rem}
.chapter h2{font-family:"Inter",sans-serif; font-size:1.16rem; font-weight:600;
  line-height:1.35; margin:2.6rem 0 .9rem; color:var(--text)}
.chapter h2::before{content:""; display:block; width:34px; height:3px;
  background:var(--accent); border-radius:3px; margin-bottom:1rem; opacity:.85}
.chapter p{margin:0 0 1.25rem}
.chapter > p:first-of-type::first-letter{
  float:left; font-size:3.3em; line-height:.78; font-weight:600;
  padding:.04em .09em 0 0; color:var(--accent)}
.chapter blockquote{margin:1.6rem 0; padding:.4rem 0 .4rem 1.3rem;
  border-left:3px solid var(--accent); color:var(--muted); font-style:italic}
.chapter ol,.chapter ul{margin:0 0 1.25rem; padding-left:1.4rem}
.chapter li{margin:.35rem 0}
.chapter hr{border:0; text-align:center; margin:2.4rem 0}
.chapter hr::before{content:"* * *"; letter-spacing:.6em; color:var(--faint);
  font-size:.9rem}
.chapter strong{font-weight:600}

footer{max-width:var(--maxw); margin:0 auto; padding:3rem 0 5rem;
  text-align:center; color:var(--faint); font-family:"Inter",sans-serif;
  font-size:.82rem; border-top:1px solid var(--border); margin-top:2rem}
footer a{color:var(--muted)}

/* скачивание */
#downloads{max-width:var(--maxw); margin:0 auto; padding:1.6rem 0 .6rem;
  text-align:center}
#downloads .dl-title{font-family:"Inter",sans-serif; font-size:.72rem;
  text-transform:uppercase; letter-spacing:.16em; color:var(--faint);
  font-weight:600; margin-bottom:1rem}
.dl-row{display:flex; flex-wrap:wrap; justify-content:center; gap:.6rem}
a.dl{display:inline-flex; align-items:center; gap:.5rem; text-decoration:none;
  font-family:"Inter",sans-serif; font-size:.9rem; font-weight:500;
  color:var(--text); background:var(--surface); border:1px solid var(--border);
  padding:.6rem .95rem; border-radius:12px; box-shadow:var(--shadow);
  transition:transform .15s ease,border-color .2s,color .2s}
a.dl:hover{transform:translateY(-2px); border-color:var(--accent);
  color:var(--accent); text-decoration:none}
a.dl svg{width:17px; height:17px; opacity:.8}
a.dl small{color:var(--faint); font-weight:400; font-size:.74rem}
#downloads .dl-hint{margin-top:.8rem; color:var(--faint);
  font-family:"Inter",sans-serif; font-size:.78rem}

.totop{position:fixed; right:18px; bottom:18px; z-index:40; opacity:0;
  visibility:hidden; transition:.25s}
.totop.show{opacity:1; visibility:visible}

@media(max-width:900px){
  #menuBtn{display:inline-flex}
  nav#toc{transform:translateX(-100%); transition:transform .3s ease;
    box-shadow:var(--shadow)}
  nav#toc.open{transform:translateX(0)}
  main{margin-left:0}
}
</style>
</head>
<body>
<div id="progress"></div>

<header>
  <button id="menuBtn" class="iconbtn" aria-label="Оглавление">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
  </button>
  <span class="brand" id="brand">Путь <b>Ветра</b></span>
  <span class="spacer"></span>
  <button id="themeBtn" class="iconbtn" aria-label="Тема">
    <svg id="iconMoon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
    <svg id="iconSun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
  </button>
</header>

<div id="overlay"></div>
<nav id="toc">
  <div class="toc-title">Оглавление</div>
  <ol>%%TOC%%</ol>
</nav>

<main>
  <div id="cover">
    <div class="kicker">Книга наставлений</div>
    <h1>Путь<br>Ветра</h1>
    <div class="by">по мотивам канала <a href="https://t.me/vetermind" target="_blank" rel="noopener">&#64;vetermind</a></div>
    <p class="epi">Эта книга не даёт ответы. Она учит спрашивать.</p>
  </div>

  <div id="downloads">
    <div class="dl-title">Скачать для читалки</div>
    <div class="dl-row">
      <a class="dl" href="dist/put-vetra.epub" download>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M8 11l4 4 4-4M5 21h14"/></svg>
        EPUB <small>читалки</small>
      </a>
      <a class="dl" href="dist/put-vetra.fb2" download>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M8 11l4 4 4-4M5 21h14"/></svg>
        FB2 <small>читалки</small>
      </a>
      <a class="dl" href="dist/put-vetra.pdf" download>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M8 11l4 4 4-4M5 21h14"/></svg>
        PDF <small>компьютер</small>
      </a>
      <a class="dl" href="dist/put-vetra-mobile.pdf" download>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12M8 11l4 4 4-4M5 21h14"/></svg>
        PDF <small>смартфон</small>
      </a>
    </div>
    <div class="dl-hint">для офлайна и чтения через читалку</div>
  </div>

  <div class="wrap">
%%CONTENT%%
  </div>
  <footer>
    Путь Ветра &middot; %%YEAR%% &middot; <a href="https://t.me/vetermind" target="_blank" rel="noopener">t.me/vetermind</a>
  </footer>
</main>

<button class="totop iconbtn" id="toTop" aria-label="Наверх">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>

<script>
(function(){
  var root=document.documentElement;
  var KEY="theway-theme";
  var iconMoon=document.getElementById("iconMoon");
  var iconSun=document.getElementById("iconSun");
  function apply(t){
    root.setAttribute("data-theme",t);
    iconMoon.style.display=t==="dark"?"none":"";
    iconSun.style.display=t==="dark"?"":"none";
  }
  var saved=localStorage.getItem(KEY);
  var sys=window.matchMedia&&window.matchMedia("(prefers-color-scheme:dark)").matches;
  apply(saved||(sys?"dark":"light"));
  document.getElementById("themeBtn").addEventListener("click",function(){
    var t=root.getAttribute("data-theme")==="dark"?"light":"dark";
    apply(t); localStorage.setItem(KEY,t);
  });

  // прогресс + кнопка наверх
  var bar=document.getElementById("progress");
  var toTop=document.getElementById("toTop");
  function onScroll(){
    var h=document.documentElement;
    var sc=h.scrollTop||document.body.scrollTop;
    var max=h.scrollHeight-h.clientHeight;
    bar.style.width=(max>0?(sc/max*100):0)+"%";
    toTop.classList.toggle("show",sc>600);
  }
  window.addEventListener("scroll",onScroll,{passive:true});
  onScroll();
  toTop.addEventListener("click",function(){window.scrollTo({top:0,behavior:"smooth"})});
  document.getElementById("brand").addEventListener("click",function(){window.scrollTo({top:0,behavior:"smooth"})});

  // мобильный drawer
  var toc=document.getElementById("toc");
  var overlay=document.getElementById("overlay");
  function closeDrawer(){toc.classList.remove("open");overlay.classList.remove("show")}
  document.getElementById("menuBtn").addEventListener("click",function(){
    toc.classList.toggle("open");overlay.classList.toggle("show");
  });
  overlay.addEventListener("click",closeDrawer);

  // активный пункт оглавления
  var links={};
  document.querySelectorAll("#toc a").forEach(function(a){
    links[a.dataset.target]=a;
    a.addEventListener("click",closeDrawer);
  });
  var obs=new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        Object.values(links).forEach(function(l){l.classList.remove("active")});
        var l=links[e.target.id]; if(l){l.classList.add("active");
          l.scrollIntoView({block:"nearest"});}
      }
    });
  },{rootMargin:"-30% 0px -60% 0px",threshold:0});
  document.querySelectorAll(".chapter").forEach(function(s){obs.observe(s)});
})();
</script>
</body>
</html>
"""


def main():
    toc, content = render()
    html = (
        TEMPLATE
        .replace("%%TOC%%", toc)
        .replace("%%CONTENT%%", content)
        .replace("%%YEAR%%", str(datetime.date.today().year))
    )
    OUT.write_text(html, encoding="utf-8")
    print("Written", OUT, len(html), "bytes")
    md_path = write_combined()
    print("Written", md_path)
    build_ebooks(md_path)


def build_ebooks(md_path):
    """EPUB, FB2, PDF (компьютер и смартфон) через pandoc + xelatex."""
    import subprocess

    epub = DIST / "put-vetra.epub"
    fb2 = DIST / "put-vetra.fb2"
    pdf = DIST / "put-vetra.pdf"
    pdf_m = DIST / "put-vetra-mobile.pdf"

    common = ["pandoc", str(md_path), "--toc", "--toc-depth=1"]

    jobs = [
        (["pandoc", str(md_path), "--toc", "--toc-depth=1",
          "--split-level=1", "-o", str(epub)], "EPUB"),
        (["pandoc", str(md_path), "-o", str(fb2)], "FB2"),
        (common + [
            "--pdf-engine=xelatex", "-V", "mainfont=Georgia",
            "-V", "fontsize=12pt", "-V", "linestretch=1.25",
            "-V", "geometry:paperwidth=152mm,paperheight=229mm,margin=18mm",
            "-V", "linkcolor=RoyalBlue", "-V", "toccolor=black",
            "-o", str(pdf)], "PDF (компьютер)"),
        (common + [
            "--pdf-engine=xelatex", "-V", "mainfont=Georgia",
            "-V", "fontsize=11pt", "-V", "linestretch=1.3",
            "-V", "geometry:paperwidth=90mm,paperheight=160mm,margin=6mm",
            "-V", "linkcolor=RoyalBlue", "-V", "toccolor=black",
            "-o", str(pdf_m)], "PDF (смартфон)"),
    ]
    for cmd, label in jobs:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("OK", label, "->", cmd[-1])
        except subprocess.CalledProcessError as e:
            print("FAIL", label, e.stderr[-800:])


if __name__ == "__main__":
    main()
