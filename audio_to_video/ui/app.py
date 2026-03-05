from __future__ import annotations

import threading
from pathlib import Path
from queue import Empty, Queue
from tkinter import BOTH, LEFT, RIGHT, StringVar, Tk, X, filedialog, messagebox
from tkinter import colorchooser
from tkinter import ttk

from ..application.render_job_service import RenderJobService
from ..domain.models import ProgressUpdate, RenderConfig
from ..domain.validation import ValidationError
from ..infrastructure.audio_analyzer import CancelledError
from ..infrastructure.ffmpeg import FfmpegError


class AudioToVideoApp:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Audio to Video")
        self.root.geometry("760x360")
        self.root.minsize(700, 330)

        self.service = RenderJobService()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.events: Queue[tuple[str, object]] = Queue()

        self.audio_var = StringVar()
        self.output_var = StringVar()
        self.avatar_var = StringVar()
        self.color_start_var = StringVar(value="#EC4899")
        self.color_end_var = StringVar(value="#6B21A8")
        self.status_var = StringVar(value="Pronto")

        self._build_ui()
        self._poll_events()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill=BOTH, expand=True)

        self._build_file_row(frame, "Áudio", self.audio_var, self._pick_audio)
        self._build_file_row(frame, "Saída MP4", self.output_var, self._pick_output)
        self._build_file_row(frame, "Avatar (opcional)", self.avatar_var, self._pick_avatar)

        colors_row = ttk.Frame(frame)
        colors_row.pack(fill=X, pady=(8, 8))

        ttk.Label(colors_row, text="Cor gradiente 1").pack(side=LEFT)
        ttk.Entry(colors_row, textvariable=self.color_start_var, width=12).pack(side=LEFT, padx=(8, 8))
        ttk.Button(colors_row, text="Escolher", command=lambda: self._pick_color(self.color_start_var)).pack(side=LEFT)

        ttk.Label(colors_row, text="Cor gradiente 2").pack(side=LEFT, padx=(16, 0))
        ttk.Entry(colors_row, textvariable=self.color_end_var, width=12).pack(side=LEFT, padx=(8, 8))
        ttk.Button(colors_row, text="Escolher", command=lambda: self._pick_color(self.color_end_var)).pack(side=LEFT)

        self.progress = ttk.Progressbar(frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill=X, pady=(12, 8))

        ttk.Label(frame, textvariable=self.status_var).pack(fill=X)

        actions = ttk.Frame(frame)
        actions.pack(fill=X, pady=(16, 0))

        self.generate_button = ttk.Button(actions, text="Gerar vídeo", command=self._start_job)
        self.generate_button.pack(side=LEFT)

        self.cancel_button = ttk.Button(actions, text="Cancelar", command=self._cancel_job, state="disabled")
        self.cancel_button.pack(side=LEFT, padx=(8, 0))

    def _build_file_row(self, parent: ttk.Frame, label: str, variable: StringVar, callback) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=X, pady=(0, 8))

        ttk.Label(row, text=label, width=18).pack(side=LEFT)
        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side=LEFT, fill=X, expand=True)
        ttk.Button(row, text="Selecionar", command=callback).pack(side=RIGHT, padx=(8, 0))
        ttk.Button(row, text="Limpar", command=lambda var=variable: self._clear(var)).pack(side=RIGHT)

    def _pick_audio(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o áudio",
            filetypes=[("Audio", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg")],
        )
        if path:
            self.audio_var.set(path)

    def _pick_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Salvar vídeo",
            defaultextension=".mp4",
            filetypes=[("MP4", "*.mp4")],
        )
        if path:
            self.output_var.set(path)

    def _pick_avatar(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecione o avatar",
            filetypes=[("Image", "*.png *.jpg *.jpeg *.webp")],
        )
        if path:
            self.avatar_var.set(path)

    @staticmethod
    def _clear(variable: StringVar) -> None:
        variable.set("")

    def _pick_color(self, variable: StringVar) -> None:
        selected = colorchooser.askcolor(title="Escolha a cor", initialcolor=variable.get())[1]
        if selected:
            variable.set(selected)

    def _start_job(self) -> None:
        if self.worker and self.worker.is_alive():
            return

        config = RenderConfig(
            audio_path=Path(self.audio_var.get().strip()),
            output_path=Path(self.output_var.get().strip()),
            gradient_start=self.color_start_var.get().strip(),
            gradient_end=self.color_end_var.get().strip(),
            avatar_path=Path(self.avatar_var.get().strip()) if self.avatar_var.get().strip() else None,
        )

        self.cancel_event.clear()
        self.progress["value"] = 0
        self.status_var.set("Iniciando...")
        self.generate_button.config(state="disabled")
        self.cancel_button.config(state="normal")

        self.worker = threading.Thread(target=self._run_job, args=(config,), daemon=True)
        self.worker.start()

    def _run_job(self, config: RenderConfig) -> None:
        try:
            self.service.render_video(
                config,
                cancel_event=self.cancel_event,
                on_progress=self._on_progress,
            )
            self.events.put(("success", "Vídeo gerado com sucesso."))
        except CancelledError:
            self.events.put(("cancelled", "Processamento cancelado."))
        except (ValidationError, FfmpegError, FileNotFoundError, OSError) as exc:
            self.events.put(("error", str(exc)))
        except Exception as exc:
            self.events.put(("error", f"Erro inesperado: {exc}"))

    def _on_progress(self, update: ProgressUpdate) -> None:
        self.events.put(("progress", update))

    def _cancel_job(self) -> None:
        self.cancel_event.set()
        self.status_var.set("Cancelando...")

    def _poll_events(self) -> None:
        try:
            while True:
                event_type, payload = self.events.get_nowait()
                if event_type == "progress":
                    update = payload
                    assert isinstance(update, ProgressUpdate)
                    self.progress["value"] = update.progress * 100
                    self.status_var.set(update.message)
                elif event_type == "success":
                    self.status_var.set(str(payload))
                    messagebox.showinfo("Sucesso", str(payload))
                    self._unlock_actions()
                elif event_type == "cancelled":
                    self.status_var.set(str(payload))
                    messagebox.showwarning("Cancelado", str(payload))
                    self._unlock_actions()
                elif event_type == "error":
                    self.status_var.set("Falha no processamento.")
                    messagebox.showerror("Erro", str(payload))
                    self._unlock_actions()
        except Empty:
            pass
        finally:
            self.root.after(100, self._poll_events)

    def _unlock_actions(self) -> None:
        self.generate_button.config(state="normal")
        self.cancel_button.config(state="disabled")


def run() -> None:
    root = Tk()
    app = AudioToVideoApp(root)
    root.mainloop()
