from __future__ import annotations

from tkinter import ttk


class PreviewPanel(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text='Vista previa')
        self.label = ttk.Label(self, text='Sin validar todavía.')
        self.label.pack(anchor='w', padx=6, pady=6)

    def update_text(self, text: str) -> None:
        self.label.configure(text=text)
