"""A simple Tkinter application for py-skytune."""
from __future__ import annotations

import sys
import tkinter as tk

from pathlib import Path
from tkinter import font, messagebox, ttk

from py_skytune.radio import Radio


class Ui:
    """Th UI for py-skytune."""

    def __init__(self: Ui) -> None:
        """Initialize the UI."""
        self._menu: tk.Menu
        self._root: tk.Tk
        self._tree: ttk.Treeview
        self._radio: Radio
        self._columns = ("name", "genre", "location")

    def _setup_ui(self: Ui) -> None:
        """Set up the UI."""
        self._root = tk.Tk(className="py-skytune")
        icon = tk.PhotoImage(file=Path(__file__).parent / "data" / "icon.png")
        self._root.tk.call("wm", "iconphoto", self._root._w, icon)  # noqa: SLF001
        self._root.title(f"Skytune radio favorites ({self._radio.ip_address})")

        self._root.grid_rowconfigure(0, weight=0)
        self._root.grid_rowconfigure(1, weight=1000)
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_columnconfigure(1, weight=1)
        self._root.grid_columnconfigure(2, weight=1)

        tk.Grid.rowconfigure(self._root, index=0, weight=1)
        tk.Grid.columnconfigure(self._root, index=0, weight=1)

        add_label = ttk.Label(self._root, text="RadioBrowser station UUID:")
        add_label.grid(row=0, column=0, padx=(10, 0), pady=(10, 10), sticky="e")
        add_box = ttk.Entry(self._root, name="add_box")
        add_box.bind("<Return>", self._add)
        add_box.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="we")
        add_btn = ttk.Button(self._root, text="Add", name="add_btn")
        add_btn.bind("<Button-1>", self._add)
        add_btn.grid(row=0, column=2, padx=(0, 10), pady=(10, 10), sticky="w")

        self._tree = ttk.Treeview(self._root, columns=self._columns, show="headings")
        self._tree.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self._tree.bind("<Button-3>", self._context_menu)
        self._tree.bind("<Double-Button-1>", self._play)

        vsb = ttk.Scrollbar(orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.bind("<Motion>", self._tree_motion)

        status_label = ttk.Label(self._root, text="", name="status")
        status_label.grid(row=3, column=0, columnspan=4, padx=(5, 0), pady=(5, 5), sticky="w")

        self._menu = tk.Menu(self._tree, tearoff=0)
        self._menu.add_command(label="Play", command=self._play)
        self._menu.add_command(label="Delete", command=self._delete)
        self._menu.add_separator()
        self._menu.add_command(label="Sort favorites on radio", command=self._sort)

        vsb.grid(column=4, row=1, sticky="ns")
        hsb.grid(column=0, row=2, sticky="ew", columnspan=3)

        self._tree.heading(0, text="Favorites", command=lambda c=0: self._col_sort(c, 0))
        self._render_favorites()

    def _render_favorites(self: Ui) -> None:
        """Add the favorites to the treeview."""
        self._tree.delete(*self._tree.get_children())
        favorites = self._radio.favorites
        for column in self._columns:
            max_width = max(
                [font.Font().measure(favorite.name) for favorite in favorites]
                + [font.Font().measure(getattr(favorite, column)) for favorite in favorites],
            )
            self._tree.heading(
                column,
                text=column.capitalize(),
                command=lambda c=column: self._col_sort(c, 0),
            )
            self._tree.column(column, width=max_width, stretch=True)

        for favorite in favorites:
            values = [
                favorite.name,
                favorite.genre,
                self._radio.locations.find_by_name(favorite.location),
            ]
            self._tree.insert("", "end", values=values, tags=(favorite.uid,))
        self._now_playing()

    def _add(self: Ui, event: tk.Event | None = None) -> str:
        """Add a favorite from radio browser.

        Args:
            event: The event that triggered the addition.
        """
        add_btn = event.widget.master.children["add_btn"]
        add_box = event.widget.master.children["add_box"]
        add_btn.configure(state="disabled", text="Adding...")
        self._root.update()
        uuid = add_box.get()
        self._radio.add_by_rb_uuid(uuid)
        self._render_favorites()
        add_box.delete(0, "end")
        add_btn.configure(state="normal", text="Add")
        self._root.update()
        return "break"

    def _col_sort(self: Ui, col: str, descending: int) -> None:
        """Sort the treeview by the given column.

        Args:
            col: The column to sort by.
            descending: Whether to sort in descending order.
        """
        carats = {0: "▲", 1: "▼"}
        data = [(self._tree.set(child, col), child) for child in self._tree.get_children("")]

        if col == "bit_rate":
            data = [(float(item[0]), item[1]) for item in data]

        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            self._tree.move(item[1], "", ix)

        for column in self._tree["columns"]:
            if column != col:
                self._tree.heading(
                    column,
                    text=column.capitalize(),
                    command=lambda col=column: self._col_sort(col, 0),
                )

        new_text = f"{col.capitalize()} {carats[descending]}"
        self._tree.heading(
            col,
            text=new_text,
            command=lambda col=col: self._col_sort(col, int(not descending)),
        )

    def _context_menu(self: Ui, event: tk.Event) -> None:
        """Provide a cotnext menu for the treeview.

        Args:
            event: The event that triggered the context menu.
        """
        iid = self._tree.identify_row(event.y)

        if iid:
            self._tree.selection_set(iid)
            try:
                self._menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self._root.grab_release()

    def _delete(self: Ui) -> None:
        """Delete the selected favorite."""
        input_id = self._tree.selection()
        item_id = self._tree.item(input_id, "tag")[0]
        status = f"Deleting: {self._tree.item(input_id, 'values')[0]}"
        self.update_status(status=status)
        self._radio.delete_favorite(int(item_id))
        self._render_favorites()
        self._now_playing()

    def _now_playing(self: Ui) -> None:
        """Show the now playing."""
        playing = self._radio.playing
        status = playing["chStatus"].split(": ")[1].capitalize()
        self.update_status(status=f"{status}: {playing['name']}")
        self._root.after(3000, self._now_playing)

    def _play(self: Ui, event: tk.Event | None = None) -> None:
        """Play the selected favorite."""
        input_id = self._tree.selection()
        item_id = self._tree.item(input_id, "tag")[0]
        self._radio.play_favorite(int(item_id))
        self._now_playing()

    def _sort(self: Ui, event: tk.Event | None = None) -> None:
        """Sort the favorites on the radio."""
        self._radio.sort_favorites(callback=self.update_status)
        self.update_status(status="Sorted")
        self._render_favorites()
        self._now_playing()

    def _tree_motion(self: Ui, event: tk.Event) -> None:
        """Highlight the row the mouse is over.

        Args:
            event: The event that triggered the highlighting.
        """
        row = self._tree.identify_row(event.y)

        self._tree.selection_set(row)

    def update_status(self: Ui, status: str) -> None:
        """Update the status label.

        Args:
            status: The status to display.
        """
        self._root.after_cancel(self._now_playing)
        self._root.children["status"].config(text=status)
        self._root.update()

    def run(self: Ui) -> None:
        """Run the UI."""
        self._radio = Radio()
        while not self._radio.find():
            answer = messagebox.askyesno("Skytune error", "Radio not found. Try again?")
            if not answer:
                return

        self._setup_ui()
        self._root.after(3000, self._now_playing)
        self._root.minsize(640, 480)
        self._root.mainloop()
