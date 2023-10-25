<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023
-->

# Sales-Lead-Qualifier Project (AMOS WS 2023/24)

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

## Contribution Workflow

### Branching Strategy

**main**: It contains fully stable production code

- **dev**: It contains stable under-development code

  - **epic**: It contains a module branch. Like high level of feature. For example, we have an authentication module then we can create a branch like "epic/authentication"

    - **feature**: It contains specific features under the module. For example, under authentication, we have a feature called registration. Sample branch name: "feature/registration"

    - **bugfix**: It contains bug fixing during the testing phase and branch name start with the issue number for example "bugfix/3-validate-for-wrong-user-name"

### Commits and Pull Requests

The stable branches `main` and `dev` are protected against direct pushes. To commit code to these branches create a pull request (PR) describing the feature/bugfix that you are committing to the `dev` branch. This PR will then be reviewed by another SD from the project. Only after being approved by another SD a PR may be merged into the `dev` branch. Periodically the stable code on the `dev` branch will be merged into the `main` branch by creating a PR from `dev`. Hence, every feature that should be committed to the `main` branch must first run without issues on the `dev` branch for some time.

Before contributing to this repository make sure that you are identifiable in your git user settings. This way commits and PRs created by you can be identified and easily traced back.

```[bash]
git config --local user.name "Manu Musterperson"
git config --local user.email "manu@musterperson.org"
```

Any commit should always contain a commit message that references an issue created in the project. Also, always signoff on your commits for identification reasons.

```[bash]
git commit -m "Fixed issue #123" --signoff
```

When doing pair programming be sure to always have all SDs mentioned in the commit message. Each SD should be listed on a new line for clarity reasons.

```[bash]
git commit -a -m "Fixed problem #123
> Co-authored-by: Manu Musterperson <manu.musterperson@fau.de>"
```

### License

This project is operated under an MIT license. Every file must contain the REUSE-compliant license and copyright declaration:

[REUSE documentation](https://reuse.software/)

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
