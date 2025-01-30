# Contributing to *`Eyes`* on Github from VS Code

## Create a Github account and log in

Of course, if you haven't already done so.

## Go to the project's Github repository

If you're reading this file, you're probably already there. If not, go to https://github.com/Hugues-DTANKOUO/Eyes.
Take the opportunity to star this repository and follow my account accessible at https://github.com/Hugues-DTANKOUO.

## Create a personal copy of the repository (Fork)

Once [on the repository](https://github.com/Hugues-DTANKOUO/Eyes), click on the `Fork` button, then on `Create fork`.

Copy your fork's address. It will probably look like this: https://github.com/<your_git_username>/eyes

## Install Git on your machine if you haven't already

To check if you have git in your command prompt, execute the command:
```shell
git
```

## Clone your fork

- Open `VS Code` in the folder where you want to work on this project.
- Open your `terminal` in `VS Code`
- Execute the command (Replace `<your_fork_address>` with the address you copied)
```shell
git clone <your_fork_address>
```

## Install the following GitHub extensions in your VS Code

- `GitHub`
- `GitHub Markdown Preview`

## Configure a remote upstream

To track changes from the original repository, add the original repository as an "upstream" remote using the command:
```shell
git remote add upstream https:github.com/Hugues-DTANKOUO/Eyes
```

## Create a new branch

Before making changes, create a new branch with the command
```shell
git checkout -b branch_name
```
You can also do this in `VS Code` by clicking on your branch name at the bottom left (which is probably currently `main`)

![screenshot of branch position in VS Code](/assets/Screenshot/main-branch-vs-code.png)

Then click on `Create new branch...`, give your branch a simple name without spaces (`snake_case` recommended with `_` or `-`), and create it.

![screenshot to create a new branch](/assets/Screenshot/create-branch-vs-code.png)

## Make your changes

Before doing so, make sure you've installed the project dependencies [with poetry using this link](/eyes/docs/python-3-poetry.md)

Use VS Code to modify the code as you know how to do it or as we did in the previous exercises of our Python training.

## Push your changes to your online fork (`Commit`)

Use the command:
```shell
git add
```
To add your changes, then the command
```shell
git commit -m "Your commit message"
```
To `commit` your changes.

You can also do this in `VS Code` like this:
In the menu bar on the left, click on the icon

![Git branch in VS Code](/assets/Screenshot/git-branch-vs-code.png)

Then enter your `commit` message and click on `Commit`.

## Push your branch to your `fork` on Github

Execute the command
```shell
git push origin branch_name
```

## Open a Pull Request (PR)

On GitHub:
- Go to [the original repository](https://github.com/Hugues-DTANKOUO/eyes) and click on *`"New pull request"`*
- Select your branch and follow the instructions to create the `PR`.