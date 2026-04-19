from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class PipelinePanel(ttk.LabelFrame):
    def __init__(
        self,
        master,
        task_var: tk.StringVar,
        domain_var: tk.StringVar,
        token_budget_var: tk.StringVar,
        max_pairs_var: tk.StringVar,
        max_segments_var: tk.StringVar,
        max_documents_var: tk.StringVar,
        max_tokens_var: tk.StringVar,
        sample_export_size_var: tk.StringVar,
        preview_only_var: tk.BooleanVar,
        stop_after_first_var: tk.BooleanVar,
        export_samples_var: tk.BooleanVar,
    ):
        super().__init__(master, text='Configuración de Fase 1')
        row = 0
        ttk.Label(self, text='Tarea destino').grid(row=row, column=0, sticky='w', padx=4, pady=4)
        ttk.Combobox(self, textvariable=task_var, values=['seq2seq_mt', 'bert_pretrain', 'gpt_pretrain'], state='readonly', width=20).grid(row=row, column=1, sticky='w', padx=4)
        ttk.Label(self, text='Dominio objetivo').grid(row=row, column=2, sticky='w', padx=4, pady=4)
        ttk.Combobox(self, textvariable=domain_var, values=['mixed', 'conversational', 'institutional', 'parliamentary', 'legal'], state='readonly', width=20).grid(row=row, column=3, sticky='w', padx=4)

        row += 1
        ttk.Label(self, text='Presupuesto total aprox. de tokens').grid(row=row, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=token_budget_var, width=20).grid(row=row, column=1, sticky='w', padx=4)
        ttk.Label(self, text='Límite de pares').grid(row=row, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=max_pairs_var, width=20).grid(row=row, column=3, sticky='w', padx=4)

        row += 1
        ttk.Label(self, text='Límite de segmentos').grid(row=row, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=max_segments_var, width=20).grid(row=row, column=1, sticky='w', padx=4)
        ttk.Label(self, text='Límite de documentos').grid(row=row, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=max_documents_var, width=20).grid(row=row, column=3, sticky='w', padx=4)

        row += 1
        ttk.Label(self, text='Límite aprox. de tokens de salida').grid(row=row, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=max_tokens_var, width=20).grid(row=row, column=1, sticky='w', padx=4)
        ttk.Label(self, text='Tamaño de muestra exportada').grid(row=row, column=2, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=sample_export_size_var, width=20).grid(row=row, column=3, sticky='w', padx=4)

        row += 1
        ttk.Checkbutton(self, text='Modo prueba / solo previsualización', variable=preview_only_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=4, pady=4)
        ttk.Checkbutton(self, text='Detener tras el primer dataset activo', variable=stop_after_first_var).grid(row=row, column=2, columnspan=2, sticky='w', padx=4, pady=4)

        row += 1
        ttk.Checkbutton(self, text='Exportar muestras legibles (JSONL/CSV/MD)', variable=export_samples_var).grid(row=row, column=0, columnspan=2, sticky='w', padx=4, pady=4)
