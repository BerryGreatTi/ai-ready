"""AIReady entry point."""
from __future__ import annotations


def run(tool: str | None = None):
    from aiready.platforms.detect import detect_platform
    from aiready.i18n.strings import I18n
    from aiready.gui.app import AIReadyApp

    platform = detect_platform()
    i18n = I18n("en")
    app = AIReadyApp(platform=platform, i18n=i18n, preset_tool=tool)
    app.mainloop()


if __name__ == "__main__":
    run()
