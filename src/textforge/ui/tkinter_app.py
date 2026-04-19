from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import yaml

from textforge.ui.app_state import AppState, DatasetSelection
from textforge.ui.panels.datasets_panel import DatasetsPanel
from textforge.ui.panels.pipeline_panel import PipelinePanel
from textforge.ui.panels.preview_panel import PreviewPanel


class TextForgeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TextForge - Fase 1")
        self.geometry("1080x720")

        dataset_root = Path(r"/home/felpipe/Datasets/Textos paralelos")
        self.state_obj = AppState(
            dataset_selections=[
                DatasetSelection(name="dgt", domain="legal_institutional", input_root=str(dataset_root / "DGT-2019.en-es"), enabled=True, percentage=20.0),
                DatasetSelection(name="eubookshop", domain="institutional_publications", input_root=str(dataset_root / "EUbookshop.en-es"), enabled=True, percentage=10.0),
                DatasetSelection(name="europarl", domain="parliamentary", input_root=str(dataset_root / "Europarl.v8.en-es"), enabled=True, percentage=15.0),
                DatasetSelection(name="multiun", domain="institutional_un", input_root=str(dataset_root / "MultiUN.en-es"), enabled=True, percentage=20.0),
                DatasetSelection(name="opensubtitles", domain="conversational_subtitles", input_root=str(dataset_root / "OpenSubtitles.en-es"), enabled=True, percentage=20.0),
                DatasetSelection(name="unpc", domain="institutional_un", input_root=str(dataset_root / "UNPC.en-es"), enabled=True, percentage=15.0),
            ]
        )

        self.task_var = tk.StringVar(value=self.state_obj.task)
        self.domain_var = tk.StringVar(value=self.state_obj.target_domain)
        self.token_budget_var = tk.StringVar(value=str(self.state_obj.approximate_token_budget))

        self._build()

    def _build(self) -> None:
        header = ttk.Frame(self, padding=12)
        header.pack(fill="x")
        ttk.Label(header, text="TextForge · configurador de Fase 1", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="Genera presets reproducibles para lectura, canonización y silver Parquet sobre el layout confirmado.",
        ).pack(anchor="w")

        pipeline_panel = PipelinePanel(self, self.task_var, self.domain_var, self.token_budget_var)
        pipeline_panel.pack(fill="x", padx=12, pady=8)

        self.datasets_panel = DatasetsPanel(self, self.state_obj)
        self.datasets_panel.pack(fill="both", expand=True, padx=12, pady=8)

        self.preview_panel = PreviewPanel(self)
        self.preview_panel.pack(fill="x", padx=12, pady=8)

        actions = ttk.Frame(self, padding=12)
        actions.pack(fill="x")
        ttk.Button(actions, text="Validar mezcla", command=self._validate_mix).pack(side="left")
        ttk.Button(actions, text="Guardar preset YAML", command=self._save_preset).pack(side="left", padx=8)
        ttk.Button(actions, text="Exportar configs de datasets", command=self._export_dataset_overrides).pack(side="left", padx=8)
        ttk.Button(actions, text="Salir", command=self.destroy).pack(side="right")

    def _collect_state(self) -> dict:
        datasets = []
        for item in self.state_obj.dataset_selections:
            vars_ = self.datasets_panel.vars[item.name]
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
        preview = [f"Activos: {len(active)}", f"Suma porcentual: {total:.2f}%"]
        if abs(total - 100.0) > 1e-6 and active:
            preview.append("Advertencia: la mezcla no suma 100%.")
        self.preview_panel.update_text(" | ".join(preview))
        messagebox.showinfo("Validación", "\n".join(preview))

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

    def _export_dataset_overrides(self) -> None:
        state = self._collect_state()
        target_dir = filedialog.askdirectory(title="Selecciona carpeta para exportar overrides")
        if not target_dir:
            return
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        for item in state["datasets"]:
            if not item["enabled"]:
                continue
            out = target_dir / f"{item['name']}.override.yaml"
            with out.open("w", encoding="utf-8") as handle:
                yaml.safe_dump(
                    {
                        "dataset": {
                            "input_roots": [item["input_root"]],
                            "domain": item["domain"],
                        },
                        "mix": {"percentage": item["percentage"]},
                    },
                    handle,
                    allow_unicode=True,
                    sort_keys=False,
                )
        messagebox.showinfo("Overrides exportados", f"Se exportaron en:\n{target_dir}")


def run() -> None:
    app = TextForgeApp()
    app.mainloop()


if __name__ == "__main__":
    run()
