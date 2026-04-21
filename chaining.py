from prompt_engine import generate_prompt


def run_chaining(steps, initial_input, temperature=0.7, max_tokens=300):
    """
    Executes a sequence of prompt steps where each step's output
    becomes the input for the next step.

    Args:
        steps (list): List of prompt templates (can contain {input})
        initial_input (str): Initial input for the first step
        temperature (float): Controls randomness of output
        max_tokens (int): Maximum tokens for response

    Returns:
        list: List of tuples containing (step_name, prompt_used, output)
    """

    if not steps:
        raise ValueError("Steps list cannot be empty")

    all_outputs = []
    current_input = initial_input

    for step_index, step_prompt in enumerate(steps, start=1):

        if not isinstance(step_prompt, str) or not step_prompt.strip():
            raise ValueError(f"Invalid prompt at step {step_index}")

        # Replace placeholder or append input
        if "{input}" in step_prompt:
            full_prompt = step_prompt.replace("{input}", current_input)
        else:
            full_prompt = f"{step_prompt.strip()} {current_input}"

        try:
            output = generate_prompt(
                full_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            output = f"[Error at Step {step_index}]: {str(e)}"

        all_outputs.append((f"Step {step_index}", full_prompt, output))
        current_input = output

    return all_outputs
