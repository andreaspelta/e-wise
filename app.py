import streamlit as st
from dataclasses import dataclass, asdict
from typing import List

st.set_page_config(
    page_title="E-WISE | Well Architecture Studio",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass
class OperationItem:
    name: str
    diameter_in: float
    duration_value: float
    duration_unit: str


@dataclass
class PhaseItem:
    name: str
    operations: List[OperationItem]


DEFAULT_PHASE_LIBRARY = [
    "Conductor",
    "Surface",
    "Intermediate",
    "Production",
    "Completion",
    "Workover",
]

DEFAULT_OPERATION_LIBRARY = [
    "Drill",
    "Run Casing",
    "Cement",
    "Pressure Test",
    "Logging",
    "Displacement",
    "BOP Test",
]


def bootstrap_state() -> None:
    if "phase_library" not in st.session_state:
        st.session_state.phase_library = DEFAULT_PHASE_LIBRARY.copy()
    if "operation_library" not in st.session_state:
        st.session_state.operation_library = DEFAULT_OPERATION_LIBRARY.copy()
    if "phases" not in st.session_state:
        st.session_state.phases = []


def render_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0e1117;
            --panel: #151924;
            --panel-2: #1b2130;
            --border: #2a3348;
            --text: #e6edf8;
            --subtext: #9fb0cf;
            --brand: #4da3ff;
            --brand-2: #64c8ff;
            --ok: #45d483;
        }
        .stApp {
            background: radial-gradient(1200px 500px at 20% -20%, #1f2c49 0%, var(--bg) 60%);
            color: var(--text);
        }
        .title-card {
            background: linear-gradient(135deg, rgba(77,163,255,0.20), rgba(100,200,255,0.08));
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .kpi-card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: .9rem;
        }
        .phase-chip {
            background: var(--panel-2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: .7rem .9rem;
            margin-bottom: .6rem;
        }
        .small-muted { color: var(--subtext); font-size: 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_admin() -> None:
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Go to",
            ["Well Architecture Builder", "Risk Inputs (coming soon)", "Review & Submit (coming soon)"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### Admin Configuration")
        with st.expander("Phase catalog", expanded=False):
            new_phase = st.text_input("Add a phase")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Add phase", use_container_width=True) and new_phase.strip():
                    if new_phase.strip() not in st.session_state.phase_library:
                        st.session_state.phase_library.append(new_phase.strip())
            with c2:
                phase_to_delete = st.selectbox(
                    "Remove phase",
                    options=[""] + st.session_state.phase_library,
                    key="phase_to_delete",
                )
                if st.button("Remove", use_container_width=True) and phase_to_delete:
                    st.session_state.phase_library = [
                        p for p in st.session_state.phase_library if p != phase_to_delete
                    ]

        with st.expander("Operation catalog", expanded=False):
            new_operation = st.text_input("Add an operation")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Add operation", use_container_width=True) and new_operation.strip():
                    if new_operation.strip() not in st.session_state.operation_library:
                        st.session_state.operation_library.append(new_operation.strip())
            with c2:
                op_to_delete = st.selectbox(
                    "Remove operation",
                    options=[""] + st.session_state.operation_library,
                    key="op_to_delete",
                )
                if st.button("Remove operation", use_container_width=True) and op_to_delete:
                    st.session_state.operation_library = [
                        o for o in st.session_state.operation_library if o != op_to_delete
                    ]

        st.markdown("---")
        st.caption("Designed for engineering workflows · Dark enterprise UI")
    return page


def add_phase_form() -> None:
    st.markdown("### Build sequence")
    with st.container(border=True):
        st.markdown("#### Add next phase")
        col1, col2 = st.columns([2, 1])
        with col1:
            phase_name = st.selectbox(
                "Phase name",
                st.session_state.phase_library,
                key="new_phase_name",
            )
        with col2:
            operation_count = st.number_input("Operations", min_value=1, max_value=10, value=1)

        operations: List[OperationItem] = []
        for i in range(operation_count):
            st.markdown(f"**Operation {i + 1}**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                op_name = st.selectbox(
                    "Operation",
                    st.session_state.operation_library,
                    key=f"new_op_name_{i}",
                    label_visibility="collapsed",
                )
            with c2:
                diameter = st.number_input(
                    "Diameter (in)",
                    min_value=0.0,
                    step=0.25,
                    value=8.5,
                    key=f"new_op_diam_{i}",
                )
            with c3:
                duration = st.number_input(
                    "Time",
                    min_value=0.0,
                    step=0.5,
                    value=6.0,
                    key=f"new_op_time_{i}",
                )
            with c4:
                unit = st.selectbox("Unit", ["hours", "days"], key=f"new_op_unit_{i}")

            operations.append(OperationItem(op_name, float(diameter), float(duration), unit))

        if st.button("Add phase to sequence", type="primary", use_container_width=True):
            st.session_state.phases.append(PhaseItem(name=phase_name, operations=operations))
            st.success(f"Added phase: {phase_name}")


def render_sequence() -> None:
    st.markdown("### Current well sequence")
    if not st.session_state.phases:
        st.info("No phase added yet. Start by adding your first phase.")
        return

    for idx, phase in enumerate(st.session_state.phases, start=1):
        with st.expander(f"{idx}. {phase.name}", expanded=True):
            for op_idx, op in enumerate(phase.operations, start=1):
                st.markdown(
                    f"""
                    <div class='phase-chip'>
                      <strong>Op {op_idx} · {op.name}</strong><br>
                      <span class='small-muted'>Diameter: {op.diameter_in} in · Time: {op.duration_value} {op.duration_unit}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if st.button(f"Delete phase {idx}", key=f"delete_{idx}", use_container_width=True):
                st.session_state.phases.pop(idx - 1)
                st.rerun()


def render_export() -> None:
    payload = [
        {
            "phase_name": p.name,
            "operations": [asdict(op) for op in p.operations],
        }
        for p in st.session_state.phases
    ]
    st.download_button(
        "Download sequence JSON",
        data=str(payload),
        file_name="well_architecture_sequence.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    bootstrap_state()
    render_theme()
    page = sidebar_admin()

    st.markdown(
        """
        <div class='title-card'>
          <h2 style='margin:0;'>Well Architecture Studio</h2>
          <p style='margin:.4rem 0 0 0; color:#c3d4f2;'>Design drilling phases and operation sequence for blowout probability evaluation input.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if page != "Well Architecture Builder":
        st.warning("This module is planned for the next build iteration.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='kpi-card'><strong>Phases</strong><br>{len(st.session_state.phases)}</div>", unsafe_allow_html=True)
    with c2:
        total_ops = sum(len(p.operations) for p in st.session_state.phases)
        st.markdown(f"<div class='kpi-card'><strong>Operations</strong><br>{total_ops}</div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='kpi-card'><strong>Status</strong><br>Draft</div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])
    with left:
        add_phase_form()
    with right:
        render_sequence()
        if st.session_state.phases:
            render_export()


if __name__ == "__main__":
    main()
