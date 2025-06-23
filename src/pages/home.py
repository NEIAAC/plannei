from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QSoundEffect
from qfluentwidgets import (
    BodyLabel,
    LineEdit,
    PrimaryToolButton,
    FluentIcon,
    SingleDirectionScrollArea,
    SmoothMode,
    TextBrowser,
    InfoBar,
    InfoBarPosition,
)

from app import App
from services.example import ExampleThread
from utils.data_saver import config
from utils import file_loader


class HomePage(QWidget):
    worker: ExampleThread | None = None

    def __init__(self):
        super().__init__()
        self.setObjectName("Home")

        self.finishSound = QSoundEffect()
        self.finishSound.setSource(
            QUrl.fromLocalFile(file_loader.loadResource("sounds/success.wav"))
        )
        self.finishSound.setVolume(0.2)

        self.firstInputLabel = BodyLabel("<b>FIRST EXAMPLE INPUT<b>")
        self.firstInputField = LineEdit()
        self.firstInputField.setMaximumWidth(500)
        self.firstInputField.setPlaceholderText(
            "Text written on this one is saved between app restarts!"
        )
        self.firstInputField.textChanged.connect(
            lambda text: config.input.set(text)
        )
        self.firstInputField.setText(config.input.get())
        self.firstInputLayout = QVBoxLayout()
        self.firstInputLayout.setSpacing(10)
        self.firstInputLayout.addWidget(self.firstInputLabel)
        self.firstInputLayout.addWidget(self.firstInputField)

        self.secondInputLabel = BodyLabel("<b>SECOND EXAMPLE INPUT<b>")
        self.secondInputField = LineEdit()
        self.secondInputField.setMaximumWidth(500)
        self.secondInputField.setPlaceholderText("This is a placeholder.")
        self.secondInputLayout = QVBoxLayout()
        self.secondInputLayout.setSpacing(10)
        self.secondInputLayout.addWidget(self.secondInputLabel)
        self.secondInputLayout.addWidget(self.secondInputField)

        self.inputLayout = QVBoxLayout()
        self.inputLayout.setSpacing(20)
        self.inputLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.inputLayout.addLayout(self.firstInputLayout)
        self.inputLayout.addLayout(self.secondInputLayout)

        self.runLogsBox = TextBrowser()
        self.runLogsBox.setHtml("")
        self.runLogsBox.setMinimumHeight(150)
        self.runLogsBox.setMaximumHeight(300)
        self.runLogsBox.setReadOnly(True)
        self.runLogsBox.setPlaceholderText(
            "Press the start button on the left to begin. \
            \nLog output from the run will be shown here. \
            \nThe trash can button will clear this box."
        )
        self.runButton = PrimaryToolButton(FluentIcon.PLAY)
        self.runButton.setFixedWidth(100)
        self.runButton.clicked.connect(self.runExample)
        self.runLogsClearButton = PrimaryToolButton(FluentIcon.DELETE)
        self.runLogsClearButton.setDisabled(True)
        self.runLogsClearButton.setFixedWidth(100)
        self.runLogsClearButton.clicked.connect(
            lambda: (
                self.runLogsBox.clear(),  # type: ignore
                self.runLogsClearButton.setDisabled(True),
            )
        )
        self.runButtonLayout = QVBoxLayout()
        self.runButtonLayout.setSpacing(10)
        self.runButtonLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.runButtonLayout.addWidget(self.runButton)
        self.runButtonLayout.addWidget(self.runLogsClearButton)
        self.runContentLayout = QHBoxLayout()
        self.runContentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.runContentLayout.setSpacing(10)
        self.runContentLayout.addLayout(self.runButtonLayout)
        self.runContentLayout.addWidget(self.runLogsBox)

        self.contentLayout = QVBoxLayout()
        self.contentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.contentLayout.setContentsMargins(40, 40, 50, 40)
        self.contentLayout.setSpacing(40)
        self.contentLayout.addLayout(self.inputLayout)
        self.contentLayout.addLayout(self.runContentLayout)
        self.contentWidget = QWidget()
        self.contentWidget.setLayout(self.contentLayout)

        self.scrollArea = SingleDirectionScrollArea(
            orient=Qt.Orientation.Vertical
        )
        self.scrollArea.setWidget(self.contentWidget)
        self.scrollArea.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding
        )
        self.scrollArea.horizontalScrollBar().setVisible(False)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.enableTransparentBackground()
        self.scrollArea.setSmoothMode(SmoothMode.NO_SMOOTH)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.scrollArea)

        self.setLayout(self.mainLayout)

    def runExample(self):
        """Runs the example logic for this page."""
        if self.worker is not None and self.worker.isRunning():
            return

        schema = {
            "First input": self.firstInputField.text(),
        }
        for input in schema:
            if not schema[input]:
                InfoBar.error(
                    title=f"{input} field cannot be empty!",
                    content="",
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=4000,
                    parent=self,
                )
                return

        self.runButton.setDisabled(True)

        self.worker = ExampleThread(
            self.firstInputField.text(),
            self.secondInputField.text(),
        )

        def output(text, level):
            if level == "ERROR":
                self.runLogsBox.append(f'<font color="red">{text}</font>')
            else:
                self.runLogsBox.append(f'<font color="green">{text}</font>')
            self.runLogsClearButton.setDisabled(False)

        self.worker.outputSignal.connect(output)

        def finished():
            self.runButton.setDisabled(False)
            App.alert(self, 0)
            # if (
            #     App.applicationState()
            #     == Qt.ApplicationState.ApplicationInactive
            # ):
            #     SystemTray().send("Example finished!", "Go back to the app.")
            self.finishSound.play()

        self.worker.finished.connect(finished)
        self.worker.start()
