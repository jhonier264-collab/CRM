
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const userService = {
  list: () => api.get('/users').then(res => res.data),
  get: (id) => api.get(`/users/${id}`).then(res => res.data),
  create: (data) => api.post('/users', data).then(res => res.data),
  update: (id, data) => api.put(`/users/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/users/${id}`).then(res => res.data),
  restore: (id) => api.post(`/users/${id}/restore`).then(res => res.data),
};

export const companyService = {
  list: () => api.get('/companies').then(res => res.data),
  get: (id) => api.get(`/companies/${id}`).then(res => res.data),
  create: (data) => api.post('/companies', data).then(res => res.data),
  update: (id, data) => api.put(`/companies/${id}`, data).then(res => res.data),
};

export const geoService = {
  getCountries: () => api.get('/geography/countries').then(res => res.data),
};

export const catalogService = {
  getGenders: () => api.get('/catalog/genders').then(res => res.data),
  getLabels: () => api.get('/catalog/labels').then(res => res.data),
  getPositions: () => api.get('/catalog/positions').then(res => res.data),
  getDepartments: () => api.get('/catalog/departments').then(res => res.data),
  link: (data) => api.post('/professional/link', data).then(res => res.data),
  unlink: (user_id, company_id) => api.delete(`/professional/unlink?user_id=${user_id}&company_id=${company_id}`).then(res => res.data),
};

export const hygieneService = {
  getTrash: (table) => api.get(`/hygiene/trash/${table}`).then(res => res.data),
  purge: (table) => api.post(`/hygiene/purge/${table}`).then(res => res.data),
};

export default api;
