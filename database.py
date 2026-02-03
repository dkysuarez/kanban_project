# database.py
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Any


class ConstructionDB:
    def __init__(self, db_path: str = "construction_system.db"):
        self.db_path = db_path
        self.init_database()
        self._seed_initial_data()  # datos de ejemplo solo si está vacío

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_database(self):
        """Crear tablas si no existen – ahora con AUTOINCREMENT"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabla construction_sites – ID autoincremental
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS construction_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                manager TEXT,
                phone TEXT,
                creation_date TEXT,
                status TEXT CHECK(status IN ('Active', 'Inactive'))
            )
        ''')

        # Tabla employees – ID autoincremental
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                employee_id TEXT UNIQUE,
                creation_date TEXT,
                status TEXT CHECK(status IN ('Active', 'Inactive'))
            )
        ''')

        # Tabla assignments (sin cambios)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER,
                employee_id INTEGER,
                assignment_date TEXT,
                UNIQUE(site_id, employee_id),
                FOREIGN KEY (site_id) REFERENCES construction_sites(id) ON DELETE CASCADE,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def _seed_initial_data(self):
        """Inserta datos de ejemplo SOLO si las tablas están vacías"""
        if len(self.get_sites()) == 0:
            initial_sites = [
                {"name": "12 Buildings in Minnesota", "manager": "Juan Pérez", "phone": "555-0101", "creation_date": "2024-01-15", "status": "Active"},
                {"name": "Soccer Camp NYC", "manager": "María Gómez", "phone": "555-0102", "creation_date": "2024-02-20", "status": "Active"},
                {"name": "Central Building", "manager": "Carlos Ruiz", "phone": "555-0103", "creation_date": "2024-03-10", "status": "Active"}
            ]
            for site in initial_sites:
                self.create_site(site)

        if len(self.get_employees()) == 0:
            initial_employees = [
                {"name": "Luis", "surname": "Fernández", "employee_id": "SS-12345", "creation_date": "2024-01-10", "status": "Active"},
                {"name": "Sofía", "surname": "Martínez", "employee_id": "SS-12346", "creation_date": "2024-02-15", "status": "Active"},
                {"name": "Roberto", "surname": "Díaz", "employee_id": "SS-12347", "creation_date": "2024-01-20", "status": "Inactive"},
                {"name": "Ana", "surname": "Gómez", "employee_id": "SS-12348", "creation_date": "2024-03-01", "status": "Active"}
            ]
            for emp in initial_employees:
                self.create_employee(emp)

    # ────────────────────────────────────────────────
    # CONSTRUCTION_SITES
    # ────────────────────────────────────────────────

    def get_sites(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM construction_sites"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        conn = self._get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df.to_dict(orient="records")

    def get_site_by_id(self, site_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM construction_sites WHERE id = ?", (site_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def create_site(self, data: Dict[str, Any]) -> int:
        """Inserta y retorna el ID generado automáticamente"""
        required = {"name", "status"}
        if not all(k in data for k in required):
            raise ValueError("Faltan campos requeridos: name, status")

        fields = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        values = tuple(data.values())

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO construction_sites ({fields}) VALUES ({placeholders})", values)
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def update_site(self, site_id: int, data: Dict[str, Any]) -> bool:
        if "id" in data:
            del data["id"]
        if not data:
            return True

        sets = ", ".join(f"{k} = ?" for k in data)
        values = tuple(data.values()) + (site_id,)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE construction_sites SET {sets} WHERE id = ?", values)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def delete_site(self, site_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM construction_sites WHERE id = ?", (site_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # ────────────────────────────────────────────────
    # EMPLOYEES (mismo patrón)
    # ────────────────────────────────────────────────

    def get_employees(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM employees"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        conn = self._get_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df.to_dict(orient="records")

    def get_employee_by_id(self, emp_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def create_employee(self, data: Dict[str, Any]) -> int:
        required = {"name", "surname", "employee_id", "status"}
        if not all(k in data for k in required):
            raise ValueError("Faltan campos requeridos")

        conn_check = self._get_connection()
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT 1 FROM employees WHERE employee_id = ?", (data["employee_id"],))
        if cursor_check.fetchone():
            conn_check.close()
            raise ValueError(f"El ID Seguridad Social {data['employee_id']} ya está en uso")
        conn_check.close()

        fields = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        values = tuple(data.values())

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO employees ({fields}) VALUES ({placeholders})", values)
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def update_employee(self, emp_id: int, data: Dict[str, Any]) -> bool:
        if "id" in data:
            del data["id"]

        if "employee_id" in data:
            conn_check = self._get_connection()
            cursor_check = conn_check.cursor()
            cursor_check.execute(
                "SELECT 1 FROM employees WHERE employee_id = ? AND id != ?",
                (data["employee_id"], emp_id)
            )
            if cursor_check.fetchone():
                conn_check.close()
                raise ValueError("El ID Seguridad Social ya está en uso por otro empleado")
            conn_check.close()

        if not data:
            return True

        sets = ", ".join(f"{k} = ?" for k in data)
        values = tuple(data.values()) + (emp_id,)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE employees SET {sets} WHERE id = ?", values)
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def delete_employee(self, emp_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    # ────────────────────────────────────────────────
    # ASSIGNMENTS (sin cambios por ahora)
    # ────────────────────────────────────────────────

    def get_assignments_for_site(self, site_id: int) -> List[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id FROM assignments WHERE site_id = ?", (site_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def assign_employee_to_site(self, site_id: int, emp_id: int, assignment_date: Optional[str] = None) -> bool:
        if assignment_date is None:
            assignment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO assignments (site_id, employee_id, assignment_date) VALUES (?, ?, ?)",
                (site_id, emp_id, assignment_date)
            )
            inserted = cursor.rowcount > 0
            conn.commit()
            return inserted
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def remove_assignment(self, site_id: int, emp_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assignments WHERE site_id = ? AND employee_id = ?", (site_id, emp_id))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    def reset_database(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS assignments")
        cursor.execute("DROP TABLE IF EXISTS employees")
        cursor.execute("DROP TABLE IF EXISTS construction_sites")
        conn.commit()
        conn.close()
        self.init_database()
        self._seed_initial_data()