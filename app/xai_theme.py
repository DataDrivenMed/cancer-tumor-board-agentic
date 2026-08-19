from __future__ import annotations

import streamlit as st


def inject_xai_theme() -> None:
    """Midnight Editorial, the single authoritative theme for every page."""
    st.markdown(
        r'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');
:root{
  --bg:#12100f; --bg2:#0e0c0b; --panel:#1b1917; --panel2:#171512; --panelhi:#211e1b;
  --line:#302c28; --line2:#26231f; --linehi:#413c36;
  --ink:#f5f1ea; --body:#c3bcb0; --muted:#8d867a; --faint:#6a635a;
  --accent:#d9915f; --accent2:#e8b48a; --accent-ink:#f0c8a6;
  --mint:#6cc2a0; --mint-dim:#54a888; --warn:#e0b062; --danger:#e58a86; --verified:#6cc2a0;
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --x-canvas:#12100f; --x-canvas-soft:#171512; --x-card:#1b1917; --x-card2:#171512;
  --x-mid:#302c28; --x-hair:#302c28; --x-hair-soft:#26231f; --x-hair-strong:#413c36;
  --x-ink:#f5f1ea; --x-body:#c3bcb0; --x-muted:#8d867a; --x-muted-soft:#6a635a;
  --x-primary:#d9915f; --x-primary-active:#e8b48a; --x-thinking:#d9915f; --x-grep:#6cc2a0;
  --x-read:#d9915f; --x-edit:#e8b48a; --x-done:#6cc2a0; --x-green:#6cc2a0; --x-danger:#e58a86; --x-amber:#e0b062;
  --r:14px; --rlg:18px; --rsm:9px;
}
html,body,[class*=css]{font-family:Inter,system-ui,"Helvetica Neue",Helvetica,Arial,sans-serif!important}
.stApp{background:var(--bg)!important;color:var(--ink)!important}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important}
[data-testid="stHeader"]{background:rgba(18,16,15,.92)!important;border-bottom:1px solid var(--line)!important}
.block-container{max-width:1200px!important;padding-top:1.1rem!important;padding-bottom:4.5rem!important}
h1,h2,h3{font-family:var(--serif)!important;color:var(--ink)!important;font-weight:500!important;letter-spacing:-.02em!important}
h4,h5,h6{color:var(--ink)!important;font-weight:600!important}p,li{color:var(--body)}hr{border-color:var(--line)!important}
code,pre,.stCode,[data-testid="stCodeBlock"]{font-family:var(--mono)!important;background:var(--panel2)!important;color:var(--accent2)!important}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="stPageLink-NavLink"]{border-radius:11px!important;border:1px solid var(--line)!important;background:var(--panel)!important;color:var(--ink)!important;box-shadow:none!important;font-family:Inter!important;font-size:14px!important;font-weight:600!important;min-height:42px!important;padding:.62rem 1.1rem!important}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stPageLink-NavLink"]:hover{background:var(--panelhi)!important;border-color:var(--accent)!important;color:#fff!important;transform:none!important}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"]{background:var(--accent)!important;color:#231a13!important;border-color:var(--accent)!important}
.stButton>button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] button[kind="primary"]:hover{background:var(--accent2)!important;border-color:var(--accent2)!important;color:#231a13!important}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox [data-baseweb="select"]>div,[data-testid="stFileUploader"] section{background:var(--panel2)!important;color:var(--ink)!important;border:1px solid var(--line)!important;border-radius:9px!important;box-shadow:none!important}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(217,145,95,.2)!important}
[data-testid="stExpander"]{background:var(--panel)!important;border:1px solid var(--line)!important;border-radius:12px!important;box-shadow:none!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p{color:var(--ink)!important;font-size:14.5px!important}
.stTabs [data-baseweb="tab-list"]{border-bottom:1px solid var(--line)!important;gap:4px!important;background:transparent!important}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;font-weight:600!important;font-size:13.5px!important;padding:.65rem .9rem!important}.stTabs [aria-selected="true"]{color:var(--accent2)!important}.stTabs [data-baseweb="tab-highlight"]{background:var(--accent)!important}
[data-testid="stAlert"]{background:var(--panel)!important;border:1px solid var(--line)!important;color:var(--body)!important;border-radius:12px!important;box-shadow:none!important}
[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.fx-kicker,.ws-eye,.eyebrow,.ov-kicker,.ov-label,.arch-hero .eyebrow,.sect-label,.fx-lbl,.fl,.decision-label,.dv-eyebrow{font-family:var(--mono)!important;text-transform:uppercase!important;letter-spacing:.13em!important;color:var(--muted)!important;font-weight:600!important;font-size:11px!important}
.fx-hero h1,.ov-hero h1,.arch-hero h1,.ws-hero h1,.hero h2,.arch-hero h2,.fx-section,.ov-section,.arch-section,.ws-section,.sect-h,.decision-title,.d-title,.fx-thirty-title,.fx-core h2,.fx-decision-banner h2{font-family:var(--serif)!important;color:var(--ink)!important;font-weight:500!important;letter-spacing:-.02em!important}
.fx-card,.ov-card,.fx-node,.ov-node,.fx-status,.fx-program,.ws-card,.fact,.decision,.reason,.fx-decision-banner,.fx-answer,.arch-handoff,.arch-principle,.arch-compare>div,.ov-step,.ov-agent-item,.ov-safeguard,.ov-preview,.channel,.agent,.card,.prog,.principle,.comp{background:var(--panel)!important;border:1px solid var(--line)!important;color:var(--ink)!important;box-shadow:none!important;border-radius:var(--r)!important}
.fx-thirty,.fx-core,.decision{background:var(--panelhi)!important;border:1px solid var(--line)!important;border-left:3px solid var(--accent)!important;color:var(--ink)!important;border-radius:var(--rlg)!important}
.source{color:var(--mint)!important;font-weight:600!important;font-size:12px!important}
.chip,.fx-source-chip,.ov-badge,.fx-synthetic{border-radius:999px!important;font-weight:600!important;font-family:var(--mono)!important;font-size:10.5px!important;text-transform:uppercase!important;letter-spacing:.05em!important}
.chip.ok,.ok{background:rgba(108,194,160,.12)!important;color:var(--mint)!important;border:1px solid rgba(108,194,160,.28)!important}.chip.warn,.warn{background:rgba(224,176,98,.12)!important;color:var(--warn)!important;border:1px solid rgba(224,176,98,.28)!important}.chip.bad,.bad{background:rgba(229,138,134,.12)!important;color:var(--danger)!important;border:1px solid rgba(229,138,134,.28)!important}.chip.neutral,.neutral,.chip.off{background:var(--panel2)!important;color:var(--muted)!important;border:1px solid var(--line2)!important}
.fx-missing,.ws-alert{background:rgba(224,176,98,.08)!important;border:1px solid rgba(224,176,98,.3)!important;color:var(--warn)!important;border-radius:var(--r)!important}
.ws-call,.fx-chat-note,.arch-callout,.callout{background:var(--panel2)!important;border:1px solid var(--line2)!important;color:var(--body)!important;border-radius:var(--r)!important}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--line)!important;min-width:270px!important;max-width:270px!important}[data-testid="stSidebarNav"]{display:none!important}[data-testid="stSidebarContent"]{padding:17px 15px 22px!important}
.fx-side-brand{display:flex;align-items:center;gap:10px;padding:4px 3px 15px;border-bottom:1px solid var(--line);margin-bottom:14px;flex-wrap:wrap}.fx-side-mark{width:34px;height:34px;border-radius:9px;background:var(--accent);display:grid;place-items:center;color:#231a13;font:800 10px/1 var(--mono)}.fx-side-name{font-family:var(--serif);font-size:16px;color:var(--ink);font-weight:500}.fx-side-sub{font-size:12px;color:var(--muted);margin-top:2px}.fx-side-label{font:600 10px/14px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:16px 3px 7px}
.fx-footer,.footer{border-top:1px solid var(--line)!important;color:var(--muted)!important;margin-top:34px;padding:16px 0}.fx-footer{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:12px!important}
.verified{display:inline-flex;align-items:center;gap:5px;font:600 10px/1 var(--mono);color:var(--mint);text-transform:uppercase;letter-spacing:.05em}.verified.review-needed{color:var(--warn)}
@media(max-width:1024px){.block-container{max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important}[data-testid="stSidebar"]{min-width:240px!important;max-width:240px!important}}
</style>
''', unsafe_allow_html=True)
