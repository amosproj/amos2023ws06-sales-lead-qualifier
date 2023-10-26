<!--
SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2023 Ruchita Nathani
SPDX-FileCopyrightText: 2023 Ahmed Sheta
-->

# Contribution Workflow

## Branching Strategy

**main**: It contains fully stable production code

- **dev**: It contains stable under-development code

  - **epic**: It contains a module branch. Like high level of feature. For example, we have an authentication module then we can create a branch like "epic/authentication"

    - **feature**: It contains specific features under the module. For example, under authentication, we have a feature called registration. Sample branch name: "feature/registration"

    - **bugfix**: It contains bug fixing during the testing phase and branch name start with the issue number for example "bugfix/3-validate-for-wrong-user-name"

## Commits and Pull Requests

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
> Co-authored-by: Manu Musterperson <manu.musterperson@fau.de>" --signoff
```

## Pull Request Workflow

The **main** and **dev** branches are protected against direct pushes, which means that we want to do a Pull Request (PR) in order to merge a developed branch into these branches. Having developed a branch (let's call it **feature-1**) and we want to merge **feature-1** branch into **main** branch.

Here is a standard way to merge pull requests:

1. Have all your local changes added, committed, and pushed on the remote **feature-1** branch

   ```[bash]
   git checkout feature-1
   git add .
   git commit -m "added a feature" --signoff  # don't forget the signoff ;)
   git push
   ```

2. Make sure your local main branch up-to-date

   ```[bash]
   git checkout main
   git pull main
   ```

3. Go to [Pull Requests](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/pulls) > click on "New pull request" > make sure the base is **main** branch (or **dev** branch, depends on which branch you want to update) and the compare to be your **feature-1** branch, as highlighted in the photo below and click "create pull requests":
   ![image](https://github.com/amosproj/amos2023ws06-sales-lead-qualifier/assets/95130956/3eceb19d-bdb7-41bd-aa58-07ed7fb6148a)

   Make sure to link the issue your PR relates to.

4. Inform the other SDs on slack that you have created the PR and it is awaiting a review and wait for others to review your code. The reviewers will potentially leave comments and change requests in their PR review. If this is the case reason why the change request is not warranted or checkout your branch again and apply the requested changes. Then push your branch once more and request another review by the reviewer. Once there are no more change requests and the PR has been approved by another SD you can merge the PR into the target branch.

5. Delete the feature branch **feature-1** once it has been merged into the target branch.

_**In case of merge conflict:**_

Should we experience merge conflict after step 3, we should solve the merge conflicts manually, below the title of "This branch has conflicts that must be resolved" click on web editor (you can use vscode or any editor you want).
The conflict should look like this:

```[bash]
<<<<<<< HEAD
// Your changes at **feature-1** branch
=======
// Data already on the main branch
>>>>>>> main
```

-choose which one of these you would adopt for the merge to the **main** branch, we would be better off solving the merge -conflicts together rather than alone, feel free to announce it in the slack group chat.
-mark it as resolved and remerge the PR again, there shouldn't any problem with it.

Feel free to add more about that matter here.