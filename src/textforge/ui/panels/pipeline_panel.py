from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class PipelinePanel(ttk.LabelFrame):
    def __init__(self, master, task_var: tk.StringVar, domain_var: tk.StringVar, token_budget_var: tk.StringVar):
        super().__init__(master, text='Configuración de Fase 1')
        ttk.Label(self, text='Tarea destino').grid(row=0, column=0, sticky='w', padx=4, pady=4)
        ttk.Combobox(self, textvariable=task_var, values=['seq2seq_mt', 'bert_pretrain', 'gpt_pretrain'], state='readonly', width=20).grid(row=0, column=1, sticky='w', padx=4)

        ttk.Label(self, text='Dominio objetivo').grid(row=1, column=0, sticky='w', padx=4, pady=4)
        ttk.Combobox(self, textvariable=domain_var, values=['mixed', 'conversational', 'institutional', 'parliamentary', 'legal'], state='readonly', width=20).grid(row=1, column=1, sticky='w', padx=4)

        ttk.Label(self, text='Presupuesto aprox. de tokens').grid(row=2, column=0, sticky='w', padx=4, pady=4)
        ttk.Entry(self, textvariable=token_budget_var, width=20).grid(row=2, column=1, sticky='w', padx=4)
