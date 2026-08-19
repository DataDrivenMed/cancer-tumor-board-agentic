from __future__ import annotations

import streamlit as st


def inject_xai_theme() -> None:
    "Premium dark editorial theme optimized for clinical readability."
    st.markdown(
        r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

:root{
  --bg:#12100f; --bg2:#0e0c0b; --panel:#1b1917; --panel2:#171512; --panelhi:#211e1b;
  --line:#302c28; --line2:#26231f; --linehi:#413c36;
  --ink:#f5f1ea; --body:#d1c9bd; --muted:#9f978b; --faint:#756e64;
  --accent:#d9915f; --accent2:#e8b48a; --accent-ink:#f0c8a6;
  --mint:#6cc2a0; --mint-dim:#54a888; --warn:#e0b062; --danger:#e58a86; --verified:#6cc2a0;
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --r:14px; --rlg:18px; --rsm:9px;
}

html,body,[class*=css]{font-family:Inter,system-ui,"Helvetica Neue",Helvetica,Arial,sans-serif!important}
html{font-size:17px!important}
.stApp{background:var(--bg)!important;color:var(--ink)!important}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important}
[data-testid="stHeader"]{background:rgba(18,16,15,.95)!important;border-bottom:1px solid var(--line)!important}
.block-container{max-width:1320px!important;padding-top:1.25rem!important;padding-bottom:5rem!important}

h1,h2,h3{font-family:var(--serif)!important;color:var(--ink)!important;font-weight:500!important;letter-spacing:-.02em!important}
h1{font-size:3rem!important;line-height:1.04!important}
h2{font-size:2.1rem!important;line-height:1.12!important}
h3{font-size:1.55rem!important;line-height:1.18!important}
h4,h5,h6{color:var(--ink)!important;font-weight:650!important}
p,li,.stMarkdown{color:var(--body);font-size:1rem;line-height:1.65}
small{font-size:.88rem!important}
hr{border-color:var(--line)!important}

[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,.stCaption{color:var(--muted)!important;font-size:.9rem!important;line-height:1.5!important}
[data-testid="stWidgetLabel"] p,label{font-size:.96rem!important;color:var(--body)!important;font-weight:550!important}
code,pre,.stCode,[data-testid="stCodeBlock"]{font-family:var(--mono)!important;background:var(--panel2)!important;color:var(--accent2)!important}

.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button,[data-testid="stPageLink-NavLink"]{
  border-radius:12px!important;border:1px solid var(--linehi)!important;background:var(--panelhi)!important;
  color:var(--ink)!important;box-shadow:none!important;font-family:Inter!important;font-size:.98rem!important;
  font-weight:650!important;min-height:50px!important;padding:.76rem 1.15rem!important;transition:.15s ease!important
}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stPageLink-NavLink"]:hover{
  background:#29241f!important;border-color:var(--accent)!important;color:#fff!important
}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"]{
  background:var(--accent)!important;color:#231a13!important;border-color:var(--accent)!important
}
.stButton>button[kind="primary"]:hover,[data-testid="stFormSubmitButton"] button[kind="primary"]:hover{
  background:var(--accent2)!important;border-color:var(--accent2)!important;color:#231a13!important
}
.stButton>button:disabled{opacity:.5!important}

.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox [data-baseweb="select"]>div,
[data-testid="stFileUploader"] section,[data-testid="stChatInput"] textarea{
  background:var(--panel2)!important;color:var(--ink)!important;border:1px solid var(--linehi)!important;
  border-radius:11px!important;box-shadow:none!important;font-size:.98rem!important
}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus{
  border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(217,145,95,.2)!important
}
[data-testid="stFileUploader"] section{padding:1.1rem!important}
[data-testid="stFileUploaderDropzoneInstructions"] span,[data-testid="stFileUploaderDropzoneInstructions"] small{color:var(--body)!important}

[data-testid="stExpander"]{background:var(--panel)!important;border:1px solid var(--line)!important;border-radius:13px!important;box-shadow:none!important;overflow:hidden!important}
[data-testid="stExpander"] summary{background:var(--panelhi)!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p{color:var(--ink)!important;font-size:1rem!important;font-weight:650!important}
[data-testid="stExpanderDetails"]{background:var(--panel)!important}

.stTabs [data-baseweb="tab-list"]{border-bottom:1px solid var(--line)!important;gap:6px!important;background:transparent!important}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;font-weight:650!important;font-size:.98rem!important;padding:.8rem 1rem!important}
.stTabs [aria-selected="true"]{color:var(--accent2)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--accent)!important}

[data-testid="stSegmentedControl"]{background:var(--panel2)!important;border:1px solid var(--line)!important;border-radius:12px!important;padding:4px!important}
[data-testid="stSegmentedControl"] label{font-size:.9rem!important}
[data-testid="stAlert"]{background:var(--panel)!important;border:1px solid var(--linehi)!important;color:var(--body)!important;border-radius:13px!important;box-shadow:none!important}
[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:15px 17px}
[data-testid="stMetricLabel"] p{font-size:.86rem!important;color:var(--muted)!important}
[data-testid="stMetricValue"]{font-size:1.7rem!important;color:var(--ink)!important}

[data-testid="stDataFrame"],[data-testid="stJson"]{border-radius:12px!important;overflow:hidden!important;border:1px solid var(--line)!important}
[data-testid="stJson"]{background:var(--panel2)!important;color:var(--ink)!important}
[data-testid="stChatInput"]{background:var(--bg)!important;border-top:1px solid var(--line)!important}

.fx-kicker,.ws-eye,.eyebrow,.ov-kicker,.ov-label,.arch-hero .eyebrow,.sect-label,.fx-lbl,.fl,.decision-label,.dv-eyebrow{
  font-family:var(--mono)!important;text-transform:uppercase!important;letter-spacing:.13em!important;color:var(--muted)!important;
  font-weight:600!important;font-size:.72rem!important
}
.fx-card,.ov-card,.fx-node,.ov-node,.fx-status,.fx-program,.ws-card,.fact,.decision,.reason,.fx-decision-banner,.fx-answer,.arch-handoff,.arch-principle,.arch-compare>div,.ov-step,.ov-agent-item,.ov-safeguard,.ov-preview,.channel,.agent,.card,.prog,.principle,.comp{
  background:var(--panel)!important;border:1px solid var(--line)!important;color:var(--ink)!important;box-shadow:none!important;border-radius:var(--r)!important
}
.fx-thirty,.fx-core,.decision{
  background:var(--panelhi)!important;border:1px solid var(--line)!important;border-left:3px solid var(--accent)!important;color:var(--ink)!important;border-radius:var(--rlg)!important
}
.source{color:var(--mint)!important;font-weight:600!important;font-size:.82rem!important}
.chip,.fx-source-chip,.ov-badge,.fx-synthetic{
  border-radius:999px!important;font-weight:600!important;font-family:var(--mono)!important;font-size:.69rem!important;
  text-transform:uppercase!important;letter-spacing:.05em!important
}
.chip.ok,.ok{background:rgba(108,194,160,.12)!important;color:var(--mint)!important;border:1px solid rgba(108,194,160,.28)!important}
.chip.warn,.warn{background:rgba(224,176,98,.12)!important;color:var(--warn)!important;border:1px solid rgba(224,176,98,.28)!important}
.chip.bad,.bad{background:rgba(229,138,134,.12)!important;color:var(--danger)!important;border:1px solid rgba(229,138,134,.28)!important}
.chip.neutral,.neutral,.chip.off{background:var(--panel2)!important;color:var(--muted)!important;border:1px solid var(--line2)!important}

[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--line)!important;min-width:290px!important;max-width:290px!important}
[data-testid="stSidebarNav"]{display:none!important}
[data-testid="stSidebarContent"]{padding:19px 16px 24px!important}
.fx-side-brand{display:flex;align-items:center;gap:11px;padding:4px 3px 16px;border-bottom:1px solid var(--line);margin-bottom:14px;flex-wrap:wrap}
.fx-side-mark{width:38px;height:38px;border-radius:10px;background:var(--accent);display:grid;place-items:center;color:#231a13;font:800 .66rem/1 var(--mono)}
.fx-side-name{font-family:var(--serif);font-size:1.1rem;color:var(--ink);font-weight:500}
.fx-side-sub{font-size:.78rem;color:var(--muted);margin-top:2px}
.fx-side-label{font:600 .67rem/14px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:18px 3px 8px}

.fx-footer,.footer{border-top:1px solid var(--line)!important;color:var(--muted)!important;margin-top:38px;padding:18px 0}
.fx-footer{display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:.78rem!important}
.verified{display:inline-flex;align-items:center;gap:5px;font:600 .68rem/1 var(--mono);color:var(--mint);text-transform:uppercase;letter-spacing:.05em}
.verified.review-needed{color:var(--warn)}

@media(max-width:1100px){
  .block-container{max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important}
  [data-testid="stSidebar"]{min-width:250px!important;max-width:250px!important}
}
</style>
""",
        unsafe_allow_html=True,
    )
