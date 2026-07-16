import apiClient from './client';
const BASE = '/weekly-plans'

export async function getWeeklyPlans() {
  const response = await apiClient.get(`${BASE}`);
  return response.data;
}

export async function createWeeklyPlan(name, isDefault) {
  const response = await apiClient.post(`${BASE}`, {
    name,
    is_default: isDefault,
  });
  return response.data;
}

export async function deleteWeeklyPlan(id) {
  await apiClient.delete(`${BASE}/${id}`);
}

export async function addDishesToPlan(planId, dishEntries) {
  const response = await apiClient.post(`${BASE}/${planId}/dishes`, {
    dishes: dishEntries,
  });
  return response.data;
}

export async function deleteDishFromPlan(planId, entryId) {
  await apiClient.delete(`${BASE}/${planId}/dishes/${entryId}`);
}