from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import yaml

from textforge.ui.app_state import AppState, DatasetSelection


_DATASETS = [
    ("dgt", "legal"),
    ("eubookshop", "institutional"),
    ("europarl", "parliamentary"),
    ("multiun", "institutional"),
    ("opensubtitles", "conversational"),
    ("unpc", "institutional"),
]


class TextForgeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TextForge")
        self.geometry("980x620")
        self.state = AppState(
            dataset_selections=[
                DatasetSelection(name=name, domain=domain)
                for name, domain in _DATASETS
            ]
        )
        self._dataset_vars: dict[str, dict[str, tk.Variable]] = {}
        self._build()

    def _build(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        top = ttk.LabelFrame(root, text="Objetivo del dataset", padding=12)
        top.pack(fill="x", padx=4, pady=4)

        self.task_var = tk.StringVar(value=self.state.task)
        self.domain_var = tk.StringVar(value=self.state.target_domain)
        self.token_budget_var = tk.StringVar(value=str(self.state.approximate_token_budget))

        ttk.Label(top, text="Tarea").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            top,
            textvariable=self.task_var,
            values=["seq2seq_mt", "bert_pretrain", "gpt_pretrain", "classification", "ner", "qa", "summarization"],
            state="readonly",
            width=22,
        ).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(top, text="Dominio objetivo").grid(row=0, column=2, sticky="w")
        ttk.Combobox(
            top,
            textvariable=self.domain_var,
            values=["mixed", "conversational", "institutional", "parliamentary", "legal", "custom"],
            state="readonly",
            width=22,
        ).grid(row=0, column=3, sticky="w", padx=8)

        ttk.Label(top, text="Tokens aprox.").grid(row=0, column=4, sticky="w")
        ttk.Entry(top, textvariable=self.token_budget_var, width=16).grid(row=0, column=5, sticky="w", padx=8)

        datasets_frame = ttk.LabelFrame(root, text="Datasets y mezcla", padding=12)
        datasets_frame.pack(fill="both", expand=True, padx=4, pady=4)

        headers = ["Usar", "Dataset", "Dominio", "Carpeta", "% mezcla", "Acción"]
        for col, title in enumerate(headers):
            ttk.Label(datasets_frame, text=title).grid(row=0, column=col, sticky="w", padx=4, pady=4)

        for idx, item in enumerate(self.state.dataset_selections, start=1):
            enabled = tk.BooleanVar(value=item.enabled)
            folder = tk.StringVar(value=item.input_root)
            percentage = tk.StringVar(value=str(item.percentage))

            self._dataset_vars[item.name] = {
                "enabled": enabled,
                "folder": folder,
                "percentage": percentage,
            }

            ttk.Checkbutton(datasets_frame, variable=enabled).grid(row=idx, column=0, sticky="w")
            ttk.Label(datasets_frame, text=item.name).grid(row=idx, column=1, sticky="w", padx=4)
            ttk.Label(datasets_frame, text=item.domain).grid(row=idx, column=2, sticky="w", padx=4)
            ttk.Entry(datasets_frame, textvariable=folder, width=50).grid(row=idx, column=3, sticky="we", padx=4)
            ttk.Entry(datasets_frame, textvariable=percentage, width=10).grid(row=idx, column=4, sticky="w", padx=4)
            ttk.Button(
                datasets_frame,
                text="Seleccionar",
                command=lambda name=item.name: self._pick_folder(name),
            ).grid(row=idx, column=5, sticky="w", padx=4)

        actions = ttk.Frame(root, padding=(0, 8, 0, 0))
        actions.pack(fill="x")

        ttk.Button(actions, text="Guardar preset YAML", command=self._save_preset).pack(side="left")
        ttk.Button(actions, text="Validar mezcla", command=self._validate_mix).pack(side="left", padx=8)
        ttk.Button(actions, text="Salir", command=self.destroy).pack(side="right")

    def _pick_folder(self, dataset_name: str) -> None:
        selected = filedialog.askdirectory(title=f"Selecciona carpeta para {dataset_name}")
        if selected:
            self._dataset_vars[dataset_name]["folder"].set(selected)
            self._dataset_vars[dataset_name]["enabled"].set(True)

    def _collect_state(self) -> dict:
        datasets = []
        for item in self.state.dataset_selections:
            vars_ = self._dataset_vars[item.name]
            datasets.append(
                {
                    "name": item.name,
                    "domain": item.domain,
                    "enabled": bool(vars_["enabled"].get()),
                    "input_root": str(vars_["folder"].get()).strip(),
                    "percentage": float(vars_["percentage"].get() or 0.0),
                }
            )

        return {
            "task": self.task_var.get(),
            "target_domain": self.domain_var.get(),
            "approximate_token_budget": int(self.token_budget_var.get() or 0),
            "datasets": datasets,
        }

    def _validate_mix(self) -> None:
        state = self._collect_state()
        active = [d for d in state["datasets"] if d["enabled"]]
        total = sum(d["percentage"] for d in active)
        messagebox.showinfo(
            "Validación",
            f"Datasets activos: {len(active)}\nSuma porcentual: {total:.2f}%",
        )

    def _save_preset(self) -> None:
        state = self._collect_state()
        target = filedialog.asksaveasfilename(
            title="Guardar preset",
            defaultextension=".yaml",
            filetypes=[("YAML", "*.yaml"), ("YML", "*.yml")],
        )
        if not target:
            return

        path = Path(target)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(state, handle, allow_unicode=True, sort_keys=False)

        messagebox.showinfo("Preset guardado", f"Se guardó en:\n{path}")


def run() -> None:
    app = TextForgeApp()
    app.mainloop()


if __name__ == "__main__":
    run()
