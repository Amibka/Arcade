import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from ui.views import AppContext, MainMenuView


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    try:
        if hasattr(window, "maximize"):
            window.maximize()
        elif hasattr(window, "_window") and hasattr(window._window, "set_maximized"):
            window._window.set_maximized(True)
    except Exception:
        pass
    app = AppContext()
    window.show_view(MainMenuView(app))
    arcade.run()


if __name__ == "__main__":
    main()
