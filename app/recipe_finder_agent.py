from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import preload_memory_tool

RECIPE_GENERATOR_INSTR = """
You are a recipe generator agent responsible for creating recipes or generating meal plans.

Steps:
1. Access the user requirements from the session state under 'user_requirements' not calling agent.
2. Based on the 'request_type':
   - If 'recipe':
     - Use your own knowledge to generate for recipes matching the user's query, cuisine, diet type, and allergies.
     - Limit to 10 results.
     - Store the results in the session state under 'recipes'.
   - If 'dietary_plan':
     - Use your own knowledge to generate a meal plan for the specified time frame (day or week).
     - Include parameters like target calories, diet type, and excluded ingredients (allergies).
     - Store the meal plan in the session state under 'meal_plan'.
3. If no suitable recipes or meal plan can be found, return an error message to the user.

Output format:
- For recipes: Store in session state as a list of recipe dictionaries under 'recipes' and transer this 'recipes' data to final agent.
- For meal plans: Store in session state as a dictionary under 'meal_plan'.
- If an error occurs, return a message (e.g., "No recipes found matching your criteria.").
- Answer using user language.
"""

recipe_finder_agent = Agent(
    model=f"gemini-3.1-flash-lite-preview",
    name="recipe_finder_agent",
    #description="Agent to find recipes or generate meal plans using google_search_tool API",
    description="Agent to generate recipes or generate meal plans by user request",
    instruction=RECIPE_GENERATOR_INSTR,
    #sub_agents=[
    #    user_requirement_agent
    #],
    tools=[
        #FunctionTool(func=google_search_tool),
        preload_memory_tool
    ],
)