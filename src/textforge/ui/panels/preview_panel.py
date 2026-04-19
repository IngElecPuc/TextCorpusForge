from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class PreviewPanel(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.preview_text = self._build_tab('Vista previa')
        self.log_text = self._build_tab('Log')
        self.summary_text = self._build_tab('Resumen')

    def _build_tab(self, title: str):
        frame = ttk.Frame(self)
        text = tk.Text(frame, height=18, wrap='none')
        yscroll = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        xscroll = ttk.Scrollbar(frame, orient='horizontal', command=text.xview)
        text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        text.grid(row=0, column=0, sticky='nsew', padx=(6, 0), pady=(6, 0))
        yscroll.grid(row=0, column=1, sticky='ns', pady=(6, 0), padx=(0, 6))
        xscroll.grid(row=1, column=0, sticky='ew', padx=(6, 0), pady=(0, 6))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        text.insert('1.0', 'Sin validar todavía.\n')
        text.configure(state='disabled')
        self.add(frame, text=title)
        return text

    def update_text(self, text: str, tab: str = 'preview') -> None:
        widget = self._widget(tab)
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', text)
        widget.configure(state='disabled')

    def append_text(self, text: str, tab: str = 'log') -> None:
        widget = self._widget(tab)
        widget.configure(state='normal')
        widget.insert('end', text + '\n')
        widget.see('end')
        widget.configure(state='disabled')

    def _widget(self, tab: str):
        return {'preview': self.preview_text, 'log': self.log_text, 'summary': self.summary_text}[tab]
