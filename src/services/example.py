from PySide6.QtCore import QThread, Signal

from utils.logger import logger


class ExampleThread(QThread):
    outputSignal = Signal(str, str)

    def __init__(self, firstInput: str, secondInput: str | None = None):
        super().__init__()
        self.firstInput = firstInput
        self.secondInput = secondInput

    def output(self, text: str, level="INFO"):
        logger.log(level, text)
        self.outputSignal.emit(text, level)

    def run(self):
        inputs = self.__dict__.copy()
        inputs.pop("loginEmail", False)
        inputs.pop("loginPassword", False)

        logger.info(f"Starting browser thread with input parameters: {inputs}")

        self.output("...")
        with logger.catch():
            self.output("Your first input was: " + self.firstInput)
            self.output(
                "If you entered text in the second input it will be shown here after 3 seconds"
            )
            self.msleep(1500)
            try:
                raise Exception("This is an example error after 1.5 seconds")
            except Exception as e:
                self.output(str(e), "ERROR")
            self.msleep(1500)
            if self.secondInput:
                self.output("Your second input was: " + self.secondInput)
