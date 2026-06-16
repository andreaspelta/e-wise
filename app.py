from dataclasses import dataclass
from typing import List

import streamlit as st

st.set_page_config(
    page_title="E-WISE | Well builder",
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
    open_hole_diameter_in: float
    tubular_type: str
    tubular_od_in: float
    depth_md_mrkb: float
    drillpipe_od_in: float
    pore_gradient_sg: str
    fracture_gradient_sg: str
    mud_weight_kg_l: str
    mud_type: str
    lithology: str
    depleted_levels: str
    faults: str
    fractures: str
    ecd: bool
    mpd: bool
    enbd: bool
    annular_preventer_count: int
    pipe_ram_count: int
    blind_shear_ram_count: int
    casing_shear_ram_count: int
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

WELL_SECTIONS = ["DRILLING", "LOWER COMPLETION", "UPPER COMPLETION", "WELL TESTING", "P&A"]
WELLHEAD_TYPES = ["Unitized", "Flanged"]
XTREE_TYPES = ["Dry tee", "Subsea HXT", "Subsea VXT"]
SECONDARY_INTERVENTION_OPTIONS = ["None", "Single ROV", "Dual ROV"]
MUD_TYPES = ["WBM", "OBM"]
YES_NO_OPTIONS = ["Yes", "No"]
TUBULAR_TYPES = ["Casing", "Liner"]


def bootstrap_state() -> None:
    if "phase_library" not in st.session_state:
        st.session_state.phase_library = DEFAULT_PHASE_LIBRARY.copy()
    if "activity_library" not in st.session_state:
        st.session_state.activity_library = DEFAULT_ACTIVITY_LIBRARY.copy()
    if "lithology_library" not in st.session_state:
        st.session_state.lithology_library = DEFAULT_LITHOLOGY_LIBRARY.copy()
    if "phases" not in st.session_state:
        st.session_state.phases = []
    if "section_enabled" not in st.session_state:
        st.session_state.section_enabled = {section: section == "DRILLING" for section in WELL_SECTIONS}
    if "secondary_intervention" not in st.session_state:
        st.session_state.secondary_intervention = "None"
    if "acoustic_system" not in st.session_state:
        st.session_state.acoustic_system = False


def render_catalog_editor(title: str, item_label: str, state_key: str, add_key: str, remove_key: str) -> None:
    with st.expander(title, expanded=False):
        new_item = st.text_input(f"Add {item_label}", key=add_key)
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"Add {item_label}", key=f"{add_key}_button", use_container_width=True) and new_item.strip():
                if new_item.strip() not in st.session_state[state_key]:
                    st.session_state[state_key].append(new_item.strip())
        with c2:
            item_to_delete = st.selectbox(
                f"Remove {item_label}",
                options=[""] + st.session_state[state_key],
                key=remove_key,
            )
            if st.button(f"Remove {item_label}", key=f"{remove_key}_button", use_container_width=True) and item_to_delete:
                st.session_state[state_key] = [item for item in st.session_state[state_key] if item != item_to_delete]


def sidebar_admin() -> None:
    with st.sidebar:
        st.markdown("### Admin Configuration")
        st.caption("Manage the selectable catalogs used while building the well.")
        render_catalog_editor("Phase catalog", "phase", "phase_library", "new_phase", "phase_to_delete")
        render_catalog_editor("Activity catalog", "activity", "activity_library", "new_activity", "activity_to_delete")
        render_catalog_editor("Lithology catalog", "lithology", "lithology_library", "new_lithology", "lithology_to_delete")


def is_subsea_xtree(xtree_type: str) -> bool:
    return "subsea" in xtree_type.lower()


def render_well_header() -> None:
    st.header("Well configuration")
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Wellhead Type", WELLHEAD_TYPES, key="wellhead_type")
    with col2:
        xtree_type = st.selectbox("Xtree", XTREE_TYPES, key="xtree_type")

    if is_subsea_xtree(xtree_type):
        with st.container(border=True):
            st.markdown("#### Secondary Intervention System")
            st.radio(
                "ROV availability",
                SECONDARY_INTERVENTION_OPTIONS,
                key="secondary_intervention",
                horizontal=True,
            )
            st.checkbox("Acoustic System", key="acoustic_system")
    else:
        st.session_state.secondary_intervention = "None"
        st.session_state.acoustic_system = False



def render_section_activation(section: str) -> bool:
    st.session_state.setdefault(f"section_toggle_{section}", st.session_state.section_enabled.get(section, False))
    enabled = st.toggle(f"Activate {section}", key=f"section_toggle_{section}")
    st.session_state.section_enabled[section] = enabled
    return enabled


def add_drilling_phase_form() -> None:
    with st.container(border=True):
        st.markdown("#### Add next drilling phase")
        top_col1, top_col2, top_col3 = st.columns([2, 1, 1])
        with top_col1:
            phase_name = st.selectbox("Phase name", st.session_state.phase_library, key="new_phase_name")
        with top_col2:
            activity_count = st.number_input("Activities in sequence", min_value=1, max_value=20, value=1)
        with top_col3:
            tubular_type = st.selectbox("Tubular type", TUBULAR_TYPES, key="new_tubular_type")

        geometry_cols = st.columns(5)
        with geometry_cols[0]:
            open_hole_diameter = st.number_input("Open Hole (OH) diameter (in)", min_value=0.0, step=0.125, value=8.5)
        with geometry_cols[1]:
            tubular_od = st.number_input("OD tubular (in)", min_value=0.0, step=0.125, value=7.0)
        with geometry_cols[2]:
            depth_md_mrkb = st.number_input("Depth MD mRKB", min_value=0.0, step=10.0, value=1000.0)
        with geometry_cols[3]:
            drillpipe_od = st.number_input("Drillpipe OD (in)", min_value=0.0, step=0.125, value=5.0)
        with geometry_cols[4]:
            technology = st.multiselect("Drilling technology", ["e-cd", "MPD", "e-NBD"], key="new_drilling_technology")

        details_col1, details_col2, details_col3, details_col4 = st.columns(4)
        with details_col1:
            pore_gradient_sg = st.text_input("Max Pore Gradient (s.g.)")
            mud_type = st.selectbox("Mud Type", MUD_TYPES)
        with details_col2:
            fracture_gradient_sg = st.text_input("Min Fracture Gradient (s.g.)")
            mud_weight_kg_l = st.text_input("Mud weight (kg/L)")
        with details_col3:
            lithology = st.selectbox("Lithology", st.session_state.lithology_library)
            depleted_levels = st.selectbox("Depleted Levels", YES_NO_OPTIONS)
        with details_col4:
            faults = st.selectbox("Faults", YES_NO_OPTIONS)
            fractures = st.selectbox("Fractures", YES_NO_OPTIONS)

        bop_cols = st.columns(4)
        with bop_cols[0]:
            annular_preventer_count = st.number_input("Annular Preventer", min_value=1, max_value=2, value=1, step=1)
        with bop_cols[1]:
            pipe_ram_count = st.number_input("Pipe Ram", min_value=0, value=0, step=1)
        with bop_cols[2]:
            blind_shear_ram_count = st.number_input("Blind Shear Ram", min_value=0, value=0, step=1)
        with bop_cols[3]:
            casing_shear_ram_count = st.number_input("Casing Shear Ram", min_value=0, value=0, step=1)

        activities: List[ActivityItem] = []
        st.markdown("#### Activity sequence")
        for i in range(activity_count):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                activity_name = st.selectbox("Activity", st.session_state.activity_library, key=f"new_activity_name_{i}")
            with c2:
                duration = st.number_input("Duration", min_value=0.0, step=0.5, value=6.0, key=f"new_activity_time_{i}")
            with c3:
                unit = st.selectbox("Unit", ["hours", "days"], key=f"new_activity_unit_{i}")
            activities.append(ActivityItem(activity_name, float(duration), unit))

        if st.button("Add phase to drilling sequence", type="primary", use_container_width=True):
            st.session_state.phases.append(
                PhaseItem(
                    name=phase_name,
                    open_hole_diameter_in=float(open_hole_diameter),
                    tubular_type=tubular_type,
                    tubular_od_in=float(tubular_od),
                    depth_md_mrkb=float(depth_md_mrkb),
                    drillpipe_od_in=float(drillpipe_od),
                    pore_gradient_sg=pore_gradient_sg,
                    fracture_gradient_sg=fracture_gradient_sg,
                    mud_weight_kg_l=mud_weight_kg_l,
                    mud_type=mud_type,
                    lithology=lithology,
                    depleted_levels=depleted_levels,
                    faults=faults,
                    fractures=fractures,
                    ecd="e-cd" in technology,
                    mpd="MPD" in technology,
                    enbd="e-NBD" in technology,
                    annular_preventer_count=int(annular_preventer_count),
                    pipe_ram_count=int(pipe_ram_count),
                    blind_shear_ram_count=int(blind_shear_ram_count),
                    casing_shear_ram_count=int(casing_shear_ram_count),
                    activities=activities,
                )
            )
            st.success(f"Added phase: {phase_name}")


def render_drilling_sequence() -> None:
    st.markdown("#### Drilling phase sequence")
    if not st.session_state.phases:
        st.info("No drilling phase added yet. Add phases from first to last.")
        return

    for idx, phase in enumerate(st.session_state.phases, start=1):
        with st.expander(f"{idx}. {phase.name} — OH {phase.open_hole_diameter_in} in / {phase.tubular_type} OD {phase.tubular_od_in} in", expanded=True):
            st.markdown(
                f"""
                - **Depth MD mRKB**: {phase.depth_md_mrkb}
                - **Drillpipe OD (in)**: {phase.drillpipe_od_in}
                - **Max Pore Gradient (s.g.)**: {phase.pore_gradient_sg or '-'}
                - **Min Fracture Gradient (s.g.)**: {phase.fracture_gradient_sg or '-'}
                - **Mud weight (kg/L)**: {phase.mud_weight_kg_l or '-'}
                - **Mud Type**: {phase.mud_type}
                - **Lithology**: {phase.lithology}
                - **Depleted Levels / Faults / Fractures**: {phase.depleted_levels} / {phase.faults} / {phase.fractures}
                - **e-cd / MPD / e-NBD**: {'Yes' if phase.ecd else 'No'} / {'Yes' if phase.mpd else 'No'} / {'Yes' if phase.enbd else 'No'}
                - **Annular / Pipe Ram / Blind Shear Ram / Casing Shear Ram**: {phase.annular_preventer_count} / {phase.pipe_ram_count} / {phase.blind_shear_ram_count} / {phase.casing_shear_ram_count}
                """
            )
            for act_idx, act in enumerate(phase.activities, start=1):
                st.markdown(f"- **Activity {act_idx} · {act.name}** — Duration: {act.duration_value} {act.duration_unit}")
            if st.button(f"Delete phase {idx}", key=f"delete_{idx}", use_container_width=True):
                st.session_state.phases.pop(idx - 1)
                st.rerun()


def render_drilling_section() -> None:
    left, right = st.columns([1.25, 1])
    with left:
        add_drilling_phase_form()
    with right:
        render_drilling_sequence()


def render_placeholder_section(section: str) -> None:
    with st.container(border=True):
        st.info(f"{section} is active. Detailed inputs for this macro section can now be configured in the next iteration.")


def render_well_sections() -> None:
    st.header("Well construction")
    tabs = st.tabs(WELL_SECTIONS)
    for section, tab in zip(WELL_SECTIONS, tabs):
        with tab:
            if not render_section_activation(section):
                st.info("This section is screened until activated.")
                continue
            if section == "DRILLING":
                render_drilling_section()
            else:
                render_placeholder_section(section)


def render_summary() -> None:
    with st.expander("Well build summary", expanded=False):
        st.markdown(
            f"""
            - **Wellhead Type**: {st.session_state.get('wellhead_type', '-')}
            - **Xtree**: {st.session_state.get('xtree_type', '-')}
            - **Secondary Intervention System**: {st.session_state.secondary_intervention if is_subsea_xtree(st.session_state.get('xtree_type', '')) else '-'}
            - **Acoustic System**: {'Yes' if st.session_state.acoustic_system and is_subsea_xtree(st.session_state.get('xtree_type', '')) else 'No'}
            - **Active sections**: {', '.join(section for section, enabled in st.session_state.section_enabled.items() if enabled) or '-'}
            - **Drilling phases**: {len(st.session_state.phases)}
            """
        )


def main() -> None:
    bootstrap_state()
    sidebar_admin()

    st.title("E-WISE Well Builder")
    st.write("Build the complete well on a single page before submitting it for blowout probability evaluation.")

    render_well_header()
    render_well_sections()
    render_summary()


if __name__ == "__main__":
    main()
