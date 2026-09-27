"""Widget Tkinter kecil."""

from __future__ import annotations

import tkinter as tk
from typing import Literal

from otobpn.gui import ACCENT, BG2, BG3, BG4, BORDER, TEXT


def frm(parent, bg=None, **kw):
    kw["bg"] = bg or BG2
    kw.setdefault("bd", 0)
    return tk.Frame(parent, **kw)


def lbl(
    parent,
    text="",
    bold=False,
    color=TEXT,
    size=9,
    anchor: Literal["center", "e", "n", "ne", "nw", "s", "se", "sw", "w"] = "w",
    **kw,
):
    kw.setdefault("bg", parent.cget("bg"))
    return tk.Label(
        parent,
        text=text,
        anchor=anchor,
        font=("Segoe UI", size, "bold" if bold else "normal"),
        fg=color,
        **kw,
    )


def ent(parent, var=None, w=10, **kw):
    return tk.Entry(
        parent,
        textvariable=var,
        width=w,
        bg=BG4,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        bd=3,
        highlightthickness=1,
        highlightcolor=ACCENT,
        highlightbackground=BORDER,
        **kw,
    )


def txt_widget(parent, h=2, w=40, **kw):
    return tk.Text(
        parent,
        height=h,
        width=w,
        bg=BG4,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        bd=3,
        wrap="word",
        highlightthickness=1,
        highlightcolor=ACCENT,
        highlightbackground=BORDER,
        font=("Segoe UI", 9),
        **kw,
    )


def chk(parent, text, var, **kw):
    kw.setdefault("bg", parent.cget("bg"))
    return tk.Checkbutton(
        parent,
        text=text,
        variable=var,
        fg=TEXT,
        selectcolor=BG4,
        activebackground=kw["bg"],
        activeforeground=TEXT,
        font=("Segoe UI", 9),
        **kw,
    )


def btn(parent, text, cmd, color=ACCENT, w=14, **kw):
    return tk.Button(
        parent,
        text=text,
        command=cmd,
        bg=color,
        fg="white",
        activebackground=BG3,
        activeforeground=TEXT,
        relief="flat",
        bd=0,
        padx=6,
        pady=3,
        width=w,
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
        **kw,
    )


def section_bar(parent, title, bg=BG3):
    f = frm(parent, bg=bg)
    f.pack(fill="x", pady=(6, 1))
    lbl(f, f"  {title}", bold=True, color=ACCENT, size=9, bg=bg).pack(
        side="left", padx=6, pady=3
    )
    return f
