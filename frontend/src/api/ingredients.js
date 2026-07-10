import apiClient from './client';

export async function getIngredients() {
  const response = await apiClient.get('/ingredients/');
  return response.data;
}

export async function createIngredient(name, shoppingCategory) {
  const response = await apiClient.post('/ingredients/', {
    name,
    shopping_category: shoppingCategory,
  });
  return response.data;
}

export async function deleteIngredient(id) {
  await apiClient.delete(`/ingredients/${id}`);
}