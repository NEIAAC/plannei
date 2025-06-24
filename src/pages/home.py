from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QFileDialog,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QSoundEffect
from qfluentwidgets import (
    BodyLabel,
    LineEdit,
    PrimaryToolButton,
    FluentIcon,
    SpinBox,
    CheckBox,
    ComboBox,
    FlowLayout,
    SingleDirectionScrollArea,
    SmoothMode,
    TextBrowser,
    InfoBar,
    InfoBarPosition,
)

from app import App
from services.browser import BrowserThread
from utils.data_saver import config
from utils import file_loader
from services.browser import BrowserChoice
from utils.logger import LogLevel


class HomePage(QWidget):
    worker: BrowserThread | None = None

    def __init__(self):
        super().__init__()
        self.setObjectName("Home")

        self.finishSound = QSoundEffect()
        self.finishSound.setSource(
            QUrl.fromLocalFile(file_loader.loadResource("sounds/success.wav"))
        )
        self.finishSound.setVolume(0.2)

        self.loginEmailLabel = BodyLabel("<b>LOGIN EMAIL<b>")
        self.loginEmailField = LineEdit()
        self.loginEmailField.setMaximumWidth(500)
        self.loginEmailField.setPlaceholderText("example@student.uc.pt")
        self.loginEmailField.textChanged.connect(
            lambda text: config.loginEmail.set(text)
        )
        self.loginEmailField.setText(config.loginEmail.get())
        self.loginEmailLayout = QVBoxLayout()
        self.loginEmailLayout.setSpacing(10)
        self.loginEmailLayout.addWidget(self.loginEmailLabel)
        self.loginEmailLayout.addWidget(self.loginEmailField)

        self.loginPasswordLabel = BodyLabel("<b>LOGIN PASSWORD<b>")
        self.loginPasswordField = LineEdit()
        self.loginPasswordField.setMaximumWidth(500)
        self.loginPasswordField.setPlaceholderText("********")
        self.loginPasswordField.setEchoMode(LineEdit.EchoMode.Password)
        self.loginPasswordField.textChanged.connect(
            lambda text: config.loginPassword.set(text)
        )
        self.loginPasswordField.setText(config.loginPassword.get())
        self.loginPasswordLayout = QVBoxLayout()
        self.loginPasswordLayout.setSpacing(10)
        self.loginPasswordLayout.addWidget(self.loginPasswordLabel)
        self.loginPasswordLayout.addWidget(self.loginPasswordField)

        self.loginLayout = QVBoxLayout()
        self.loginLayout.setSpacing(20)
        self.loginLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.loginLayout.addLayout(self.loginEmailLayout)
        self.loginLayout.addLayout(self.loginPasswordLayout)

        self.browserChoiceLabel = BodyLabel("<b>BROWSER</b>")
        self.browserChoiceCombo = ComboBox()
        self.browserChoiceCombo.setMaximumWidth(500)
        for choice in BrowserChoice:
            self.browserChoiceCombo.addItem(
                choice.value.title(), userData=choice.value
            )
        for i in range(self.browserChoiceCombo.count()):
            if (
                self.browserChoiceCombo.itemData(i)
                == config.browserChoice.get()
            ):
                self.browserChoiceCombo.setCurrentIndex(i)
                break
        self.browserChoiceCombo.currentIndexChanged.connect(
            lambda: config.browserChoice.set(
                self.browserChoiceCombo.currentData()
            )
        )

        self.browserChoiceLayout = QVBoxLayout()
        self.browserChoiceLayout.setSpacing(10)
        self.browserChoiceLayout.addWidget(self.browserChoiceLabel)
        self.browserChoiceLayout.addWidget(self.browserChoiceCombo)

        self.headlessLabel = BodyLabel("<b>HEADLESS</b>")
        self.headlessCheckBox = CheckBox()
        self.headlessCheckBox.setChecked(config.headless.get())
        self.headlessCheckBox.toggled.connect(
            lambda checked: config.headless.set(checked)
        )

        self.headlessLayout = QVBoxLayout()
        self.headlessLayout.setSpacing(10)
        self.headlessLayout.addWidget(self.headlessLabel)
        self.headlessLayout.addWidget(self.headlessCheckBox)

        self.dryRunLabel = BodyLabel("<b>DRY RUN</b>")
        self.dryRunCheckBox = CheckBox()
        self.dryRunLayout = QVBoxLayout()
        self.dryRunLayout.setSpacing(10)
        self.dryRunLayout.addWidget(self.dryRunLabel)
        self.dryRunLayout.addWidget(self.dryRunCheckBox)

        self.configsLayout = FlowLayout()
        self.configsLayout.setVerticalSpacing(20)
        self.configsLayout.setHorizontalSpacing(20)
        self.configsLayout.addItem(self.browserChoiceLayout)
        self.configsLayout.addItem(self.headlessLayout)
        self.configsLayout.addItem(self.dryRunLayout)

        self.enrollmentIndexLabel = BodyLabel("<b>ENROLLMENT INDEX</b>")
        self.enrollmentIndexInput = SpinBox()
        self.enrollmentIndexInput.setFixedWidth(200)
        self.enrollmentIndexInput.setMinimum(1)
        self.enrollmentIndexInput.setMaximum(99)
        self.enrollmentIndexInput.valueChanged.connect(
            lambda value: config.enrollmentIndex.set(value)
        )
        self.enrollmentIndexInput.setValue(config.enrollmentIndex.get())
        self.enrollmentIndexLayout = QVBoxLayout()
        self.enrollmentIndexLayout.setSpacing(10)
        self.enrollmentIndexLayout.addWidget(self.enrollmentIndexLabel)
        self.enrollmentIndexLayout.addWidget(self.enrollmentIndexInput)

        self.tableLabel = BodyLabel("<b>SCHEDULE TABLE FILE</b>")
        self.tableFileInput = LineEdit()
        self.tableFileInput.setReadOnly(True)
        self.tableFileInput.setMaximumWidth(500)
        self.tableFileInput.setPlaceholderText("No table file selected.")
        self.tableFileInput.setText(config.tablePath.get())
        self.tableFileInput.textChanged.connect(
            lambda text: config.tablePath.set(text)
        )
        self.tableFileDialog = QFileDialog()
        self.tableFileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.tableFilePickButton = PrimaryToolButton(FluentIcon.FOLDER)
        self.tableFilePickButton.clicked.connect(
            lambda: self.tableFileInput.setText(
                self.tableFileDialog.getOpenFileName(
                    self, "Select a table file!"
                )[0]
            )
        )
        self.tableContentLayout = QHBoxLayout()
        self.tableContentLayout.setSpacing(10)
        self.tableContentLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tableContentLayout.addWidget(self.tableFilePickButton)
        self.tableContentLayout.addWidget(self.tableFileInput)
        self.tableLayout = QVBoxLayout()
        self.tableLayout.setSpacing(10)
        self.tableLayout.addWidget(self.tableLabel)
        self.tableLayout.addLayout(self.tableContentLayout)

        self.inputsLayout = QVBoxLayout()
        self.inputsLayout.setSpacing(20)
        self.inputsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.inputsLayout.addLayout(self.enrollmentIndexLayout)
        self.inputsLayout.addLayout(self.tableLayout)

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
        self.runButton.clicked.connect(self.runBrowser)
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
        self.contentLayout.addLayout(self.loginLayout)
        self.contentLayout.addLayout(self.configsLayout)
        self.contentLayout.addLayout(self.inputsLayout)
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

    def runBrowser(self):
        if self.worker is not None and self.worker.isRunning():
            return

        schema = {
            "Email": self.loginEmailField.text(),
            "Password": self.loginPasswordField.text(),
            "Browser choice": self.browserChoiceCombo.currentData(),
            "Enrollment index": self.enrollmentIndexInput.value(),
            "Table file": self.tableFileInput.text(),
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

        self.worker = BrowserThread(
            loginEmail=self.loginEmailField.text(),
            loginPassword=self.loginPasswordField.text(),
            browserChoice=BrowserChoice(self.browserChoiceCombo.currentData()),
            headless=self.headlessCheckBox.isChecked(),
            dryRun=self.dryRunCheckBox.isChecked(),
            enrollmentIndex=self.enrollmentIndexInput.value(),
            tablePath=self.tableFileInput.text(),
        )

        def output(text: str, level: LogLevel):
            if level == LogLevel.ERROR.value:
                self.runLogsBox.append(f'<font color="red">{text}</font>')
            elif level == LogLevel.WARNING.value:
                self.runLogsBox.append(f'<font color="olive">{text}</font>')
            elif level == LogLevel.SUCCESS.value:
                self.runLogsBox.append(f'<font color="green">{text}</font>')
            else:
                self.runLogsBox.append(f'<font color="gray">{text}</font>')
            self.runLogsClearButton.setDisabled(False)

        self.worker.outputSignal.connect(output)

        def finished():
            self.runButton.setDisabled(False)
            App.alert(self, 0)
            self.finishSound.play()

        self.worker.finished.connect(finished)
        self.worker.start()
