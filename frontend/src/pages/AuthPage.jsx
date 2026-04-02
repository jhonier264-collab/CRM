
import React, { useState } from 'react';
import { ShieldCheck, Loader2, Building2, User } from 'lucide-react';
import { authService } from '../services/api';
import './AuthPage.css';

const AuthPage = ({ onLogin }) => {
  const [view, setView] = useState('login'); // login, register, recovery
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form States
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    passwordConfirm: '',
    token: '',
    username: '', // Para empresas se usa como identificador único también
    first_name: '',
    last_name: '',
    account_type: 'INDIVIDUAL', // INDIVIDUAL, COMPANY
    rut: '',
    company_name: '' 
  });

  const [rutValid, setRutValid] = useState(true);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const validateRut = async () => {
    if (formData.account_type === 'COMPANY' && formData.rut) {
      try {
        const res = await authService.validateRut(formData.rut);
        setRutValid(res.isValid);
        if (!res.isValid) setError('El RUT ingresado no es válido (Módulo 11).');
      } catch (err) {
        console.error(err);
        setRutValid(false);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      let response;
      if (view === 'login') {
        response = await authService.login({
          identifier: formData.email, // Puede ser username o email
          password: formData.password
        });
      } else if (view === 'register') {
        if (formData.account_type === 'COMPANY' && !rutValid) {
          throw new Error('Debe ingresar un RUT válido.');
        }

        // Construir payload
        const payload = {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password_confirm: formData.password, // Frontend simplificado
          first_name: formData.first_name,
          last_name: formData.last_name || formData.company_name,
          account_type: formData.account_type,
          rut: formData.rut
        };
        
        response = await authService.register(payload);
      } else if (view === 'recovery') {
        await authService.requestRecovery(formData.email);
        alert('Se ha enviado un código de recuperación a su correo.');
        setView('reset');
        setIsLoading(false);
        return;
      } else if (view === 'reset') {
        if (formData.password !== formData.passwordConfirm) {
          throw new Error('Las contraseñas no coinciden.');
        }
        await authService.resetPassword({
          identifier: formData.email,
          token: formData.token,
          new_password: formData.password
        });
        alert('Contraseña actualizada correctamente. Inicie sesión.');
        setView('login');
        setIsLoading(false);
        return;
      }

      if (response && response.token) {
        localStorage.setItem('crm_token', response.token);
        localStorage.setItem('crm_user', JSON.stringify(response));
        onLogin(response);
      } else if (view === 'register') {
          // Auto login after register or show success
          alert('Registro exitoso. Por favor inicie sesión.');
          setView('login');
      }

    } catch (err) {
      console.error(err);
      setError(err.response?.data?.message || err.response?.data?.error || err.message || 'Ocurrió un error inesperado.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && view === 'register') {
    return (
      <div className="auth-container">
        <div className="auth-card loading-overlay">
          <Loader2 size={48} className="spinner auth-logo" />
          <h3>Configurando su entorno</h3>
          <p className="loading-text">Esto puede tardar unos segundos mientras aprovisionamos su base de datos segura y aislada...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <ShieldCheck className="auth-logo" />
          <h1 className="auth-title">CRM Industrial SaaS</h1>
          <p className="auth-subtitle">Gestión inteligente para su negocio</p>
        </div>

        {error && (
          <div className="error-message" style={{marginBottom: '1rem', textAlign: 'center', background: '#FEE2E2', padding: '0.5rem', borderRadius: '4px'}}>
            {error}
          </div>
        )}

        {view === 'register' && (
          <div className="account-type-selector">
            <div 
              className={`type-option ${formData.account_type === 'INDIVIDUAL' ? 'active' : ''}`}
              onClick={() => setFormData(prev => ({ ...prev, account_type: 'INDIVIDUAL' }))}
            >
              <User size={16} style={{marginBottom: '-3px', marginRight: '4px'}}/>
              Persona Natural
            </div>
            <div 
              className={`type-option ${formData.account_type === 'COMPANY' ? 'active' : ''}`}
              onClick={() => setFormData(prev => ({ ...prev, account_type: 'COMPANY' }))}
            >
              <Building2 size={16} style={{marginBottom: '-3px', marginRight: '4px'}}/>
              Empresa
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {view === 'register' && (
            <>
              <div className="form-group">
                <label className="form-label">Usuario (ID de cuenta)</label>
                <input 
                  type="text" 
                  name="username"
                  className="form-input"
                  placeholder="Ej: empresa_sa"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                />
              </div>

              {formData.account_type === 'COMPANY' ? (
                <>
                  <div className="form-group">
                    <label className="form-label">Razón Social</label>
                    <input 
                      type="text" 
                      name="first_name" // Usamos first_name como field genérico en backend a veces, o ajustamos
                      className="form-input"
                      placeholder="Nombre de la empresa"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">RUT / NIT</label>
                    <input 
                      type="text" 
                      name="rut"
                      className={`form-input ${!rutValid ? 'error' : ''}`}
                      placeholder="900.123.456-1"
                      value={formData.rut}
                      onChange={handleInputChange}
                      onBlur={validateRut}
                      required
                    />
                    {!rutValid && <span className="error-message">RUT inválido. Verifique el dígito de verificación.</span>}
                  </div>
                </>
              ) : (
                <div style={{display: 'flex', gap: '1rem'}}>
                    <div className="form-group" style={{flex: 1}}>
                        <label className="form-label">Nombre</label>
                        <input 
                        type="text" 
                        name="first_name"
                        className="form-input"
                        placeholder="Juan"
                        value={formData.first_name}
                        onChange={handleInputChange}
                        required
                        />
                    </div>
                    <div className="form-group" style={{flex: 1}}>
                        <label className="form-label">Apellido</label>
                        <input 
                        type="text" 
                        name="last_name"
                        className="form-input"
                        placeholder="Perez"
                        value={formData.last_name}
                        onChange={handleInputChange}
                        required
                        />
                    </div>
                </div>
              )}
            </>
          )}

          <div className="form-group">
            <label className="form-label">
              {view === 'register' ? 'Correo electrónico' : 'Usuario o Correo electrónico'}
            </label>
            <input 
              type={view === 'register' ? 'email' : 'text'} 
              name="email"
              className="form-input"
              placeholder={view === 'register' ? 'nombre@ejemplo.com' : 'Usuario o email'}
              value={formData.email}
              onChange={handleInputChange}
              required
              disabled={view === 'reset'}
            />
          </div>

          {view !== 'recovery' && (
            <div className="form-group">
              <label className="form-label">{view === 'reset' ? 'Nueva Contraseña' : 'Contraseña'}</label>
              <input 
                type="password" 
                name="password"
                className="form-input"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleInputChange}
                required
              />
            </div>
          )}
          
          {view === 'reset' && (
            <>
              <div className="form-group">
                <label className="form-label">Confirmar Contraseña</label>
                <input 
                  type="password" 
                  name="passwordConfirm"
                  className="form-input"
                  placeholder="••••••••"
                  value={formData.passwordConfirm}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Código (Token)</label>
                <input 
                  type="text" 
                  name="token"
                  className="form-input"
                  placeholder="Ej: ABC123"
                  value={formData.token}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </>
          )}

          <button type="submit" className="btn-primary" disabled={isLoading || (view === 'register' && formData.account_type === 'COMPANY' && !rutValid)}>
            {isLoading ? <Loader2 className="spinner" /> : (
              view === 'login' ? 'Iniciar Sesión' : 
              view === 'register' ? 'Registrar Cuenta' : 
              view === 'recovery' ? 'Enviar Código' : 'Actualizar Contraseña'
            )}
          </button>
        </form>

        <div className="auth-footer">
          {view === 'login' && (
            <>
              <p>¿No tiene una cuenta? <button className="link-btn" onClick={() => setView('register')}>Regístrese</button></p>
              <p style={{marginTop: '0.5rem'}}><button className="link-btn" onClick={() => setView('recovery')}>Olvidé mi contraseña</button></p>
            </>
          )}
          
          {view === 'register' && (
             <p>¿Ya tiene cuenta? <button className="link-btn" onClick={() => setView('login')}>Inicie Sesión</button></p>
          )}

           {view === 'recovery' && (
             <p><button className="link-btn" type="button" onClick={() => setView('login')}>Volver al inicio</button></p>
          )}
           {view === 'reset' && (
             <p><button className="link-btn" type="button" onClick={() => setView('login')}>Cancelar y volver</button></p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
