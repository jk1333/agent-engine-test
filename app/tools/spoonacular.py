"""Wrapper to Spoonacular API for recipe and dietary planning."""

import os
import logging
from typing import Dict, List, Any, Optional

import requests
from google.adk.tools import ToolContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpoonacularService:
    """Wrapper for Spoonacular API to handle recipe searches, meal plans, and nutritional data."""

    def __init__(self):
        self._check_key()
        self.base_url = "https://api.spoonacular.com"

    def _check_key(self):
        """Ensure the Spoonacular API key is available in the environment."""
        if not hasattr(self, "api_key") or not self.api_key:
            self.api_key = os.getenv("SPOONACULAR_API_KEY")
            if not self.api_key:
                raise ValueError("SPOONACULAR_API_KEY not found in environment variables.")
            logger.info(f"Spoonacular API Key loaded: {self.api_key[:5]}...")

    def search_recipes(self, query: str, diet: Optional[str] = None, intolerances: Optional[List[str]] = None, 
                      cuisine: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for recipes based on user preferences using Spoonacular API.

        Args:
            query: The search query (e.g., "chicken curry").
            diet: Diet type (e.g., "vegetarian", "keto").
            intolerances: List of allergens to exclude (e.g., ["nuts", "dairy"]).
            cuisine: Preferred cuisine (e.g., "Italian").
            max_results: Maximum number of results to return.

        Returns:
            A list of recipe dictionaries in the specified format.
        """
        endpoint = f"{self.base_url}/recipes/complexSearch"
        request_params = {
            "apiKey": self.api_key,
            "query": query,
            "number": max_results,
            "addRecipeNutrition": True
        }
        if diet:
            request_params["diet"] = diet
        if intolerances:
            request_params["intolerances"] = ",".join(intolerances)
        if cuisine:
            request_params["cuisine"] = cuisine

        try:
            response = requests.get(endpoint, params=request_params, timeout=10)
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Spoonacular API response: {data}")

            recipes = []
            for recipe in data.get("results", []):
                ingredients = [
                    ing["name"] for ing in recipe.get("nutrition", {}).get("ingredients", [])
                ]
                protein_content = next(
                    (f"{nut['amount']}g" for nut in recipe.get("nutrition", {}).get("nutrients", []) if nut["name"] == "Protein"),
                    "0g"
                )
                description = recipe.get("summary", "No description available.")[:200]

                recipes.append({
                    "title": recipe["title"],
                    "url": f"https://spoonacular.com/recipes/{recipe['id']}",
                    "ingredients": ingredients,
                    "protein_content": protein_content,
                    "description": description
                })

            return recipes

        except requests.Timeout:
            logger.error("Spoonacular API request timed out after 10 seconds.")
            return []
        except requests.HTTPError as e:
            logger.error(f"Spoonacular API returned an error: {e.response.status_code} - {e.response.text}")
            return []
        except requests.RequestException as e:
            logger.error(f"Error making request to Spoonacular API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while calling Spoonacular API: {e}")
            return []

    def get_nutritional_info(self, recipe_id: int) -> Dict[str, Any]:
        """
        Retrieve nutritional information for a specific recipe.

        Args:
            recipe_id: The ID of the recipe from Spoonacular API.

        Returns:
            A dictionary with nutritional data or an error message.
        """
        endpoint = f"{self.base_url}/recipes/{recipe_id}/nutritionWidget.json"
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                "calories": data.get("calories", "0"),
                "protein": data.get("protein", "0g"),
                "sugar": data.get("sugar", "0g"),
                "carbs": data.get("carbs", "0g"),
                "fat": data.get("fat", "0g")
            }

        except requests.Timeout:
            logger.error("Spoonacular API request timed out after 10 seconds.")
            return {"error": "Request timed out"}
        except requests.HTTPError as e:
            logger.error(f"Spoonacular API returned an error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}"}
        except requests.RequestException as e:
            logger.error(f"Error making request to Spoonacular API: {e}")
            return {"error": f"Request error: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error while fetching nutritional data: {e}")
            return {"error": f"Unexpected error: {e}"}

    def generate_meal_plan(self, time_frame: str = "day", target_calories: Optional[int] = None,
                          diet: Optional[str] = None, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a meal plan based on user constraints.

        Args:
            time_frame: "day" or "week".
            target_calories: Target daily calorie intake.
            diet: Diet type (e.g., "vegetarian", "keto").
            exclude: Ingredients to exclude (e.g., ["nuts", "dairy"]).

        Returns:
            A dictionary with meal plan data or an error message.
        """
        endpoint = f"{self.base_url}/mealplanner/generate"
        params = {
            "apiKey": self.api_key,
            "timeFrame": time_frame
        }
        if target_calories:
            params["targetCalories"] = target_calories
        if diet:
            params["diet"] = diet
        if exclude:
            params["exclude"] = ",".join(exclude)

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data

        except requests.Timeout:
            logger.error("Spoonacular API request timed out after 10 seconds.")
            return {"error": "Request timed out"}
        except requests.HTTPError as e:
            logger.error(f"Spoonacular API returned an error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}"}
        except requests.RequestException as e:
            logger.error(f"Error making request to Spoonacular API: {e}")
            return {"error": f"Request error: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error while generating meal plan: {e}")
            return {"error": f"Unexpected error: {e}"}

# Singleton instance of SpoonacularService, created on first access
_spoonacular_service = None

def get_spoonacular_service() -> SpoonacularService:
    """Get the singleton instance of SpoonacularService."""
    global _spoonacular_service
    if _spoonacular_service is None:
        _spoonacular_service = SpoonacularService()
    return _spoonacular_service

def spoonacular_tool(query: str, tool_context: ToolContext) -> List[Dict[str, Any]]:
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

    # Use the singleton service
    service = get_spoonacular_service()

    # Parse query as JSON if needed, assuming query contains parameters
    params = eval(query) if isinstance(query, str) and query.startswith("{") else {"query": query}
    result = service.search_recipes(
        query=params.get("query", ""),
        diet=params.get("diet"),
        intolerances=params.get("intolerances"),
        cuisine=params.get("cuisine")
    )
    tool_context.state["recipes"] = result
    return result