# ui_helpers.py
# Reusable UI components for Construction Management System
import streamlit as st
from datetime import datetime


def render_page_header(title, subtitle="", icon="📋"):
    """
    Render a professional page header with gradient background.

    Args:
        title (str): Main header title
        subtitle (str): Optional subtitle
        icon (str): Emoji icon for the header

    Returns:
        str: HTML string for the header
    """
    return f"""
    <div style='
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        border-radius: 12px;
    '>
        <h1 style='
            color: #0D47A1;
            font-size: 32px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        '>
            {icon} {title}
        </h1>
        <p style='
            color: #1565C0;
            font-size: 16px;
            margin: 0;
            font-weight: 500;
        '>
            {subtitle}
        </p>
    </div>
    """


def metric_card_simple(value, label, color_scheme="blue", icon=None):
    """
    Render a simple metric card with gradient background.

    Args:
        value (str/int): The main value to display
        label (str): Label for the metric
        color_scheme (str): One of "blue", "green", "red", "yellow", "gray"
        icon (str): Optional emoji icon

    Returns:
        str: HTML string for the metric card
    """
    # Color schemes
    colors = {
        "blue": {
            "bg_gradient": "#f0f7ff, #dbeafe",
            "border_color": "#93c5fd",
            "value_color": "#1e40af",
            "icon_color": "#3b82f6"
        },
        "green": {
            "bg_gradient": "#f0fff4, #dcfce7",
            "border_color": "#86efac",
            "value_color": "#065f46",
            "icon_color": "#10b981"
        },
        "red": {
            "bg_gradient": "#FFEBEE, #FFCDD2",
            "border_color": "#ef9a9a",
            "value_color": "#C62828",
            "icon_color": "#ef4444"
        },
        "yellow": {
            "bg_gradient": "#fef3c7, #fde68a",
            "border_color": "#fcd34d",
            "value_color": "#92400e",
            "icon_color": "#f59e0b"
        },
        "gray": {
            "bg_gradient": "#f3f4f6, #e5e7eb",
            "border_color": "#d1d5db",
            "value_color": "#374151",
            "icon_color": "#6b7280"
        }
    }

    # Get color scheme or default to blue
    scheme = colors.get(color_scheme, colors["blue"])

    # Build the HTML
    icon_html = f"<div style='font-size: 20px; color: {scheme['icon_color']}; margin-bottom: 5px;'>{icon}</div>" if icon else ""

    return f"""
    <div style='
        background: linear-gradient(135deg, {scheme['bg_gradient']});
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {scheme['border_color']};
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 1rem;
    '>
        {icon_html}
        <div style='
            font-size: 28px;
            font-weight: 700;
            color: {scheme['value_color']};
            margin: 5px 0;
        '>
            {value}
        </div>
        <div style='
            font-size: 12px;
            color: #475569;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        '>
            {label}
        </div>
    </div>
    """


def metric_card_with_percentage(value, label, percentage, color_scheme="blue"):
    """
    Render a metric card with a percentage indicator.

    Args:
        value (str): The main value (e.g., "3/4")
        label (str): Label for the metric
        percentage (str): Percentage value (e.g., "75%")
        color_scheme (str): Color scheme to use

    Returns:
        str: HTML string for the metric card
    """
    # Color schemes
    colors = {
        "blue": {
            "bg_gradient": "#f0f7ff, #dbeafe",
            "border_color": "#93c5fd",
            "value_color": "#1e40af",
            "percentage_color": "#3b82f6"
        },
        "green": {
            "bg_gradient": "#f0fff4, #dcfce7",
            "border_color": "#86efac",
            "value_color": "#065f46",
            "percentage_color": "#10b981"
        },
        "yellow": {
            "bg_gradient": "#fef3c7, #fde68a",
            "border_color": "#fcd34d",
            "value_color": "#92400e",
            "percentage_color": "#f59e0b"
        }
    }

    scheme = colors.get(color_scheme, colors["blue"])

    return f"""
    <div style='
        background: linear-gradient(135deg, {scheme['bg_gradient']});
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {scheme['border_color']};
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 1rem;
    '>
        <div style='
            font-size: 28px;
            font-weight: 700;
            color: {scheme['value_color']};
            margin: 5px 0;
        '>
            {value}
        </div>
        <div style='
            font-size: 12px;
            color: #475569;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        '>
            {label}
        </div>
        <div style='
            font-size: 11px;
            color: {scheme['percentage_color']};
            font-weight: 500;
            margin-top: 5px;
        '>
            {percentage}
        </div>
    </div>
    """


def get_current_date(format="%Y-%m-%d"):
    """
    Get current date formatted consistently.

    Args:
        format (str): Date format string

    Returns:
        str: Formatted date string
    """
    return datetime.now().strftime(format)


def get_current_datetime(format="%Y-%m-%d %H:%M:%S"):
    """
    Get current datetime formatted consistently.

    Args:
        format (str): Datetime format string

    Returns:
        str: Formatted datetime string
    """
    return datetime.now().strftime(format)


def get_timestamp_filename():
    """
    Get a timestamp string for use in filenames.

    Returns:
        str: Timestamp in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def apply_global_styles():
    """
    Apply minimal global CSS styles that are used across all modules.
    Call this function at the beginning of each module.
    """
    st.markdown("""
    <style>
    /* Consistent button styling */
    .stButton > button {
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
    }

    /* Active tab styling */
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5 !important;
        color: white !important;
    }

    /* Consistent tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }

    /* Consistent input styling */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
    }

    .stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }

    /* Consistent metric display */
    .dataframe-container {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e2e8f0;
        margin: 20px 0;
    }

    /* Success and warning boxes */
    .success-box {
        background: #d1fae5;
        border-left: 5px solid #10b981;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }

    .warning-box {
        background: #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_system_info_sidebar():
    """
    Render the system info section for the sidebar.

    Returns:
        str: HTML string for system info
    """
    current_time = datetime.now().strftime('%I:%M %p')
    current_date = datetime.now().strftime('%d/%m/%Y')

    return f"""
    <div style='
        background: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    '>
        <div style='display: flex; justify-content: space-between;'>
            <span style='color: #555; font-size: 13px;'>🕒 Time:</span>
            <span style='color: #0D47A1; font-weight: 600; font-size: 13px;'>{current_time}</span>
        </div>
        <div style='display: flex; justify-content: space-between; margin-top: 5px;'>
            <span style='color: #555; font-size: 13px;'>📅 Date:</span>
            <span style='color: #0D47A1; font-weight: 600; font-size: 13px;'>{current_date}</span>
        </div>
    </div>
    """


def render_info_message(title, message, message_type="info"):
    """
    Render a styled info/warning/success message.

    Args:
        title (str): Message title
        message (str): Message content
        message_type (str): One of "info", "warning", "success", "error"

    Returns:
        str: HTML string for the message
    """
    colors = {
        "info": {"bg": "#E3F2FD", "border": "#2196F3", "title": "#0D47A1"},
        "warning": {"bg": "#FFF3E0", "border": "#FF9800", "title": "#E65100"},
        "success": {"bg": "#E8F5E9", "border": "#4CAF50", "title": "#1B5E20"},
        "error": {"bg": "#FFEBEE", "border": "#F44336", "title": "#B71C1C"}
    }

    color = colors.get(message_type, colors["info"])

    return f"""
    <div style='
        background: {color['bg']};
        border-left: 4px solid {color['border']};
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    '>
        <h4 style='color: {color['title']}; margin: 0 0 10px 0;'>{title}</h4>
        <p style='margin: 0; color: #555; font-size: 14px;'>{message}</p>
    </div>
    """