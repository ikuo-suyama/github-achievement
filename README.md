# github-achievement
Simple scripts to count your or someone's achievement.

# How to use
Python 11+

1. Install poetry
```sh
$ pipx install poetry
$ poetry install
```

2. run scripts
You need to generate classic Github Token which has repo.read

```sh
$ export GITHUB_TOKEN=<<YOUR PERSONAL GITHUB TOKEN>>

# Generate PR lists which the user open and merged in specified duration
$ poetry run python github_achievement.py -u ikuo-suyama -s YYYY-MM-DD -e YYYY-MM-DD

# Generate PR lists which the user give PR comment in specified duration
$ poetry run python github_comment.py -u ikuo-suyama -s YYYY-MM-DD -e YYYY-MM-DD
```

these command generates ./data/username/reviewed_pr_list.md, ./data/username/merged_pr_list.md, and summarize contribution by repo.