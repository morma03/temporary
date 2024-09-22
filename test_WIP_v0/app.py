import sys
from PyQt5 import QtWidgets
from src.views.dashboard.models_overview import MainModelsOverviewWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainModelsOverviewWindow()
    window.show()
    sys.exit(app.exec_())

# TODO: Be able to pick multiple models and run at the same time on one graph, checkboxes for all models
# TODO: histogram of daily win/loss
