import apiClient from './client';
const BASE = '/ingredients'

export async function getIngredients() {
  const response = await apiClient.get(`${BASE}/`);
  return response.data;
}

export async function createIngredient(name, shoppingCategory) {
  const response = await apiClient.post(`${BASE}/`, {
    name,
    shopping_category: shoppingCategory,
  });
  return response.data;
}

export async function deleteIngredient(id) {
  await apiClient.delete(`${BASE}/${id}`);
}