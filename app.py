import requests
import concurrent.futures
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    ingredients = request.form.get('ingredients', '')
    ingredient_list = [i.strip().lower() for i in ingredients.split(',') if i.strip()]

    # Step 1: Collect unique meal IDs from all ingredients
    meal_ids = set()
    for ingredient in ingredient_list:
        try:
            url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('meals'):
                for meal in data['meals']:
                    meal_ids.add(meal['idMeal'])
        except Exception as e:
            print(f"Error fetching meals for {ingredient}: {e}")

    # Step 2: Fetch meal details in parallel
    def fetch_meal_details(meal_id):
        try:
            detail_url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
            detail_response = requests.get(detail_url, timeout=5)
            detail_data = detail_response.json()
            if detail_data.get('meals'):
                full_recipe = detail_data['meals'][0]
                ingredients_list = [
                    full_recipe.get(f'strIngredient{i}').strip()
                    for i in range(1, 21)
                    if full_recipe.get(f'strIngredient{i}') and full_recipe.get(f'strIngredient{i}').strip()
                ]
                return {
                    'name': full_recipe.get('strMeal'),
                    'instructions': full_recipe.get('strInstructions'),
                    'image': full_recipe.get('strMealThumb'),
                    'ingredients': ingredients_list
                }
        except Exception as e:
            print(f"Error fetching details for meal {meal_id}: {e}")
        return None

    matched_recipes = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(fetch_meal_details, meal_ids)
        matched_recipes = [r for r in results if r]

    return render_template('results.html', recipes=matched_recipes)

if __name__ == '__main__':
    app.run(debug=False)
