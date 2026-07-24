import apiClient from './client';
const BASE = '/ingredients'

export async function getIngredients(cursor) {
  const response = await apiClient.get(`${BASE}/`, {
    params: cursor ? { after: cursor } : {},
  });
  return response.data; // { items, next_cursor, has_next }
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