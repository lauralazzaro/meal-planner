import apiClient from './client';
const BASE = '/dishes';

export async function getDishes() {
  const response = await apiClient.get(`${BASE}`);
  return response.data.items;
}

export async function createDish(label, comment, mainIngredientId) {
  const response = await apiClient.post(`${BASE}`, {
    label: label || null,
    comment: comment || null,
    main_ingredient_id: parseInt(mainIngredientId),
  });
  return response.data;
}

export async function deleteDish(id) {
  await apiClient.delete(`${BASE}${id}`);
}