import tkinter as tk
import threading
import queue
import math
import sys

import customtkinter as ctk

from core import AssistantCore

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG       = "#0a0712"
SURF     = "#0f0d1a"
SURF2    = "#150f24"
BORDER   = "#2a1f45"
PUR      = "#a855f7"
PUR_DIM  = "#2d1554"
PUR_LO   = "#1a0f30"
PUR_MID  = "#7c3aed"
PINK     = "#e879f9"
CYAN     = "#67e8f9"
GREEN    = "#34d399"
RED      = "#f87171"
MUTED    = "#4a3a6a"
TEXT     = "#e2d9f3"
TEXT_DIM = "#5a4a7a"

MONO  = ("Courier New", 11)
MONO_S= ("Courier New", 9)
MONO_H= ("Courier New", 13, "bold")

STATE_META = {
    "idle":       ("STANDBY",            TEXT_DIM, MUTED),
    "wake":       ("WAKE WORD DETECTED", PUR,      PUR),
    "listening":  ("LISTENING",          CYAN,     CYAN),
    "processing": ("PROCESSING",         PINK,     PINK),
    "speaking":   ("SPEAKING",           GREEN,    GREEN),
}

STATUS_META = {
    "idle":       ("READY · WAITING FOR WAKE WORD", MUTED),
    "wake":       ("ACTIVATED · SAY YOUR COMMAND",  PUR),
    "listening":  ("LISTENING FOR COMMAND",          CYAN),
    "processing": ("PROCESSING COMMAND",             PINK),
    "speaking":   ("SPEAKING",                       GREEN),
}


class MicCanvas(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG, highlightthickness=0, **kw)
        self._state = "idle"
        self._phase = 0.0
        self._alive = True
        self._tick()

    def set_state(self, s):
        self._state = s

    def _color(self):
        return {
            "idle":       MUTED,
            "wake":       PUR,
            "listening":  CYAN,
            "processing": PINK,
            "speaking":   GREEN,
        }.get(self._state, MUTED)

    def _lerp(self, a, b, t):
        t = max(0.0, min(1.0, t))
        ar, ag, ab = int(a[1:3],16), int(a[3:5],16), int(a[5:7],16)
        br, bg, bb = int(b[1:3],16), int(b[3:5],16), int(b[5:7],16)
        return "#{:02x}{:02x}{:02x}".format(
            int(ar+(br-ar)*t), int(ag+(bg-ag)*t), int(ab+(bb-ab)*t))

    def _tick(self):
        if not self._alive:
            return
        self.delete("all")
        w = self.winfo_width() or 240
        h = self.winfo_height() or 240
        cx, cy = w//2, h//2
        self._phase += 0.04
        ph = self._phase
        col = self._color()

        if self._state == "idle":
            pulse = math.sin(ph * 0.35) * 0.5 + 0.5
            r = 68 + pulse * 5
            ring = self._lerp(BG, MUTED, 0.25)
            self.create_oval(cx-r, cy-r, cx+r, cy+r, outline=ring, width=1)

        if self._state in ("wake", "listening", "speaking"):
            for i in range(4):
                off = i * (math.pi * 2 / 4)
                w_val = math.sin(ph + off)
                r = 74 + i*18 + w_val * 9
                alpha = max(0, (55 + w_val*45) / 255)
                c = self._lerp(BG, col, alpha)
                self.create_oval(cx-r, cy-r, cx+r, cy+r, outline=c, width=1)

        if self._state == "processing":
            for i in range(10):
                angle = ph*2.2 + i*(math.pi*2/10)
                r = 66
                dx, dy = math.cos(angle)*r, math.sin(angle)*r
                dot_c = self._lerp(BG, PINK, i/10)
                self.create_oval(cx+dx-4, cy+dy-4, cx+dx+4, cy+dy+4,
                                 fill=dot_c, outline="")

        self.create_oval(cx-52, cy-52, cx+52, cy+52,
                         fill=SURF2, outline=col, width=2)

        self._draw_mic(cx, cy, col)

        if self._state in ("wake","listening"):
            for i in range(7):
                bh = 3 + int(abs(math.sin(ph*1.6+i*0.9)) * 16)
                x = cx - 36 + i*12
                alpha = 0.35 + abs(math.sin(ph*1.1+i)) * 0.65
                c = self._lerp(BG, col, alpha)
                self.create_rectangle(x, cy+60-bh, x+7, cy+60+bh,
                                      fill=c, outline="")

        self.after(28, self._tick)

    def _draw_mic(self, cx, cy, col):
        self.create_rectangle(cx-6, cy-16, cx+6, cy+5,
                               fill=col, outline="")
        self.create_arc(cx-8, cy+1, cx+8, cy+13,
                        start=180, extent=180, style="arc",
                        outline=col, width=2)
        self.create_line(cx, cy+13, cx, cy+19, fill=col, width=2)
        self.create_line(cx-9, cy+19, cx+9, cy+19, fill=col, width=2)

    def destroy(self):
        self._alive = False
        super().destroy()


class LogPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self._rows = []

    def push(self, role, text):
        colors = {"user": CYAN, "assistant": PUR, "system": TEXT_DIM}
        icons  = {"user": "›", "assistant": "◆", "system": "·"}
        col = colors.get(role, TEXT_DIM)
        ico = icons.get(role, "·")

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=1, padx=4)

        ctk.CTkLabel(row, text=ico, font=MONO_H, text_color=col,
                     width=16).pack(side="left", anchor="nw", padx=(2,4))
        ctk.CTkLabel(row, text=text, font=MONO, text_color=TEXT,
                     anchor="w", justify="left",
                     wraplength=290).pack(side="left", fill="x", expand=True)

        self._rows.append(row)
        if len(self._rows) > 80:
            self._rows.pop(0).destroy()

        self.after(60, self._scroll)

    def _scroll(self):
        try:
            self._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("nico  ·  Voice Assistant")
        self.geometry("400x660")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self._q = queue.Queue()
        self._running = False
        self._core = None
        self._build()
        self._poll()
        self.protocol("WM_DELETE_WINDOW", self._quit)

    def _build(self):
        topbar = ctk.CTkFrame(self, fg_color=SURF, corner_radius=0, height=42)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(topbar, text="◈  NICO  ·  VOICE ASSISTANT",
                     font=("Courier New", 11, "bold"),
                     text_color=PUR).pack(side="left", padx=14)

        body = ctk.CTkFrame(self, fg_color=BG)
        body.pack(fill="both", expand=True)

        self._mic = MicCanvas(body, width=240, height=240)
        self._mic.pack(pady=(20, 0))

        self._lbl_state = ctk.CTkLabel(body, text="STANDBY",
                                        font=("Courier New", 10, "bold"),
                                        text_color=TEXT_DIM)
        self._lbl_state.pack(pady=(3, 0))

        self._lbl_hint = ctk.CTkLabel(
            body,
            text='say "nico" to activate',
            font=MONO_S, text_color=TEXT_DIM)
        self._lbl_hint.pack(pady=(2, 12))

        log_wrap = ctk.CTkFrame(body, fg_color=SURF2, corner_radius=10,
                                 border_width=1, border_color=BORDER)
        log_wrap.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        ctk.CTkLabel(log_wrap, text="TRANSCRIPT",
                     font=MONO_S, text_color=TEXT_DIM).pack(
            anchor="w", padx=10, pady=(7, 2))

        self._log = LogPanel(log_wrap, fg_color="transparent",
                              scrollbar_button_color=BORDER,
                              scrollbar_button_hover_color=MUTED)
        self._log.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(pady=(0, 14))

        self._btn_on = ctk.CTkButton(
            btn_row, text="START", width=130, height=34,
            font=MONO_H,
            fg_color=PUR_DIM, hover_color="#3d1a6e",
            text_color=PUR, border_width=1, border_color=PUR,
            corner_radius=4, command=self._start)
        self._btn_on.pack(side="left", padx=(0, 8))

        self._btn_off = ctk.CTkButton(
            btn_row, text="STOP", width=130, height=34,
            font=MONO_H,
            fg_color="#2a0d14", hover_color="#3a1020",
            text_color=RED, border_width=1, border_color=RED,
            corner_radius=4, state="disabled", command=self._stop)
        self._btn_off.pack(side="left")

        self._statusbar = ctk.CTkFrame(self, fg_color=SURF, corner_radius=0, height=22)
        self._statusbar.pack(fill="x", side="bottom")
        self._statusbar.pack_propagate(False)

        self._sb_dot = ctk.CTkLabel(self._statusbar, text="●",
                                     font=MONO_S, text_color=MUTED, width=20)
        self._sb_dot.pack(side="left", padx=(8, 2))

        self._sb_text = ctk.CTkLabel(self._statusbar,
                                      text="OFFLINE",
                                      font=MONO_S, text_color=TEXT_DIM)
        self._sb_text.pack(side="left")

        ctk.CTkLabel(self._statusbar, text="vosk · offline",
                     font=MONO_S, text_color=TEXT_DIM).pack(
            side="right", padx=10)

    def _set_state(self, s):
        label, lcolor, dot_color = STATE_META.get(s, ("STANDBY", TEXT_DIM, MUTED))
        sb_text, sb_color = STATUS_META.get(s, ("READY", MUTED))
        hints = {
            "idle":       'say "nico" to activate',
            "wake":       "say your command...",
            "listening":  "listening...",
            "processing": "processing command...",
            "speaking":   "speaking...",
        }
        self._lbl_state.configure(text=label, text_color=lcolor)
        self._lbl_hint.configure(text=hints.get(s, ""))
        self._mic.set_state(s)
        self._sb_dot.configure(text_color=dot_color)
        self._sb_text.configure(text=sb_text, text_color=sb_color)

    def _start(self):
        if self._running:
            return
        self._running = True
        self._btn_on.configure(state="disabled")
        self._btn_off.configure(state="normal")
        self._core = AssistantCore(
            on_state=lambda s: self._q.put(("state", s)),
            on_log=lambda r, t: self._q.put(("log", r, t)),
        )
        self._core.start()

    def _stop(self):
        if self._core:
            self._core.stop()
        self._running = False
        self._btn_on.configure(state="normal")
        self._btn_off.configure(state="disabled")

    def _poll(self):
        try:
            while True:
                item = self._q.get_nowait()
                if item[0] == "state":
                    self._set_state(item[1])
                elif item[0] == "log":
                    self._log.push(item[1], item[2])
        except queue.Empty:
            pass
        self.after(40, self._poll)

    def _quit(self):
        if self._core:
            self._core.stop()
        self.destroy()
        sys.exit(0)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
