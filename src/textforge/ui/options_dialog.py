from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from textforge.ui.app_state import AppState


class AdvancedOptionsDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, state: AppState):
        super().__init__(master)
        self.title('Opciones avanzadas')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result: dict | None = None
        self.vars = {
            'output_root': tk.StringVar(value=state.output_root),
            'reports_subdir': tk.StringVar(value=state.reports_subdir),
            'silver_subdir': tk.StringVar(value=state.silver_subdir),
            'temp_subdir': tk.StringVar(value=state.temp_subdir),
            'read_chunk_lines': tk.StringVar(value=str(state.read_chunk_lines)),
            'write_chunk_size': tk.StringVar(value=str(state.write_chunk_size)),
            'parquet_compression': tk.StringVar(value=state.parquet_compression),
            'parquet_rows_per_file': tk.StringVar(value=str(state.parquet_rows_per_file)),
        }
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky='nsew')
        labels = [
            ('Carpeta raíz de salida', 'output_root'),
            ('Subcarpeta de reportes', 'reports_subdir'),
            ('Subcarpeta silver', 'silver_subdir'),
            ('Subcarpeta temporal', 'temp_subdir'),
            ('Chunk de lectura (líneas)', 'read_chunk_lines'),
            ('Chunk de escritura (registros)', 'write_chunk_size'),
            ('Compresión Parquet', 'parquet_compression'),
            ('Máx. filas por archivo Parquet (0=único)', 'parquet_rows_per_file'),
        ]
        for row, (label, key) in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky='w', padx=4, pady=4)
            ttk.Entry(frame, textvariable=self.vars[key], width=36).grid(row=row, column=1, sticky='ew', padx=4, pady=4)
        btns = ttk.Frame(frame)
        btns.grid(row=len(labels), column=0, columnspan=2, sticky='ew', pady=(8, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)
        ttk.Button(btns, text='Cancelar', command=self.destroy).grid(row=0, column=0, sticky='ew', padx=4)
        ttk.Button(btns, text='Guardar', command=self._save).grid(row=0, column=1, sticky='ew', padx=4)

    def _save(self) -> None:
        self.result = {k: v.get().strip() for k, v in self.vars.items()}
        self.destroy()
