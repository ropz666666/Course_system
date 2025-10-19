import argparse

PROMPT_CHOOSE_PROMPT = '''
You are a helpful assistant with access to these prompts:
{prompts_description}
Choose the appropriate prompt based on the user's instruction.
If no prompt is needed, reply None.
IMPORTANT: When you need to use a prompt, you must ONLY respond with the exact JSON object format below, nothing else:
{{
    "prompt": "prompt-name",
}}
Here are some Error output cases:
Please use only the prompts that are explicitly defined above.
'''

parser = argparse.ArgumentParser(description='Agent module')
parser.add_argument("--model_name", type=str, default="gpt-4o", help='Radius of cylinder')
parser.add_argument("--base_url", type=str, default="https://api.rcouyi.com/v1", help='Radius of cylinder')
parser.add_argument("--api_key", type=str, default="sk-pAauG9ss64pQW9FVA703F1453b334eFb95B7447b9083BaBd", help='Radius of cylinder')
parser.add_argument("--select_agent_prompt", type=str, default=PROMPT_CHOOSE_PROMPT, help="")

args = parser.parse_args()







