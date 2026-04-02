/**
 * runtime_config.js
 * 
 * Actúa como puente entre las variables de entorno de Vite (.env raíz)
 * y la lógica de negocio del frontend.
 */

const runtimeConfig = {
  BACKEND_PORT: import.meta.env.VITE_BACKEND_PORT || '8000',
  FRONTEND_PORT: import.meta.env.VITE_FRONTEND_PORT || '3000',
  BASE_URL: import.meta.env.VITE_BASE_URL || 'http://localhost',
  
  /**
   * Construye la URL base del API combinando los valores del entorno.
   * @returns {string} URL completa del Backend.
   */
  getApiBaseUrl() {
    return `${this.BASE_URL}:${this.BACKEND_PORT}`;
  }
};

export default runtimeConfig;
