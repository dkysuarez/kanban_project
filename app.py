# app.py - CONSTRUCTION MANAGEMENT SYSTEM
import streamlit as st
from datetime import datetime
import time
from database import ConstructionDB

# IMPORTAR UI HELPERS
from ui_helpers import render_page_header, render_system_info_sidebar, apply_global_styles

# ========== CONFIGURACIÓN ==========
st.set_page_config(
    page_title="Construction Management System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# APLICAR ESTILOS GLOBALES
apply_global_styles()


# ========== INICIALIZAR BASE DE DATOS ==========
@st.cache_resource
def init_database():
    return ConstructionDB()


db = init_database()


# ========== LOADING SCREEN ==========
def show_cool_loading_screen():
    st.markdown("""
    <style>
    /* OCULTAR TODOS LOS ELEMENTOS DE STREAMLIT */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* PANTALLA COMPLETA DE CARGA */
    .loading-fullscreen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        color: white;
    }

    /* MENSAJE DE BIENVENIDA */
    .welcome-message {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: center;
        background: linear-gradient(135deg, #ffffff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .welcome-subtitle {
        font-size: 18px;
        font-weight: 300;
        margin-bottom: 40px;
        text-align: center;
        opacity: 0.9;
    }

    .pulse-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin: 30px 0; 
    }

    .pulse-circle {
        width: 100px; 
        height: 100px; 
        background: white; 
        border-radius: 50%; 
        position: relative;
        animation: pulse 2s infinite; 
        display: flex; 
        align-items: center; 
        justify-content: center;
        font-size: 50px; 
        color: #764ba2;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    .pulse-circle::before, .pulse-circle::after {
        content: ''; 
        position: absolute; 
        border: 2px solid white; 
        border-radius: 50%;
        width: 100%; 
        height: 100%; 
        animation: ripple 2s infinite;
        opacity: 0.7;
    }

    .pulse-circle::after { 
        animation-delay: 0.5s; 
    }

    @keyframes pulse { 
        0% { 
            transform: scale(0.95); 
            box-shadow: 0 0 0 0 rgba(255,255,255,0.7); 
        }
        70% { 
            transform: scale(1); 
            box-shadow: 0 0 0 30px rgba(255,255,255,0); 
        }
        100% { 
            transform: scale(0.95); 
            box-shadow: 0 0 0 0 rgba(255,255,255,0); 
        } 
    }

    @keyframes ripple { 
        0% { 
            transform: scale(1); 
            opacity: 1; 
        } 
        100% { 
            transform: scale(2); 
            opacity: 0; 
        } 
    }

    .loading-text { 
        font-size: 20px; 
        font-weight: 300; 
        margin-top: 30px; 
        text-align: center; 
        opacity: 0.8;
    }

    .progress-container { 
        width: 400px; 
        height: 6px; 
        background: rgba(255,255,255,0.2); 
        border-radius: 3px; 
        margin-top: 30px; 
        overflow: hidden; 
    }

    .progress-bar { 
        height: 100%; 
        background: linear-gradient(90deg, #ffffff, #f0f0f0); 
        width: 0%; 
        border-radius: 3px; 
        animation: progress 2.5s ease-in-out; 
    }

    @keyframes progress { 
        0% { 
            width: 0%; 
        } 
        100% { 
            width: 100%; 
        } 
    }

    /* OCULTAR CONTENIDO MIENTRAS CARGA */
    .app-content {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # PANTALLA DE CARGA CON MENSAJE DE BIENVENIDA
    st.markdown("""
    <div class='loading-fullscreen'>
        <div class='welcome-message'>🚧 Construction Management System</div>
        <div class='welcome-subtitle'>Professional Site & Employee Management</div>
        <div class='pulse-container'>
            <div class='pulse-circle'>🏗️</div>
        </div>
        <div class='loading-text'>Initializing system components...</div>
        <div class='progress-container'>
            <div class='progress-bar'></div>
        </div>
        <div style='margin-top: 20px; font-size: 12px; opacity: 0.6;'>
            Loading sites, employees and assignments...
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Esperar 3 segundos
    time.sleep(3)


# ========== IMPORTAR MÓDULOS ==========
from construction_module import show_construction_site
from employees_module import show_employees
from report_module import show_report_generator


# ========== KANBAN BOARD PRINCIPAL ==========
def show_kanban_board():
    """Show the main Kanban board for assignments - CORREGIDO"""

    st.markdown(render_page_header(
        "Assignment Board",
        "Assign ACTIVE employees to ACTIVE construction sites",
        icon="📋"
    ), unsafe_allow_html=True)

    # ========== FILTROS SOLO ACTIVOS ==========
    # SOLO sitios ACTIVOS para el Kanban
    sites = [s for s in db.get_sites() if s.get("status") == "Active" and s.get("id") is not None]

    # SOLO empleados ACTIVOS para el Kanban
    all_employees = db.get_employees()
    employees = [e for e in all_employees if e.get("status") == "Active" and e.get("id") is not None]

    if not sites:
        st.warning("⚠️ No active construction sites available.")
        return
    if not employees:
        st.warning("⚠️ No active employees available.")
        return

    # CSS con hover y estilo profesional
    st.markdown("""
    <style>
    .kanban-container { display: flex; gap: 15px; overflow-x: auto; padding: 10px 0; }
    .kanban-column { flex: 1; min-width: 250px; background: #f8f9fa; border-radius: 12px; padding: 15px; border: 2px solid #e9ecef; display: flex; flex-direction: column; }
    .available-column { background: #f0f7ff; border: 2px dashed #1E88E5; }
    .employee-card-compact {
        display: flex; justify-content: space-between; align-items: center;
        background: white; border-radius: 8px; padding: 8px 10px; margin: 4px 0;
        border-left: 4px solid #4CAF50; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.25s ease;
    }
    .employee-card-compact:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .assigned-employee-card { border-left: 4px solid #1E88E5; }
    .employee-info { display: flex; align-items: center; gap: 8px; }
    .remove-x {
        background: #f44336 !important; color: white !important;
        border-radius: 50% !important; width: 28px !important; height: 28px !important;
        font-size: 16px !important; line-height: 28px !important; padding: 0 !important;
        min-width: unset !important; border: none !important;
    }
    .remove-x:hover { background: #d32f2f !important; transform: scale(1.1); }
    .site-buttons-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
    .site-header {
        text-align: center; padding: 12px; border-radius: 10px; margin-bottom: 15px;
        border-bottom: 3px solid; min-height: 100px; display: flex; flex-direction: column;
        justify-content: center; transition: all 0.3s ease;
    }
    .site-header:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .available-header { background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-bottom-color: #4CAF50; }
    .site-name { font-size: 15px; font-weight: 600; margin: 0; line-height: 1.3; }
    .site-manager { font-size: 12px; color: #555; margin: 4px 0 0 0; }
    .site-id { font-size: 10px; color: #777; background: #f0f0f0; padding: 2px 6px; border-radius: 4px; margin-top: 4px; display: inline-block; }
    .employee-name { font-size: 13px; font-weight: 600; color: #222; }
    .employee-id { font-size: 11px; color: #666; background: #f5f5f5; padding: 2px 6px; border-radius: 6px; }
    .assign-button { background: #2196F3 !important; color: white !important; font-size: 13px !important; padding: 4px 10px !important; }
    .assign-button:hover { background: #1976D2 !important; }
    .refresh-button { 
        background: linear-gradient(135deg, #42A5F5, #2196F3) !important;
        color: white !important; 
        border: none !important;
        font-weight: 600 !important;
    }
    .refresh-button:hover { 
        background: linear-gradient(135deg, #2196F3, #1976D2) !important; 
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3) !important;
    }
    .report-button { 
        background: linear-gradient(135deg, #1E88E5, #1565C0) !important;
        color: white !important; 
        border: none !important;
        font-weight: 600 !important;
    }
    .report-button:hover { 
        background: linear-gradient(135deg, #1565C0, #0D47A1) !important; 
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    columns = st.columns(len(sites) + 1)

    # ========== COLUMNA "AVAILABLE EMPLOYEES" ==========
    with columns[0]:
        st.markdown("""
        <div class='site-header available-header'>
            <h3 style='margin:0; color:#2E7D32;'>👷 Available Employees</h3>
            <p style='margin:6px 0 0; font-size:11px; color:#555;'>ACTIVE employees not assigned to ANY site</p>
        </div>
        """, unsafe_allow_html=True)

        # Obtener TODAS las asignaciones de TODOS los sitios (activos e inactivos)
        all_assigned_ids = set()
        all_sites_in_db = db.get_sites()  # Todos los sitios (activos e inactivos)

        for site in all_sites_in_db:
            site_id = site.get("id")
            if site_id:
                all_assigned_ids.update(db.get_assignments_for_site(site_id))

        # Solo empleados ACTIVOS que NO estén asignados a NINGÚN sitio
        avail = [e for e in employees if e["id"] not in all_assigned_ids]

        if avail:
            for emp in avail:
                st.markdown(f"""
                <div class='employee-card-compact'>
                    <div class='employee-info'>
                        <div class='employee-name'>Emp: {emp['id']}</div>
                        <span class='employee-id'>{emp['employee_id']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="site-buttons-row">', unsafe_allow_html=True)
                for site in sites:
                    sid = site.get("id")
                    if sid is None: continue
                    key = f"assign_{emp['id']}_{sid}"
                    if st.button(f"📌 {sid}", key=key, help=f"Assign to {site['name']}", type="secondary"):
                        if db.assign_employee_to_site(sid, emp["id"]):
                            st.success(f"Assigned to {site['name']} ✓")
                            time.sleep(0.3)
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<hr style="margin:6px 0; border-color:#eee;">', unsafe_allow_html=True)
        else:
            st.info("📭 No available active employees")

    # ========== COLUMNAS DE SITIOS ACTIVOS ==========
    for i, site in enumerate(sites, 1):
        with columns[i]:
            sid = site.get("id")
            if sid is None: continue

            st.markdown(f"""
            <div class='site-header' style='background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-bottom-color: #1E88E5;'>
                <p class='site-name'>🏗️ {site['name']}</p>
                <p class='site-manager'>Manager: {site.get('manager', '—')}</p>
                <span class='site-id'>ID: {sid}</span>
            </div>
            """, unsafe_allow_html=True)

            # Obtener asignaciones de este sitio
            assigned_emp_ids = db.get_assignments_for_site(sid)

            # Filtrar solo empleados ACTIVOS que estén asignados a este sitio
            assigned = [e for e in employees if e["id"] in assigned_emp_ids]

            if assigned:
                for emp in assigned:
                    st.markdown(f"""
                    <div class='employee-card-compact assigned-employee-card'>
                        <div class='employee-info'>
                            <div class='employee-name'>Emp: {emp['id']}</div>
                            <span class='employee-id'>{emp['employee_id']}</span>
                        </div>
                        <div>
                    """, unsafe_allow_html=True)

                    if st.button("❌", key=f"rm_{sid}_{emp['id']}", help=f"Remove from {site['name']}",
                                 type="secondary"):
                        if db.remove_assignment(sid, emp["id"]):
                            st.success(f"Removed from {site['name']} ✓")
                            time.sleep(0.3)
                            st.rerun()

                    st.markdown("</div></div>", unsafe_allow_html=True)
                    st.markdown('<hr style="margin:4px 0; border-color:#eee;">', unsafe_allow_html=True)
            else:
                st.info("📭 Empty – assign from Available column")

    # ========== CONTROLES INFERIORES ==========
    st.divider()
    c1, c2, c3 = st.columns(3)

    with c1:
        # Contador de asignaciones en sitios ACTIVOS
        total_assignments = sum(len(db.get_assignments_for_site(s["id"])) for s in sites if s.get("id"))

        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        '>
            <div style='font-size: 26px; color: #0D47A1; font-weight: 700;'>
                {total_assignments}
            </div>
            <div style='font-size: 13px; color: #1565C0; font-weight: 500;'>
                📋 Active Assignments
            </div>
            <div style='font-size: 10px; color: #1E88E5; margin-top: 4px;'>
                ({len(sites)} active sites)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        # BOTÓN REFRESH VIEW - CORREGIDO
        if st.button("🔄 Refresh View", use_container_width=True, key="refresh_kanban",
                     help="Remove all assignments from ACTIVE sites only",
                     type="primary"):

            assignments_to_remove = []

            # Solo remover asignaciones de sitios ACTIVOS
            for site in sites:  # sites ya son solo los activos
                site_id = site.get("id")
                if site_id:
                    assignments = db.get_assignments_for_site(site_id)
                    for emp_id in assignments:
                        assignments_to_remove.append((site_id, emp_id))

            # Remover las asignaciones
            removed_count = 0
            for site_id, emp_id in assignments_to_remove:
                if db.remove_assignment(site_id, emp_id):
                    removed_count += 1

            # Mostrar mensaje
            if removed_count > 0:
                success_msg = st.empty()
                success_msg.success(f"✅ {removed_count} employees unassigned from active sites!")
                time.sleep(1.5)
                success_msg.empty()
            else:
                st.info("No assignments to reset from active sites")
                time.sleep(0.5)

            # Refrescar
            st.rerun()

    with c3:
        # BOTÓN GENERATE REPORT
        if st.button("📊 Generate Report", use_container_width=True, key="to_report",
                     type="primary"):
            st.session_state.selected_page = "Reports"
            st.rerun()


# ========== SIDEBAR Y MAIN ==========
def render_sidebar():
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <div style='
                font-size: 28px;
                color: #1E88E5;
                margin-bottom: 5px;
            '>🏗️</div>
            <div style='
                font-size: 18px;
                color: #0D47A1;
                font-weight: 700;
                margin-bottom: 3px;
            '>CMS</div>
            <div style='
                font-size: 11px;
                color: #1565C0;
                opacity: 0.8;
            '>Construction Management</div>
        </div>
        """, unsafe_allow_html=True)

        # Mensaje de bienvenida
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
            border-radius: 10px;
            padding: 12px;
            margin: 10px 0 20px 0;
            text-align: center;
        '>
            <div style='font-size: 14px; color: #0D47A1; font-weight: 600;'>
                👋 Welcome Back!
            </div>
            <div style='font-size: 11px; color: #1565C0; margin-top: 4px;'>
                Manage construction operations
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Navegación
        st.markdown("### 🧭 Navigation")
        pages = ["Assignment Board", "Construction Sites", "Employees", "Reports"]
        sel = st.selectbox("Go to:", pages,
                           index=pages.index(st.session_state.get('selected_page', pages[0])),
                           label_visibility="collapsed")

        if sel != st.session_state.get('selected_page'):
            st.session_state.selected_page = sel
            st.rerun()

        st.divider()

        # Información del sistema - USANDO UI HELPERS
        st.markdown("### 📊 System Info")
        st.markdown(render_system_info_sidebar(), unsafe_allow_html=True)

        # Información adicional del sistema
        total_sites = len(db.get_sites())
        active_sites = len([s for s in db.get_sites() if s.get("status") == "Active"])
        total_employees = len(db.get_employees())
        active_employees = len([e for e in db.get_employees() if e.get("status") == "Active"])

        st.markdown(f"""
        <div style='
            background: #f8f9fa;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        '>
            <div style='display: flex; justify-content: space-between;'>
                <span style='color: #555; font-size: 13px;'>🏗️ Sites:</span>
                <span style='color: #0D47A1; font-weight: 600; font-size: 13px;'>{active_sites}/{total_sites}</span>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 5px;'>
                <span style='color: #555; font-size: 13px;'>👷 Employees:</span>
                <span style='color: #0D47A1; font-weight: 600; font-size: 13px;'>{active_employees}/{total_employees}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.caption("v2.1 • Professional Edition • Active Filtering")


def main():
    # ========== PANTALLA DE CARGA INICIAL ==========
    if 'initial_loaded' not in st.session_state:
        # Mostrar pantalla de carga completa
        show_cool_loading_screen()
        st.session_state.initial_loaded = True

        # Mostrar mensaje de bienvenida después de cargar
        welcome_msg = st.empty()
        welcome_msg.success("✅ Sistema cargado exitosamente | Construction Management System")
        time.sleep(1.5)
        welcome_msg.empty()

        st.rerun()

    # ========== SIDEBAR ==========
    render_sidebar()

    # ========== MOSTRAR CONTENIDO PRINCIPAL ==========
    # Agregar CSS para mostrar contenido después de cargar
    st.markdown("""
    <style>
    /* Mostrar contenido después de cargar */
    .app-content {
        display: block !important;
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Mejorar botones Refresh y Report */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: linear-gradient(135deg, #42A5F5, #2196F3) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #2196F3, #1976D2) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Envolver contenido principal en div para control de visibilidad
    st.markdown('<div class="app-content">', unsafe_allow_html=True)

    # ========== NAVEGACIÓN POR PÁGINAS ==========
    page = st.session_state.get('selected_page', 'Assignment Board')

    if page == "Assignment Board":
        show_kanban_board()

    elif page == "Construction Sites":
        st.markdown(render_page_header(
            "Construction Sites",
            "Manage your construction sites and projects",
            icon="🏗️"
        ), unsafe_allow_html=True)
        show_construction_site(db)

    elif page == "Employees":
        st.markdown(render_page_header(
            "Employees",
            "Manage employee information and assignments",
            icon="👷"
        ), unsafe_allow_html=True)
        show_employees(db)

    elif page == "Reports":
        st.markdown(render_page_header(
            "Reports",
            "Generate reports and analytics",
            icon="📄"
        ), unsafe_allow_html=True)
        show_report_generator(db)

    # Cerrar div del contenido
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== FOOTER ==========
    st.divider()

    # Footer mejorado
    st.markdown("""
    <div style='
        text-align: center;
        padding: 15px;
        color: #555;
        font-size: 14px;
    '>
        <div>🏗️ <strong>Construction Management System v2.1</strong> • 2026</div>
        <div style='font-size: 12px; color: #777; margin-top: 5px;'>
            Professional Construction Site & Employee Management | Active Filtering Enabled
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()