import json
from dataclasses import asdict, dataclass
from typing import List

import streamlit as st

st.set_page_config(
    page_title="Blowout probability data collection",
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
    "Drilling int. zone 2 - 12.1/4\"",
    "Surface drilling",
    "Intermediate drilling",
    "Production drilling",
    "Completion",
]

DEFAULT_OPERATION_LIBRARY = [
    "Drill Formation",
    "Tripping",
    "Run Casing",
    "Cement",
    "Pressure Test",
    "Logging",
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
            --bg: #eff5ff;
            --panel: #ffffff;
            --panel-muted: #f2f6fc;
            --text: #10233e;
            --subtext: #4c607a;
            --brand: #1165c1;
            --brand-strong: #0b4f9a;
            --line: #c6d8f1;
            --phase: #f2c400;
            --op: #e7e7e7;
        }

        .stApp {
            background: linear-gradient(180deg, #e8f2ff 0%, var(--bg) 45%, #f4f8ff 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f4077 0%, #1559a5 100%);
            border-right: 1px solid rgba(255,255,255,.16);
        }

        [data-testid="stSidebar"] * {
            color: #f2f7ff !important;
        }

        .app-title {
            background: linear-gradient(90deg, #0f4f96 0%, #2d7bd7 100%);
            color: #ffffff;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: .8rem;
            box-shadow: 0 8px 20px rgba(16, 58, 109, 0.16);
        }

        .card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: .9rem;
            box-shadow: 0 4px 12px rgba(17, 70, 132, 0.08);
        }

        .scenario-table {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #d4dbe7;
            margin-top: .6rem;
        }

        .phase-row {
            display: grid;
            grid-template-columns: 50px 1fr 120px 120px 220px;
            align-items: center;
            min-height: 56px;
            border-bottom: 1px solid #e4e7ed;
            background: var(--phase);
            color: #1d2b3e;
            font-weight: 600;
        }

        .operation-header {
            background: #cfcfcf;
            color: #1b2a3d;
            font-weight: 700;
            padding: 10px 14px;
            border-bottom: 1px solid #bdbdbd;
        }

        .operation-row {
            display: grid;
            grid-template-columns: 50px 1fr 220px;
            align-items: center;
            min-height: 52px;
            background: var(--op);
            color: #1f2d40;
            border-bottom: 1px solid #d0d0d0;
            padding-right: 10px;
        }

        .cell {
            padding: 0 10px;
            border-right: 1px solid rgba(18,35,62,.15);
        }

        .cell:last-child { border-right: none; }

        .pill {
            background: #1f73d0;
            color: #fff;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 12px;
        }

        .time-box {
            background: #f0f0f0;
            border: 2px solid #16a085;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 10px;
            font-weight: 700;
        }

        .header-grid {
            display: grid;
            grid-template-columns: 50px 1fr 120px 120px 220px;
            background: #ffffff;
            border-bottom: 1px solid #d9e3f5;
            color: #143357;
            font-weight: 700;
            min-height: 44px;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_admin() -> str:
    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio(
            "Go to",
            ["Architecture builder", "Risk Inputs (coming soon)", "Review & Submit (coming soon)"],
            label_visibility="collapsed",
            index=0,
        )

        st.markdown("---")
        st.markdown("## Admin configuration")

        with st.expander("Configure phase catalog", expanded=False):
            new_phase = st.text_input("Add phase")
            if st.button("Add phase", use_container_width=True) and new_phase.strip():
                if new_phase.strip() not in st.session_state.phase_library:
                    st.session_state.phase_library.append(new_phase.strip())

            phase_to_remove = st.selectbox("Remove phase", [""] + st.session_state.phase_library)
            if st.button("Delete selected phase", use_container_width=True) and phase_to_remove:
                st.session_state.phase_library = [p for p in st.session_state.phase_library if p != phase_to_remove]

        with st.expander("Configure operation catalog", expanded=False):
            new_operation = st.text_input("Add operation")
            if st.button("Add operation", use_container_width=True) and new_operation.strip():
                if new_operation.strip() not in st.session_state.operation_library:
                    st.session_state.operation_library.append(new_operation.strip())

            op_to_remove = st.selectbox("Remove operation", [""] + st.session_state.operation_library)
            if st.button("Delete selected operation", use_container_width=True) and op_to_remove:
                st.session_state.operation_library = [o for o in st.session_state.operation_library if o != op_to_remove]

    return page


def add_phase_form() -> None:
    st.markdown("### Add next phase in sequence")
    with st.container(border=True):
        phase_name = st.selectbox("Phase name", st.session_state.phase_library)
        operation_count = st.number_input("Number of operations", min_value=1, max_value=12, value=2, step=1)

        operations: List[OperationItem] = []
        for i in range(int(operation_count)):
            st.markdown(f"**Operation {i + 1}**")
            c1, c2, c3, c4 = st.columns([2.2, 1, 1, 1])
            with c1:
                op_name = st.selectbox("Operation name", st.session_state.operation_library, key=f"op_name_{i}")
            with c2:
                diameter = st.number_input("Diameter [in]", min_value=0.0, step=0.25, value=8.5, key=f"diam_{i}")
            with c3:
                duration_value = st.number_input("Time", min_value=0.0, step=0.5, value=12.0, key=f"time_{i}")
            with c4:
                duration_unit = st.selectbox("Unit", ["hours", "days"], key=f"unit_{i}")
            operations.append(OperationItem(op_name, float(diameter), float(duration_value), duration_unit))

        if st.button("Add phase", use_container_width=True, type="primary"):
            st.session_state.phases.append(PhaseItem(name=phase_name, operations=operations))
            st.success(f"Phase added: {phase_name}")


def total_phase_hours(phase: PhaseItem) -> float:
    total = 0.0
    for op in phase.operations:
        total += op.duration_value * (24 if op.duration_unit == "days" else 1)
    return total


def render_sequence() -> None:
    st.markdown("### Scenario sequence")

    if not st.session_state.phases:
        st.info("No phase created yet. Use the left panel to add the first phase.")
        return

    st.markdown(
        """
        <div class='header-grid'>
          <div class='cell'></div>
          <div class='cell'>Scenarios</div>
          <div class='cell'>K-BOS</div>
          <div class='cell'>Position</div>
          <div class='cell'>Total Time [h]</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for idx, phase in enumerate(st.session_state.phases):
        total_h = total_phase_hours(phase)
        up_disabled = idx == 0
        down_disabled = idx == len(st.session_state.phases) - 1

        up_col, down_col = st.columns([1, 20], vertical_alignment="center")
        with up_col:
            if st.button("◀", key=f"toggle_{idx}"):
                pass
        with down_col:
            st.markdown(
                f"""
                <div class='phase-row'>
                  <div class='cell'>⌄</div>
                  <div class='cell'>{phase.name}</div>
                  <div class='cell'><span class='pill'>☐</span></div>
                  <div class='cell'><span class='pill'>↑ ↓</span></div>
                  <div class='cell'><div class='time-box'>{total_h:.2f} <span>⏱</span></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if not up_disabled or not down_disabled:
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Move up", key=f"up_{idx}", disabled=up_disabled):
                    st.session_state.phases[idx - 1], st.session_state.phases[idx] = st.session_state.phases[idx], st.session_state.phases[idx - 1]
                    st.rerun()
            with b2:
                if st.button("Move down", key=f"down_{idx}", disabled=down_disabled):
                    st.session_state.phases[idx + 1], st.session_state.phases[idx] = st.session_state.phases[idx], st.session_state.phases[idx + 1]
                    st.rerun()
            with b3:
                if st.button("Delete phase", key=f"del_{idx}"):
                    st.session_state.phases.pop(idx)
                    st.rerun()

        for op in phase.operations:
            st.markdown(
                f"""
                <div class='operation-header'>({phase.name}) {op.name}</div>
                <div class='operation-row'>
                  <div class='cell'>|</div>
                  <div class='cell'>{op.name} · Diameter {op.diameter_in:.2f} in</div>
                  <div class='cell'>{op.duration_value:.2f} {op.duration_unit}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_export() -> None:
    payload = [
        {"phase_name": phase.name, "operations": [asdict(op) for op in phase.operations]}
        for phase in st.session_state.phases
    ]
    st.download_button(
        "Download sequence JSON",
        data=json.dumps(payload, indent=2),
        file_name="blowout_probability_sequence.json",
        mime="application/json",
        use_container_width=True,
    )


def main() -> None:
    bootstrap_state()
    render_theme()
    page = sidebar_admin()

    st.markdown(
        """
        <div class='app-title'>
          <h2 style='margin:0;'>Blowout probability data collection</h2>
          <p style='margin:.4rem 0 0 0;'>Configure well architecture and create phase-operation sequences for risk evaluation inputs.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if page != "Architecture builder":
        st.warning("This page will be available in the next release.")
        return

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='card'><strong>Total phases</strong><br>{len(st.session_state.phases)}</div>", unsafe_allow_html=True)
    c2.markdown(
        f"<div class='card'><strong>Total operations</strong><br>{sum(len(p.operations) for p in st.session_state.phases)}</div>",
        unsafe_allow_html=True,
    )
    c3.markdown("<div class='card'><strong>Workflow status</strong><br>Draft</div>", unsafe_allow_html=True)

    left, right = st.columns([1.1, 1.4])
    with left:
        add_phase_form()
        render_export()
    with right:
        render_sequence()


if __name__ == "__main__":
    main()
