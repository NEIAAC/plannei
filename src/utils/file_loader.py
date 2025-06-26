import os
import sys

from utils.logger import logger


def loadFile(fileName: str) -> str:
    locations = (
        # Files bundled inside the single binary build
        os.path.dirname(__file__),
        # Files in the directory the single binary build is in
        os.path.dirname(sys.argv[0]),
    )
    try:
        # Files in the standalone build directory
        locations = locations + (__compiled__.containing_dir,)  # type: ignore
    except NameError:
        pass

    for location in locations:
        file = os.path.join(location, fileName)
        if os.path.isfile(file):
            return file
    logger.error(
        f"Got a request to load file {fileName} but it could not be found, returning empty string"
    )
    return ""


def loadResource(resourceName: str) -> str:
    file = loadFile(os.path.join("resources", resourceName))
    return file
