from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st

from services.governed_chat import answer_governed_question


def _txt(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if hasattr(value, "value"):
        value = value.value
    text = str(value).strip()
    return text or default


def chat_css() -> None:
    st.markdown(
        """
<style>
.tb-chat-shell{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;margin-top:9px}
.tb-chat-head{background:var(--panelhi);color:var(--ink);border:1px solid var(--linehi);border-radius:12px;padding:17px}
.tb-chat-head strong{font-family:var(--serif);font-size:1.45rem;line-height:1.2;display:block;font-weight:500;letter-spacing:-.02em;color:var(--ink)}
.tb-chat-head span{font-size:.88rem;color:var(--body);line-height:1.58;display:block;margin-top:7px}
.tb-chat-note{font-size:.8rem;line-height:1.55;color:var(--muted);background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px 11px;margin:9px 0 0}
.tb-chat-note strong{color:var(--accent2);font-weight:650}.tb-turn{margin:13px 0}.tb-user{font-size:.9rem;font-weight:650;color:var(--ink);margin:0 0 7px}
.tb-answer{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:13px 14px}.tb-status{font:600 .65rem/13px var(--mono);color:var(--muted);text-transform:uppercase;letter-spacing:.09em}.tb-answer-text{font-size:.94rem;line-height:1.66;color:var(--body);margin:8px 0 0;white-space:pre-wrap}.tb-block-title{font:600 .65rem/13px var(--mono);color:var(--muted);margin-top:12px;text-transform:uppercase;letter-spacing:.08em}.tb-chip{display:inline-flex;padding:5px 8px;border-radius:999px;background:var(--panel2);color:var(--body);border:1px solid var(--line);font-size:.72rem;font-weight:600;margin:5px 4px 0 0}.tb-limit{font-size:.8rem;line-height:1.5;color:#e7c98a;background:rgba(224,176,98,.08);border:1px solid rgba(224,176,98,.28);border-radius:9px;padding:9px 10px;margin-top:7px}.tb-change{font-size:.8rem;line-height:1.5;color:var(--body);margin-top:5px}
</style>
""",
        unsafe_allow_html=True,
    )


def _history_for_model(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    history=[]
    for row in rows[-6:]:
        history.append({"role":"user","content":_txt(row.get("question"))}); history.append({"role":"assistant","content":_txt(row.get("answer"))})
    return history


def _render_answer(row: dict[str, Any]) -> None:
    agents=row.get("agents_consulted",[]) or []; evidence=row.get("evidence_used",[]) or []; limitations=row.get("limitations",[]) or []; changes=row.get("what_could_change",[]) or []
    st.markdown(f'<div class="tb-turn"><div class="tb-user">You: {escape(_txt(row.get("question")))}</div><div class="tb-answer"><div class="tb-status">{escape(_txt(row.get("status"),"Case-grounded synthesis"))}</div><div class="tb-answer-text">{escape(_txt(row.get("answer")))}</div>', unsafe_allow_html=True)
    if agents: st.markdown('<div class="tb-block-title">Agents consulted</div>'+''.join(f'<span class="tb-chip">{escape(_txt(x))}</span>' for x in agents),unsafe_allow_html=True)
    if evidence: st.markdown('<div class="tb-block-title">Evidence used</div>'+''.join(f'<span class="tb-chip">{escape(_txt(x))}</span>' for x in evidence),unsafe_allow_html=True)
    if limitations: st.markdown('<div class="tb-block-title">Limitations</div>'+''.join(f'<div class="tb-limit">{escape(_txt(x))}</div>' for x in limitations[:6]),unsafe_allow_html=True)
    if changes: st.markdown('<div class="tb-block-title">What could change the answer</div>'+''.join(f'<div class="tb-change">• {escape(_txt(x))}</div>' for x in changes[:6]),unsafe_allow_html=True)
    st.markdown('</div></div>',unsafe_allow_html=True)


def render_governed_chat(result: dict[str, Any], case: Any, *, key_prefix: str = "brief") -> None:
    chat_css()
    st.markdown('<div class="tb-chat-shell"><div class="tb-chat-head"><strong>Ask Tumor Board</strong><span>Ask follow-up questions about this specific case and the evidence the governed workflow actually produced. The assistant will abstain rather than create a new patient-specific recommendation from unrestricted model memory.</span></div><div class="tb-chat-note"><strong>Useful questions:</strong> What is the best-supported strategy and why? What is missing? Which trials surfaced? What did the challenge review question? What could change the decision?</div></div>',unsafe_allow_html=True)
    hist_key=f"{key_prefix}_governed_chat"
    if hist_key not in st.session_state: st.session_state[hist_key]=[]
    prompts=["Summarize this case for tumor board","What is the best-supported treatment strategy and why?","Which clinical trials matched and what still needs verification?","What is missing or uncertain?","What did the safety & challenge review question?","What could change the decision?"]
    if not st.session_state[hist_key]:
        cols=st.columns(2,gap="small")
        for i,prompt in enumerate(prompts):
            with cols[i%2]:
                if st.button(prompt,key=f"{key_prefix}_smart_prompt_{i}",use_container_width=True):
                    response=answer_governed_question(prompt,result,case,history=[]); response["question"]=prompt; st.session_state[hist_key].append(response); st.rerun()
    for row in st.session_state[hist_key][-6:]: _render_answer(row)
    question=st.chat_input("Ask a question about this case and its governed evidence",key=f"{key_prefix}_smart_chat_input")
    if question:
        history=_history_for_model(st.session_state[hist_key])
        with st.spinner("Reviewing the governed case and relevant specialist outputs..."): response=answer_governed_question(question,result,case,history=history)
        response["question"]=question; st.session_state[hist_key].append(response); st.rerun()
