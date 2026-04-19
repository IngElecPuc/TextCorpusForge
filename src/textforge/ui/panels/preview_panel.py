from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class PreviewPanel(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Vista previa y log')
        self.text = tk.Text(self, height=10, wrap='word')
        scroll = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.grid(row=0, column=0, sticky='nsew', padx=(6, 0), pady=6)
        scroll.grid(row=0, column=1, sticky='ns', pady=6, padx=(0, 6))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.text.insert('1.0', 'Sin validar todavía.\n')
        self.text.configure(state='disabled')

    def update_text(self, text: str) -> None:
        self.text.configure(state='normal')
        self.text.delete('1.0', 'end')
        self.text.insert('1.0', text)
        self.text.configure(state='disabled')

    def append_text(self, text: str) -> None:
        self.text.configure(state='normal')
        self.text.insert('end', text + '\n')
        self.text.see('end')
        self.text.configure(state='disabled')
