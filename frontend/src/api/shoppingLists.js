import apiClient from './client';

export async function getShoppingLists() {
  const response = await apiClient.get('/shopping-lists/');
  return response.data;
}

export async function createShoppingList(name) {
  const response = await apiClient.post('/shopping-lists/', { name });
  return response.data;
}

export async function deleteShoppingList(id) {
  await apiClient.delete(`/shopping-lists/${id}`);
}

export async function addItemToList(listId, item) {
  const response = await apiClient.post(`/shopping-lists/${listId}/items`, item);
  return response.data;
}

export async function deleteItemFromList(listId, itemId) {
  await apiClient.delete(`/shopping-lists/${listId}/items/${itemId}`);
}

export async function updateItem(listId, itemId, updates) {
  const response = await apiClient.patch(`/shopping-lists/${listId}/items/${itemId}`, updates);
  return response.data;
}