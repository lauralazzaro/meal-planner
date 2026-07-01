def create_test_ingredient(client, name="Pomodoro", category="vegetables"):
    """Helper to create an ingredient and return its data."""
    response = client.post(
        "/ingredients/",
        json={"name": name, "shopping_category": category},
    )
    
    return response.json()


def test_create_dish_with_ingredients(client):
    """Creating a dish should link it to existing ingredients with quantities."""
    ingredient = create_test_ingredient(client)

    response = client.post(
        "/dishes",
        json={
            "name": "Pasta al pomodoro",
            "meal_type": "both",
            "nutritional_tags": ["carbs", "vegetables"],
            "ingredients": [
                {"ingredient_id": ingredient["id"], "quantity": 200, "unit": "g"}
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Pasta al pomodoro"
    assert len(data["dish_ingredients"]) == 1
    assert data["dish_ingredients"][0]["quantity"] == 200
    assert data["dish_ingredients"][0]["ingredient"]["name"] == "Pomodoro"


def test_create_dish_with_nonexistent_ingredient_returns_404(client):
    """Creating a dish with an ingredient_id that doesn't exist should fail clearly."""
    response = client.post(
        "/dishes",
        json={
            "name": "Piatto impossibile",
            "meal_type": "lunch",
            "nutritional_tags": [],
            "ingredients": [{"ingredient_id": 9999}],
        },
    )

    assert response.status_code == 404