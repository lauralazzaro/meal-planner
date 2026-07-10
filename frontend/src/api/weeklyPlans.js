import apiClient from './client';

export async function getWeeklyPlans() {
  const response = await apiClient.get('/weekly-plans/');
  return response.data;
}

export async function createWeeklyPlan(name, isDefault) {
  const response = await apiClient.post('/weekly-plans/', {
    name,
    is_default: isDefault,
  });
  return response.data;
}

export async function deleteWeeklyPlan(id) {
  await apiClient.delete(`/weekly-plans/${id}`);
}

export async function addDishesToPlan(planId, dishEntries) {
  const response = await apiClient.post(`/weekly-plans/${planId}/dishes`, {
    dishes: dishEntries,
  });
  return response.data;
}

export async function deleteDishFromPlan(planId, entryId) {
  await apiClient.delete(`/weekly-plans/${planId}/dishes/${entryId}`);
}