from __future__ import annotations

from pathlib import Path
import queue
import threading
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import yaml

from textforge.orchestration.pipeline import run_pipeline
from textforge.ui.app_state import AppState, DatasetSelection
from textforge.ui.config_builder import build_ui_pipeline_files
from textforge.ui.panels.datasets_panel import DatasetsPanel
from textforge.ui.panels.pipeline_panel import PipelinePanel
from textforge.ui.panels.preview_panel import PreviewPanel
from textforge.ui.preview_runner import run_preview


class TextForgeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('TextForge - Fase 1')
        self.geometry('1360x900')
        self.minsize(1180, 760)
        dataset_root = Path(r'/home/felpipe/Datasets/Textos paralelos')
        self.workspace = Path.cwd()
        self.state_obj = AppState(dataset_selections=[
            DatasetSelection(name='dgt', domain='legal_institutional', input_root=str(dataset_root / 'DGT-2019.en-es'), enabled=True, percentage=20.0),
            DatasetSelection(name='eubookshop', domain='institutional_publications', input_root=str(dataset_root / 'EUbookshop.en-es'), enabled=True, percentage=10.0),
            DatasetSelection(name='europarl', domain='parliamentary', input_root=str(dataset_root / 'Europarl.v8.en-es'), enabled=True, percentage=15.0),
            DatasetSelection(name='multiun', domain='institutional_un', input_root=str(dataset_root / 'MultiUN.en-es'), enabled=True, percentage=20.0),
            DatasetSelection(name='opensubtitles', domain='conversational_subtitles', input_root=str(dataset_root / 'OpenSubtitles.en-es'), enabled=True, percentage=20.0),
            DatasetSelection(name='unpc', domain='institutional_un', input_root=str(dataset_root / 'UNPC.en-es'), enabled=True, percentage=15.0),
        ])
        self.task_var = tk.StringVar(value=self.state_obj.task)
        self.domain_var = tk.StringVar(value=self.state_obj.target_domain)
        self.token_budget_var = tk.StringVar(value=str(self.state_obj.approximate_token_budget))
        self.max_pairs_var = tk.StringVar(value='0')
        self.max_segments_var = tk.StringVar(value='0')
        self.max_documents_var = tk.StringVar(value='0')
        self.max_tokens_var = tk.StringVar(value='0')
        self.sample_export_size_var = tk.StringVar(value='20')
        self.preview_only_var = tk.BooleanVar(value=False)
        self.stop_after_first_var = tk.BooleanVar(value=True)
        self.export_samples_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value='Listo.')
        self.progress_var = tk.DoubleVar(value=0.0)
        self._job_queue: queue.Queue = queue.Queue()
        self._worker: threading.Thread | None = None
        self._cancel_event = threading.Event()
        self._build()
        self.after(120, self._poll_job_queue)

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, padding=12)
        header.grid(row=0, column=0, sticky='ew')
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text='TextForge · ejecutor de Fase 1', font=('TkDefaultFont', 14, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(header, text='Configura, previsualiza y genera silver Parquet parcial con parada temprana y muestras legibles.').grid(row=1, column=0, sticky='w')
        ttk.Label(header, text=f'Workspace actual: {self.workspace}').grid(row=2, column=0, sticky='w')
        body = ttk.Panedwindow(self, orient='horizontal')
        body.grid(row=1, column=0, sticky='nsew', padx=12, pady=8)
        left = ttk.Frame(body, padding=0)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)
        right = ttk.Frame(body, padding=0)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)
        body.add(left, weight=3)
        body.add(right, weight=2)
        pipeline_panel = PipelinePanel(left, self.task_var, self.domain_var, self.token_budget_var, self.max_pairs_var, self.max_segments_var, self.max_documents_var, self.max_tokens_var, self.sample_export_size_var, self.preview_only_var, self.stop_after_first_var, self.export_samples_var)
        pipeline_panel.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        self.datasets_panel = DatasetsPanel(left, self.state_obj)
        self.datasets_panel.grid(row=1, column=0, sticky='nsew', pady=(0, 8))
        actions = ttk.LabelFrame(left, text='Acciones')
        actions.grid(row=2, column=0, sticky='ew')
        for col in range(3):
            actions.columnconfigure(col, weight=1)
        self.validate_btn = ttk.Button(actions, text='Validar mezcla', command=self._validate_mix)
        self.validate_btn.grid(row=0, column=0, sticky='ew', padx=6, pady=6)
        self.save_btn = ttk.Button(actions, text='Guardar preset YAML', command=self._save_preset)
        self.save_btn.grid(row=0, column=1, sticky='ew', padx=6, pady=6)
        self.preview_btn = ttk.Button(actions, text='Previsualizar 20 ejemplos', command=self._preview_examples)
        self.preview_btn.grid(row=0, column=2, sticky='ew', padx=6, pady=6)
        self.run_btn = ttk.Button(actions, text='Generar silver Parquet', command=self._run_generation)
        self.run_btn.grid(row=1, column=0, sticky='ew', padx=6, pady=6)
        self.cancel_btn = ttk.Button(actions, text='Cancelar ejecución', command=self._cancel_run, state='disabled')
        self.cancel_btn.grid(row=1, column=1, sticky='ew', padx=6, pady=6)
        self.outputs_btn = ttk.Button(actions, text='Abrir carpeta de outputs', command=self._show_outputs_path)
        self.outputs_btn.grid(row=1, column=2, sticky='ew', padx=6, pady=6)
        ttk.Button(actions, text='Salir', command=self.destroy).grid(row=2, column=2, sticky='e', padx=6, pady=6)
        progress_box = ttk.LabelFrame(right, text='Ejecución')
        progress_box.grid(row=0, column=0, sticky='nsew')
        progress_box.columnconfigure(0, weight=1)
        progress_box.rowconfigure(3, weight=1)
        ttk.Label(progress_box, textvariable=self.status_var).grid(row=0, column=0, sticky='w', padx=8, pady=(8, 4))
        self.progress = ttk.Progressbar(progress_box, orient='horizontal', mode='determinate', maximum=100, variable=self.progress_var)
        self.progress.grid(row=1, column=0, sticky='ew', padx=8, pady=(0, 8))
        ttk.Label(progress_box, text='Vista previa y log').grid(row=2, column=0, sticky='w', padx=8)
        self.preview_panel = PreviewPanel(progress_box)
        self.preview_panel.grid(row=3, column=0, sticky='nsew', padx=8, pady=8)

    def _set_running(self, running: bool) -> None:
        state = 'disabled' if running else 'normal'
        for btn in (self.validate_btn, self.save_btn, self.preview_btn, self.run_btn, self.outputs_btn):
            btn.configure(state=state)
        self.cancel_btn.configure(state='normal' if running else 'disabled')

    def _collect_state(self) -> AppState:
        datasets = []
        for item in self.state_obj.dataset_selections:
            vars_ = self.datasets_panel.vars[item.name]
            datasets.append(DatasetSelection(name=item.name, domain=item.domain, enabled=bool(vars_['enabled'].get()), input_root=str(vars_['folder'].get()).strip(), percentage=float(vars_['percentage'].get() or 0.0)))
        return AppState(task=self.task_var.get(), target_domain=self.domain_var.get(), approximate_token_budget=int(self.token_budget_var.get() or 0), max_pairs=int(self.max_pairs_var.get() or 0), max_segments=int(self.max_segments_var.get() or 0), max_documents=int(self.max_documents_var.get() or 0), max_tokens_approx=int(self.max_tokens_var.get() or 0), sample_export_size=int(self.sample_export_size_var.get() or 20), mode_preview_only=bool(self.preview_only_var.get()), stop_after_first_dataset=bool(self.stop_after_first_var.get()), export_samples=bool(self.export_samples_var.get()), dataset_selections=datasets)

    def _validate_mix(self) -> None:
        state = self._collect_state()
        active = [d for d in state.dataset_selections if d.enabled]
        total = sum(d.percentage for d in active)
        preview = [f'Activos: {len(active)}', f'Suma porcentual: {total:.2f}%', f'Max pairs: {state.max_pairs}', f'Max tokens aprox: {state.max_tokens_approx}']
        if abs(total - 100.0) > 1e-6 and active:
            preview.append('Advertencia: la mezcla no suma 100%.')
        joined = '\n'.join(preview)
        self.preview_panel.update_text(joined)
        messagebox.showinfo('Validación', joined)

    def _save_preset(self) -> None:
        state = self._collect_state()
        payload = {
            'task': state.task, 'target_domain': state.target_domain, 'approximate_token_budget': state.approximate_token_budget,
            'max_pairs': state.max_pairs, 'max_segments': state.max_segments, 'max_documents': state.max_documents, 'max_tokens_approx': state.max_tokens_approx,
            'sample_export_size': state.sample_export_size, 'mode_preview_only': state.mode_preview_only, 'stop_after_first_dataset': state.stop_after_first_dataset,
            'export_samples': state.export_samples,
            'datasets': [{'name': d.name, 'domain': d.domain, 'input_root': d.input_root, 'enabled': d.enabled, 'percentage': d.percentage} for d in state.dataset_selections],
        }
        target = filedialog.asksaveasfilename(title='Guardar preset', defaultextension='.yaml', filetypes=[('YAML', '*.yaml'), ('YML', '*.yml')])
        if not target:
            return
        path = Path(target)
        with path.open('w', encoding='utf-8') as handle:
            yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
        messagebox.showinfo('Preset guardado', f'Se guardó en:\n{path}')

    def _preview_examples(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        state = self._collect_state()
        self._cancel_event.clear()
        self._set_running(True)
        self.status_var.set('Previsualizando...')
        self.progress_var.set(5)
        def work():
            try:
                result = run_preview(self.workspace, state)
                self._job_queue.put(('preview_done', result))
            except Exception as exc:
                self._job_queue.put(('error', f'Error en previsualización:\n{exc}\n\n{traceback.format_exc()}'))
        self._worker = threading.Thread(target=work, daemon=True)
        self._worker.start()

    def _run_generation(self) -> None:
        state = self._collect_state()
        if state.mode_preview_only:
            self._preview_examples()
            return
        if self._worker and self._worker.is_alive():
            return
        self._cancel_event.clear()
        self._set_running(True)
        self.status_var.set('Preparando ejecución...')
        self.progress_var.set(0)
        self.preview_panel.update_text('Iniciando ejecución...\n')
        def progress_callback(event: dict):
            self._job_queue.put(('progress', event))
        def work():
            try:
                pipeline_cfg_path, dataset_cfgs = build_ui_pipeline_files(self.workspace, state)
                result = run_pipeline('canonicalize', workspace=self.workspace, config_path=pipeline_cfg_path, progress_callback=progress_callback, cancel_event=self._cancel_event)
                summary = {'pipeline_config': str(pipeline_cfg_path), 'dataset_configs': [str(p) for p in dataset_cfgs], 'result': result, 'outputs_dir': str(self.workspace / 'data')}
                self._job_queue.put(('run_done', summary))
            except Exception as exc:
                self._job_queue.put(('error', f'Error durante la generación:\n{exc}\n\n{traceback.format_exc()}'))
        self._worker = threading.Thread(target=work, daemon=True)
        self._worker.start()

    def _cancel_run(self) -> None:
        self._cancel_event.set()
        self.status_var.set('Cancelando...')
        self.preview_panel.append_text('Se solicitó cancelación.')

    def _show_outputs_path(self) -> None:
        out = self.workspace / 'data'
        self.preview_panel.append_text(f'Outputs: {out}')
        messagebox.showinfo('Outputs', f'Revisa la carpeta:\n{out}')

    def _poll_job_queue(self) -> None:
        try:
            while True:
                kind, payload = self._job_queue.get_nowait()
                if kind == 'progress':
                    total = max(int(payload.get('total', 1)), 1)
                    progress = int(payload.get('progress', 0))
                    percent = max(0, min(100, (progress / total) * 100))
                    self.progress_var.set(percent)
                    message = payload.get('message', '')
                    if message:
                        self.status_var.set(message)
                        self.preview_panel.append_text(message)
                elif kind == 'preview_done':
                    self.progress_var.set(100)
                    self.status_var.set('Previsualización finalizada.')
                    self.preview_panel.update_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))
                    self._set_running(False)
                elif kind == 'run_done':
                    self.progress_var.set(100)
                    self.status_var.set('Generación finalizada.')
                    self.preview_panel.update_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))
                    self._set_running(False)
                    messagebox.showinfo('Generación finalizada', f'Outputs en:\n{self.workspace / "data"}')
                elif kind == 'error':
                    self.status_var.set('Error.')
                    self.preview_panel.update_text(payload)
                    self._set_running(False)
        except queue.Empty:
            pass
        self.after(120, self._poll_job_queue)


def run() -> None:
    app = TextForgeApp()
    app.mainloop()


if __name__ == '__main__':
    run()
