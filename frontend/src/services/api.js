
import axios from 'axios';
import API_CONFIG from '../config/api_config';

const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir token si existe
api.interceptors.request.use(config => {
  const token = localStorage.getItem('crm_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para desempaquetar ApiResponse
api.interceptors.response.use(
  response => {
    if (response.data && response.data.status === 'success' && response.data.data !== undefined) {
      console.log(`[API SUCCESS] ${response.config.url}`, response.data.data);
      return { ...response, data: response.data.data };
    }
    console.log(`[API OTHER] ${response.config.url}`, response.data);
    return response;
  },
  error => {
    const message = error.response?.data?.message || error.message;
    console.error(`[API ERROR] ${error.config?.url}`, error.response?.data || error.message);
    return Promise.reject(new Error(message));
  }
);

export const authService = {
  login: (credentials) => api.post('/auth/login', credentials).then(res => res.data),
  register: (data) => api.post('/auth/register', data).then(res => res.data),
  validateRut: (rut) => api.post('/auth/validate-rut', { rut }).then(res => res.data),
  requestRecovery: (email) => api.post('/auth/recovery/request', { email }).then(res => res.data),
  resetPassword: (data) => api.post('/auth/recovery/reset', data).then(res => res.data),
};

export const userService = {
  list: () => api.get('/users').then(res => res.data),
  get: (id) => api.get(`/users/${id}`).then(res => res.data),
  create: (data) => api.post('/users', data).then(res => res.data),
  update: (id, data) => api.put(`/users/${id}`, data).then(res => res.data),
  delete: (id) => api.delete(`/users/${id}`).then(res => res.data),
  restore: (id) => api.post(`/users/${id}/restore`).then(res => res.data),
  unlinkCompany: (userId, companyId) => api.delete(`/users/${userId}/companies/${companyId}`).then(res => res.data),
  relateUser: (userId, data) => api.post(`/users/${userId}/relate`, data).then(res => res.data),
  unlinkUser: (userId, targetId) => api.delete(`/users/${userId}/relate/${targetId}`).then(res => res.data),
};

export const companyService = {
  list: () => api.get('/companies').then(res => res.data),
  get: (id) => api.get(`/companies/${id}`).then(res => res.data),
  create: (data) => api.post('/companies', data).then(res => res.data),
  update: (id, data) => api.put(`/companies/${id}`, data).then(res => res.data),
  relate: (id, data) => api.post(`/companies/${id}/relate`, data).then(res => res.data),
  updateRel: (id, targetId, data) => api.put(`/companies/${id}/relate/${targetId}`, data).then(res => res.data),
  unlinkRel: (id, targetId) => api.delete(`/companies/${id}/relate/${targetId}`).then(res => res.data),
  delete: (id) => api.delete(`/companies/${id}`).then(res => res.data),
  parseRut: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/companies/parse-rut', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data);
  },
};

export const geoService = {
  getCountries: () => api.get('/geography/countries').then(res => res.data),
  getStates: (countryId) => api.get(`/geography/states/${countryId}`).then(res => res.data),
  getCities: (stateId) => api.get(`/geography/cities/${stateId}`).then(res => res.data),
};

export const catalogService = {
  getGenders: () => api.get('/catalog/genders').then(res => res.data),
  getLabels: () => api.get('/catalog/labels').then(res => res.data),
  getPositions: () => api.get('/catalog/positions').then(res => res.data),
  getDepartments: () => api.get('/catalog/departments').then(res => res.data),
  getRoles: () => api.get('/catalog/roles').then(res => res.data),
  getTags: () => api.get('/catalog/tags').then(res => res.data),
  getStatuses: () => api.get('/catalog/statuses').then(res => res.data),
  getAgents: () => api.get('/catalog/agents').then(res => res.data),
  getEconomicActivities: (q) => api.get('/catalog/economic-activities', { params: { q } }).then(res => res.data),
  getUserRelationTypes: () => api.get('/catalog/user-relation-types').then(res => res.data),
  getCompanyRelationTypes: () => api.get('/catalog/company-relation-types').then(res => res.data),
  createUserRelType: (data) => api.post('/catalog/user-relation-types', data).then(res => res.data),
  createCompanyRelType: (data) => api.post('/catalog/company-relation-types', data).then(res => res.data),
  deleteCompanyRelType: (id) => api.delete(`/catalog/company-relation-types/${id}`).then(res => res.data),
  createTag: (data) => api.post('/catalog/tags', data).then(res => res.data),
  link: (data) => api.post('/professional/link', data).then(res => res.data),
  unlink: (user_id, company_id) => api.delete(`/users/${user_id}/companies/${company_id}`).then(res => res.data),
};

export const hygieneService = {
  getTrash: (table) => api.get(`/hygiene/trash/${table}`).then(res => res.data),
  purge: (table) => api.post(`/hygiene/purge/${table}`).then(res => res.data),
};

export default api;
