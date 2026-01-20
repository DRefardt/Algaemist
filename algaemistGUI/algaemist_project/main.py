from algaemistGUI.gui import AlgaemistGUI
from reactor.logger import setup_logger

logger = setup_logger()


if __name__ == "__main__":
    app = AlgaemistGUI()
    app.run()