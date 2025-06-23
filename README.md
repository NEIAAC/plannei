# Python, now with 39% more GUI 🐍💻

Template for pythons apps with a GUI. Features automated builds on release with binaries for Windows, MacOS and Linux users to download. Contains linting, formatting and testing tools.

Although this template is meant to be a base for bigger projects, there are some limitations and annoyances that derive from using python bindings with Qt. To name a few, testing can be cumbersome with PyTest-Qt and the API is not always easy to work with or well documented. Other than that, there is also no tooling for using Qt translations with ease so this template essencially provides a non-localized app, this is not to say that it can't be added when building upon it.

With the exception of the points above, we believe this template to be decently production ready.

## Usage 🚀

- The app is automatically built by a pipeline with every release, so we provide **direct download links** for most operating systems.

- ### Windows 🪟

  - [Use this link to start the download.](https://github.com/NEIAAC/python-template/releases/latest/download/Windows.zip)

  - Start the `exe` file **inside** the extracted folder by _double clicking_ on it, you can create a shortcut with any name you like for this file.

  - If you get a message from Windows with a warning that blocks the app from running, look for the **hidden** continue **button** and use it to **safely ignore** this warning.

- ### Linux 🐧

  - [Use this link to start the download.](https://github.com/NEIAAC/python-template/releases/latest/download/Linux.zip)

  - Start the `bin` file **inside** the extracted folder, remember to **update the execution permissions** first by opening a terminal and running:

      ```shell
      chmod +x <name>.bin
      ./<name>.bin
      ```

  - This binary has been successfully tested on Ubuntu and Arch with both the Wayland and X11 protocols, other setups may need additional tinkering.

- ### MacOS 🍎

  - [Use this link to start the download.](https://github.com/NEIAAC/python-template/releases/latest/download/MacOS.zip)

  - Start the extracted bundle `app` by _clicking_ on it.

  - If the app fails to open, go to [this support page](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac) and select your OS version at the top, then follow the instructions.

## Development 🛠️

- ### Requirements 📋

  - Python 3.12.0+

- ### Setup ⚙️

  - Clone the repository and open a terminal **inside** it.

  - Install the dependencies:

    ```shell
    # It is it recommend that a virtual environment is set before doing this!

    pip install .
    ```

  - Start the app:

    ```shell
    python src/main.py
    ```

- ### Tooling 🧰

  - Mypy is used for type checking:

    ```shell
    pip install .[lint]
    mypy src/main.py
    ```

  - Ruff is used as a linter and formatter:

    ```shell
    pip install .[lint]
    ruff check --fix
    ruff format

    # To automatically lint and format on every commit install the pre-commit hooks:
    pre-commit install

    # When using pre-commit hooks, git commands may fail if any files are checked with errors.
    # Changed files must be added to the staged area and commited again to apply fixes.
    ```

- ### Testing 🧪

  - PyTest and PyTest-Qt are used for testing:

    ```shell
    pip install .[test]
    pytest
    ```

- ### Building 📦

  - Nuitka is used for cross-compiling to all supported platforms, this is how the app is built from the source code, in each release:

    ```shell
    pip install .[build]
    nuitka <options> src/main.py
    ```

    See the [deploy workflow](./.github/workflows/deploy.yaml) for a list of options used for each platform.

## Notes 📝

When using this repository as a template make sure to:

- Edit the app information in the `src/config/metadata.py` file. Along with being used in the code, these values are
also used during the build process to set specific data in the binaries.

- Change the version string in the `.manifest.json` file, otherwise the project will start at the same version as the template. You only need to change the version here, the next triggered release will update any other related files based on the new version.

- Update the description and hard coded repository links in this `README.md`, specifically the download links in the **Usage** section.

- Be aware that signing apps for MacOS and Windows is not done automatically. If you need app signing, it is recommended to introduce it in the build/deploy workflow.

- Delete these notes.
