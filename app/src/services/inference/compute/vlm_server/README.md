# GNOSIS VLM SERVER
- **Goal**: Being able to run inference on as many VLMs as we want thru one endpoint. As modular and flexible as possible.
- **Status**: WIP
- **Todo**: Figure out how to serve all these models in one server. 
- **Down the Line**: Build more
- **Thoughts**: None.

## HOW TO DO WORK

## ENVIRONMENT
- Make sure to have uv on your machine. 
- I will change to use python 3.14 but for now just 3.13. Why? Because cooler and **threading is cool**. If you have a problem with this *please forward complaints to HR.*

```bash
# Use uv or else...
uv venv
uv pip install -r requirements.txt
```

```bash
# Install pre-commit hook (formats with Ruff on commit) - ruff is cool because Rust omg rust moment hype
pre-commit install
```

## Commits and formatting
```bash
pre-commit run --all-files # in case you forgot to do this before
```

```bash
git commit -m "[YOUR COOL COMMIT MESSAGE]" # otherwise just commit normally and it should format your code.
```

## EXCECUTE

## NOTES