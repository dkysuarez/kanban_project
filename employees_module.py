# employees_module.py
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_searchbox import st_searchbox
import time

# IMPORTAR UI HELPERS
from ui_helpers import apply_global_styles, render_page_header, metric_card_simple, get_current_date


def search_employees(search_term: str, db):
    """Search function for st_searchbox"""
    employees = db.get_employees()
    results = []
    for emp in employees:
        full_name = f"{emp['name']} {emp['surname']}"
        if search_term.lower() in full_name.lower():
            results.append(f"{full_name} (ID: {emp['id']})")
    return results


def show_employees(db):
    """Main view of Employees module"""

    # APLICAR ESTILOS GLOBALES
    apply_global_styles()

    # Get fresh data from DB
    employees = db.get_employees()

    # ========== MÉTRICAS MEJORADAS CON UI HELPERS ==========
    col1, col2, col3 = st.columns(3)

    with col1:
        total_employees = len(employees)
        st.markdown(metric_card_simple(
            value=total_employees,
            label="Total Employees",
            color_scheme="blue",
            icon="👷"
        ), unsafe_allow_html=True)

    with col2:
        active_employees = len([e for e in employees if e.get("status") == "Active"])
        st.markdown(metric_card_simple(
            value=active_employees,
            label="Active Employees",
            color_scheme="green",
            icon="✅"
        ), unsafe_allow_html=True)

    with col3:
        inactive_employees = len([e for e in employees if e.get("status") == "Inactive"])
        st.markdown(metric_card_simple(
            value=inactive_employees,
            label="Inactive Employees",
            color_scheme="red",
            icon="⏸️"
        ), unsafe_allow_html=True)

    st.markdown("---")

    # ========== FILTROS HORIZONTALES ==========
    st.markdown("""
    <style>
    .filters-section-employees {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .filter-header-employees {
        color: #1e40af;
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 14px;
    }
    .dataframe-container-employees {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        margin-top: 15px;
    }

    /* BOTONES CON HOVER COOL - EMPLEADOS */
    .create-button-employees {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    .create-button-employees:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(16, 185, 129, 0.3) !important;
    }

    .update-button-employees {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    .update-button-employees:hover {
        background: linear-gradient(135deg, #2563eb, #1e40af) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.3) !important;
    }

    .delete-button-employees {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
    }
    .delete-button-employees:hover {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(239, 68, 68, 0.3) !important;
    }

    /* COLOR DE STATUS EN DATAFRAME */
    .status-active {
        background-color: #d1fae5 !important;
        color: #065f46 !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
    }
    .status-inactive {
        background-color: #fee2e2 !important;
        color: #991b1b !important;
        font-weight: 600 !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="filter-header-employees">🔍 FILTERS & CONTROLS</p>', unsafe_allow_html=True)

    # Fila de filtros en horizontal
    search_col, status_col, columns_col = st.columns([3, 2, 3])

    with search_col:
        selected_employee = st_searchbox(
            lambda term: search_employees(term, db),
            placeholder="Search employee by name...",
            label="Quick Search:",
            key="emp_searchbox"
        )

    with status_col:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "Active", "Inactive"],
            key="emp_status_filter",
            label_visibility="visible"
        )

    with columns_col:
        columns_to_show = st.multiselect(
            "Show columns:",
            ["id", "name", "surname", "employee_id", "creation_date", "status"],
            default=["id", "name", "surname", "employee_id", "status"],
            key="emp_columns_selector",
            label_visibility="visible"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ========== DATAFRAME CON FILTROS APLICADOS ==========
    df = pd.DataFrame(employees)
    filtered_df = df.copy()

    # Aplicar filtros
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["status"] == status_filter]

    if selected_employee:
        employee_name = selected_employee.split(" (ID: ")[0]
        name_parts = employee_name.split()
        if len(name_parts) >= 2:
            filtered_df = filtered_df[
                (filtered_df["name"] == name_parts[0]) &
                (filtered_df["surname"] == name_parts[1])
                ]
        elif len(name_parts) == 1:
            filtered_df = filtered_df[
                (filtered_df["name"] == name_parts[0]) |
                (filtered_df["surname"] == name_parts[0])
                ]

    if columns_to_show:
        display_columns = []
        for col in columns_to_show:
            if col == "id":
                display_columns.append("ID")
            elif col == "name":
                display_columns.append("Name")
            elif col == "surname":
                display_columns.append("Surname")
            elif col == "employee_id":
                display_columns.append("Employee ID")
            elif col == "creation_date":
                display_columns.append("Creation Date")
            elif col == "status":
                display_columns.append("Status")
            else:
                display_columns.append(col)

        filtered_df = filtered_df[columns_to_show]
        filtered_df.columns = display_columns

    # Función para estilizar el DataFrame
    def style_employees_dataframe(df):
        if df.empty:
            return df.style

        # Crear una copia para no modificar el original
        styled_df = df.copy()

        # Aplicar clases CSS para status
        if 'Status' in df.columns:
            def format_status(val):
                if val == "Active":
                    return 'background-color: #d1fae5; color: #065f46; font-weight: 600; padding: 4px 8px; border-radius: 4px;'
                elif val == "Inactive":
                    return 'background-color: #fee2e2; color: #991b1b; font-weight: 600; padding: 4px 8px; border-radius: 4px;'
                return ''

            styled = df.style.applymap(format_status, subset=['Status'])
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
        styled_df = style_employees_dataframe(filtered_df)
        st.markdown('<div class="dataframe-container-employees">', unsafe_allow_html=True)
        st.dataframe(styled_df, use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📭 No employees found with the current filters")

    st.caption(f"📋 Showing {len(filtered_df)} of {len(employees)} employees")

    # ========== SECTION 2: TABS (CRUD) MEJORADOS ==========
    st.divider()
    st.markdown("<h3 style='color: #1e40af;'>👷 Employee Management</h3>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Create New Employee", "✏️ Edit Existing Employee", "🗑️ Delete Employee"])

    # ---------- TAB 1: CREATE ----------
    with tab1:
        st.markdown("<h4 style='color: #059669;'>Create New Employee</h4>", unsafe_allow_html=True)

        st.info("💡 ID will be auto-generated by the system")

        # Formulario en dos columnas
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "First Name *",
                placeholder="e.g., John",
                key="emp_create_name",
                help="Employee's first name"
            )
            surname = st.text_input(
                "Last Name *",
                placeholder="e.g., Smith",
                key="emp_create_surname",
                help="Employee's last name"
            )

        with col2:
            id_employee = st.text_input(
                "Employee ID *",
                placeholder="e.g., EMP-001",
                key="emp_create_id_employee",
                help="Unique employee identifier"
            )
            creation_date = st.date_input(
                "Creation Date",
                value=datetime.now(),
                key="emp_create_date",
                help="Date when this employee was added"
            )
            status = st.selectbox(
                "Status",
                ["Active", "Inactive"],
                key="emp_create_status",
                help="Employment status"
            )

        # Botón con estilo cool
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Create Employee",
                         type="primary",
                         key="emp_create_button",
                         use_container_width=True):
                if name and surname and id_employee:
                    new_employee = {
                        "name": name,
                        "surname": surname,
                        "employee_id": id_employee,
                        "creation_date": str(creation_date),
                        "status": status
                    }
                    try:
                        new_id = db.create_employee(new_employee)
                        st.success(f"✅ Employee **'{name} {surname}'** created successfully! (ID: `{new_id}`)")
                        time.sleep(1)
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ Error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Unexpected error creating employee: {str(e)}")
                else:
                    st.error("⚠️ Required fields: **First Name**, **Last Name**, **Employee ID**")

    # ---------- TAB 2: MODIFY ----------
    with tab2:
        st.markdown("<h4 style='color: #1d4ed8;'>Edit Existing Employee</h4>", unsafe_allow_html=True)

        emp_ids = [emp["id"] for emp in employees]

        if emp_ids:
            # Selección del empleado
            selected_id = st.selectbox(
                "Select Employee ID to edit:",
                emp_ids,
                key="emp_modify_select_id",
                help="Choose an employee ID from the list"
            )

            selected_emp = db.get_employee_by_id(selected_id)

            if selected_emp:
                st.info(f"📝 Editing: **{selected_emp['name']} {selected_emp['surname']}** (ID: `{selected_id}`)")

                # Formulario de edición
                col1, col2 = st.columns(2)

                with col1:
                    new_name = st.text_input(
                        "First Name",
                        value=selected_emp["name"],
                        key="emp_modify_name"
                    )
                    new_surname = st.text_input(
                        "Last Name",
                        value=selected_emp["surname"],
                        key="emp_modify_surname"
                    )

                with col2:
                    new_id_emp = st.text_input(
                        "Employee ID",
                        value=selected_emp["employee_id"],
                        key="emp_modify_id_employee"
                    )
                    new_status = st.selectbox(
                        "Status",
                        ["Active", "Inactive"],
                        index=0 if selected_emp["status"] == "Active" else 1,
                        key="emp_modify_status"
                    )

                # Botón de actualización con hover cool
                if st.button("🔄 Update Employee",
                             type="primary",
                             key="emp_modify_button",
                             use_container_width=True):
                    updated_data = {
                        "name": new_name,
                        "surname": new_surname,
                        "employee_id": new_id_emp,
                        "status": new_status
                    }
                    try:
                        if db.update_employee(selected_id, updated_data):
                            st.success(f"✅ Employee **'{new_name} {new_surname}'** updated successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("ℹ️ No changes applied or employee not found.")
                    except ValueError as e:
                        st.error(f"❌ Error: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error updating employee: {str(e)}")
        else:
            st.info("📭 No employees yet. Create one in the 'Create' tab.")

    # ---------- TAB 3: DELETE ----------
    with tab3:
        st.markdown("<h4 style='color: #dc2626;'>Delete Employee</h4>", unsafe_allow_html=True)

        emp_ids = [emp["id"] for emp in employees]

        if emp_ids:
            # Selección del empleado a eliminar
            delete_id = st.selectbox(
                "Select Employee ID to delete:",
                emp_ids,
                key="emp_delete_select_id",
                help="Choose an employee ID to delete"
            )

            selected_emp = db.get_employee_by_id(delete_id)

            if selected_emp:
                # Mostrar información del empleado seleccionado
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #fee2e2, #fecaca); 
                            padding: 15px; border-radius: 10px; border-left: 4px solid #dc2626; 
                            margin-bottom: 20px;'>
                    <h4 style='color: #991b1b; margin: 0 0 10px 0;'>⚠️ Warning: Employee Deletion</h4>
                    <p style='margin: 5px 0;'><strong>Employee:</strong> {selected_emp['name']} {selected_emp['surname']}</p>
                    <p style='margin: 5px 0;'><strong>Employee ID:</strong> {selected_emp['employee_id']}</p>
                    <p style='margin: 5px 0;'><strong>Status:</strong> {selected_emp['status']}</p>
                    <p style='margin: 5px 0;'><strong>Database ID:</strong> {delete_id}</p>
                </div>
                """, unsafe_allow_html=True)

                st.warning(
                    "🚨 **This action cannot be undone!** All data for this employee will be permanently deleted.")

                # Confirmación adicional
                confirm = st.checkbox("I understand this action is irreversible", key="emp_delete_confirm")

                # Botón de eliminación con estilo rojo cool
                if confirm:
                    if st.button("🗑️ Delete Employee Permanently",
                                 type="primary",
                                 key="emp_delete_button",
                                 use_container_width=True):
                        if db.delete_employee(delete_id):
                            st.success("✅ Employee deleted successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Could not delete the employee.")
                else:
                    st.info("🔒 Please check the confirmation box to enable deletion")
        else:
            st.info("📭 No employees available to delete.")