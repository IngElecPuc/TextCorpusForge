from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk

from textforge.ui.app_state import AppState


class DatasetsPanel(ttk.LabelFrame):
    def __init__(self, master, state: AppState):
        super().__init__(master, text='Datasets')
        self.state = state
        self.vars: dict[str, dict[str, tk.Variable]] = {}
        self._build()

    def _build(self) -> None:
        container = ttk.Frame(self)
        container.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(container, height=230)
        yscroll = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        xscroll = ttk.Scrollbar(container, orient='horizontal', command=canvas.xview)
        inner = ttk.Frame(canvas)
        inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=inner, anchor='nw')
        canvas.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        canvas.grid(row=0, column=0, sticky='nsew')
        yscroll.grid(row=0, column=1, sticky='ns')
        xscroll.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        headers = ['Usar', 'Dataset', 'Dominio', 'Carpeta', '% mezcla', '']
        for col, title in enumerate(headers):
            ttk.Label(inner, text=title).grid(row=0, column=col, sticky='w', padx=4, pady=4)

        for idx, item in enumerate(self.state.dataset_selections, start=1):
            enabled = tk.BooleanVar(value=item.enabled)
            folder = tk.StringVar(value=item.input_root)
            pct = tk.StringVar(value=str(item.percentage))
            self.vars[item.name] = {'enabled': enabled, 'folder': folder, 'percentage': pct}
            ttk.Checkbutton(inner, variable=enabled).grid(row=idx, column=0, sticky='w')
            ttk.Label(inner, text=item.name).grid(row=idx, column=1, sticky='w')
            ttk.Label(inner, text=item.domain).grid(row=idx, column=2, sticky='w')
            ttk.Entry(inner, textvariable=folder, width=60).grid(row=idx, column=3, sticky='we', padx=4)
            ttk.Entry(inner, textvariable=pct, width=8).grid(row=idx, column=4, sticky='w')
            ttk.Button(inner, text='Seleccionar', command=lambda name=item.name: self._pick_folder(name)).grid(row=idx, column=5, sticky='w')
        inner.columnconfigure(3, weight=1)

    def _pick_folder(self, dataset_name: str) -> None:
        selected = filedialog.askdirectory(title=f'Selecciona carpeta para {dataset_name}')
        if selected:
            self.vars[dataset_name]['folder'].set(selected)
            self.vars[dataset_name]['enabled'].set(True)
