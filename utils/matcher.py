def match_recipes(ingredients, filters, all_recipes):
    matched = []

    for recipe in all_recipes:
        recipe_ingredients = [i.lower() for i in recipe.get('ingredients', [])]
        recipe_diets = recipe.get('diet', [])

        # Match if at least one ingredient overlaps
        if any(ing in recipe_ingredients for ing in ingredients):
            # Match if no filters OR any filter matches recipe's diet tags
            if not filters or any(f in recipe_diets for f in filters):
                matched.append(recipe)

    return matched