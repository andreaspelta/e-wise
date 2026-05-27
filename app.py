import streamlit as st
from dataclasses import dataclass
from typing import List

st.set_page_config(
    page_title="E-WISE | Blowout probability data collection",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@dataclass
class ActivityItem:
    name: str
    diameter_in: float
    duration_value: float
    duration_unit: str


@dataclass
class PhaseItem:
    name: str
    pore_gradient_sg: str
    mud_weight_kg_l: str
    mud_type: str
    fracture_gradient_sg: str
    lithology: str
    faults: str
    fractures: str
    depleted_levels: str
    activities: List[ActivityItem]


DEFAULT_PHASE_LIBRARY = [
    "Conductor",
    "Surface",
    "Intermediate",
    "Production",
    "Completion",
    "Workover",
]

DEFAULT_ACTIVITY_LIBRARY = [
    "Drill",
    "Run Casing",
    "Cement",
    "Pressure Test",
    "Logging",
    "Displacement",
    "BOP Test",
]

DEFAULT_LITHOLOGY_LIBRARY = [
    "Sandstone",
    "Shale",
    "Carbonate",
]


def bootstrap_state() -> None:
    if "phase_library" not in st.session_state:
        st.session_state.phase_library = DEFAULT_PHASE_LIBRARY.copy()
    if "activity_library" not in st.session_state:
        st.session_state.activity_library = DEFAULT_ACTIVITY_LIBRARY.copy()
    if "lithology_library" not in st.session_state:
        st.session_state.lithology_library = DEFAULT_LITHOLOGY_LIBRARY.copy()
    if "phases" not in st.session_state:
        st.session_state.phases = []
    if "sequence_locked" not in st.session_state:
        st.session_state.sequence_locked = False
    if "path_screenshot" not in st.session_state:
        st.session_state.path_screenshot = None


def sidebar_admin() -> None:
    with st.sidebar:
        st.markdown("### Navigation")
        builder_label = "Well architecture builder ✅" if st.session_state.sequence_locked else "Well architecture builder"
        page = st.radio(
            "Go to",
            [builder_label, "Risk Inputs (coming soon)", "Review & Submit (coming soon)"],
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
                    st.session_state.phase_library = [p for p in st.session_state.phase_library if p != phase_to_delete]

        with st.expander("Activity catalog", expanded=False):
            new_activity = st.text_input("Add an activity")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Add activity", use_container_width=True) and new_activity.strip():
                    if new_activity.strip() not in st.session_state.activity_library:
                        st.session_state.activity_library.append(new_activity.strip())
            with c2:
                activity_to_delete = st.selectbox(
                    "Remove activity",
                    options=[""] + st.session_state.activity_library,
                    key="activity_to_delete",
                )
                if st.button("Remove activity", use_container_width=True) and activity_to_delete:
                    st.session_state.activity_library = [
                        o for o in st.session_state.activity_library if o != activity_to_delete
                    ]

        with st.expander("Lithology catalog", expanded=False):
            new_lithology = st.text_input("Add lithology")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Add lithology", use_container_width=True) and new_lithology.strip():
                    if new_lithology.strip() not in st.session_state.lithology_library:
                        st.session_state.lithology_library.append(new_lithology.strip())
            with c2:
                lithology_to_delete = st.selectbox(
                    "Remove lithology",
                    options=[""] + st.session_state.lithology_library,
                    key="lithology_to_delete",
                )
                if st.button("Remove lithology", use_container_width=True) and lithology_to_delete:
                    st.session_state.lithology_library = [
                        l for l in st.session_state.lithology_library if l != lithology_to_delete
                    ]

    return page


def render_upload() -> None:
    upload = st.file_uploader(
        "Upload here a screenshot of the path of your wellcost design, otherwise build the sequence of operations",
        type=["png", "jpg", "jpeg", "webp", "pdf"],
        key="path_screenshot_uploader",
    )

    if upload is None:
        st.session_state.path_screenshot = None
        return

    st.session_state.path_screenshot = upload
    st.info("Upload detected. Build the sequence of operations is disabled.")


def add_phase_form() -> None:
    st.markdown("### Build sequence")
    if st.session_state.path_screenshot is not None:
        st.warning("Build the sequence is disabled because a screenshot has been uploaded.")
        return

    with st.container(border=True):
        st.markdown("#### Add next phase")
        st.caption("consider phases after BOP installation only")
        col1, col2 = st.columns([2, 1])
        with col1:
            phase_name = st.selectbox("Phase name", st.session_state.phase_library, key="new_phase_name")
        with col2:
            activity_count = st.number_input("Activities", min_value=1, max_value=10, value=1)

        details_col1, details_col2, details_col3 = st.columns(3)
        with details_col1:
            pore_gradient_sg = st.text_input("Pore gradient (s.g.)")
            mud_type = st.selectbox("Mud Type", ["WBM", "OBM"])
            faults = st.selectbox("Faults", ["Yes", "No"])
        with details_col2:
            mud_weight_kg_l = st.text_input("Mud weight (kg/L)")
            fracture_gradient_sg = st.text_input("Fracture gradient (s.g.)")
            fractures = st.selectbox("Fractures", ["Yes", "No"])
        with details_col3:
            lithology = st.selectbox("Lithology", st.session_state.lithology_library)
            depleted_levels = st.selectbox("Depleted Levels", ["Yes", "No"])

        activities: List[ActivityItem] = []
        for i in range(activity_count):
            st.markdown(f"**Activity {i + 1}**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                activity_name = st.selectbox(
                    "Activity",
                    st.session_state.activity_library,
                    key=f"new_activity_name_{i}",
                    label_visibility="collapsed",
                )
            with c2:
                diameter = st.number_input("Diameter (in)", min_value=0.0, step=0.25, value=8.5, key=f"new_activity_diam_{i}")
            with c3:
                duration = st.number_input("Time", min_value=0.0, step=0.5, value=6.0, key=f"new_activity_time_{i}")
            with c4:
                unit = st.selectbox("Unit", ["hours", "days"], key=f"new_activity_unit_{i}")

            activities.append(ActivityItem(activity_name, float(diameter), float(duration), unit))

        if st.button("Add phase to sequence", type="primary", use_container_width=True):
            st.session_state.phases.append(
                PhaseItem(
                    name=phase_name,
                    pore_gradient_sg=pore_gradient_sg,
                    mud_weight_kg_l=mud_weight_kg_l,
                    mud_type=mud_type,
                    fracture_gradient_sg=fracture_gradient_sg,
                    lithology=lithology,
                    faults=faults,
                    fractures=fractures,
                    depleted_levels=depleted_levels,
                    activities=activities,
                )
            )
            st.success(f"Added phase: {phase_name}")


def render_sequence() -> None:
    st.markdown("### Current well sequence")
    if not st.session_state.phases:
        st.info("No phase added yet. Start by adding your first phase.")
        return

    for idx, phase in enumerate(st.session_state.phases, start=1):
        with st.expander(f"{idx}. {phase.name}", expanded=True):
            st.markdown(
                f"""
                - **Pore gradient (s.g.)**: {phase.pore_gradient_sg or '-'}
                - **Mud weight (kg/L)**: {phase.mud_weight_kg_l or '-'}
                - **Mud Type**: {phase.mud_type}
                - **Fracture gradient (s.g.)**: {phase.fracture_gradient_sg or '-'}
                - **Lithology**: {phase.lithology}
                - **Faults**: {phase.faults}
                - **Fractures**: {phase.fractures}
                - **Depleted Levels**: {phase.depleted_levels}
                """
            )
            for act_idx, act in enumerate(phase.activities, start=1):
                st.markdown(
                    f"- **Activity {act_idx} · {act.name}** — Diameter: {act.diameter_in} in · Time: {act.duration_value} {act.duration_unit}"
                )

            if not st.session_state.sequence_locked and st.button(
                f"Delete phase {idx}", key=f"delete_{idx}", use_container_width=True
            ):
                st.session_state.phases.pop(idx - 1)
                st.rerun()


def render_freeze_controls() -> None:
    if st.session_state.sequence_locked:
        st.success("Sequence frozen.")
        if st.button("Unfreeze sequence", use_container_width=True):
            st.session_state.sequence_locked = False
            st.success("Sequence unfrozen. Editing is enabled again.")
            st.rerun()
        return

    if st.button("Freeze sequence", use_container_width=True, type="primary"):
        st.session_state.sequence_locked = True
        st.success("Sequence frozen. Well architecture builder is now marked as completed.")
        st.rerun()


def main() -> None:
    bootstrap_state()
    page = sidebar_admin()

    st.title("Blowout probability data collection")
    st.write("Design drilling phases and activity sequence for blowout probability evaluation input.")

    if "Well architecture builder" not in page:
        st.warning("This module is planned for the next build iteration.")
        return

    render_upload()

    left, right = st.columns([1.2, 1])
    with left:
        if not st.session_state.sequence_locked:
            add_phase_form()
        else:
            st.info("The sequence is frozen and cannot be edited.")
    with right:
        render_sequence()
        render_freeze_controls()


if __name__ == "__main__":
    main()
