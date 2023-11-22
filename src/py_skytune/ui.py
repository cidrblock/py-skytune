"""A simple Tkinter application for py-skytune."""
from __future__ import annotations

import tkinter as tk

from pathlib import Path
from tkinter import font, ttk

from py_skytune.radio import Radio


class Ui:
    """Th UI for py-skytune."""

    def __init__(self: Ui) -> None:
        """Initialize the UI."""
        self._menu: tk.Menu
        self._root: tk.Tk
        self._tree: ttk.Treeview
        self._radio: Radio = Radio()
        self._setup_ui()

    def _setup_ui(self: Ui) -> None:
        """Set up the UI."""
        self._root = tk.Tk(className="py-skytune")
        icon = tk.PhotoImage(file=Path(__file__).parent / "data" / "icon.png")
        self._root.tk.call("wm", "iconphoto", self._root._w, icon)  # noqa: SLF001
        self._root.title(f"Skytune radio favorites ({self._radio.ip_address})")
        columns = ("name", "genre", "location")

        tk.Grid.rowconfigure(self._root, index=0, weight=1)
        tk.Grid.columnconfigure(self._root, index=0, weight=1)

        self._tree = ttk.Treeview(self._root, columns=columns, show="headings")
        self._tree.grid(row=0, column=0, sticky="nsew")
        self._tree.bind("<Button-3>", self._context_menu)
        self._tree.bind("<Double-Button-1>", self._play)

        vsb = ttk.Scrollbar(orient="vertical", command=self._tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal", command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._tree.bind("<Motion>", self._tree_motion)

        now_playing_label = ttk.Label(self._root, text="", name="now_playing")
        now_playing_label.grid(row=2, column=0, padx=(5, 0), pady=(5, 5), sticky="w")

        self._menu = tk.Menu(self._tree, tearoff=0)
        self._menu.add_command(label="Play", command=self._play)

        vsb.grid(column=4, row=0, sticky="ns")
        hsb.grid(column=0, row=1, sticky="ew", columnspan=3)

        self._tree.heading(0, text="Favorites", command=lambda c=0: self._col_sort(c, 0))

        favorites = self._radio.favorites
        for column in columns:
            max_width = max(
                [font.Font().measure(favorite.name) for favorite in favorites]
                + [font.Font().measure(getattr(favorite, column)) for favorite in favorites],
            )
            self._tree.heading(
                column, text=column.capitalize(), command=lambda c=column: self._col_sort(c, 0)
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
            col, text=new_text, command=lambda col=col: self._col_sort(col, int(not descending))
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

    def _tree_motion(self: Ui, event: tk.Event) -> None:
        """Highlight the row the mouse is over.

        Args:
            event: The event that triggered the highlighting.
        """
        row = self._tree.identify_row(event.y)

        self._tree.selection_set(row)

    def _play(self: Ui, event: tk.Event | None = None) -> None:
        """Play the selected favorite."""
        input_id = self._tree.selection()
        item_id = self._tree.item(input_id, "tag")[0]
        self._radio.play_favorite(int(item_id))
        self._now_playing()

    def _now_playing(self: Ui) -> None:
        """Show the now playing."""
        playing = self._radio.playing
        status = playing["chStatus"].split(": ")[1].capitalize()
        self._root.children["now_playing"].config(text=f"{status}: {playing['name']}")
        self._root.after(3000, self._now_playing)

    def run(self: Ui) -> None:
        """Run the UI."""
        self._root.after(3000, self._now_playing)
        self._root.minsize(640, 480)
        self._root.mainloop()
