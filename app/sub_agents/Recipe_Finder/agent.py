from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.preload_memory_tool import preload_memory_tool

RECIPE_FINDER_INSTR = """
You are a recipe finder agent responsible for fetching recipes or generating meal plans using the google search API.

Steps:
1. Access the user requirements from the session state under 'user_requirements'.
2. Based on the 'request_type':
   - If 'recipe':
     - Use the google_search_tool to search for recipes matching the user's query, cuisine, diet type, and allergies.
     - Limit to 10 results.
     - Store the results in the session state under 'recipes'.
   - If 'dietary_plan':
     - Use the google_search_tool API to generate a meal plan for the specified time frame (day or week).
     - Include parameters like target calories, diet type, and excluded ingredients (allergies).
     - Store the meal plan in the session state under 'meal_plan'.
3. If no suitable recipes or meal plan can be found, return an error message to the user.

Output format:
- For recipes: Store in session state as a list of recipe dictionaries under 'recipes' and transer this 'recipes' data to final agent.
- For meal plans: Store in session state as a dictionary under 'meal_plan'.
- If an error occurs, return a message (e.g., "No recipes found matching your criteria.").
- Answer using user language.
"""
from typing import Dict, List, Any
from google.adk.tools import ToolContext
from google import genai
import json
from pydantic import BaseModel, Field, TypeAdapter
from google.genai import types
import os

class Recipe(BaseModel):
    recipe_name: str = Field(description="The name of the recipe.")
    summary: str = Field(description="A very brief 1-sentence summary of the dish.")
    ingredients_preview: list[str] = Field(description="A list of 3-5 main ingredients.")

def search_recipes_with_gemini(
    query: str,
    diet: str | None = None,
    intolerances: list[str] | None = None,
    cuisine: str | None = None,
    max_results: int = 3
) -> list[Recipe]:    
    # 1. Gemini에게 전달할 검색 프롬프트 구성
    # Schema가 형식을 제어하므로 프롬프트는 검색 조건에 집중합니다.
    search_prompt = f"Find exactly {max_results} distinct recipes for '{query}' using Google Search."

    constraints = []
    if cuisine:
        constraints.append(f"Cuisine style must be {cuisine}.")
    if diet:
        constraints.append(f"Must be compliant with a {diet} diet.")
    if intolerances:
        intolerance_str = ", ".join(intolerances)
        constraints.append(f"Must NOT contain ingredients: {intolerance_str}.")

    if constraints:
        search_prompt += " strictly following these constraints: " + " ".join(constraints)

    search_prompt += "\nExtract key details for each recipe found."
    search_prompt += "\nRemove any data in header like ```json"

    # 2. 모델 설정 (Google Search Grounding + JSON Schema)
    client = genai.Client(vertexai=True, 
                          project=os.environ.get("GOOGLE_CLOUD_PROJECT"), 
                          location=os.environ.get("GOOGLE_CLOUD_LOCATION"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=search_prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": TypeAdapter(list[Recipe]).json_schema(),
            "tools": [types.Tool(google_search=types.GoogleSearch())],
            "thinking_config": types.ThinkingConfig(include_thoughts=False, thinking_budget=None),
            "safety_settings": [types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
                ),types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
                ),types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
                ),types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
                )
            ]
        },
    )
    start = response.text.find("[")
    end = response.text.rfind("]")
    return json.loads(response.text[start:end+1])

def google_search_tool(query: str, tool_context: ToolContext) -> List[Dict[str, Any]]:
    """
    Tool function to search recipes and store results in the tool context state.

    Args:
        query: The search query or parameters in JSON format.
        tool_context: The ADK tool context.

    Returns:
        A list of recipe dictionaries.
    """
    if "recipes" not in tool_context.state:
        tool_context.state["recipes"] = []

    params = eval(query) if isinstance(query, str) and query.startswith("{") else {"query": query}

    result = search_recipes_with_gemini(
        query=params.get("query", ""),
        diet=params.get("diet"),
        intolerances=params.get("intolerances"),
        cuisine=params.get("cuisine")
    )
    tool_context.state["recipes"] = result
    return result

recipe_finder_agent = Agent(
    model="gemini-2.5-flash",
    name="recipe_finder_agent",
    description="Agent to find recipes or generate meal plans using google_search_tool API",
    instruction=RECIPE_FINDER_INSTR,
    tools=[
        FunctionTool(func=google_search_tool),
        preload_memory_tool
        ],
)