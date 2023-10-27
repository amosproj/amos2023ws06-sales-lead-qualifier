<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>
SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>
-->

# Sales-Lead-Qualifier Project (AMOS WS 2023/24)

## Sum Insight Logo

<picture>
  <source media="(prefers-color-scheme:dark)" scrset="https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/45459787/7d38795e-6bd5-4003-9b23-29911532b0f8">
  <source media="(prefers-color-scheme:light)" scrset="https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/45459787/a7314df0-1917-4384-8f6c-2ab9f9831047">
  <img alt="Sum Insights Logo" src="https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/45459787/a7314df0-1917-4384-8f6c-2ab9f9831047">
</picture>

## Creating the Environment

To create the virtual environment in this project you must have `pipenv` installed on your machine. Then run the following commands:

```[bash]
# for development environment
pipenv install --dev
# for production environment
pipenv install
```

To work within the environment you can now run:

```[bash]
# to activate the virtual environment
pipenv shell
# to run a single command
pipenv run <COMMAND>
```

To install new packages in the environment add them to the `Pipfile`. Always pin the exact package version to avoid package conflicts and unexpected side effects from package upgrades.

```[bash]
# to add a package to the development environment
[dev-packages]
<PACKAGE_NAME> = "==<VERSION_NUMBER>"
# to add a package to the production environment
[packages]
<PACKAGE_NAME> = "==<VERSION_NUMBER>"
```

Note that this project runs under an MIT license and we only permit the use of non-copyleft-licensed packages. Please be aware of this when installing new packages and inform yourself before blindly installing.

When you have any issues with the environment contact `felix-zailskas`.

### License

This project is operated under an MIT license. Every file must contain the REUSE-compliant license and copyright declaration:

[REUSE documentation](https://reuse.software/faq/)

```[bash]
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023
```

### Pre-Commit Hooks

This repository uses `pre-commit` hooks to ensure a consistent and clean file organization. Each registered hook will be executed when committing to the repository. To ensure that the hooks will be executed they need to be installed using the following command:

```[bash]
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
