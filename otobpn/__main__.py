"""Entry CLI/GUI."""

from otobpn.gui.app import AppDetil


def main() -> None:
    app = AppDetil()
    app.mainloop()


if __name__ == "__main__":
    main()
