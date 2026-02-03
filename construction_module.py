# construction_module.py
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_searchbox import st_searchbox
import time

# IMPORTAR UI HELPERS
from ui_helpers import apply_global_styles, render_page_header, metric_card_simple, get_current_date


def search_construction_sites(search_term: str, db) -> list:
    """Search function for st_searchbox"""
    sites = db.get_sites()
    results = []
    for site in sites:
        if search_term.lower() in site['name'].lower():
            results.append(f"{site['name']} (ID: {site['id']})")
    return results


def show_construction_site(db):
    """Main view of Construction Site module"""

    # APLICAR ESTILOS GLOBALES
    apply_global_styles()

    # Fetch fresh data from DB
    sites = db.get_sites()

    # ========== MÉTRICAS MEJORADAS CON UI HELPERS ==========
    col1, col2, col3 = st.columns(3)

    with col1:
        total_sites = len(sites)
        st.markdown(metric_card_simple(
            value=total_sites,
            label="Total Sites",
            color_scheme="blue",
            icon="🏗️"
        ), unsafe_allow_html=True)

    with col2:
        active_sites = len([s for s in sites if s.get("status") == "Active"])
        st.markdown(metric_card_simple(
            value=active_sites,
            label="Active Sites",
            color_scheme="green",
            icon="✅"
        ), unsafe_allow_html=True)

    with col3:
        inactive_sites = len([s for s in sites if s.get("status") == "Inactive"])
        st.markdown(metric_card_simple(
            value=inactive_sites,
            label="Inactive Sites",
            color_scheme="red",
            icon="⏸️"
        ), unsafe_allow_html=True)

    st.markdown("---")

    # ========== FILTROS HORIZONTALES ==========
    st.markdown("""
    <style>
    .filters-section {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .filter-header {
        color: #1e40af;
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .dataframe-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-top: 15px;
    }

    /* BOTONES CON HOVER COOL */
    .create-button-cool {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    .create-button-cool:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3) !important;
    }

    .update-button-cool {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    .update-button-cool:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.3) !important;
    }

    .delete-button-cool {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    .delete-button-cool:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(239, 68, 68, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="filter-header">🔍 FILTERS & CONTROLS</p>', unsafe_allow_html=True)

    # Fila de filtros en horizontal
    search_col, status_col, columns_col = st.columns([3, 2, 3])

    with search_col:
        selected_site = st_searchbox(
            lambda term: search_construction_sites(term, db),
            placeholder="Search construction site by name...",
            label="Quick Search:",
            key="site_searchbox"
        )

    with status_col:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "Active", "Inactive"],
            key="status_filter_main",
            label_visibility="visible"
        )

    with columns_col:
        columns_to_show = st.multiselect(
            "Show columns:",
            ["id", "name", "manager", "phone", "creation_date", "status"],
            default=["id", "name", "manager", "status"],
            key="columns_selector",
            label_visibility="visible"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ========== DATAFRAME CON FILTROS APLICADOS ==========
    df = pd.DataFrame(sites)
    filtered_df = df.copy()

    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]

    if selected_site:
        site_name = selected_site.split(" (ID: ")[0]
        filtered_df = filtered_df[filtered_df["name"] == site_name]

    if columns_to_show:
        display_columns = []
        for col in columns_to_show:
            if col == "id":
                display_columns.append("ID")
            elif col == "name":
                display_columns.append("Construction Site")
            elif col == "manager":
                display_columns.append("Manager")
            elif col == "phone":
                display_columns.append("Phone Number")
            elif col == "creation_date":
                display_columns.append("Creation Date")
            elif col == "status":
                display_columns.append("Status")
            else:
                display_columns.append(col)

        filtered_df = filtered_df[columns_to_show]
        filtered_df.columns = display_columns

    # Función para estilizar el DataFrame
    def style_dataframe(df):
        if df.empty:
            return df.style

        # Estilizar celdas basado en status
        def color_status(val):
            if val == "Active":
                return 'background-color: #d1fae5; color: #065f46; font-weight: 600; padding: 4px 8px; border-radius: 4px;'
            elif val == "Inactive":
                return 'background-color: #fee2e2; color: #991b1b; font-weight: 600; padding: 4px 8px; border-radius: 4px;'
            return ''

        # Aplicar estilos
        if 'Status' in df.columns:
            styled = df.style.applymap(color_status, subset=['Status'])
        else:
            styled = df.style

        # Estilo general para la tabla
        styled = styled.set_properties(**{
            'border': '1px solid #e2e8f0',
            'padding': '8px',
            'border-radius': '4px'
        })

        # Estilo para encabezados
        styled = styled.set_table_styles([{
            'selector': 'th',
            'props': [
                ('background-color', '#1E88E5'),
                ('color', 'white'),
                ('font-weight', 'bold'),
                ('padding', '10px'),
                ('border-radius', '8px 8px 0 0')
            ]
        }])

        return styled

    # Mostrar DataFrame con estilos
    if not filtered_df.empty:
        styled_df = style_dataframe(filtered_df)
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(styled_df, use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📭 No construction sites found with the current filters")

    st.caption(f"📋 Showing {len(filtered_df)} of {len(sites)} construction sites")

    # ========== SECTION 2: TABS (CRUD) MEJORADOS ==========
    st.divider()
    st.markdown("<h3 style='color: #1e40af;'>🏗️ Site Management</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Create New Site", "✏️ Edit Existing Site", "🗑️ Delete Site"])

    # ---------- TAB 1: CREATE ----------
    with tab1:
        st.markdown("<h4 style='color: #059669;'>Create New Construction Site</h4>", unsafe_allow_html=True)

        st.info("💡 ID will be auto-generated by the system")

        # Formulario en dos columnas
        col1, col2 = st.columns(2)

        with col1:
            site_name = st.text_input(
                "Construction Site Name *",
                placeholder="e.g., Downtown Plaza Project",
                key="create_site_name",
                help="Enter the name of the construction site"
            )
            manager = st.text_input(
                "Manager *",
                placeholder="e.g., John Smith",
                key="create_manager",
                help="Project manager responsible for this site"
            )

        with col2:
            phone = st.text_input(
                "Phone Number",
                placeholder="(555) 123-4567",
                key="create_phone",
                help="Contact phone number (optional)"
            )
            creation_date = st.date_input(
                "Creation Date",
                value=datetime.now(),
                key="create_date",
                help="Date when this site was created"
            )
            status = st.selectbox(
                "Status",
                ["Active", "Inactive"],
                key="create_status",
                help="Initial status of the construction site"
            )

        # Botón con estilo cool
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Create Construction Site",
                         type="primary",
                         key="create_button",
                         use_container_width=True):
                if site_name and manager:
                    new_site = {
                        "name": site_name,
                        "manager": manager,
                        "phone": phone or None,
                        "creation_date": str(creation_date),
                        "status": status
                    }
                    try:
                        new_id = db.create_site(new_site)
                        st.success(f"✅ Construction site **'{site_name}'** created successfully! (ID: `{new_id}`)")
                        time.sleep(1)
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ Error creating site: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error: {str(e)}")
                else:
                    st.error("⚠️ Required fields: **Construction Site Name** and **Manager**")

    # ---------- TAB 2: MODIFY ----------
    with tab2:
        st.markdown("<h4 style='color: #1d4ed8;'>Edit Existing Construction Site</h4>", unsafe_allow_html=True)

        site_ids = [site["id"] for site in sites]

        if site_ids:
            # Selección del sitio
            selected_id = st.selectbox(
                "Select Site ID to edit:",
                site_ids,
                key="modify_select_id",
                help="Choose a site ID from the list"
            )

            selected_site = db.get_site_by_id(selected_id)

            if selected_site:
                st.info(f"📝 Editing: **{selected_site['name']}** (ID: `{selected_id}`)")

                # Formulario de edición
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input(
                        "Construction Site Name",
                        value=selected_site["name"],
                        key="modify_site_name"
                    )
                    new_manager = st.text_input(
                        "Manager",
                        value=selected_site["manager"],
                        key="modify_manager"
                    )

                with col2:
                    new_phone = st.text_input(
                        "Phone Number",
                        value=selected_site.get("phone", ""),
                        key="modify_phone"
                    )
                    new_status = st.selectbox(
                        "Status",
                        ["Active", "Inactive"],
                        index=0 if selected_site["status"] == "Active" else 1,
                        key="modify_status"
                    )

                # Botón de actualización con hover cool
                if st.button("🔄 Update Site",
                             type="primary",
                             key="modify_button",
                             use_container_width=True):
                    updated_data = {
                        "name": new_name,
                        "manager": new_manager,
                        "phone": new_phone or None,
                        "status": new_status
                    }
                    try:
                        if db.update_site(selected_id, updated_data):
                            st.success(f"✅ Site **'{new_name}'** updated successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("ℹ️ No changes applied or site not found.")
                    except Exception as e:
                        st.error(f"❌ Update error: {str(e)}")
        else:
            st.info("📭 No construction sites yet. Create one in the 'Create' tab.")

    # ---------- TAB 3: DELETE ----------
    with tab3:
        st.markdown("<h4 style='color: #dc2626;'>Delete Construction Site</h4>", unsafe_allow_html=True)

        site_ids = [site["id"] for site in sites]

        if site_ids:
            # Selección del sitio a eliminar
            delete_id = st.selectbox(
                "Select Site ID to delete:",
                site_ids,
                key="delete_select_id",
                help="Choose a site ID to delete"
            )

            selected_site = db.get_site_by_id(delete_id)

            if selected_site:
                # Mostrar información del sitio seleccionado
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); 
                            padding: 15px; border-radius: 10px; border-left: 4px solid #dc2626; 
                            margin-bottom: 20px;'>
                    <h4 style='color: #991b1b; margin: 0 0 10px 0;'>⚠️ Warning: Site Deletion</h4>
                    <p style='margin: 5px 0;'><strong>Site Name:</strong> {selected_site['name']}</p>
                    <p style='margin: 5px 0;'><strong>Manager:</strong> {selected_site['manager']}</p>
                    <p style='margin: 5px 0;'><strong>Status:</strong> {selected_site['status']}</p>
                    <p style='margin: 5px 0;'><strong>ID:</strong> {delete_id}</p>
                </div>
                """, unsafe_allow_html=True)

                st.warning("🚨 **This action cannot be undone!** All data for this site will be permanently deleted.")

                # Confirmación adicional
                confirm = st.checkbox("I understand this action is irreversible", key="delete_confirm")

                # Botón de eliminación con estilo rojo cool
                if confirm:
                    if st.button("🗑️ Delete Site Permanently",
                                 type="primary",
                                 key="delete_button",
                                 use_container_width=True):
                        if db.delete_site(delete_id):
                            st.success("✅ Site deleted successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Could not delete the site.")
                else:
                    st.info("🔒 Please check the confirmation box to enable deletion")
        else:
            st.info("📭 No sites available to delete.")