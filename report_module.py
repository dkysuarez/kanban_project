# report_module.py - Professional Report Generator
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import io
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

# IMPORTAR UI HELPERS
from ui_helpers import apply_global_styles, metric_card_with_percentage, get_current_date, get_timestamp_filename, render_info_message


def generate_basic_report(db):
    """Generate report according to document specification using SQLite database"""
    # Get data from database
    construction_sites = db.get_sites()
    employees = db.get_employees()

    # Get all assignments
    all_assignments = {}
    assigned_employee_ids = set()

    for site in construction_sites:
        site_id = site.get("id")
        if site_id:
            assigned_ids = db.get_assignments_for_site(site_id)
            if assigned_ids:
                all_assignments[site_id] = assigned_ids
                assigned_employee_ids.update(assigned_ids)

    # Structure according to PDF document
    report_json = {"Employees": []}

    # 1. Add ALL employees to "Employees" list (only unassigned)
    for emp in employees:
        emp_status = emp.get("status", "Active")

        # Solo agregar si NO está asignado
        if emp["id"] not in assigned_employee_ids:
            report_json["Employees"].append({
                "name": f"{emp['name']} {emp['surname']}",
                "employee_id": emp["employee_id"],
                "status": emp_status
            })

    # 2. For EACH site (active and inactive), create an entry
    for site in construction_sites:
        site_name = site["name"]
        site_status = site.get("status", "Active")

        # Initialize site entry with status
        report_json[site_name] = {
            "status": site_status,
            "employees": []
        }

        # 3. Add employees assigned to this site
        site_id = site.get("id")
        if site_id and site_id in all_assignments:
            assigned_emp_ids = all_assignments[site_id]
            for emp_id in assigned_emp_ids:
                emp_found = next((e for e in employees if e["id"] == emp_id), None)
                if emp_found:
                    report_json[site_name]["employees"].append({
                        "name": f"{emp_found['name']} {emp_found['surname']}",
                        "employee_id": emp_found["employee_id"],
                        "status": emp_found.get("status", "Active")
                    })

    return report_json, construction_sites, employees


def generate_clean_dataframe(db):
    """
    Generate clean DataFrame for professional export
    Returns DataFrame with columns: ['Employee Name', 'Employee ID', 'Assigned Site', 'Site Status', 'Employee Status', 'Report Date']
    """
    report_json, all_sites, all_employees = generate_basic_report(db)

    report_data = []
    current_date = get_current_date()

    # 1. Employees NOT assigned (Available or Inactive)
    for emp in report_json["Employees"]:
        emp_status = emp.get("status", "Active")
        emp_status_display = "Inactive" if emp_status == "Inactive" else "Available"

        report_data.append({
            "Employee Name": emp["name"],
            "Employee ID": emp["employee_id"],
            "Assigned Site": "Not Assigned",
            "Site Status": "N/A",
            "Employee Status": emp_status_display,
            "Report Date": current_date
        })

    # 2. Employees assigned to each site (active and inactive)
    for site in all_sites:
        site_name = site["name"]
        site_status = site.get("status", "Active")

        if site_name in report_json and "employees" in report_json[site_name]:
            for emp in report_json[site_name]["employees"]:
                emp_status = emp.get("status", "Active")
                emp_status_display = "Assigned" if emp_status == "Active" else "Assigned (Inactive)"

                report_data.append({
                    "Employee Name": emp["name"],
                    "Employee ID": emp["employee_id"],
                    "Assigned Site": site_name,
                    "Site Status": site_status,
                    "Employee Status": emp_status_display,
                    "Report Date": current_date
                })

    return pd.DataFrame(report_data), report_json, all_sites, all_employees


def generate_display_dataframe(db):
    """
    Generate DataFrame for visual display only
    """
    report_json, all_sites, all_employees = generate_basic_report(db)

    display_data = []
    current_date = get_current_date()

    # 1. Employees NOT assigned
    for emp in report_json["Employees"]:
        emp_status = emp.get("status", "Active")
        if emp_status == "Inactive":
            display_data.append({
                "Status": "⏸️ Inactive",
                "Employee Name": emp["name"],
                "Employee ID": emp["employee_id"],
                "Assigned Site": "Not Assigned",
                "Site Status": "N/A",
                "Date": current_date
            })
        else:
            display_data.append({
                "Status": "🟢 Available",
                "Employee Name": emp["name"],
                "Employee ID": emp["employee_id"],
                "Assigned Site": "Not Assigned",
                "Site Status": "N/A",
                "Date": current_date
            })

    # 2. Assigned employees by site (active and inactive)
    for site in all_sites:
        site_name = site["name"]
        site_status = site.get("status", "Active")
        site_status_display = "⏸️" if site_status == "Inactive" else "🏗️"

        if site_name in report_json and "employees" in report_json[site_name]:
            for emp in report_json[site_name]["employees"]:
                emp_status = emp.get("status", "Active")
                if emp_status == "Inactive":
                    display_data.append({
                        "Status": "✅ Assigned (Inactive)",
                        "Employee Name": emp["name"],
                        "Employee ID": emp["employee_id"],
                        "Assigned Site": f"{site_status_display} {site_name}",
                        "Site Status": site_status,
                        "Date": current_date
                    })
                else:
                    display_data.append({
                        "Status": "✅ Assigned",
                        "Employee Name": emp["name"],
                        "Employee ID": emp["employee_id"],
                        "Assigned Site": f"{site_status_display} {site_name}",
                        "Site Status": site_status,
                        "Date": current_date
                    })

    return pd.DataFrame(display_data), report_json, all_sites, all_employees


def log_email_sent(recipient, subject, status="sent", details=None):
    """Log email sending attempt"""
    if 'email_history' not in st.session_state:
        st.session_state.email_history = []

    log_entry = {
        "id": f"EMAIL-{len(st.session_state.email_history) + 1:04d}",
        "recipient": recipient,
        "subject": subject,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "details": details or {}
    }
    st.session_state.email_history.append(log_entry)
    return log_entry


def send_email_real(recipient, subject, body, attachment_data=None,
                    attachment_filename="report.csv", attachment_type="csv"):
    """
    Send email using SMTP (REAL implementation)
    """
    try:
        # Configuration
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587

        # Use environment variables for security
        sender_email = os.environ.get("EMAIL_USER", "demo@example.com")
        sender_password = os.environ.get("EMAIL_PASSWORD", "demo-password")

        # If using demo credentials, show warning
        demo_mode = sender_email == "demo@example.com"

        if demo_mode:
            st.warning("⚠️ Using demo mode. For real email sending, set environment variables:")
            st.code("""
            # In your terminal:
            export EMAIL_USER="your-email@gmail.com"
            export EMAIL_PASSWORD="your-app-password"

            # Or in Python:
            import os
            os.environ["EMAIL_USER"] = "your-email@gmail.com"
            os.environ["EMAIL_PASSWORD"] = "your-app-password"
            """)
            return {"status": "demo_mode", "message": "Set real email credentials to send"}

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        if attachment_data and attachment_filename:
            if attachment_type == "csv":
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                f'attachment; filename={attachment_filename}')
                msg.attach(part)
            elif attachment_type == "json":
                part = MIMEBase('application', 'json')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                f'attachment; filename={attachment_filename}')
                msg.attach(part)
            elif attachment_type == "xlsx":
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_data)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                f'attachment; filename={attachment_filename}')
                msg.attach(part)

        # Connect to SMTP server and send
        with st.spinner(f"Connecting to {SMTP_SERVER}..."):
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

        return {"status": "sent", "message": f"Email sent successfully to {recipient}"}

    except smtplib.SMTPAuthenticationError:
        return {"status": "error", "message": "Authentication failed. Check email credentials."}
    except smtplib.SMTPException as e:
        return {"status": "error", "message": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Error sending email: {str(e)}"}


def send_email_simulation(recipient, subject, body, attachment_data=None,
                          attachment_filename="report.csv", attachment_type="csv"):
    """
    Simulation mode for demo purposes
    """
    time.sleep(2)  # Simulate sending delay

    # Return simulated success
    return {
        "status": "sent_simulation",
        "message": f"[SIMULATION] Email would be sent to: {recipient}",
        "details": {
            "smtp_server": "smtp.gmail.com:587",
            "attachment": attachment_filename,
            "size": f"{len(attachment_data) if attachment_data else 0} bytes" if attachment_data else "No attachment"
        }
    }


def show_report_generator(db):
    """Main view of Report Generator - Professional Version"""

    # ========== APLICAR ESTILOS GLOBALES ==========
    apply_global_styles()

    # ========== CSS STYLES ESPECÍFICOS DEL REPORTE ==========
    st.markdown("""
    <style>
    /* METRIC CARDS */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #cbd5e1;
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1e40af;
        margin: 5px 0;
    }

    .metric-label {
        font-size: 12px;
        color: #475569;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* TABLES */
    .dataframe-container {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        margin: 20px 0;
    }

    /* SUCCESS MESSAGE */
    .success-box {
        background: #d1fae5;
        border-left: 5px solid #10b981;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Verify basic data exists
    sites = db.get_sites()
    employees = db.get_employees()

    if not sites:
        st.markdown(render_info_message(
            "⚠️ No Construction Sites Found",
            "First create construction sites in the Construction Site module.",
            "warning"
        ), unsafe_allow_html=True)
        return

    if not employees:
        st.markdown(render_info_message(
            "⚠️ No Employees Found",
            "First create employees in the Employees module.",
            "warning"
        ), unsafe_allow_html=True)
        return

    # ========== SYSTEM OVERVIEW METRICS ==========
    st.markdown('<h3 style="color: #1e40af; margin-bottom: 1rem;">📈 SYSTEM OVERVIEW</h3>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_sites = len(sites)
        active_sites = len([s for s in sites if s.get("status") == "Active"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_sites}/{total_sites}</div>
            <div class="metric-label">ACTIVE SITES</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        total_emps = len(employees)
        active_emps = len([e for e in employees if e.get("status") == "Active"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_emps}/{total_emps}</div>
            <div class="metric-label">ACTIVE EMPLOYEES</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        total_assigned = 0
        for site in sites:
            site_id = site.get("id")
            if site_id:
                assigned = db.get_assignments_for_site(site_id)
                total_assigned += len(assigned)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_assigned}</div>
            <div class="metric-label">ASSIGNMENTS</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        current_date = get_current_date()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{current_date}</div>
            <div class="metric-label">REPORT DATE</div>
        </div>
        """, unsafe_allow_html=True)

    # ========== SECTION 1: GENERATE REPORT ==========
    st.markdown("---")
    st.markdown('<h3 style="color: #1e40af; margin-bottom: 1rem;">📋 EMPLOYEE ASSIGNMENT REPORT</h3>',
                unsafe_allow_html=True)

    # Button to generate report
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("GENERATE REPORT",
                     type="primary",
                     use_container_width=True,
                     key="btn_generate_report"):
            st.session_state.generate_report = True

    # Generate and show report if button was pressed
    if st.session_state.get('generate_report', False):
        with st.spinner("Generating report..."):
            # Generate data for display
            df_display, report_json, all_sites_list, all_employees_list = generate_display_dataframe(db)

            # Generate clean data for export
            df_clean, _, _, _ = generate_clean_dataframe(db)

            # Calculate statistics
            assigned_count = len([r for r in df_clean.to_dict('records') if r['Assigned Site'] != 'Not Assigned'])
            available_count = len([r for r in df_clean.to_dict('records') if
                                   r['Assigned Site'] == 'Not Assigned' and r['Employee Status'] == 'Available'])
            inactive_unassigned = len([r for r in df_clean.to_dict('records') if
                                       r['Assigned Site'] == 'Not Assigned' and r['Employee Status'] == 'Inactive'])

            # Count active/inactive sites
            active_sites_count = len([s for s in all_sites_list if s.get("status") == "Active"])
            inactive_sites_count = len([s for s in all_sites_list if s.get("status") == "Inactive"])

            # Count active/inactive employees
            active_emps_count = len([e for e in all_employees_list if e.get("status") == "Active"])
            inactive_emps_count = len([e for e in all_employees_list if e.get("status") == "Inactive"])

            # Show success message
            st.markdown(render_info_message(
                "✅ REPORT GENERATED SUCCESSFULLY",
                f"Summary: {len(all_employees_list)} employees | {len(all_sites_list)} sites | {assigned_count} assignments",
                "success"
            ), unsafe_allow_html=True)

            # Show DataFrame for visual display
            st.markdown('<h4 style="color: #1e40af; margin: 1.5rem 0;">EMPLOYEE ASSIGNMENTS OVERVIEW</h4>',
                        unsafe_allow_html=True)

            if not df_display.empty:
                st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                st.dataframe(df_display, use_container_width=True, height=400)
                st.markdown('</div>', unsafe_allow_html=True)

            # ========== DOWNLOAD OPTIONS ==========
            st.markdown('<h4 style="color: #1e40af; margin: 1.5rem 0;">📥 EXPORT REPORT</h4>', unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"])

            current_date_str = get_timestamp_filename()
            report_date = get_current_date()
            report_time = datetime.now().strftime("%H:%M:%S")

            with tab1:
                # Excel with multiple sheets
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Sheet 1: Assignments (clean data)
                    df_clean.to_excel(writer, index=False, sheet_name='Assignments')

                    # Sheet 2: Report Info
                    summary_data = {
                        "Field": [
                            "Report Generated Date",
                            "Report Generated Time",
                            "Total Employees",
                            "Active Employees",
                            "Inactive Employees",
                            "Total Construction Sites",
                            "Active Sites",
                            "Inactive Sites",
                            "Assigned Employees",
                            "Available Employees",
                            "Inactive Unassigned Employees",
                            "Report Format",
                            "Generated By"
                        ],
                        "Value": [
                            report_date,
                            report_time,
                            len(all_employees_list),
                            active_emps_count,
                            inactive_emps_count,
                            len(all_sites_list),
                            active_sites_count,
                            inactive_sites_count,
                            assigned_count,
                            available_count,
                            inactive_unassigned,
                            "Employee Assignment Report",
                            "Construction Management System"
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Report Info')

                    # Sheet 3: Sites Summary (ALL sites - active and inactive)
                    sites_data = []
                    for site in all_sites_list:
                        site_name = site["name"]
                        site_status = site.get("status", "Active")

                        # Count employees assigned to this site
                        assigned_count_site = 0
                        if site_name in report_json and "employees" in report_json[site_name]:
                            assigned_count_site = len(report_json[site_name]["employees"])

                        sites_data.append({
                            "Site Name": site_name,
                            "Manager": site.get("manager", "N/A"),
                            "Assigned Employees": assigned_count_site,
                            "Status": site_status
                        })
                    pd.DataFrame(sites_data).to_excel(writer, index=False, sheet_name='Sites Summary')

                excel_bytes = output.getvalue()

                col_dl1, col_dl2, col_dl3 = st.columns(3)
                with col_dl2:
                    st.download_button(
                        label="DOWNLOAD EXCEL REPORT",
                        data=excel_bytes,
                        file_name=f"employee_assignments_{current_date_str}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_excel",
                        use_container_width=True
                    )

            with tab2:
                # CSV (clean data only)
                csv_data = df_clean.to_csv(index=False)
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                with col_dl2:
                    st.download_button(
                        label="DOWNLOAD CSV REPORT",
                        data=csv_data,
                        file_name=f"employee_assignments_{current_date_str}.csv",
                        mime="text/csv",
                        key="dl_csv",
                        use_container_width=True
                    )

            with tab3:
                # JSON (original format from PDF)
                json_data = {
                    "report_info": {
                        "generated_date": report_date,
                        "generated_time": report_time,
                        "total_employees": len(all_employees_list),
                        "active_employees": active_emps_count,
                        "inactive_employees": inactive_emps_count,
                        "total_sites": len(all_sites_list),
                        "active_sites": active_sites_count,
                        "inactive_sites": inactive_sites_count
                    },
                    "assignments": report_json
                }
                json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                with col_dl2:
                    st.download_button(
                        label="DOWNLOAD JSON REPORT",
                        data=json_str,
                        file_name=f"employee_assignments_{current_date_str}.json",
                        mime="application/json",
                        key="dl_json",
                        use_container_width=True
                    )

            # ========== REPORT STATISTICS ==========
            st.markdown("---")
            st.markdown('<h4 style="color: #1e40af; margin: 1.5rem 0;">📊 REPORT STATISTICS</h4>',
                        unsafe_allow_html=True)

            col_stat1, col_stat2, col_stat3 = st.columns(3)

            with col_stat1:
                assignment_rate = round((assigned_count / active_emps_count) * 100, 1) if active_emps_count > 0 else 0
                st.markdown(metric_card_with_percentage(
                    value=f"{assigned_count}/{active_emps_count}",
                    label="ASSIGNMENT RATE",
                    percentage=f"{assignment_rate}%",
                    color_scheme="blue"
                ), unsafe_allow_html=True)

            with col_stat2:
                sites_with_assignments = len([site for site in all_sites_list if
                                              site["name"] in report_json and "employees" in report_json[
                                                  site["name"]] and report_json[site["name"]]["employees"]])
                sites_rate = round((sites_with_assignments / active_sites_count) * 100,
                                   1) if active_sites_count > 0 else 0
                st.markdown(metric_card_with_percentage(
                    value=f"{sites_with_assignments}/{active_sites_count}",
                    label="SITES WITH ASSIGNMENTS",
                    percentage=f"{sites_rate}%",
                    color_scheme="green"
                ), unsafe_allow_html=True)

            with col_stat3:
                available_rate = round((available_count / active_emps_count) * 100, 1) if active_emps_count > 0 else 0
                st.markdown(metric_card_with_percentage(
                    value=str(available_count),
                    label="AVAILABLE EMPLOYEES",
                    percentage=f"{available_rate}%",
                    color_scheme="yellow"
                ), unsafe_allow_html=True)

    # ========== SECTION 2: EMAIL SENDING ==========
    st.markdown("---")
    st.markdown('<h3 style="color: #1e40af; margin-bottom: 1rem;">📧 SEND REPORT BY EMAIL</h3>', unsafe_allow_html=True)

    # Mode selection
    email_mode = st.radio(
        "Email Delivery Mode:",
        ["REAL SMTP (Production)", "SIMULATION (Demo)"],
        horizontal=True,
        help="Choose between real email sending or simulation for testing"
    )

    with st.form("email_form"):
        st.markdown("### Email Configuration")

        col1, col2 = st.columns(2)

        with col1:
            recipient_email = st.text_input(
                "Recipient Email Address:",
                placeholder="manager@construction-company.com",
                help="Enter the email where the report will be sent"
            )

            email_subject = st.text_input(
                "Email Subject:",
                value=f"Employee Assignments Report - {get_current_date()}",
                help="Subject line for the email"
            )

        with col2:
            report_format = st.selectbox(
                "Attachment Format:",
                ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"],
                help="Select the format for the report attachment"
            )

        email_message = st.text_area(
            "Custom Message:",
            value=f"""Dear Manager,

Please find attached the employee assignments report for your review.

Report Details:
- Date: {get_current_date()}
- Time: {datetime.now().strftime('%H:%M:%S')}
- Generated by: Construction Management System

This report includes all employees (active and inactive) and their assignments to construction sites.

Best regards,

Construction Management Team
---
Automated Report System""",
            height=150,
            help="Message to accompany the report"
        )

        # Submit button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button(
                "SEND REPORT",
                type="primary",
                use_container_width=True
            )

        if submitted:
            if recipient_email:
                with st.spinner("Preparing and sending email..."):
                    # Generate clean data for attachment
                    df_clean_email, report_json_email, active_sites_email, active_employees_email = generate_clean_dataframe(
                        db)

                    attachment_data = None
                    attachment_filename = None
                    attachment_type = "csv"

                    try:
                        if report_format == "Excel (.xlsx)":
                            # Create Excel
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                df_clean_email.to_excel(writer, index=False, sheet_name='Assignments')
                            attachment_data = output.getvalue()
                            attachment_filename = f"employee_assignments_{get_current_date('%Y%m%d')}.xlsx"
                            attachment_type = "xlsx"

                        elif report_format == "CSV (.csv)":
                            attachment_data = df_clean_email.to_csv(index=False)
                            attachment_filename = f"employee_assignments_{get_current_date('%Y%m%d')}.csv"
                            attachment_type = "csv"

                        elif report_format == "JSON (.json)":
                            # Count stats for JSON
                            active_sites_count = len([s for s in active_sites_email if s.get("status") == "Active"])
                            inactive_sites_count = len([s for s in active_sites_email if s.get("status") == "Inactive"])
                            active_emps_count = len([e for e in active_employees_email if e.get("status") == "Active"])
                            inactive_emps_count = len(
                                [e for e in active_employees_email if e.get("status") == "Inactive"])

                            json_data_email = {
                                "report_info": {
                                    "generated_date": get_current_date(),
                                    "generated_time": datetime.now().strftime("%H:%M:%S"),
                                    "total_employees": len(active_employees_email),
                                    "active_employees": active_emps_count,
                                    "inactive_employees": inactive_emps_count,
                                    "total_sites": len(active_sites_email),
                                    "active_sites": active_sites_count,
                                    "inactive_sites": inactive_sites_count
                                },
                                "assignments": report_json_email
                            }
                            attachment_data = json.dumps(json_data_email, indent=2)
                            attachment_filename = f"employee_assignments_{get_current_date('%Y%m%d')}.json"
                            attachment_type = "json"

                    except Exception as e:
                        st.warning(f"Could not generate attachment: {str(e)}")

                    # Send email based on selected mode
                    if email_mode == "REAL SMTP (Production)":
                        result = send_email_real(
                            recipient=recipient_email,
                            subject=email_subject,
                            body=email_message,
                            attachment_data=attachment_data,
                            attachment_filename=attachment_filename,
                            attachment_type=attachment_type
                        )
                    else:
                        result = send_email_simulation(
                            recipient=recipient_email,
                            subject=email_subject,
                            body=email_message,
                            attachment_data=attachment_data,
                            attachment_filename=attachment_filename,
                            attachment_type=attachment_type
                        )

                    # Show result
                    if result["status"] == "sent":
                        st.success(f"✅ Email sent successfully to {recipient_email}")
                        st.balloons()
                    elif result["status"] == "sent_simulation":
                        st.info(f"📨 SIMULATION MODE: Email would be sent to: {recipient_email}")
                        st.balloons()
                    else:
                        st.error(f"❌ Email failed: {result['message']}")

                    # Log the email
                    log_email_sent(
                        recipient=recipient_email,
                        subject=email_subject,
                        status=result["status"],
                        details={
                            "mode": email_mode,
                            "format": report_format,
                            "attachment": "Yes" if attachment_data else "No"
                        }
                    )
            else:
                st.error("Please enter a valid recipient email address.")


# Initialize session state if it doesn't exist
if 'generate_report' not in st.session_state:
    st.session_state.generate_report = False
if 'email_history' not in st.session_state:
    st.session_state.email_history = []