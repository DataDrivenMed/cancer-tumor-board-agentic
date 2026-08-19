from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Agentic Workspace · Tumor Board Intelligence",
    page_icon="TB",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Design system translated from the approved HTML mockup.
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap');

:root{
  --bg:#12100f;--bg2:#0e0c0b;--panel:#1b1917;--panel2:#171512;--panelhi:#211e1b;
  --line:#302c28;--line2:#26231f;--ink:#f5f1ea;--body:#c3bcb0;--muted:#8d867a;--faint:#6a635a;
  --accent:#d9915f;--accent2:#e8b48a;--mint:#6cc2a0;--warn:#e0b062;--danger:#e58a86;
  --serif:'Newsreader',Georgia,serif;--mono:'JetBrains Mono',monospace;
}

html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif;}
.stApp{background:var(--bg);color:var(--ink);}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:var(--bg2);border-right:1px solid var(--line);}
[data-testid="stSidebar"] > div:first-child{padding-top:1rem;}
.block-container{max-width:960px;padding:1.35rem 2rem 6rem;}

/* Hide default multipage navigation while keeping the sidebar as the workup rail. */
[data-testid="stSidebarNav"]{display:none;}

.rail-brand{display:flex;gap:10px;align-items:center;padding:2px 2px 16px;border-bottom:1px solid var(--line);margin-bottom:18px}
.rail-mark{width:34px;height:34px;border-radius:9px;background:var(--accent);display:grid;place-items:center;color:#231a13;font:800 10px/1 var(--mono)}
.rail-name{font-family:var(--serif);font-size:17px;font-weight:500;color:var(--ink)}
.rail-name small{display:block;font-family:Inter;font-size:10.5px;color:var(--muted);margin-top:2px}
.rail-label{font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:4px 2px 10px}
.prog{display:flex;flex-direction:column;gap:3px;margin-bottom:8px}
.pstep{display:flex;gap:10px;align-items:center;padding:9px;border-radius:8px;font-size:13px}
.pstep .pn{width:22px;height:22px;flex:none;border-radius:6px;display:grid;place-items:center;font:700 9px/1 var(--mono);background:var(--panel);border:1px solid var(--line);color:var(--muted)}
.pstep .pl{color:var(--muted);font-weight:500}.pstep.done .pn{background:rgba(108,194,160,.14);border-color:var(--mint);color:var(--mint)}
.pstep.done .pl{color:var(--body)}.pstep.active{background:var(--panelhi)}.pstep.active .pn{background:var(--accent);border-color:var(--accent);color:#231a13}.pstep.active .pl{color:#fff;font-weight:600}
.rail-note{font-size:10.5px;color:var(--faint);line-height:1.55;padding:0 2px;margin:9px 0 20px}

.turn{display:flex;gap:12px;margin:0 0 16px;animation:rise .28s ease}
@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.av{width:30px;height:30px;flex:none;border-radius:8px;display:grid;place-items:center;font:700 10px/1 var(--mono);margin-top:1px}
.av.agent{background:var(--panelhi);border:1px solid var(--line);color:var(--accent2)}.av.user{background:var(--accent);color:#231a13}
.bubble{flex:1;min-width:0}.who{font:600 11px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:7px}
.atext{font-size:14px;color:var(--body);line-height:1.6}.atext b{color:var(--ink);font-weight:600}.umsg{background:var(--panelhi);border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-size:14px;color:var(--ink)}

.activity{display:flex;flex-direction:column;gap:2px;margin:9px 0}.act{display:flex;gap:9px;align-items:center;padding:5px 0;font-size:13px;color:var(--body)}
.act .ic{width:18px;height:18px;flex:none;border-radius:50%;display:grid;place-items:center;font-size:9px;font-weight:700;background:rgba(108,194,160,.15);border:1px solid var(--mint);color:var(--mint)}
.act .sub{color:var(--mint);font-size:12px;margin-left:5px}

[data-testid="stExpander"]{background:var(--panel);border:1px solid var(--line)!important;border-radius:12px!important;overflow:hidden;margin:9px 0 13px}
[data-testid="stExpander"] summary{background:var(--panel2);padding:.72rem .9rem!important;color:var(--accent2)!important}
[data-testid="stExpander"] summary p{font:600 10.5px/1 var(--mono)!important;text-transform:uppercase;letter-spacing:.07em}
[data-testid="stExpanderDetails"]{padding:.25rem .85rem .85rem!important}

.facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px}
.fct{background:var(--panel2);border:1px solid var(--line2);border-radius:9px;padding:11px}.fct .k{font:600 9px/1.2 var(--mono);text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}
.fct .v{font-size:14px;font-weight:600;color:var(--ink);margin-top:6px}.fct .s{font:600 9px/1 var(--mono);color:var(--mint);text-transform:uppercase;margin-top:6px;display:inline-block}

.chan{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;padding:11px 12px;border:1px solid var(--line2);border-radius:10px;background:var(--panel2);margin-bottom:8px}
.chan-t{font-size:13.5px;font-weight:600;color:var(--ink)}.chan-d{font-size:12px;color:var(--muted);line-height:1.45;margin-top:3px}
.chip{font:600 9.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.04em;padding:5px 9px;border-radius:999px;white-space:nowrap;flex:none}
.chip.ok{color:var(--mint);background:rgba(108,194,160,.1);border:1px solid rgba(108,194,160,.25)}.chip.warn{color:var(--warn);background:rgba(224,176,98,.1);border:1px solid rgba(224,176,98,.25)}.chip.off{color:var(--faint);background:var(--panel);border:1px solid var(--line2)}

.rec{padding:11px 0;border-bottom:1px solid var(--line2)}.rec:last-child{border-bottom:0}.rec-t{font-size:13.5px;font-weight:600;color:var(--ink)}.rec-m{font-size:11.5px;color:var(--muted);margin-top:3px}.rec-x{font-size:12.5px;color:var(--body);line-height:1.5;margin-top:6px}.rec-note{font-size:11.5px;color:var(--warn);margin-top:5px}

.gate{background:linear-gradient(180deg,var(--panelhi),var(--panel));border:1px solid var(--accent);border-radius:13px;padding:16px 17px;margin:10px 0 15px}.gate-tag{font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--accent2);margin-bottom:10px}.gate-q{font-size:14.5px;color:var(--ink);font-weight:500;line-height:1.4;margin-bottom:5px}.gate-why{font-size:12px;color:var(--muted);line-height:1.5}

.artifact{background:var(--panel);border:1px solid var(--line);border-radius:13px;margin-top:9px;overflow:hidden}.art-head{background:var(--panel2);padding:11px 14px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}.art-title{font:600 10.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.art-open{font:600 11px/1 Inter;color:var(--accent2)}.art-body{padding:15px 16px}.art-decision{font-family:var(--serif);font-size:22px;font-weight:500;line-height:1.2;color:var(--ink);margin-bottom:7px}.art-sum{font-size:13px;color:var(--body);line-height:1.55}

.stButton>button{border-radius:9px!important;border:1px solid var(--line)!important;background:var(--panel)!important;color:var(--ink)!important;font-size:12.5px!important;font-weight:600!important;min-height:42px!important;box-shadow:none!important}
.stButton>button:hover{border-color:var(--accent)!important;color:#fff!important}.stButton>button[kind="primary"]{background:var(--accent)!important;border-color:var(--accent)!important;color:#231a13!important}
[data-testid="stChatInput"]{background:var(--panel)!important;border:1px solid var(--line)!important;border-radius:12px!important}.stChatInputContainer{background:var(--bg)!important}
[data-testid="stPageLink-NavLink"]{background:transparent!important;border:0!important;color:var(--body)!important;padding:.45rem .25rem!important;font-size:13px!important}
[data-testid="stPageLink-NavLink"]:hover{background:var(--panel)!important;color:var(--ink)!important;border-radius:8px!important}

.demo-note{font-size:10.5px;color:var(--faint);text-align:center;margin:12px 0 2px}
@media(max-width:760px){.facts{grid-template-columns:1fr}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""",
    unsafe_allow_html=True,
)

STAGES = [
    ("intake", "Case intake"),
    ("review", "Case review"),
    ("evidence", "Evidence"),
    ("analysis", "Analysis"),
    ("brief", "Decision brief"),
]

if "agentic_demo_step" not in st.session_state:
    st.session_state.agentic_demo_step = 0

step = int(st.session_state.agentic_demo_step)


def set_step(value: int) -> None:
    st.session_state.agentic_demo_step = max(0, min(value, 5))
    st.rerun()


def turn(who: str, role: str, body: str, user: bool = False) -> None:
    cls = "user" if user else "agent"
    st.markdown(
        f'<div class="turn"><div class="av {cls}">{who}</div><div class="bubble">'
        f'<div class="who">{role}</div><div class="{("umsg" if user else "atext")}">{body}</div></div></div>',
        unsafe_allow_html=True,
    )


# Sidebar workup rail.
with st.sidebar:
    st.markdown(
        '<div class="rail-brand"><div class="rail-mark">TB</div><div class="rail-name">Tumor Board<small>Agentic workup</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="rail-label">This workup</div>', unsafe_allow_html=True)
    rows = []
    active_stage = min(max(step, 1), 5) if step else 0
    for i, (_, label) in enumerate(STAGES, start=1):
        cls = "pstep"
        number = str(i)
        if step > i:
            cls += " done"
            number = "✓"
        elif active_stage == i:
            cls += " active"
        rows.append(f'<div class="{cls}"><span class="pn">{number}</span><span class="pl">{label}</span></div>')
    st.markdown('<div class="prog">' + ''.join(rows) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="rail-note">The agent moves through these. You watch, and answer when it asks. Full detail opens in the conversation as it reaches each step.</div>', unsafe_allow_html=True)
    st.markdown('<div class="rail-label">Reference</div>', unsafe_allow_html=True)
    st.page_link("app/pages/03_Architecture.py", label="◇  Architecture", use_container_width=True)
    st.page_link("app/pages/01_Validation.py", label="◇  Validation & scope", use_container_width=True)
    st.page_link("app/pages/02_About.py", label="◇  About", use_container_width=True)
    st.markdown('<div class="rail-label" style="margin-top:18px">Existing workflow</div>', unsafe_allow_html=True)
    st.page_link("app/pages/00_Clinical_Workspace.py", label="Open Clinical Workspace", use_container_width=True)

# Step 0.
turn("TB", "Tumor Board Agent", "I'll run a full tumor-board workup and pause whenever I need your judgment. To start:")

if step == 0:
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("Use the synthetic demo case", type="primary", use_container_width=True):
            set_step(1)
        st.caption("68F relapsed AML, FLT3-ITD · ready to run")
    with c2:
        if st.button("Paste or upload a case", use_container_width=True):
            st.switch_page("app/pages/00_Clinical_Workspace.py")
        st.caption("Use the existing provenance-aware clinical intake")

# Step 1: case intake and structured review.
if step >= 1:
    turn("You", "You", "Use the synthetic demo case.", user=True)
    turn("TB", "Tumor Board Agent · Case intake", "Loaded and structured. Here's what I extracted, with the source attached to every fact. Open it to check the full case.")
    with st.expander("Case review · structured facts", expanded=True):
        st.markdown(
            """
<div class="facts">
  <div class="fct"><div class="k">Diagnosis</div><div class="v">Acute myeloid leukemia</div><span class="s">✓ source traced</span></div>
  <div class="fct"><div class="k">Disease state</div><div class="v">Relapsed</div><span class="s">✓ source traced</span></div>
  <div class="fct"><div class="k">Patient</div><div class="v">68 F · ECOG 1</div><span class="s">✓ source traced</span></div>
  <div class="fct"><div class="k">Molecular</div><div class="v">FLT3-ITD · VAF 31%</div><span class="s">✓ source traced</span></div>
  <div class="fct"><div class="k">Prior therapy</div><div class="v">Induction A · Salvage B</div><span class="s">✓ source traced</span></div>
  <div class="fct"><div class="k">Board question</div><div class="v">Next-line strategy for tumor board</div><span class="s">✓ source traced</span></div>
</div>
""",
            unsafe_allow_html=True,
        )
    if step == 1:
        if st.button("Continue case review", type="primary", use_container_width=True):
            set_step(2)

# Step 2: human guardrail.
if step >= 2:
    st.markdown(
        '<div class="turn"><div class="av agent">TB</div><div class="bubble"><div class="who">Tumor Board Agent · Case review</div>'
        '<div class="activity"><div class="act"><span class="ic">✓</span>Integrity check <span class="sub">no contradictions, provenance intact</span></div>'
        '<div class="act"><span class="ic">✓</span>Missing-info scan <span class="sub">1 decision-critical gap found</span></div></div>'
        '<div class="atext">One gap changes the recommendation, so I need your call before evidence review.</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="gate"><div class="gate-tag">● &nbsp; Guardrail · needs your call</div>'
        '<div class="gate-q">Is this patient a transplant candidate?</div>'
        '<div class="gate-why">Not in the record. Transplant-eligible leans toward FLT3-inhibitor bridging; not eligible leans toward trial or palliative-intent. I will not assume it.</div></div>',
        unsafe_allow_html=True,
    )
    if step == 2:
        g1, g2, g3 = st.columns(3, gap="small")
        with g1:
            if st.button("Transplant candidate", type="primary", use_container_width=True):
                set_step(3)
        with g2:
            if st.button("Not a candidate", use_container_width=True):
                set_step(3)
        with g3:
            if st.button("Unknown · flag it", use_container_width=True):
                set_step(3)

# Step 3: evidence.
if step >= 3:
    turn("You", "You", "Transplant candidate.", user=True)
    turn("TB", "Tumor Board Agent · Evidence", "Good. That keeps bridging in play. I pulled each evidence channel separately. Here's channel readiness:")
    with st.expander("Evidence channel readiness", expanded=True):
        st.markdown(
            """
<div class="chan"><div><div class="chan-t">Guidelines · European LeukemiaNet</div><div class="chan-d">Relapsed FLT3-ITD pathway matched by explicit label.</div></div><span class="chip ok">Ready</span></div>
<div class="chan"><div><div class="chan-t">Molecular · CIViC</div><div class="chan-d">3 candidate records retrieved · need your approval.</div></div><span class="chip warn">Needs review</span></div>
<div class="chan"><div><div class="chan-t">Safety · FDA labeling</div><div class="chan-d">2 label sections retrieved for candidate therapies.</div></div><span class="chip warn">Needs review</span></div>
<div class="chan"><div><div class="chan-t">Clinical trials</div><div class="chan-d">2 candidate matches · eligibility not established.</div></div><span class="chip ok">Ready</span></div>
<div class="chan"><div><div class="chan-t">Literature</div><div class="chan-d">Not run for this route.</div></div><span class="chip off">Not run</span></div>
""",
            unsafe_allow_html=True,
        )
    with st.expander("Molecular evidence · CIViC candidates"):
        st.markdown(
            """
<div class="rec"><div class="rec-t">EID-1042 · FLT3 · Actionable</div><div class="rec-m">Gilteritinib · CIViC Accepted · relapsed AML</div><div class="rec-x">FLT3-ITD confers sensitivity to gilteritinib in relapsed/refractory AML.</div></div>
<div class="rec"><div class="rec-t">EID-2087 · FLT3 · Actionable</div><div class="rec-m">Midostaurin · CIViC Accepted · newly diagnosed</div><div class="rec-x">FLT3-mutated AML benefits from midostaurin with induction.</div><div class="rec-note">Evidence is newly diagnosed. Read before applying it to this relapsed case.</div></div>
<div class="rec"><div class="rec-t">EID-3310 · FLT3 · Prognostic</div><div class="rec-m">CIViC Accepted · relapsed</div><div class="rec-x">High ITD allelic ratio associated with adverse prognosis.</div></div>
""",
            unsafe_allow_html=True,
        )
    with st.expander("Safety source evidence · FDA labeling"):
        st.markdown(
            """
<div class="rec"><div class="rec-t">Gilteritinib · label §5</div><div class="rec-m">Warnings: differentiation syndrome, QT prolongation, PRES</div><div class="rec-x">Monitor ECG; hold for QTc prolongation per label thresholds.</div></div>
<div class="rec"><div class="rec-t">Gilteritinib · label §2</div><div class="rec-m">Dosing reference</div><div class="rec-x">Standard label dosing; source shown for board reference, not a patient-specific dose.</div></div>
""",
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="gate"><div class="gate-tag">● &nbsp; Guardrail · approve evidence</div>'
        '<div class="gate-q">Approve records you have reviewed to continue.</div>'
        '<div class="gate-why">Retrieval finds candidates, not answers. Human evidence attestation remains explicit.</div></div>',
        unsafe_allow_html=True,
    )
    if step == 3:
        e1, e2 = st.columns(2, gap="small")
        with e1:
            if st.button("Approve gilteritinib only", type="primary", use_container_width=True):
                set_step(4)
        with e2:
            if st.button("Approve all reviewed", use_container_width=True):
                set_step(4)

# Step 4: challenge review.
if step >= 4:
    turn("TB", "Tumor Board Agent · Analysis", "Approved. Before synthesis, I ran the challenge review, attacking my own evidence stack.")
    with st.expander("Challenge review findings", expanded=True):
        st.markdown(
            """
<div class="chan"><div><div class="chan-t">Conflicts checked</div><div class="chan-d">No guideline-vs-molecular conflict for the bridging strategy.</div></div><span class="chip ok">Clear</span></div>
<div class="chan"><div><div class="chan-t">Unsupported leaps</div><div class="chan-d">Midostaurin evidence flagged as newly diagnosed, not relapsed. Excluded from the recommendation.</div></div><span class="chip warn">1 flagged</span></div>
<div class="chan"><div><div class="chan-t">Blocking gaps</div><div class="chan-d">None. Transplant eligibility was resolved earlier.</div></div><span class="chip ok">Clear</span></div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('<div class="activity"><div class="act"><span class="ic">✓</span>Consensus <span class="sub">held · disagreement preserved</span></div></div>', unsafe_allow_html=True)
    if step == 4:
        if st.button("Build decision brief", type="primary", use_container_width=True):
            set_step(5)

# Step 5: final artifact.
if step >= 5:
    turn("TB", "Tumor Board Agent · Decision brief", "Here's the brief. It held together, with one limitation worth naming at board.")
    st.markdown(
        """
<div class="artifact">
  <div class="art-head"><span class="art-title">Decision brief · SYN-AML-001</span><span class="art-open">Governed demo</span></div>
  <div class="art-body"><div class="art-decision">Multiple reasonable options · FLT3-directed therapy leads</div>
  <div class="art-sum">Relapsed FLT3-ITD AML, transplant-eligible. Guideline and approved molecular evidence support gilteritinib bridging to transplant. One nonblocking limitation: midostaurin evidence is newly diagnosed only and is excluded from the recommendation.</div></div>
</div>
""",
        unsafe_allow_html=True,
    )
    turn("TB", "Tumor Board Agent", "Want the PDF for board, or should I dig into the two trial matches?")

st.markdown('<div class="demo-note">Interactive design prototype · the existing Clinical Workspace remains available for the current provenance-aware workflow.</div>', unsafe_allow_html=True)

c_reset, c_live = st.columns([1, 2], gap="small")
with c_reset:
    if st.button("Reset demo", use_container_width=True):
        set_step(0)
with c_live:
    if st.button("Open current Clinical Workspace", use_container_width=True):
        st.switch_page("app/pages/00_Clinical_Workspace.py")

st.chat_input("Reply, ask a follow-up, or start a new case…", disabled=True)
