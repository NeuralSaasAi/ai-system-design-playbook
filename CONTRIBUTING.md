# Contributing

Thanks for helping. This playbook only works if it stays accurate and easy to read, so every fix counts, including a single clearer sentence.

## Ways to help

- **Write a case study.** Pick one marked 📝 in the [README catalog](README.md#case-studies), or propose your own with the [case study form](https://github.com/NeuralSaasAi/ai-system-design-playbook/issues/new?template=propose-case-study.yml).
- **Fix something wrong or unclear.** Use the [content fix form](https://github.com/NeuralSaasAi/ai-system-design-playbook/issues/new?template=content-fix.yml), or open a pull request.
- **Report a broken link.** Use the [broken link form](https://github.com/NeuralSaasAi/ai-system-design-playbook/issues/new?template=broken-link.yml).
- **Share a production lesson.** If you have run a system like one of ours, tell us what broke and what you changed. Open a content fix issue and we will work it into the case study with credit.

New to pull requests? Click the pencil icon on any page on GitHub, make your edit, and GitHub walks you through the rest.

## Writing a case study

1. **Claim it.** Comment on the case study's issue, or open a proposal. This avoids two people writing the same one. If you don't deliver in a few weeks, we will release the claim to others without hard feelings.
2. **Read the method.** [DESIGN-METHOD.md](DESIGN-METHOD.md) explains the 10 steps every case study follows.
3. **Copy the template.** Copy [templates/case-study-template.md](templates/case-study-template.md) to `case-studies/NN-your-slug.md`. Use the next free number, or the number shown in the catalog.
4. **Follow the style guide.** [STYLE.md](STYLE.md) covers language, numbers, sources and formatting.
5. **Update the README catalog.** Link your file in its row and set the status emoji to match the front matter.
6. **Run the checks.** `make check` must pass.
7. **Open a pull request.** Fill in the checklist honestly. Start with status `draft`. A maintainer and one other reader move it to `reviewed`.

## What we accept

- Original writing. Don't copy from other repos, courses, books or videos. Other repos can inspire topics. They cannot be a source for text, structure, diagrams or code.
- Plain language for engineers who know the Part 1 basics. If a basic idea needs explaining, link to Part 1 instead.
- Numbers that come from formulas on the page.
- Facts that link to primary sources (official docs, standards, original research, reputable reporting).
- No promotional links, referral codes or tracking parameters.

## Run the checks locally

You need Python 3.12 or later, [uv](https://docs.astral.sh/uv/), and Node.js (for the markdown linter).

```bash
make check   # case study format, catalog, relative links, markdown lint, checker tests
make links   # external link check (needs lychee: brew install lychee)
```

## Disclosure

If you work for, own, or are paid by a product you feature in a case study, say so in the pull request. You are welcome to contribute. We just need to know.

## Code of Conduct

By taking part, you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
