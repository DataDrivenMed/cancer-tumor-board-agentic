from __future__ import annotations

import streamlit as st


STAGES = [
    ("intake", "Case intake"),
    ("review", "Case review"),
    ("evidence", "Evidence"),
    ("analysis", "Analysis"),
    ("brief", "Decision brief"),
]


def _css() -> None:
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
html,body,[class*=css]{font-family:Inter,system-ui,sans-serif!important}
.stApp,[data-testid=stAppViewContainer],[data-testid=stMain]{background:var(--bg)!important;color:var(--ink)!important}
[data-testid=stHeader]{background:rgba(18,16,15,.94)!important;border-bottom:1px solid var(--line)!important}
[data-testid=stSidebar]{background:var(--bg2)!important;border-right:1px solid var(--line)!important;min-width:292px!important;max-width:292px!important}
[data-testid=stSidebarNav]{display:none!important}
[data-testid=stSidebarContent]{padding:18px 14px 24px!important}
.block-container{max-width:1040px!important;padding:1.7rem 2rem 6rem!important}
.rail-brand{display:flex;gap:10px;align-items:center;padding:3px 2px 17px;border-bottom:1px solid var(--line);margin-bottom:19px}
.rail-mark{width:34px;height:34px;border-radius:9px;background:var(--accent);display:grid;place-items:center;color:#231a13;font:800 10px/1 var(--mono)}
.rail-name{font-family:var(--serif);font-size:17px;font-weight:500;color:var(--ink)}
.rail-name small{display:block;font-family:Inter;font-size:10.5px;color:var(--muted);margin-top:2px}
.rail-label{font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:4px 2px 10px}
.prog{display:flex;flex-direction:column;gap:3px;margin-bottom:8px}.pstep{display:flex;gap:10px;align-items:center;padding:9px;border-radius:8px;font-size:13px}
.pstep .pn{width:22px;height:22px;flex:none;border-radius:6px;display:grid;place-items:center;font:700 9px/1 var(--mono);background:var(--panel);border:1px solid var(--line);color:var(--muted)}
.pstep .pl{color:var(--muted);font-weight:500}.pstep.done .pn{background:rgba(108,194,160,.14);border-color:var(--mint);color:var(--mint)}
.pstep.done .pl{color:var(--body)}.pstep.active{background:var(--panelhi)}.pstep.active .pn{background:var(--accent);border-color:var(--accent);color:#231a13}.pstep.active .pl{color:#fff;font-weight:600}
.rail-note{font-size:10.5px;color:var(--faint);line-height:1.55;padding:0 2px;margin:9px 0 20px}
.ref-row{padding:7px 3px;color:var(--body);font-size:12.5px}.ref-row span{color:var(--muted);margin-right:8px}
.hero{padding:5px 0 18px;border-bottom:1px solid var(--line);margin-bottom:22px}.hero-k{font:600 10px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent2);margin-bottom:9px}.hero h1{font-family:var(--serif);font-weight:500;font-size:34px;letter-spacing:-.02em;margin:0;color:var(--ink)}.hero p{font-size:13.5px;line-height:1.6;color:var(--muted);max-width:760px;margin:8px 0 0}
.turn{display:flex;gap:12px;margin:0 0 16px}.av{width:30px;height:30px;flex:none;border-radius:8px;display:grid;place-items:center;font:700 10px/1 var(--mono);margin-top:1px}.av.agent{background:var(--panelhi);border:1px solid var(--line);color:var(--accent2)}.av.user{background:var(--accent);color:#231a13}
.bubble{flex:1;min-width:0}.who{font:600 11px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:7px}.atext{font-size:14px;color:var(--body);line-height:1.6}.umsg{background:var(--panelhi);border:1px solid var(--line);border-radius:12px;padding:12px 14px;font-size:14px;color:var(--ink)}
.activity{display:flex;flex-direction:column;gap:2px;margin:9px 0}.act{display:flex;gap:9px;align-items:center;padding:5px 0;font-size:13px;color:var(--body)}.act .ic{width:18px;height:18px;flex:none;border-radius:50%;display:grid;place-items:center;font-size:9px;font-weight:700;background:rgba(108,194,160,.15);border:1px solid var(--mint);color:var(--mint)}.act .sub{color:var(--mint);font-size:12px;margin-left:5px}
[data-testid=stExpander]{background:var(--panel)!important;border:1px solid var(--line)!important;border-radius:12px!important;overflow:hidden;margin:9px 0 13px!important}[data-testid=stExpander] summary{background:var(--panel2)!important;color:var(--accent2)!important}[data-testid=stExpander] summary p{font:600 10.5px/1.1 var(--mono)!important;text-transform:uppercase;letter-spacing:.07em!important;color:var(--accent2)!important}
.facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:8px}.fct{background:var(--panel2);border:1px solid var(--line2);border-radius:9px;padding:11px}.fct .k{font:600 9px/1.2 var(--mono);text-transform:uppercase;letter-spacing:.07em;color:var(--muted)}.fct .v{font-size:14px;font-weight:600;color:var(--ink);margin-top:6px}.fct .s{font:600 9px/1 var(--mono);color:var(--mint);text-transform:uppercase;margin-top:6px;display:inline-block}
.chan{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;padding:11px 12px;border:1px solid var(--line2);border-radius:10px;background:var(--panel2);margin-bottom:8px}.chan-t{font-size:13.5px;font-weight:600;color:var(--ink)}.chan-d{font-size:12px;color:var(--muted);line-height:1.45;margin-top:3px}.chip{font:600 9.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.04em;padding:5px 9px;border-radius:999px;white-space:nowrap;flex:none}.chip.ok{color:var(--mint);background:rgba(108,194,160,.1);border:1px solid rgba(108,194,160,.25)}.chip.warn{color:var(--warn);background:rgba(224,176,98,.1);border:1px solid rgba(224,176,98,.25)}.chip.off{color:var(--faint);background:var(--panel);border:1px solid var(--line2)}
.rec{padding:11px 0;border-bottom:1px solid var(--line2)}.rec:last-child{border-bottom:0}.rec-t{font-size:13.5px;font-weight:600;color:var(--ink)}.rec-m{font-size:11.5px;color:var(--muted);margin-top:3px}.rec-x{font-size:12.5px;color:var(--body);line-height:1.5;margin-top:6px}.rec-note{font-size:11.5px;color:var(--warn);margin-top:5px}
.gate{background:linear-gradient(180deg,var(--panelhi),var(--panel));border:1px solid var(--accent);border-radius:13px;padding:16px 17px;margin:10px 0 15px}.gate-tag{font:600 10px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--accent2);margin-bottom:10px}.gate-q{font-size:14.5px;color:var(--ink);font-weight:500;line-height:1.4;margin-bottom:5px}.gate-why{font-size:12px;color:var(--muted);line-height:1.5}
.artifact{background:var(--panel);border:1px solid var(--line);border-radius:13px;margin-top:9px;overflow:hidden}.art-head{background:var(--panel2);padding:11px 14px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}.art-title{font:600 10.5px/1 var(--mono);text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}.art-open{font:600 11px/1 Inter;color:var(--accent2)}.art-body{padding:15px 16px}.art-decision{font-family:var(--serif);font-size:22px;font-weight:500;line-height:1.2;color:var(--ink);margin-bottom:7px}.art-sum{font-size:13px;color:var(--body);line-height:1.55}
.stButton>button{border-radius:9px!important;border:1px solid var(--line)!important;background:var(--panel)!important;color:var(--ink)!important;font-size:12.5px!important;font-weight:600!important;min-height:42px!important;box-shadow:none!important}.stButton>button:hover{border-color:var(--accent)!important;color:#fff!important}.stButton>button[kind=primary]{background:var(--accent)!important;border-color:var(--accent)!important;color:#231a13!important}
[data-testid=stCaptionContainer]{color:var(--muted)!important}.demo-note{font-size:10.5px;color:var(--faint);text-align:center;margin:14px 0 4px}
@media(max-width:760px){.facts{grid-template-columns:1fr}.block-container{padding-left:1rem!important;padding-right:1rem!important}}
</style>
""",
        unsafe_allow_html=True,
    )


def _turn(who: str, role: str, body: str, user: bool = False) -> None:
    cls = "user" if user else "agent"
    body_cls = "umsg" if user else "atext"
    st.markdown(
        f'<div class="turn"><div class="av {cls}">{who}</div><div class="bubble"><div class="who">{role}</div><div class="{body_cls}">{body}</div></div></div>',
        unsafe_allow_html=True,
    )


def _set_step(value: int) -> None:
    st.session_state.agentic_demo_step = max(0, min(int(value), 5))
    st.rerun()


def render_agentic_home() -> None:
    _css()
    if "agentic_demo_step" not in st.session_state:
        st.session_state.agentic_demo_step = 0
    step = int(st.session_state.agentic_demo_step)

    with st.sidebar:
        st.markdown('<div class="rail-brand"><div class="rail-mark">TB</div><div class="rail-name">Tumor Board<small>Agentic workup</small></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="rail-label">This workup</div>', unsafe_allow_html=True)
        rows = []
        active = min(max(step, 1), 5) if step else 0
        for i, (_, label) in enumerate(STAGES, start=1):
            cls = "pstep"
            num = str(i)
            if step > i:
                cls += " done"
                num = "✓"
            elif active == i:
                cls += " active"
            rows.append(f'<div class="{cls}"><span class="pn">{num}</span><span class="pl">{label}</span></div>')
        st.markdown('<div class="prog">' + ''.join(rows) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="rail-note">The agent moves through these. You watch, and answer when it asks. Full detail opens in the conversation as it reaches each step.</div>', unsafe_allow_html=True)
        st.markdown('<div class="rail-label">Reference</div>', unsafe_allow_html=True)
        st.markdown('<div class="ref-row"><span>◇</span>Architecture</div><div class="ref-row"><span>◇</span>Validation & scope</div><div class="ref-row"><span>◇</span>About</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero"><div class="hero-k">Agentic tumor board intelligence</div><h1>Full detail, revealed in rhythm.</h1><p>The agent runs the workup, exposes the evidence trail, and pauses only where human judgment is required.</p></div>', unsafe_allow_html=True)

    _turn("TB", "Tumor Board Agent", "I'll run a full tumor-board workup and pause whenever I need your judgment. To start:")
    if step == 0:
        c1, c2 = st.columns(2, gap="small")
        with c1:
            if st.button("Use the synthetic demo case", type="primary", use_container_width=True):
                _set_step(1)
            st.caption("68F relapsed AML, FLT3-ITD · ready to run")
        with c2:
            st.button("Paste or upload a case", use_container_width=True, disabled=True)
            st.caption("Live clinical intake remains in the production workflow")

    if step >= 1:
        _turn("You", "You", "Use the synthetic demo case.", user=True)
        _turn("TB", "Tumor Board Agent · Case intake", "Loaded and structured. Here's what I extracted, with the source attached to every fact. Open it to check the full case.")
        with st.expander("Case review · structured facts", expanded=True):
            st.markdown('''<div class="facts"><div class="fct"><div class="k">Diagnosis</div><div class="v">Acute myeloid leukemia</div><span class="s">✓ source traced</span></div><div class="fct"><div class="k">Disease state</div><div class="v">Relapsed</div><span class="s">✓ source traced</span></div><div class="fct"><div class="k">Patient</div><div class="v">68 F · ECOG 1</div><span class="s">✓ source traced</span></div><div class="fct"><div class="k">Molecular</div><div class="v">FLT3-ITD · VAF 31%</div><span class="s">✓ source traced</span></div><div class="fct"><div class="k">Prior therapy</div><div class="v">Induction A · Salvage B</div><span class="s">✓ source traced</span></div><div class="fct"><div class="k">Board question</div><div class="v">Next-line strategy for tumor board</div><span class="s">✓ source traced</span></div></div>''', unsafe_allow_html=True)
        if step == 1 and st.button("Continue case review", type="primary", use_container_width=True):
            _set_step(2)

    if step >= 2:
        st.markdown('<div class="turn"><div class="av agent">TB</div><div class="bubble"><div class="who">Tumor Board Agent · Case review</div><div class="activity"><div class="act"><span class="ic">✓</span>Integrity check <span class="sub">no contradictions, provenance intact</span></div><div class="act"><span class="ic">✓</span>Missing-info scan <span class="sub">1 decision-critical gap found</span></div></div><div class="atext">One gap changes the recommendation, so I need your call before evidence review.</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="gate"><div class="gate-tag">● &nbsp; Guardrail · needs your call</div><div class="gate-q">Is this patient a transplant candidate?</div><div class="gate-why">Not in the record. Transplant-eligible keeps FLT3-inhibitor bridging in play. I will not assume it.</div></div>', unsafe_allow_html=True)
        if step == 2:
            a, b, c = st.columns(3, gap="small")
            with a:
                if st.button("Transplant candidate", type="primary", use_container_width=True): _set_step(3)
            with b:
                if st.button("Not a candidate", use_container_width=True): _set_step(3)
            with c:
                if st.button("Unknown · flag it", use_container_width=True): _set_step(3)

    if step >= 3:
        _turn("You", "You", "Transplant candidate.", user=True)
        _turn("TB", "Tumor Board Agent · Evidence", "Good. That keeps bridging in play. I pulled each evidence channel separately. Here's channel readiness:")
        with st.expander("Evidence channel readiness", expanded=True):
            st.markdown('''<div class="chan"><div><div class="chan-t">Guidelines · European LeukemiaNet</div><div class="chan-d">Relapsed FLT3-ITD pathway matched by explicit label.</div></div><span class="chip ok">Ready</span></div><div class="chan"><div><div class="chan-t">Molecular · CIViC</div><div class="chan-d">3 candidate records retrieved · need your approval.</div></div><span class="chip warn">Needs review</span></div><div class="chan"><div><div class="chan-t">Safety · FDA labeling</div><div class="chan-d">2 label sections retrieved for candidate therapies.</div></div><span class="chip warn">Needs review</span></div><div class="chan"><div><div class="chan-t">Clinical trials</div><div class="chan-d">2 candidate matches · eligibility not established.</div></div><span class="chip ok">Ready</span></div><div class="chan"><div><div class="chan-t">Literature</div><div class="chan-d">Not run for this route.</div></div><span class="chip off">Not run</span></div>''', unsafe_allow_html=True)
        with st.expander("Molecular evidence · CIViC candidates"):
            st.markdown('''<div class="rec"><div class="rec-t">EID-1042 · FLT3 · Actionable</div><div class="rec-m">Gilteritinib · CIViC Accepted · relapsed AML</div><div class="rec-x">FLT3-ITD confers sensitivity to gilteritinib in relapsed/refractory AML.</div></div><div class="rec"><div class="rec-t">EID-2087 · FLT3 · Actionable</div><div class="rec-m">Midostaurin · CIViC Accepted · newly diagnosed</div><div class="rec-x">FLT3-mutated AML benefits from midostaurin with induction.</div><div class="rec-note">Evidence is newly diagnosed. Read before applying it to this relapsed case.</div></div>''', unsafe_allow_html=True)
        with st.expander("Safety source evidence · FDA labeling"):
            st.markdown('''<div class="rec"><div class="rec-t">Gilteritinib · label §5</div><div class="rec-m">Warnings: differentiation syndrome, QT prolongation, PRES</div><div class="rec-x">Monitor ECG; hold for QTc prolongation per label thresholds.</div></div><div class="rec"><div class="rec-t">Gilteritinib · label §2</div><div class="rec-m">Dosing reference</div><div class="rec-x">Standard label dosing; source shown for board reference, not a patient-specific dose.</div></div>''', unsafe_allow_html=True)
        st.markdown('<div class="gate"><div class="gate-tag">● &nbsp; Guardrail · approve evidence</div><div class="gate-q">Approve records you have reviewed to continue.</div><div class="gate-why">Retrieval finds candidates, not answers. Human evidence attestation remains explicit.</div></div>', unsafe_allow_html=True)
        if step == 3:
            a, b = st.columns(2, gap="small")
            with a:
                if st.button("Approve gilteritinib only", type="primary", use_container_width=True): _set_step(4)
            with b:
                if st.button("Approve all reviewed", use_container_width=True): _set_step(4)

    if step >= 4:
        _turn("TB", "Tumor Board Agent · Analysis", "Approved. Before synthesis, I ran the challenge review, attacking my own evidence stack.")
        with st.expander("Challenge review findings", expanded=True):
            st.markdown('''<div class="chan"><div><div class="chan-t">Conflicts checked</div><div class="chan-d">No guideline-vs-molecular conflict for the bridging strategy.</div></div><span class="chip ok">Clear</span></div><div class="chan"><div><div class="chan-t">Unsupported leaps</div><div class="chan-d">Midostaurin evidence flagged as newly diagnosed, not relapsed. Excluded from the recommendation.</div></div><span class="chip warn">1 flagged</span></div><div class="chan"><div><div class="chan-t">Blocking gaps</div><div class="chan-d">None. Transplant eligibility was resolved earlier.</div></div><span class="chip ok">Clear</span></div>''', unsafe_allow_html=True)
        st.markdown('<div class="activity"><div class="act"><span class="ic">✓</span>Consensus <span class="sub">held · disagreement preserved</span></div></div>', unsafe_allow_html=True)
        if step == 4 and st.button("Build decision brief", type="primary", use_container_width=True):
            _set_step(5)

    if step >= 5:
        _turn("TB", "Tumor Board Agent · Decision brief", "Here's the brief. It held together, with one limitation worth naming at board.")
        st.markdown('''<div class="artifact"><div class="art-head"><span class="art-title">Decision brief · SYN-AML-001</span><span class="art-open">Governed demo</span></div><div class="art-body"><div class="art-decision">Multiple reasonable options · FLT3-directed therapy leads</div><div class="art-sum">Relapsed FLT3-ITD AML, transplant-eligible. Guideline and approved molecular evidence support gilteritinib bridging to transplant. One nonblocking limitation: midostaurin evidence is newly diagnosed only and is excluded from the recommendation.</div></div></div>''', unsafe_allow_html=True)
        _turn("TB", "Tumor Board Agent", "Want the PDF for board, or should I dig into the two trial matches?")

    st.markdown('<div class="demo-note">Interactive agentic prototype · current production workflow remains separate from this demonstration.</div>', unsafe_allow_html=True)
    if st.button("Reset demo", use_container_width=True):
        _set_step(0)
