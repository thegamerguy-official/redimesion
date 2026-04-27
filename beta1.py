import os
import math
import sqlite3
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Tuple

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


DB_FILE = os.path.join(os.path.dirname(__file__), "redimension.db")


# =========================
# Modelos y utilidades
# =========================


@dataclass(frozen=True)
class TemplateItem:
    item_id: int
    kind: str  # "Caja" o "Producto"
    name: str
    largo: float
    ancho: float
    alto: float

    @property
    def volume(self) -> float:
        return self.largo * self.ancho * self.alto


@dataclass(frozen=True)
class InstanceItem:
    label: str
    kind: str
    largo: float
    ancho: float
    alto: float
    template_id: int

    @property
    def volume(self) -> float:
        return self.largo * self.ancho * self.alto


@dataclass(frozen=True)
class Placement:
    label: str
    kind: str
    x: float
    y: float
    z: float
    largo: float
    ancho: float
    alto: float
    template_id: int


@dataclass(frozen=True)
class Space:
    x: float
    y: float
    z: float
    largo: float
    ancho: float
    alto: float

    @property
    def volume(self) -> float:
        return self.largo * self.ancho * self.alto


def unique_orientations(largo: float, ancho: float, alto: float):
    seen = set()
    for dims in [
        (largo, ancho, alto),
        (largo, alto, ancho),
        (ancho, largo, alto),
        (ancho, alto, largo),
        (alto, largo, ancho),
        (alto, ancho, largo),
    ]:
        if dims not in seen:
            seen.add(dims)
            yield dims


def contains_space(a: Space, b: Space, eps: float = 1e-9) -> bool:
    return (
        b.x >= a.x - eps
        and b.y >= a.y - eps
        and b.z >= a.z - eps
        and b.x + b.largo <= a.x + a.largo + eps
        and b.y + b.ancho <= a.y + a.ancho + eps
        and b.z + b.alto <= a.z + a.alto + eps
    )


def prune_spaces(spaces: List[Space]) -> List[Space]:
    cleaned = []
    for s in spaces:
        if s.largo > 1e-9 and s.ancho > 1e-9 and s.alto > 1e-9:
            cleaned.append(s)

    result = []
    for i, s in enumerate(cleaned):
        dominated = False
        for j, other in enumerate(cleaned):
            if i != j and contains_space(other, s):
                dominated = True
                break
        if not dominated:
            result.append(s)
    return result


def split_space(space: Space, item_dims: Tuple[float, float, float]) -> List[Space]:
    iw, id_, ih = item_dims

    right = Space(
        space.x + iw,
        space.y,
        space.z,
        space.largo - iw,
        space.ancho,
        space.alto,
    )
    front = Space(
        space.x,
        space.y + id_,
        space.z,
        iw,
        space.ancho - id_,
        space.alto,
    )
    top = Space(
        space.x,
        space.y,
        space.z + ih,
        iw,
        id_,
        space.alto - ih,
    )
    return [right, front, top]


def heuristic_pack(
    container: Tuple[float, float, float],
    items: List[InstanceItem],
) -> Tuple[List[Placement], List[InstanceItem]]:
    container_l, container_a, container_h = container
    spaces = [Space(0, 0, 0, container_l, container_a, container_h)]
    placed: List[Placement] = []
    remaining = sorted(items, key=lambda it: (it.volume, max(it.largo, it.ancho, it.alto)), reverse=True)

    for item in remaining:
        best = None
        best_score = None

        for si, space in enumerate(spaces):
            for dims in unique_orientations(item.largo, item.ancho, item.alto):
                iw, id_, ih = dims
                if iw <= space.largo + 1e-9 and id_ <= space.ancho + 1e-9 and ih <= space.alto + 1e-9:
                    leftover_volume = space.volume - (iw * id_ * ih)
                    # Puntuación: menor volumen sobrante, después menor hueco total, después más cercano al origen.
                    score = (
                        leftover_volume,
                        (space.largo - iw) + (space.ancho - id_) + (space.alto - ih),
                        space.x + space.y + space.z,
                    )
                    if best_score is None or score < best_score:
                        best_score = score
                        best = (si, space, dims)

        if best is None:
            return placed, [item] + [x for x in remaining if x not in {p for p in placed}]

        space_index, space, dims = best
        iw, id_, ih = dims
        placement = Placement(
            label=item.label,
            kind=item.kind,
            x=space.x,
            y=space.y,
            z=space.z,
            largo=iw,
            ancho=id_,
            alto=ih,
            template_id=item.template_id,
        )
        placed.append(placement)

        new_spaces = split_space(space, dims)
        spaces.pop(space_index)
        spaces.extend(new_spaces)
        spaces = prune_spaces(spaces)

    return placed, []


# =========================
# Persistencia SQLite
# =========================


class Database:
    def __init__(self, path: str):
        self.path = path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _init_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS boxes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    largo REAL NOT NULL,
                    ancho REAL NOT NULL,
                    alto REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    largo REAL NOT NULL,
                    ancho REAL NOT NULL,
                    alto REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    largo REAL NOT NULL,
                    ancho REAL NOT NULL,
                    alto REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    result_text TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS project_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    template_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    qty INTEGER NOT NULL,
                    largo REAL NOT NULL,
                    ancho REAL NOT NULL,
                    alto REAL NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id)
                )
                """
            )
            conn.commit()

    def add_template(self, kind: str, name: str, largo: float, ancho: float, alto: float):
        table = "boxes" if kind == "Caja" else "products"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                f"INSERT INTO {table} (name, largo, ancho, alto, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, largo, ancho, alto, datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()

    def delete_template(self, kind: str, item_id: int):
        table = "boxes" if kind == "Caja" else "products"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
            conn.commit()

    def list_templates(self, kind: str) -> List[TemplateItem]:
        table = "boxes" if kind == "Caja" else "products"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT id, name, largo, ancho, alto FROM {table} ORDER BY id DESC")
            rows = cur.fetchall()
        return [TemplateItem(r[0], kind, r[1], float(r[2]), float(r[3]), float(r[4])) for r in rows]

    def get_template_by_id(self, kind: str, item_id: int) -> Optional[TemplateItem]:
        table = "boxes" if kind == "Caja" else "products"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT id, name, largo, ancho, alto FROM {table} WHERE id = ?", (item_id,))
            row = cur.fetchone()
        if not row:
            return None
        return TemplateItem(row[0], kind, row[1], float(row[2]), float(row[3]), float(row[4]))

    def save_project(self, name: str, largo: float, ancho: float, alto: float, items: List[Dict], result_text: str) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO projects (name, largo, ancho, alto, created_at, result_text) VALUES (?, ?, ?, ?, ?, ?)",
                (name, largo, ancho, alto, datetime.now().isoformat(timespec="seconds"), result_text),
            )
            project_id = cur.lastrowid
            for it in items:
                cur.execute(
                    """
                    INSERT INTO project_items
                    (project_id, kind, template_id, name, qty, largo, ancho, alto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        it["kind"],
                        it["template_id"],
                        it["name"],
                        it["qty"],
                        it["largo"],
                        it["ancho"],
                        it["alto"],
                    ),
                )
            conn.commit()
        return project_id


# =========================
# Widgets genéricos
# =========================


class TemplatePage(ttk.Frame):
    def __init__(self, parent, app, kind: str):
        super().__init__(parent)
        self.app = app
        self.kind = kind
        self.selected_id: Optional[int] = None

        header = ttk.Frame(self)
        header.pack(fill="x", padx=16, pady=(16, 8))

        title = "Gestión de cajas" if kind == "Caja" else "Gestión de productos"
        subtitle = (
            "Introduce y guarda las dimensiones de cada caja."
            if kind == "Caja"
            else "Introduce y guarda las dimensiones de cada producto."
        )

        ttk.Label(header, text=title, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(header, text=subtitle).pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=16, pady=16)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(body, text="Nuevo registro")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.name_var = tk.StringVar()
        self.largo_var = tk.StringVar()
        self.ancho_var = tk.StringVar()
        self.alto_var = tk.StringVar()

        self._build_form(form)

        list_frame = ttk.LabelFrame(body, text="Base de datos")
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("id", "name", "largo", "ancho", "alto"),
            show="headings",
            height=12,
        )
        for col, txt, width in [
            ("id", "ID", 60),
            ("name", "Nombre", 180),
            ("largo", "Largo", 90),
            ("ancho", "Ancho", 90),
            ("alto", "Alto", 90),
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        controls = ttk.Frame(list_frame)
        controls.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        ttk.Button(controls, text="Eliminar seleccionado", command=self.delete_selected).pack(side="left")
        ttk.Button(controls, text="Refrescar", command=self.refresh).pack(side="left", padx=8)

        self.refresh()

    def _build_form(self, parent):
        pad = {"padx": 12, "pady": 6}
        ttk.Label(parent, text="Nombre").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(parent, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", **pad)

        ttk.Label(parent, text="Largo (X)").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(parent, textvariable=self.largo_var).grid(row=3, column=0, sticky="ew", **pad)

        ttk.Label(parent, text="Ancho (Y)").grid(row=4, column=0, sticky="w", **pad)
        ttk.Entry(parent, textvariable=self.ancho_var).grid(row=5, column=0, sticky="ew", **pad)

        ttk.Label(parent, text="Alto (Z)").grid(row=6, column=0, sticky="w", **pad)
        ttk.Entry(parent, textvariable=self.alto_var).grid(row=7, column=0, sticky="ew", **pad)

        ttk.Button(parent, text="Guardar", command=self.save).grid(row=8, column=0, sticky="ew", padx=12, pady=(10, 14))
        parent.columnconfigure(0, weight=1)

    def _parse_float(self, var: tk.StringVar, field_name: str) -> float:
        raw = var.get().strip().replace(",", ".")
        if not raw:
            raise ValueError(f"Falta el campo {field_name}.")
        value = float(raw)
        if value <= 0:
            raise ValueError(f"{field_name} debe ser mayor que 0.")
        return value

    def save(self):
        try:
            name = self.name_var.get().strip()
            if not name:
                raise ValueError("El nombre no puede estar vacío.")
            largo = self._parse_float(self.largo_var, "Largo")
            ancho = self._parse_float(self.ancho_var, "Ancho")
            alto = self._parse_float(self.alto_var, "Alto")
            self.app.db.add_template(self.kind, name, largo, ancho, alto)
            self.name_var.set("")
            self.largo_var.set("")
            self.ancho_var.set("")
            self.alto_var.set("")
            self.refresh()
            self.app.refresh_project_controls()
            messagebox.showinfo("Guardado", f"{self.kind} guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        templates = self.app.db.list_templates(self.kind)
        for item in templates:
            self.tree.insert(
                "",
                "end",
                values=(item.item_id, item.name, f"{item.largo:.2f}", f"{item.ancho:.2f}", f"{item.alto:.2f}"),
            )

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])

    def delete_selected(self):
        if self.selected_id is None:
            messagebox.showwarning("Atención", "Selecciona un registro para eliminar.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar {self.kind.lower()} ID {self.selected_id}?"):
            return
        self.app.db.delete_template(self.kind, self.selected_id)
        self.selected_id = None
        self.refresh()
        self.app.refresh_project_controls()


class ProjectPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.project_name_var = tk.StringVar(value="Proyecto nuevo")
        self.van_largo_var = tk.StringVar()
        self.van_ancho_var = tk.StringVar()
        self.van_alto_var = tk.StringVar()
        self.kind_var = tk.StringVar(value="Caja")
        self.template_var = tk.StringVar()
        self.qty_var = tk.IntVar(value=1)
        self.project_items: Dict[Tuple[str, int], Dict] = {}
        self.canvas = None
        self.figure = None
        self.ax = None

        header = ttk.Frame(self)
        header.pack(fill="x", padx=16, pady=(16, 8))
        ttk.Label(header, text="Nuevo proyecto", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(header, text="Selecciona cajas y productos, define el furgón y ejecuta el algoritmo heurístico.").pack(anchor="w", pady=(4, 0))

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=16, pady=16)
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        self._build_left_panel(left)
        self._build_right_panel(right)
        self.refresh_template_choices()

    def _build_left_panel(self, parent):
        project_box = ttk.LabelFrame(parent, text="Datos del proyecto")
        project_box.pack(fill="x", pady=(0, 12))

        def add_field(row, label, var):
            ttk.Label(project_box, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=(8 if row == 0 else 4, 2))
            ttk.Entry(project_box, textvariable=var, width=24).grid(row=row + 1, column=0, sticky="ew", padx=10, pady=(0, 6))

        add_field(0, "Nombre del proyecto", self.project_name_var)
        add_field(2, "Largo del furgón (X)", self.van_largo_var)
        add_field(4, "Ancho del furgón (Y)", self.van_ancho_var)
        add_field(6, "Alto del furgón (Z)", self.van_alto_var)
        project_box.columnconfigure(0, weight=1)

        add_box = ttk.LabelFrame(parent, text="Añadir cajas / productos")
        add_box.pack(fill="x", pady=(0, 12))

        ttk.Label(add_box, text="Tipo").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 3))
        kind = ttk.Combobox(add_box, textvariable=self.kind_var, values=["Caja", "Producto"], state="readonly", width=22)
        kind.grid(row=1, column=0, sticky="ew", padx=10)
        kind.bind("<<ComboboxSelected>>", lambda e: self.refresh_template_choices())

        ttk.Label(add_box, text="Elemento").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 3))
        self.template_combo = ttk.Combobox(add_box, textvariable=self.template_var, state="readonly", width=22)
        self.template_combo.grid(row=3, column=0, sticky="ew", padx=10)

        ttk.Label(add_box, text="Cantidad").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 3))
        qty = ttk.Spinbox(add_box, from_=1, to=500, textvariable=self.qty_var, width=10)
        qty.grid(row=5, column=0, sticky="w", padx=10)

        ttk.Button(add_box, text="Añadir al proyecto", command=self.add_item).grid(row=6, column=0, sticky="ew", padx=10, pady=12)
        add_box.columnconfigure(0, weight=1)

        actions = ttk.LabelFrame(parent, text="Acciones")
        actions.pack(fill="x")
        ttk.Button(actions, text="Calcular y dibujar", command=self.calculate).pack(fill="x", padx=10, pady=(10, 6))
        ttk.Button(actions, text="Limpiar proyecto", command=self.clear_project).pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(actions, text="Guardar proyecto", command=self.save_project).pack(fill="x", padx=10, pady=(0, 10))

    def _build_right_panel(self, parent):
        summary = ttk.LabelFrame(parent, text="Resumen del proyecto")
        summary.grid(row=0, column=0, sticky="ew")
        summary.columnconfigure(0, weight=1)

        self.summary_label = ttk.Label(summary, text="Añade cajas y productos para empezar.", justify="left")
        self.summary_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        items_frame = ttk.LabelFrame(parent, text="Elementos seleccionados")
        items_frame.grid(row=1, column=0, sticky="ew", pady=12)
        items_frame.columnconfigure(0, weight=1)

        self.items_tree = ttk.Treeview(
            items_frame,
            columns=("kind", "name", "qty", "largo", "ancho", "alto"),
            show="headings",
            height=6,
        )
        for col, txt, width in [
            ("kind", "Tipo", 80),
            ("name", "Nombre", 180),
            ("qty", "Cant.", 60),
            ("largo", "Largo", 80),
            ("ancho", "Ancho", 80),
            ("alto", "Alto", 80),
        ]:
            self.items_tree.heading(col, text=txt)
            self.items_tree.column(col, width=width, anchor="center")
        self.items_tree.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.result_frame = ttk.LabelFrame(parent, text="Resultado 3D")
        self.result_frame.grid(row=2, column=0, sticky="nsew")
        self.result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)

        self.result_placeholder = ttk.Label(self.result_frame, text="Aquí aparecerá la representación 3D.")
        self.result_placeholder.grid(row=0, column=0, padx=10, pady=10)

    def parse_positive(self, var: tk.StringVar, field_name: str) -> float:
        raw = var.get().strip().replace(",", ".")
        if not raw:
            raise ValueError(f"Falta el campo {field_name}.")
        value = float(raw)
        if value <= 0:
            raise ValueError(f"{field_name} debe ser mayor que 0.")
        return value

    def refresh_template_choices(self):
        kind = self.kind_var.get()
        templates = self.app.db.list_templates(kind)
        self.templates_by_name = {f"{t.name} (ID {t.item_id})": t for t in templates}
        values = list(self.templates_by_name.keys())
        self.template_combo["values"] = values
        if values:
            self.template_var.set(values[0])
        else:
            self.template_var.set("")

    def add_item(self):
        try:
            kind = self.kind_var.get()
            template_name = self.template_var.get().strip()
            if not template_name or template_name not in self.templates_by_name:
                raise ValueError("Selecciona un elemento válido.")
            qty = int(self.qty_var.get())
            if qty <= 0:
                raise ValueError("La cantidad debe ser mayor que 0.")

            template = self.templates_by_name[template_name]
            key = (kind, template.item_id)
            if key not in self.project_items:
                self.project_items[key] = {
                    "kind": kind,
                    "template_id": template.item_id,
                    "name": template.name,
                    "qty": 0,
                    "largo": template.largo,
                    "ancho": template.ancho,
                    "alto": template.alto,
                }
            self.project_items[key]["qty"] += qty
            self.refresh_items_tree()
            self.update_summary()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_items_tree(self):
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        for item in self.project_items.values():
            self.items_tree.insert(
                "",
                "end",
                values=(
                    item["kind"],
                    item["name"],
                    item["qty"],
                    f"{item['largo']:.2f}",
                    f"{item['ancho']:.2f}",
                    f"{item['alto']:.2f}",
                ),
            )

    def update_summary(self, result_text: Optional[str] = None):
        if result_text:
            self.summary_label.config(text=result_text)
            return
        total_qty = sum(item["qty"] for item in self.project_items.values())
        total_volume = sum(item["qty"] * item["largo"] * item["ancho"] * item["alto"] for item in self.project_items.values())
        self.summary_label.config(
            text=(
                f"Elementos en el proyecto: {total_qty}\n"
                f"Volumen total de referencia: {total_volume:.2f} u³\n"
                f"Define el furgón y ejecuta el cálculo."
            )
        )

    def clear_project(self):
        if not messagebox.askyesno("Confirmar", "¿Limpiar el proyecto actual?"):
            return
        self.project_items.clear()
        self.refresh_items_tree()
        self.update_summary()
        self._clear_plot()

    def build_instances(self) -> List[InstanceItem]:
        instances: List[InstanceItem] = []
        counters: Dict[Tuple[str, int], int] = {}
        for key, item in self.project_items.items():
            kind, template_id = key
            template = self.app.db.get_template_by_id(kind, template_id)
            if not template:
                continue
            counters.setdefault(key, 0)
            for _ in range(item["qty"]):
                counters[key] += 1
                label = f"{template.name} #{counters[key]}"
                instances.append(
                    InstanceItem(
                        label=label,
                        kind=kind,
                        largo=template.largo,
                        ancho=template.ancho,
                        alto=template.alto,
                        template_id=template.item_id,
                    )
                )
        return instances

    def calculate(self):
        try:
            largo = self.parse_positive(self.van_largo_var, "Largo del furgón")
            ancho = self.parse_positive(self.van_ancho_var, "Ancho del furgón")
            alto = self.parse_positive(self.van_alto_var, "Alto del furgón")
            instances = self.build_instances()
            if not instances:
                raise ValueError("Añade al menos un elemento al proyecto.")

            placed, unplaced = heuristic_pack((largo, ancho, alto), instances)

            if unplaced:
                names = ", ".join(x.label for x in unplaced[:8])
                if len(unplaced) > 8:
                    names += " ..."
                self.update_summary(f"Error: no caben todos los elementos. No colocados: {names}")
                self._clear_plot()
                return

            used_volume = sum(p.largo * p.ancho * p.alto for p in placed)
            container_volume = largo * ancho * alto
            fill_pct = (used_volume / container_volume) * 100 if container_volume else 0

            result_text = (
                f"Proyecto: {self.project_name_var.get().strip() or 'Sin nombre'}\n"
                f"Dimensiones del furgón: {largo:.2f} x {ancho:.2f} x {alto:.2f}\n"
                f"Elementos colocados: {len(placed)}\n"
                f"Volumen ocupado: {used_volume:.2f} / {container_volume:.2f} u³ ({fill_pct:.1f}%)\n"
                f"Estado: todo cabe correctamente."
            )
            self.update_summary(result_text)
            self.draw_plot((largo, ancho, alto), placed)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._clear_plot()

    def save_project(self):
        try:
            largo = self.parse_positive(self.van_largo_var, "Largo del furgón")
            ancho = self.parse_positive(self.van_ancho_var, "Ancho del furgón")
            alto = self.parse_positive(self.van_alto_var, "Alto del furgón")
            instances = self.build_instances()
            if not instances:
                raise ValueError("No hay elementos para guardar.")

            project_name = self.project_name_var.get().strip() or "Proyecto sin nombre"
            items_for_db = list(self.project_items.values())
            result_text = self.summary_label.cget("text")
            self.app.db.save_project(project_name, largo, ancho, alto, items_for_db, result_text)
            messagebox.showinfo("Guardado", "Proyecto guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_plot(self):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.result_placeholder.winfo_exists():
            self.result_placeholder.destroy()
        self.result_placeholder = ttk.Label(self.result_frame, text="Aquí aparecerá la representación 3D.")
        self.result_placeholder.grid(row=0, column=0, padx=10, pady=10)

    def draw_plot(self, container: Tuple[float, float, float], placements: List[Placement]):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.result_placeholder.winfo_exists():
            self.result_placeholder.destroy()

        fig = Figure(figsize=(7.5, 6), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        self.figure = fig
        self.ax = ax

        L, A, H = container
        ax.set_xlim(0, L)
        ax.set_ylim(0, A)
        ax.set_zlim(0, H)
        try:
            ax.set_box_aspect((L, A, H))
        except Exception:
            pass

        ax.set_xlabel("X / Largo")
        ax.set_ylabel("Y / Ancho")
        ax.set_zlabel("Z / Alto")
        ax.set_title("Distribución 3D del furgón")

        self._draw_container_wireframe(ax, L, A, H)

        for idx, p in enumerate(placements):
            self._draw_cuboid(ax, p.x, p.y, p.z, p.largo, p.ancho, p.alto, self._color_for_index(idx), label=p.label)

        ax.legend(loc="upper left", fontsize=8)
        self.canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _color_for_index(self, idx: int):
        palette = [
            (0.90, 0.45, 0.45, 0.75),
            (0.45, 0.70, 0.90, 0.75),
            (0.55, 0.80, 0.55, 0.75),
            (0.80, 0.60, 0.90, 0.75),
            (0.95, 0.75, 0.45, 0.75),
            (0.45, 0.85, 0.80, 0.75),
            (0.85, 0.55, 0.70, 0.75),
            (0.70, 0.70, 0.70, 0.75),
        ]
        return palette[idx % len(palette)]

    def _draw_container_wireframe(self, ax, L, A, H):
        verts = [
            (0, 0, 0),
            (L, 0, 0),
            (L, A, 0),
            (0, A, 0),
            (0, 0, H),
            (L, 0, H),
            (L, A, H),
            (0, A, H),
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        for i, j in edges:
            xs = [verts[i][0], verts[j][0]]
            ys = [verts[i][1], verts[j][1]]
            zs = [verts[i][2], verts[j][2]]
            ax.plot(xs, ys, zs, color="black", linewidth=1)

    def _draw_cuboid(self, ax, x, y, z, dx, dy, dz, color, label: str = ""):
        p = [
            (x, y, z),
            (x + dx, y, z),
            (x + dx, y + dy, z),
            (x, y + dy, z),
            (x, y, z + dz),
            (x + dx, y, z + dz),
            (x + dx, y + dy, z + dz),
            (x, y + dy, z + dz),
        ]
        faces = [
            [p[0], p[1], p[2], p[3]],
            [p[4], p[5], p[6], p[7]],
            [p[0], p[1], p[5], p[4]],
            [p[2], p[3], p[7], p[6]],
            [p[1], p[2], p[6], p[5]],
            [p[4], p[7], p[3], p[0]],
        ]
        poly = Poly3DCollection(faces, facecolors=[color], linewidths=0.8, edgecolors=(0.2, 0.2, 0.2, 1.0))
        ax.add_collection3d(poly)
        ax.text(x + dx / 2, y + dy / 2, z + dz / 2, label, fontsize=7, ha="center", va="center")


# =========================
# App principal
# =========================


class RedimensionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("REDIMENSION")
        self.geometry("1400x860")
        self.minsize(1180, 760)

        self.db = Database(DB_FILE)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._build_layout()
        self.show_page("project")

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, width=240)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.rowconfigure(4, weight=1)

        ttk.Label(sidebar, text="REDIMENSION", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, padx=16, pady=(18, 8), sticky="w")
        ttk.Label(sidebar, text="Optimizar embalaje 3D", font=("Segoe UI", 10)).grid(row=1, column=0, padx=16, pady=(0, 18), sticky="w")

        ttk.Button(sidebar, text="Cajas", command=lambda: self.show_page("boxes")).grid(row=2, column=0, sticky="ew", padx=16, pady=6)
        ttk.Button(sidebar, text="Productos", command=lambda: self.show_page("products")).grid(row=3, column=0, sticky="ew", padx=16, pady=6)
        ttk.Button(sidebar, text="+ Nuevo proyecto", command=lambda: self.show_page("project")).grid(row=4, column=0, sticky="new", padx=16, pady=6)

        info = ttk.LabelFrame(sidebar, text="Flujo")
        info.grid(row=5, column=0, padx=16, pady=16, sticky="ew")
        ttk.Label(
            info,
            text=(
                "1. Guarda cajas y productos\n"
                "2. Crea un proyecto\n"
                "3. Introduce el furgón\n"
                "4. Ejecuta el heurístico 3D"
            ),
            justify="left",
        ).pack(anchor="w", padx=10, pady=10)

        self.content = ttk.Frame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.pages: Dict[str, ttk.Frame] = {}
        self.pages["boxes"] = TemplatePage(self.content, self, "Caja")
        self.pages["products"] = TemplatePage(self.content, self, "Producto")
        self.pages["project"] = ProjectPage(self.content, self)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        footer = ttk.Label(self, text="Hecho en Tkinter + SQLite + algoritmo heurístico de colocación tridimensional.")
        footer.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

    def show_page(self, page_name: str):
        page = self.pages[page_name]
        page.tkraise()
        if page_name == "project":
            page.refresh_template_choices()
            page.update_summary()
        else:
            page.refresh()

    def refresh_project_controls(self):
        project_page: ProjectPage = self.pages["project"]
        project_page.refresh_template_choices()


if __name__ == "__main__":
    app = RedimensionApp()
    app.mainloop()
