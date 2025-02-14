# Report for assignment 3

## Project

Name: `python-discord/bot`

URL: https://github.com/python-discord/bot/tree/main

It is a Discord bot specifically for use with the Python Discord server which has ~400k members. It provides numerous utilities and other tools to help keep the server running like a well-oiled machine.

## Onboarding experience

It mostly ran flawlessly, with a few caveats as outlined below:
- @strengthless was on Apple Silicon M2 chip, and some docker images were not pulled successfully on the first try.
  - I had to refer to [this stack overflow article](https://stackoverflow.com/questions/65456814/docker-apple-silicon-m1-preview-mysql-no-matching-manifest-for-linux-arm64-v8) and run the command `export DOCKER_DEFAULT_PLATFORM=linux/x86_64/v8`
- @strengthless kept getting the `PrivilegedIntentsRequired` error upon docker startup.
  - Turns out when setting up [Privileged Gateway Intents](https://www.pythondiscord.com/pages/guides/pydis-guides/contributing/bot/#privileged-intents), aside from `Server Member Intent`, you also need to enable `Message Content Intent`, which is a relatively new intent introduced by Discord.
  - We have submitted a PR in [python-discord/site](https://github.com/python-discord/site/pull/1470) for updating the relevant documentations, which has been accepted.

After setting up the environment, we ran a quick analysis on LoCs and test coverage:
```bash
# lines of code in python (~19.3k)
cloc ./bot
# branch coverage (~50%)
poetry run task test-cov && poetry run task report
```

With everything combined, we deemed the project suitable for this assignment.

## Complexity

1. What are your results for five complex functions?
    * Did all methods (tools vs. manual count) get the same result?
    * Are the results clear?
2. Are the functions just complex, or also long?
3. What is the purpose of the functions?
4. Are exceptions taken into account in the given measurements?
5. Is the documentation clear w.r.t. all the possible outcomes?

## Refactoring

Plan for refactoring complex code:

Estimated impact of refactoring (lower CC, but other drawbacks?).

Carried out refactoring (optional, P+):

git diff ...

## Coverage

### Tools

Document your experience in using a "new"/different coverage tool.

How well was the tool documented? Was it possible/easy/difficult to
integrate it with your build environment?

### Your own coverage tool

Show a patch (or link to a branch) that shows the instrumented code to
gather coverage measurements.

The patch is probably too long to be copied here, so please add
the git command that is used to obtain the patch instead:

git diff ...

What kinds of constructs does your tool support, and how accurate is
its output?

### Evaluation

1. How detailed is your coverage measurement?

2. What are the limitations of your own tool?

3. Are the results of your tool consistent with existing coverage tools?

## Coverage improvement

Show the comments that describe the requirements for the coverage.

Report of old coverage: [link]

Report of new coverage: [link]

Test cases added:

git diff ...

Number of test cases added: two per team member (P) or at least four (P+).

## Self-assessment: Way of working

Current state according to the Essence standard: ...

Was the self-assessment unanimous? Any doubts about certain items?

How have you improved so far?

Where is potential for improvement?

## Overall experience

What are your main take-aways from this project? What did you learn?

Is there something special you want to mention here?
