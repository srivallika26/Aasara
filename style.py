import html as _html
import math
import re

import io
import wave

import streamlit as st

# Optional: feedback link (form URL or mailto:you@example.com). Leave "" to hide it.
FEEDBACK_URL = ""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Noto+Sans+Telugu:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg:#08082a; --bg2:#0e0e3d; --ind:#3a3fc0; --peri:#8b91ff; --mint:#5eead4;
  --ink:#eef0ff; --muted:#b4b9e0; --glass:rgba(255,255,255,.06); --line:rgba(255,255,255,.14);
}

/* ---------- Page ---------- */
.stApp { color:var(--ink) !important;
  background:
    radial-gradient(1.2px 1.2px at 12% 18%, rgba(255,255,255,.55), transparent),
    radial-gradient(1.2px 1.2px at 78% 9%, rgba(255,255,255,.45), transparent),
    radial-gradient(1px 1px at 40% 62%, rgba(255,255,255,.35), transparent),
    radial-gradient(1.2px 1.2px at 90% 55%, rgba(255,255,255,.4), transparent),
    radial-gradient(900px 500px at 50% -5%, rgba(92,98,230,.45), transparent 65%),
    linear-gradient(180deg,var(--bg2) 0%,var(--bg) 60%) !important; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div { color:var(--ink); }
header[data-testid="stHeader"], #MainMenu, footer { visibility:hidden; height:0; }
.block-container { max-width:1200px !important; width:100%; margin-left:auto !important; margin-right:auto !important; padding:1rem clamp(14px,3vw,40px) 3rem !important; }
html { scroll-behavior:smooth; }
h1, h2, h3, h4 { font-family:'Fraunces','Noto Sans Telugu',serif !important; color:#fff !important; font-weight:400 !important; }
h3 { font-size:clamp(1.5rem,2.6vw,2.2rem) !important; margin-top:1.6rem !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:var(--muted) !important; font-size:.95rem !important; }
[data-testid="stWidgetLabel"] p { color:var(--ink) !important; font-weight:600; font-size:1rem !important; }
.hero, .feat, .card, .step, .foot, .device { font-family:'Inter','Noto Sans Telugu',sans-serif; }

/* ---------- Nav ---------- */
.nav { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; padding:8px 4px 20px; font-family:'Inter',sans-serif; }
.logo { display:flex; align-items:center; gap:10px; font-family:'Fraunces',serif; font-size:1.55rem; color:#fff !important; text-decoration:none !important; }
.logo i { display:grid; place-items:center; width:38px; height:38px; border-radius:50%; font-style:normal; font-size:1.1rem; font-family:'Noto Sans Telugu',sans-serif; color:#fff; background:linear-gradient(135deg,#8b91ff,#3a3fc0); box-shadow:0 2px 10px rgba(58,63,192,.5); }
.nav ul { display:flex; gap:26px; list-style:none; margin:0; padding:0; align-items:center; flex-wrap:wrap; }
.nav ul a { color:var(--muted) !important; text-decoration:none !important; font-size:.98rem; }
.nav ul a:hover { color:#fff !important; }
.login { border:1px solid rgba(139,145,255,.7); border-radius:10px; padding:8px 20px; color:#fff !important; font-size:.95rem; font-weight:600; cursor:default; }
.what { margin:34px 0 6px; padding:30px 28px; border-radius:18px; background:var(--glass); border:1px solid var(--line); }
.what h3 { margin:0 0 10px !important; font-size:2rem !important; }
.what p { font-size:1.08rem; line-height:1.7; color:var(--muted) !important; margin:0 0 10px; max-width:70ch; }
.what b { color:#fff !important; }

/* ---------- Hero ---------- */
.hero { padding:34px 8px 6px; }
.chip { display:inline-block; font-size:.85rem; color:var(--ink) !important; background:var(--glass); border:1px solid var(--line); border-radius:8px; padding:6px 12px; margin:0 8px 8px 0; }
.hgrid { display:grid; grid-template-columns:1.7fr 1fr; gap:36px; align-items:center; margin-top:16px; }
.hero h1 { font-size:clamp(2.4rem,5.2vw,5rem); line-height:1.05; margin:0; padding:0; letter-spacing:-.01em; }
.hero .side { font-size:1.2rem; line-height:1.55; color:var(--muted) !important; padding:4px 0 4px 20px; border-left:2px solid rgba(139,145,255,.5); }
.hero .side b { color:#fff !important; }
.cta { display:inline-flex; align-items:center; gap:10px; margin-top:52px; background:#f1f2fb; color:#14164a !important; font-weight:700; font-size:1.2rem; padding:18px 40px; border-radius:12px; text-decoration:none !important; box-shadow:0 10px 26px rgba(0,0,0,.38); }
.cta:hover { background:#fff; }

/* Glowing device mockup */
.device { margin:44px 0 10px; width:100%; max-width:100%; box-sizing:border-box; border-radius:22px; padding:20px 22px 26px;
  background:linear-gradient(180deg,rgba(14,18,70,.95),rgba(8,10,42,.98));
  box-shadow:0 0 0 1px rgba(139,145,255,.4), 0 18px 50px rgba(0,0,0,.45); }
.dtop { font-size:.85rem; color:var(--muted) !important; display:flex; align-items:center; gap:8px; }
.dtop i { width:8px; height:8px; border-radius:50%; background:var(--mint); display:inline-block; box-shadow:0 0 10px var(--mint); }
.dhi { display:flex; align-items:center; gap:14px; margin:16px 0 4px; }
.dhi .av { width:44px; height:44px; border-radius:50%; background:linear-gradient(135deg,var(--peri),var(--ind)); display:grid; place-items:center; font-size:1.3rem; }
.dhi b { font-size:1.35rem; color:#fff !important; font-family:'Noto Sans Telugu',sans-serif; }
.dhi span { display:block; font-size:.9rem; color:var(--muted) !important; }
.wave { display:flex; align-items:center; justify-content:center; gap:5px; height:70px; margin:14px 0 18px; }
.wave i { display:block; width:5px; border-radius:3px; background:linear-gradient(180deg,var(--mint),#22c55e); height:12px; animation:pulse 1.2s ease-in-out infinite; }
.wave i:nth-child(4n+1){ animation-delay:0s } .wave i:nth-child(4n+2){ animation-delay:.25s }
.wave i:nth-child(4n+3){ animation-delay:.5s } .wave i:nth-child(4n){ animation-delay:.75s }
@keyframes pulse { 0%,100%{ height:10px } 50%{ height:60px } }
@media (prefers-reduced-motion: reduce){ .wave i{ animation:none; height:30px } html{ scroll-behavior:auto } }
.mini { margin-top:20px; display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.mini div { background:rgba(255,255,255,.05); border:1px solid var(--line); border-radius:12px; padding:14px; }
.mini b { display:block; font-size:1.5rem; color:#fff !important; font-weight:600; }
.mini span { font-size:.82rem; color:var(--muted) !important; }

/* ---------- Feature cards ---------- */
.feats { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:26px 0 20px; }
.feat { background:var(--glass); border:1px solid var(--line); border-radius:16px; padding:28px 22px; min-height:200px; backdrop-filter:blur(6px); }
.feat .ic { font-size:2.4rem; line-height:1; margin-bottom:16px; }
.feat b { display:block; font-size:1.25rem; font-weight:700; color:#fff !important; margin-bottom:8px; }
.feat span { font-size:1rem; color:var(--muted) !important; line-height:1.55; }

/* ---------- Scheme cards ---------- */
.cards { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:22px; }
.card { display:flex; flex-direction:column; background:var(--glass); border:1px solid var(--line); border-radius:16px; padding:22px; min-height:290px; }
.card .ico { width:52px; height:52px; border-radius:14px; display:grid; place-items:center; font-size:1.7rem; margin-bottom:12px; background:rgba(139,145,255,.18); }
.card h4 { margin:0 0 4px; font-size:1.3rem; line-height:1.25; padding:0; }
.card .te { color:var(--peri) !important; font-size:1rem; font-weight:600; margin-bottom:10px; }
.card p { font-size:1rem; line-height:1.55; color:var(--ink) !important; margin:0 0 12px; }
.card .meta { font-size:.92rem; color:var(--muted) !important; margin:0 0 12px; }
.card .meta b { color:#fff !important; }
.card .bottom { margin-top:auto; display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap; }
.badge { font-size:.78rem; background:rgba(255,255,255,.1); color:var(--ink) !important; border-radius:6px; padding:3px 10px; font-weight:600; }
.more { font-size:.95rem; font-weight:700; color:var(--peri) !important; text-decoration:none !important; }
.more:hover { text-decoration:underline !important; }
.c-health .ico { background:rgba(96,165,250,.25); } .c-farm .ico { background:rgba(74,222,128,.22); }
.c-pension .ico { background:rgba(251,191,36,.22); } .c-girl .ico { background:rgba(244,114,182,.24); }
.c-biz .ico { background:rgba(167,139,250,.28); } .c-energy .ico { background:rgba(251,146,60,.24); }

/* ---------- Input card (wrap mic + text box in st.container(border=True)) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] { background:var(--glass); border:1px solid var(--line) !important; border-radius:18px !important; box-shadow:0 14px 40px rgba(0,0,0,.35); padding:8px; }
[data-testid="stAudioInput"] { min-height:92px; background:linear-gradient(160deg,#171a6b,#0d0f45) !important; border:1px solid rgba(139,145,255,.5) !important; border-radius:14px !important; padding:10px 14px; }
[data-testid="stAudioInput"] * { color:#fff !important; }
[data-testid="stAudioInput"] svg { color:#fff !important; fill:#fff !important; }
[data-testid="stAudioInput"] button { transform:scale(1.25); }
.stTextInput input, .stTextArea textarea { background:rgba(255,255,255,.07) !important; color:#fff !important; border:1.5px solid var(--line) !important; border-radius:12px !important; font-size:1.05rem !important; padding:12px 14px !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#8f95c4 !important; }
[data-baseweb="select"] > div { background:rgba(255,255,255,.07) !important; border:1.5px solid var(--line) !important; border-radius:10px !important; }
[data-baseweb="select"] span, [data-baseweb="select"] div, [data-baseweb="select"] svg { color:#fff !important; fill:#fff !important; }
[data-baseweb="popover"] ul, [data-baseweb="popover"] li { background:#14166b !important; color:#fff !important; }
[data-testid="stForm"] { background:var(--glass); border:1px solid var(--line) !important; border-radius:18px; }
[data-testid="stExpander"] { background:var(--glass); border:1px solid var(--line); border-radius:12px; }

/* ---------- Buttons ---------- */
.stButton > button { background:rgba(255,255,255,.07) !important; border-radius:999px !important; border:1.5px solid rgba(139,145,255,.7) !important; color:#fff !important; font-weight:600; padding:.5rem 1.2rem; font-size:1rem; }
.stButton > button:hover { background:#f1f2fb !important; color:#14164a !important; border-color:#f1f2fb !important; }
.stButton > button, .stButton > button * { color:#fff !important; }
.stButton > button:hover, .stButton > button:hover * { color:#14164a !important; }
.stFormSubmitButton > button { background:linear-gradient(135deg,#5b5bf0,#8a5cf6) !important; border:0 !important; border-radius:999px !important; font-weight:700; font-size:1.05rem; padding:.65rem 1.7rem; box-shadow:0 8px 22px rgba(70,60,200,.4); }
.stFormSubmitButton > button, .stFormSubmitButton > button * { color:#fff !important; }
.stFormSubmitButton > button:hover { background:linear-gradient(135deg,#6e6eff,#a070ff) !important; }

[data-testid="stChatMessage"] { border-radius:14px; background:var(--glass); border:1px solid var(--line); }
[data-testid="stChatMessage"] * { color:var(--ink); }

/* ---------- How it works ---------- */
.steps { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }
.step { background:var(--glass); border:1px solid var(--line); border-radius:16px; padding:26px 20px; text-align:center; color:var(--muted) !important; font-size:1rem; line-height:1.55; }
.step b { color:#fff !important; font-size:1.1rem; }
.step .ic { font-size:2rem; width:64px; height:64px; line-height:64px; margin:0 auto 10px; border-radius:50%; background:rgba(139,145,255,.2); }

/* ---------- Footer ---------- */
.foot { background:rgba(255,255,255,.05); border:1px solid var(--line); border-radius:18px; padding:30px 28px 22px; margin-top:30px; font-size:.95rem; line-height:1.65; }
.foot .cols { display:grid; grid-template-columns:1.4fr 1fr 1fr; gap:26px; }
.foot h5 { color:var(--peri) !important; font-size:1rem; margin:0 0 8px; font-family:'Inter',sans-serif; font-weight:700; }
.foot p { margin:0; color:var(--muted) !important; }
.foot a { color:#fff !important; text-decoration:underline; }
.foot .copy { border-top:1px solid var(--line); margin-top:20px; padding-top:14px; font-size:.85rem; color:var(--muted) !important; }

@media (max-width:1000px){
  .hgrid{ grid-template-columns:1fr; gap:14px; } .hero .side{ padding-bottom:0; }
  .feats{ grid-template-columns:repeat(2,1fr); } .foot .cols{ grid-template-columns:1fr 1fr; }
}
@media (max-width:700px){
  .nav{ justify-content:center; text-align:center; } .nav ul{ gap:14px 18px; justify-content:center; }
  .nav ul a{ font-size:.9rem; }
  .feats, .mini, .foot .cols{ grid-template-columns:1fr; }
  .feat{ min-height:0; padding:22px 18px; } .card{ min-height:0; }
  .device{ padding:16px 14px 20px; } .wave{ gap:3px; } .wave i{ width:4px; }
  .cta{ width:100%; justify-content:center; box-sizing:border-box; }
  .what{ padding:22px 18px; } .foot{ padding:24px 18px 18px; }
}
@media (min-width:1500px){
  .feat, .card{ padding:30px 28px; } .hero .side{ font-size:1.2rem; }
}

/* ---------- Final refinement ---------- */
html, body, .stApp { overflow-x:hidden; }
*:focus-visible { outline:2px solid #c7caff !important; outline-offset:3px; }
#what, #schemes, #how, #about, #talk, #faq { scroll-margin-top:24px; }
.hero h1 { letter-spacing:-.015em; }
.cta:hover { transform:translateY(-1px); }

/* Subtle hero waveform */
.hwave { display:flex; align-items:center; gap:4px; height:34px; margin-top:28px; opacity:.55; }
.hwave i { display:block; width:3px; height:100%; border-radius:2px; background:linear-gradient(180deg,#8b91ff,#5b5bf0); transform:scaleY(var(--h)); animation:breathe 3.4s ease-in-out infinite; animation-delay:var(--d); }
@keyframes breathe { 0%,100%{ transform:scaleY(var(--h)); } 50%{ transform:scaleY(calc(var(--h) * .55)); } }

/* Navbar hover and active */
.nav ul a { padding:6px 2px; border-bottom:2px solid transparent; transition:color .15s, border-color .15s; }
.nav ul a:hover { color:#fff !important; border-bottom-color:rgba(139,145,255,.7); }
.stApp:has(#what:target) .nav a[href="#what"], .stApp:has(#schemes:target) .nav a[href="#schemes"],
.stApp:has(#how:target) .nav a[href="#how"], .stApp:has(#about:target) .nav a[href="#about"] { color:#fff !important; border-bottom-color:var(--peri); }

/* Hover polish */
.feat, .card, .step { transition:transform .2s ease, border-color .2s ease, box-shadow .2s ease; }
.feat:hover, .card:hover, .step:hover { transform:translateY(-3px); border-color:rgba(139,145,255,.55); box-shadow:0 14px 34px rgba(0,0,0,.35); }

/* Scheme cards */
.card { min-height:300px; }
.card .top { display:flex; justify-content:space-between; align-items:flex-start; }
.card .lvl { font-size:.8rem; font-weight:600; color:var(--ink) !important; border:1px solid var(--line); border-radius:999px; padding:3px 11px; }
.card h4 { font-size:1.22rem; }
.card h4, .card p, .card .te, .card .meta { overflow-wrap:anywhere; }
.card p { font-size:1.02rem; }
.amt { background:rgba(139,145,255,.24); color:#fff !important; font-weight:700; padding:1px 7px; border-radius:6px; }
.vers { display:flex; flex-wrap:wrap; gap:6px; }
.badge.ok { background:rgba(74,222,128,.14); color:#86efac !important; }
.badge.warn { background:rgba(251,191,36,.16); color:#fcd34d !important; }

/* Voice panel: four states */
.vp { --sc:#8b91ff; display:grid; grid-template-columns:auto 1fr minmax(120px,280px); align-items:center; gap:22px; padding:22px 26px; margin:6px 0 16px; border-radius:18px; border:1px solid var(--sc); background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.03)); font-family:'Inter','Noto Sans Telugu',sans-serif; }
.vp-ready { --sc:#8b91ff; } .vp-listening { --sc:#fb7185; } .vp-processing { --sc:#fbbf24; } .vp-speaking { --sc:#5eead4; }
.vp-mic { position:relative; width:76px; height:76px; display:grid; place-items:center; }
.vp-mic .mic { position:relative; z-index:1; width:64px; height:64px; border-radius:50%; background:var(--sc); display:grid; place-items:center; }
.vp-mic .ring { position:absolute; inset:6px; border-radius:50%; border:2px solid var(--sc); opacity:0; }
.vp-listening .ring { animation:ripple 1.9s ease-out infinite; } .vp-listening .r2 { animation-delay:.95s; }
@keyframes ripple { 0%{ transform:scale(.9); opacity:.7; } 100%{ transform:scale(1.5); opacity:0; } }
.vp-txt b { display:block; font-size:1.3rem; color:#fff !important; font-weight:600; }
.vp-txt span { color:var(--muted) !important; font-size:1rem; }
.vp-vis { display:flex; align-items:center; justify-content:flex-end; gap:4px; height:52px; }
.vp-vis i { display:block; width:4px; height:100%; border-radius:2px; background:var(--sc); transform:scaleY(.18); opacity:.5; }
.vp-listening .vp-vis i, .vp-speaking .vp-vis i { opacity:1; animation:wv 1.1s ease-in-out infinite; animation-delay:var(--d); }
@keyframes wv { 0%,100%{ transform:scaleY(.18); } 50%{ transform:scaleY(var(--h)); } }
.vp-vis.dots i { width:11px; height:11px; border-radius:50%; transform:none; opacity:.4; animation:dot 1.2s ease-in-out infinite; animation-delay:var(--d); }
@keyframes dot { 0%,80%,100%{ transform:translateY(0); opacity:.4; } 40%{ transform:translateY(-9px); opacity:1; } }
.spin { width:28px; height:28px; border-radius:50%; border:3px solid rgba(11,12,51,.25); border-top-color:#0b0c33; animation:spin 1s linear infinite; }
@keyframes spin { to{ transform:rotate(360deg); } }

/* FAQ */
.faq { margin:44px 0 0; }
.faq h3 { margin:0 0 16px !important; }
.faq details { background:var(--glass); border:1px solid var(--line); border-radius:14px; padding:0 22px; margin-bottom:10px; }
.faq details[open] { border-color:rgba(139,145,255,.55); }
.faq summary { cursor:pointer; list-style:none; padding:18px 0; font-size:1.08rem; font-weight:600; color:#fff !important; display:flex; justify-content:space-between; gap:16px; }
.faq summary::-webkit-details-marker { display:none; }
.faq summary::after { content:"+"; color:var(--peri); font-size:1.5rem; line-height:1; }
.faq details[open] summary::after { content:"–"; }
.faq p { margin:0 0 18px; color:var(--muted) !important; line-height:1.7; font-size:1.02rem; max-width:80ch; }

/* Footer readability */
.foot { font-size:1rem; }
.foot p { color:#cdd1f2 !important; font-size:1rem; line-height:1.7; }
.foot h5 { font-size:1.05rem; }
.foot .copy { color:#b9bfe6 !important; font-size:.9rem; }

@media (max-width:1023px){ .cards{ grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width:767px){ .cards{ grid-template-columns:1fr; } }
@media (max-width:700px){
  .cards{ grid-template-columns:1fr; }
  .vp{ grid-template-columns:1fr; text-align:center; justify-items:center; }
  .vp-vis{ justify-content:center; } .hwave{ display:none; }
}
@media (prefers-reduced-motion: reduce){
  .hwave i, .vp i, .ring, .spin{ animation:none !important; }
  .feat:hover, .card:hover, .step:hover, .cta:hover{ transform:none; }
}
.card .meta { display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }

/* ---------- v5 refinements ---------- */
[data-testid="stCaptionContainer"] { max-width:80ch; }
.card p { font-size:.96rem; line-height:1.6; }
.card .bottom { flex-direction:column; align-items:flex-start; gap:12px; }
.card .meta { display:block; -webkit-line-clamp:unset; overflow:visible; background:rgba(94,234,212,.08); border-left:3px solid #5eead4; border-radius:6px; padding:9px 12px; font-size:.9rem; line-height:1.5; color:var(--ink) !important; }
.card .meta b { display:block; color:#5eead4 !important; font-size:.8rem; margin-bottom:2px; }
.card .lvl.central { border-color:rgba(139,145,255,.8); color:#c7caff !important; }
.card .lvl.tg { border-color:rgba(251,191,36,.7); color:#fcd34d !important; }
.badge { font-size:.82rem; padding:4px 10px; }
[data-testid="stRadio"] [role="radiogroup"] { gap:6px 18px; flex-wrap:wrap; }
.vp-txt { display:grid; }
.vp-txt > .t, .vp-mic .mic > .ic { grid-area:1 / 1; }
.vp-mic .mic .ic { display:grid; place-items:center; }
.vp-speaking .a { animation:vpOut .35s ease forwards; animation-delay:var(--T,6s); }
.vp-speaking .b { opacity:0; animation:vpIn .35s ease forwards; animation-delay:var(--T,6s); }
@keyframes vpOut { to{ opacity:0; } }
@keyframes vpIn { to{ opacity:1; } }
.stApp:has(#talk:target) .vp { animation:vcpulse 1.6s ease 1; }
@keyframes vcpulse { 0%{ box-shadow:0 0 0 0 rgba(139,145,255,.6); } 100%{ box-shadow:0 0 0 18px rgba(139,145,255,0); } }

</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)


def anchor(name="talk"):
    """Call this right above the mic/input section so Start Speaking scrolls there."""
    st.markdown(f'<div id="{name}"></div>', unsafe_allow_html=True)


def hero(n=0):
    html = "".join([
        '<div id="top"></div>',
        '<div class="nav"><a class="logo" href="#top" target="_self"><i>ఆ</i>Aasara</a><ul>'
        '<li><a href="#what" target="_self">What is Aasara?</a></li><li><a href="#schemes" target="_self">Schemes</a></li>'
        '<li><a href="#how" target="_self">How it works</a></li><li><a href="#about" target="_self">About</a></li>'
        '</ul></div>',
        '<div class="hero">',
        '<span class="chip">Gnani Prisma speech-to-text</span><span class="chip">Gnani Timbre text-to-speech</span><span class="chip">Telugu · Hindi</span>',
        '<div class="hgrid">',
        '<h1>ఆసరా<br>Ask in Telugu. Hear the answer.</h1>',
        '<div class="side"><b>A voice guide</b> to government schemes and income tax, with an source and last-checked date for every scheme.</div>',
        '</div>',
        '<a class="cta" href="#talk" target="_self">🎙️ Start Speaking</a>',
        '<div class="device" aria-hidden="true">',
        '<div class="dtop"><i></i>Aasara · voice</div>',
        '<div class="dhi"><div class="av">🎙️</div><div><b>ఆసరా</b><span>Ready to listen</span></div></div>',
        f'<div class="mini"><div><b>{n}</b><span>schemes with sources</span></div><div><b>Telugu · Hindi</b><span>speak and listen</span></div><div><b>✔</b><span>last-checked date on each</span></div></div>',
        '</div>',
        '</div>',
        '<div class="feats">',
        f'<div class="feat"><div class="ic">📋</div><b>{n} schemes</b><span>Central and Telangana schemes, each with a source and check date.</span></div>',
        '<div class="feat"><div class="ic">🎙️</div><b>Speak and listen</b><span>Ask out loud in Telugu or Hindi and hear the reply.</span></div>',
        '<div class="feat"><div class="ic">✔️</div><b>Checked facts</b><span>Every scheme shows its source and last-checked date.</span></div>',
        '</div>',
    ])
    st.markdown(html, unsafe_allow_html=True)
    st.markdown(
        '<div class="what" id="what"><h3>What is Aasara?</h3>'
        '<p><b>Aasara</b> (ఆసరా means support) is a voice assistant that helps people in Telugu and Hindi find the government schemes they may be eligible for, and make a simple income tax estimate.</p>'
        f'<p>You speak, Aasara asks a few questions, then reads out the matching schemes with a source and last-checked date for every scheme. It answers only from its own checked list of {n} schemes, and says so when it does not know.</p></div>',
        unsafe_allow_html=True,
    )


def _look(name):
    n = name.lower()
    if "kisan" in n: return "🌾", "c-farm"
    if "ayushman" in n or "aarogya" in n: return "🏥", "c-health"
    if "ujjwala" in n: return "🔥", "c-energy"
    if "gruha" in n or "jyothi" in n: return "💡", "c-energy"
    if "sukanya" in n: return "👧", "c-girl"
    if "pension" in n or "atal" in n or "aasara" in n or "cheyutha" in n: return "💰", "c-pension"
    if "mudra" in n: return "💼", "c-biz"
    return "📄", "c-health"


_AMT = re.compile(r"((?:₹|\bRs\.?)\s?(?:\d{1,3}(?:,\d{2,3})+|\d+)(?:\.\d+)?(?:\s?(?:lakh|crore))?)")


def level_label(level):
    return "Telangana Government" if str(level).lower() == "telangana" else "Central Government"


def scheme_cards(schemes):
    items = []
    for s in schemes.values():
        icon, tint = _look(s["name"])
        short = s["benefit"].split(". ")[0].rstrip(".") + "."
        short_html = _AMT.sub(r'<mark class="amt">\1</mark>', _html.escape(short, quote=False))
        level = s.get("level", "Central")
        lvl_cls = "tg" if str(level).lower() == "telangana" else "central"
        elig = s.get("eligibility")
        if isinstance(elig, (list, tuple)) and elig:
            elig = elig[0]
        if isinstance(elig, str) and len(elig) > 150:
            elig = elig[:147].rsplit(" ", 1)[0] + "…"
        elig_html = (f'<div class="meta"><b>Who can apply</b>{_html.escape(elig, quote=False)}</div>'
                     if isinstance(elig, str) and elig else "")
        url = s.get("source_url") or s.get("url") or s.get("official_url") or s.get("link")
        if not url:
            for src in s.get("sources") or []:
                if isinstance(src, dict) and str(src.get("url", "")).startswith("http"):
                    url = src["url"]
                    break
        note = s.get("verification_note")
        link_text = "View source →" if note else "View details →"
        more = (f'<a class="more" href="{url}" target="_blank" rel="noopener">{link_text}</a>'
                if isinstance(url, str) and url.startswith("http") else "")
        if note:
            badges = (f'<span class="badge warn" title="{_html.escape(note, quote=True)}">News-based · confirm locally</span>'
                      f'<span class="badge">Checked {s["last_checked"]}</span>')
        else:
            badges = f'<span class="badge ok">✔ Source checked {s["last_checked"]}</span>'
        items.append(
            f'<div class="card {tint}"><div class="top"><div class="ico">{icon}</div>'
            f'<span class="lvl {lvl_cls}">{level_label(level)}</span></div>'
            f'<h4>{s["name"]}</h4><div class="te">{s["name_te"]}</div>'
            f'<p>{short_html}</p>{elig_html}'
            f'<div class="bottom"><div class="vers">{badges}</div>{more}</div></div>'
        )
    st.markdown('<div class="cards">' + "".join(items) + '</div>', unsafe_allow_html=True)


def steps():
    st.markdown('<div id="how"></div>', unsafe_allow_html=True)
    st.markdown("### How it works")
    st.markdown('<div class="steps">' + "".join([
        '<div class="step"><div class="ic">🎙️</div><b>Ask by voice</b><br>Speak in Telugu or Hindi, or type.</div>',
        '<div class="step"><div class="ic">💬</div><b>Answer a few questions</b><br>Aasara asks only what it needs.</div>',
        '<div class="step"><div class="ic">🔊</div><b>Hear and verify</b><br>Spoken answer plus sources and documents.</div>',
    ]) + '</div>', unsafe_allow_html=True)


def footer():
    faq()
    fb = f'<p><a href="{FEEDBACK_URL}" target="_blank" rel="noopener">Send feedback</a></p>' if FEEDBACK_URL else ""
    st.markdown(
        '<div id="about"></div><div class="foot"><div class="cols">'
        '<div><h5>ఆసరా · Aasara</h5><p>A Telugu voice guide to government schemes and income tax. '
        'Built with Gnani Prisma (speech-to-text) and Timbre (text-to-speech) for the Great Indian AI Internship Challenge.</p></div>'
        '<div><h5>Data sources</h5><p>Facts come from official scheme pages where available. Each scheme shows its source and the date it was last checked. '
        'Telangana scheme details are still being verified.</p></div>'
        f'<div><h5>Please note</h5><p>Informational only. The relevant government department makes the final decision. '
        f'Always confirm on the source shown with each scheme.</p>{fb}</div>'
        '</div><div class="copy">© 2026 Aasara. Your answers stay in this browser session and are not stored.</div></div>',
        unsafe_allow_html=True,
    )


_VP = {
    "ready": ("Ready to listen", "Tap the mic below to speak."),
    "listening": ("Listening…", "Speak now. Tap stop when you finish."),
    "processing": ("Processing", "Understanding your question…"),
    "speaking": ("Speaking", "Playing the answer in Telugu."),
}
_SVG = 'viewBox="0 0 24 24" fill="none" stroke="#0b0c33" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
_ICON = {
    "ready": f'<svg {_SVG} width="30" height="30"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>',
    "listening": '<svg viewBox="0 0 24 24" width="26" height="26" fill="#0b0c33"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>',
    "processing": '<div class="spin"></div>',
    "speaking": f'<svg {_SVG} width="30" height="30"><path d="M4 9v6h4l5 4V5L8 9z"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/></svg>',
}


def audio_seconds(data):
    """Length of a WAV clip in seconds, or None if it cannot be read."""
    try:
        if isinstance(data, (bytes, bytearray)):
            with wave.open(io.BytesIO(bytes(data))) as w:
                return w.getnframes() / float(w.getframerate())
    except Exception:
        pass
    return None


def voice_panel(state="ready", slot=None, seconds=None):
    """Show the assistant state: ready, listening, processing or speaking.
    Waveform bars only appear while the app is really listening or speaking.
    For speaking, the panel returns to the ready look after the clip length."""
    state = state if state in _VP else "ready"
    title, hint = _VP[state]
    speaking = state == "speaking"
    T = min(max(seconds or 6.0, 2.0), 90.0)
    n_iter = max(1, math.ceil(T / 1.1))
    if state == "ready":
        vis = ""
    elif state == "processing":
        vis = '<div class="vp-vis dots">' + "".join(f'<i style="--d:{k * 0.2:.1f}s"></i>' for k in range(3)) + '</div>'
    else:
        extra = f"animation-iteration-count:{n_iter};" if speaking else ""
        vis = '<div class="vp-vis" aria-hidden="true">' + "".join(
            f'<i style="--h:{0.3 + 0.7 * abs(math.sin(k * 0.8) * math.cos(k * 0.31)):.2f};--d:{(k % 6) * 0.18:.2f}s;{extra}"></i>'
            for k in range(26)) + '</div>'
    text = f'<div class="t a"><b>{title}</b><span>{hint}</span></div>'
    icon = f'<div class="ic a">{_ICON[state]}</div>'
    if speaking:
        rt, rh = _VP["ready"]
        text += f'<div class="t b"><b>{rt}</b><span>{rh}</span></div>'
        icon += f'<div class="ic b">{_ICON["ready"]}</div>'
    attr = f' style="--T:{T:.1f}s"' if speaking else ""
    html = (
        f'<div class="vp vp-{state}" role="status" aria-live="polite"{attr}>'
        f'<div class="vp-mic"><span class="ring"></span><span class="ring r2"></span><div class="mic">{icon}</div></div>'
        f'<div class="vp-txt">{text}</div>{vis}</div>'
    )
    (slot or st).markdown(html, unsafe_allow_html=True)


def faq():
    qa = [
        ("Is Aasara an official government service?",
         "No. Aasara is an informational project. The relevant government department makes the final decision on every scheme, so always confirm on the source shown with each scheme."),
        ("Which schemes does Aasara cover?",
         "A small, checked list of central and Telangana schemes, shown in the Schemes section. If you ask about something else, Aasara says it does not know instead of guessing."),
        ("How current is the information?",
         "Every scheme shows the date its facts were last checked, with a link to the official source where one is available. Telangana scheme details are still being verified, so confirm them with your local office."),
        ("Which languages can I use?",
         "You can choose Telugu or Hindi as the language you speak, and you can type your question instead of speaking."),
        ("Are my answers stored?",
         "Aasara does not store your answers. Your voice is sent to Gnani’s speech service to be turned into text. That text is sent to Google’s Gemini model to understand your question and write the reply, and Gnani’s service turns the reply back into speech."),
        ("Can Aasara work out my income tax?",
         "It gives a simple estimate only. It is informational and not financial advice."),
    ]
    items = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in qa)
    st.markdown(f'<div class="faq" id="faq"><h3>Frequently asked questions</h3>{items}</div>', unsafe_allow_html=True)