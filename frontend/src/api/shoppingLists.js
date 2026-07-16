import apiClient from './client';
const BASE = '/shopping-lists';


export async function getShoppingLists() {
  const response = await apiClient.get(`${BASE}/`);
  return response.data;
}

export async function createShoppingList(name) {
  const response = await apiClient.post(`${BASE}/`, { name });
  return response.data;
}

export async function deleteShoppingList(id) {
  await apiClient.delete(`${BASE}/${id}`);
}

export async function addItemToList(listId, item) {
  const response = await apiClient.post(`${BASE}/${listId}/items`, item);
  return response.data;
}

export async function deleteItemFromList(listId, itemId) {
  await apiClient.delete(`${BASE}/${listId}/items/${itemId}`);
}

export async function updateItem(listId, itemId, updates) {
  const response = await apiClient.patch(`${BASE}/${listId}/items/${itemId}`, updates);
  return response.data;
}