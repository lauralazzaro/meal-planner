import apiClient from "./client";
const BASE = '/auth'

export async function registerUser(email, password) {
    const response = await apiClient.post(`${BASE}/register`, {email, password});
    return response.data;    
}

export async function loginUser(email, password) {
  // The backend expects form-encoded data for login (OAuth2 standard),
  // not JSON -- so we build a URLSearchParams body instead.
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await apiClient.post(`${BASE}/login`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return response.data;
}