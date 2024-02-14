<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
-->

# Creating the Environment

The repository contains the file `.env.template`. This file is a template for
the environment variables that need to be set for the application to run. Copy
this file into a file called `.env` at the root level of this repository and
fill in all values with the corresponding secrets.

To create the virtual environment in this project you must have `pipenv`
installed on your machine. Then run the following commands:

```bash
# for development environment
pipenv install --dev
# for production environment
pipenv install
```

To work within the environment you can now run:

```bash
# to activate the virtual environment
pipenv shell
# to run a single command
pipenv run <COMMAND>
```

# Build Process

This application is built and tested on every push and pull request creation
through Github actions. For this, the `pipenv` environment is installed and then
the code style is checked using `flake8`. Finally, the `tests/` directory is
executed using `pytest` and a test coverage report is created using `coverage`.
The test coverage report can be found in the Github actions output.

In another task, all used packages are tested for their license to ensure that
the software does not use any copy-left licenses and remains open source and
free to use.

If any of these steps fail for a pull request the pull request is blocked from
being merged until the corresponding step is fixed.

Furthermore, it is required to install the pre-commit hooks as described
[here](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/wiki/Knowledge#pre-commit).
This ensures uniform coding style throughout the project as well as that the
software is compliant with the REUSE licensing specifications.

# Running the app

To run the application the `pipenv` environment must be installed and all needed
environment variables must be set in the `.env` file. Then the application can
be started via

```bash
pipenv run python src/main.py
```

# Pre-Commit Hooks

This repository uses `pre-commit` hooks to ensure a consistent and clean file organization. Each registered hook will be executed when committing to the repository. To ensure that the hooks will be executed they need to be installed using the following command:

```bash
pre-commit install
```

The following things are done by hooks automatically:

- formatting of python files using black and isort
- formatting of other files using prettier
- syntax check of JSON and yaml files
- adding new line at the end of files
- removing trailing whitespaces
- prevent commits to `dev` and `main` branch
- check adherence to REUSE licensing format
