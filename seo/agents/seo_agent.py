from agents import Agent, Runner

from .client import get_model_name
from .tools import ALL_TOOLS

INSTRUCTIONS = """\
You are an expert SEO consultant. You help users improve their website's \
search engine optimization through audits, keyword research, and content \
optimization.

When a user asks you to audit a site, research keywords, or optimize content, \
use the appropriate tool. Always provide actionable, specific recommendations.

For general SEO questions, answer directly from your knowledge.
"""


def get_agent():
    return Agent(
        name="SEO Agent",
        instructions=INSTRUCTIONS,
        model=get_model_name(),
        tools=ALL_TOOLS,
    )


def run_seo_agent(user_input, history=None):
    """Run the SEO agent synchronously.

    Args:
        user_input: The user's message string.
        history: Optional list of previous message dicts for conversation context.

    Returns:
        The agent's response text.
    """
    agent = get_agent()

    if history:
        input_items = []
        for msg in history:
            input_items.append({
                "role": msg["role"],
                "content": msg["content"],
            })
        input_items.append({"role": "user", "content": user_input})
    else:
        input_items = user_input

    result = Runner.run_sync(agent, input_items, max_turns=15)
    return result.final_output
