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
    diameter_in: float
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

WELLHEAD_TYPES = ["Unitized", "Flanged"]
XTREE_TYPES = ["Dry tee", "Subsea HXT", "Subsea VXT"]
SECONDARY_INTERVENTION_OPTIONS = ["None", "Single ROV", "Dual ROV"]


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
    if "secondary_intervention" not in st.session_state:
        st.session_state.secondary_intervention = "None"
    if "acoustic_system" not in st.session_state:
        st.session_state.acoustic_system = False


def sidebar_admin() -> None:
    with st.sidebar:
        st.markdown("### Navigation")
        builder_label = "Well architecture builder ✅" if st.session_state.sequence_locked else "Well architecture builder"
        page = st.radio(
            "Go to",
            [builder_label, "Barriers"],
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
    st.info("Upload detected. You can still use the Build sequence tab to define operations.")


def add_phase_form() -> None:
    st.markdown("### Build sequence")
    with st.container(border=True):
        st.markdown("#### Add next phase")
        st.caption("consider phases after BOP installation only")
        col1, col2 = st.columns([2, 1])
        with col1:
            phase_name = st.selectbox("Phase name", st.session_state.phase_library, key="new_phase_name")
        with col2:
            activity_count = st.number_input("Activities", min_value=1, max_value=10, value=1)

        details_col1, details_col2, details_col3, details_col4 = st.columns(4)
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
        with details_col4:
            diameter = st.number_input("Diameter (in)", min_value=0.0, step=0.25, value=8.5, key="new_phase_diameter")

        activities: List[ActivityItem] = []
        for i in range(activity_count):
            st.markdown(f"**Activity {i + 1}**")
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                activity_name = st.selectbox(
                    "Activity",
                    st.session_state.activity_library,
                    key=f"new_activity_name_{i}",
                    label_visibility="collapsed",
                )
            with c2:
                duration = st.number_input("Time", min_value=0.0, step=0.5, value=6.0, key=f"new_activity_time_{i}")
            with c3:
                unit = st.selectbox("Unit", ["hours", "days"], key=f"new_activity_unit_{i}")

            activities.append(ActivityItem(activity_name, float(duration), unit))

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
                    diameter_in=float(diameter),
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
                - **Diameter (in)**: {phase.diameter_in}
                """
            )
            for act_idx, act in enumerate(phase.activities, start=1):
                st.markdown(
                    f"- **Activity {act_idx} · {act.name}** — Time: {act.duration_value} {act.duration_unit}"
                )

            if not st.session_state.sequence_locked and st.button(
                f"Delete phase {idx}", key=f"delete_{idx}", use_container_width=True
            ):
                st.session_state.phases.pop(idx - 1)
                st.rerun()


def format_pipe_ram_specs(pipe_ram_specs: List[dict]) -> str:
    if not pipe_ram_specs:
        return "-"

    formatted_specs = []
    for spec in pipe_ram_specs:
        diameter = spec["diameter"] or "not specified"
        formatted_specs.append(f"Pipe Ram {spec['index']}: {spec['type']} ({diameter})")
    return "; ".join(formatted_specs)


def render_barriers_page() -> None:
    st.header("Barriers")
    st.write("Collect secondary barrier configuration for the selected well architecture.")

    top_col1, top_col2 = st.columns(2)
    with top_col1:
        st.selectbox("Wellhead Type", WELLHEAD_TYPES, key="wellhead_type")
    with top_col2:
        st.selectbox("Xtree", XTREE_TYPES, key="xtree_type")

    with st.expander("BOP Stack", expanded=True):
        st.number_input(
            "Annular Preventer",
            min_value=1,
            max_value=2,
            step=1,
            value=1,
            key="annular_preventer_count",
        )

        pipe_ram_count = st.number_input(
            "Pipe Ram",
            min_value=0,
            step=1,
            value=0,
            help="able to close against drillpipes (no shear)",
            key="pipe_ram_count",
        )
        st.caption("able to close against drillpipes (no shear)")

        pipe_ram_specs = []
        if pipe_ram_count > 0:
            with st.expander("Pipe Ram closure diameters", expanded=True):
                st.caption(
                    "For each Pipe Ram, choose whether it is fixed or variable and enter "
                    "the diameter it can close against."
                )
                for pipe_ram_index in range(1, pipe_ram_count + 1):
                    st.markdown(f"**Pipe Ram {pipe_ram_index}**")
                    type_col, diameter_col = st.columns([1, 2])
                    pipe_ram_type_key = f"pipe_ram_type_{pipe_ram_index}"
                    with type_col:
                        pipe_ram_type = st.radio(
                            "Type",
                            ["Fixed", "Variable"],
                            key=pipe_ram_type_key,
                            horizontal=True,
                        )
                    with diameter_col:
                        if pipe_ram_type == "Fixed":
                            diameter = st.text_input(
                                "Closing diameter (in)",
                                placeholder="Example: 5 1/2",
                                key=f"pipe_ram_fixed_diameter_{pipe_ram_index}",
                            )
                            help_text = "Enter one diameter value."
                            if "x" in diameter.lower():
                                st.warning("Fixed Pipe Ram diameters must be a single value.")
                        else:
                            diameter = st.text_input(
                                "Closing diameter range (in)",
                                placeholder="Example: 3 1/2 x 7 5/8",
                                key=f"pipe_ram_variable_diameter_{pipe_ram_index}",
                            )
                            help_text = "Enter two diameter values separated by X."
                            if diameter.strip() and "x" not in diameter.lower():
                                st.warning("Variable Pipe Ram diameters must contain an X separator.")
                        st.caption(help_text)
                    pipe_ram_specs.append(
                        {
                            "index": pipe_ram_index,
                            "type": pipe_ram_type,
                            "diameter": diameter.strip(),
                        }
                    )
        st.session_state.pipe_ram_specs = pipe_ram_specs

        casing_ram_count = st.number_input(
            "Casing Ram",
            min_value=0,
            step=1,
            value=0,
            help="able to close against casing (no shear)",
            key="casing_ram_count",
        )
        st.caption("able to close against casing (no shear)")

        casing_od_values = []
        if casing_ram_count > 0:
            with st.expander("Casing OD", expanded=True):
                for casing_ram_index in range(1, casing_ram_count + 1):
                    casing_od_values.append(
                        st.number_input(
                            f"Casing Ram {casing_ram_index} OD (in)",
                            min_value=0.0,
                            step=0.125,
                            value=9.625,
                            key=f"casing_od_in_{casing_ram_index}",
                        )
                    )
        st.session_state.casing_od_values = casing_od_values

        st.number_input(
            "Blind Shear Ram",
            min_value=0,
            step=1,
            value=0,
            help="able to shear drill pipes",
            key="blind_shear_ram_count",
        )
        st.caption("able to shear drill pipes")

        st.number_input(
            "Casing Shear Ram",
            min_value=0,
            step=1,
            value=0,
            help="able to shear casing joints",
            key="casing_shear_ram_count",
        )
        st.caption("able to shear casing joints")

    with st.expander("Secondary Intervention System", expanded=True):
        st.radio(
            "ROV availability",
            SECONDARY_INTERVENTION_OPTIONS,
            key="secondary_intervention",
            horizontal=True,
        )
        st.checkbox(
            "Acoustic System",
            key="acoustic_system",
        )

    with st.expander("Barrier selection summary", expanded=False):
        st.markdown(
            f"""
            - **Wellhead Type**: {st.session_state.wellhead_type}
            - **Xtree**: {st.session_state.xtree_type}
            - **Annular Preventer**: {st.session_state.annular_preventer_count}
            - **Pipe Ram**: {st.session_state.pipe_ram_count}
            - **Pipe Ram closure diameters**: {format_pipe_ram_specs(st.session_state.pipe_ram_specs) if st.session_state.pipe_ram_count > 0 else '-'}
            - **Casing Ram**: {st.session_state.casing_ram_count}
            - **Casing OD (in)**: {", ".join(str(od) for od in st.session_state.casing_od_values) if st.session_state.casing_ram_count > 0 else '-'}
            - **Blind Shear Ram**: {st.session_state.blind_shear_ram_count}
            - **Casing Shear Ram**: {st.session_state.casing_shear_ram_count}
            - **Secondary Intervention System**: {st.session_state.secondary_intervention}
            - **Acoustic System**: {'Yes' if st.session_state.acoustic_system else 'No'}
            """
        )


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

    if page == "Barriers":
        render_barriers_page()
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
