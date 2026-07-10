import apiClient from './client';

export async function getDishes() {
  const response = await apiClient.get('/dishes/');
  return response.data;
}

export async function createDish(label, comment, mainIngredientId) {
  const response = await apiClient.post('/dishes/', {
    label: label || null,
    comment: comment || null,
    main_ingredient_id: parseInt(mainIngredientId),
  });
  return response.data;
}

export async function deleteDish(id) {
  await apiClient.delete(`/dishes/${id}`);
}