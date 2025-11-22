import os


def get_prompt(prompt_name: str):
    prompt_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_paths = os.listdir(prompt_dir)

    for path in prompt_paths:
        if prompt_name == path:
            with open(os.path.join(prompt_dir, path), "r", encoding="UTF-8") as f:
                return f.read().strip()

    raise ValueError(f"prompt {prompt_name} does not exist")
