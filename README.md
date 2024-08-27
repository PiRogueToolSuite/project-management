<div align="center">
<img width="60px" src="https://pts-project.org/android-chrome-512x512.png">
<h1>PiRogue project management</h1>
<p>
The unique place where we describe the ongoing tasks as well as what have been done so far.
</p>
<p>
<a href="https://pts-project.org">Website</a> | 
<a href="https://pts-project.org/docs/">Documentation</a> | 
<a href="https://discord.gg/qGX73GYNdp">Support</a>
</p>
</div>

# How to report activities

If a user story has no tasks, add a comment at the user story level. If a user story has tasks, add a comment at the task level.

Use the following template:
```markdown 
#### This month
What have you done this month? You can include images, links, etc.

#### Next month
What are you planning to do the next month?

#### Challenges
What challenges have you faced this month?
```

# How to generate the list of all the commits of the month

You first have to export your GitHub token as an environment variable `GITHUB_TOKEN`. If you don't have generated a token yet, you can do it [here](https://github.com/settings/tokens).

Then, you run the Python script `generate_commits.py` to generate the list of all commits of the month. The script will generate a markdown file `commits.md`in the folder `output`.

