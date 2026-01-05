import React, { useState } from 'react';
import { 
  X, Save, Trash2, ChevronDown, ChevronUp, User, MapPin, Mail, 
  Phone, Building, Globe, CreditCard, Calendar, Hash, Type, 
  PlusCircle, BookOpen, Settings, Briefcase, Users, Tag, Search
} from 'lucide-react';
import { catalogService, userService, companyService } from '../services/api';

const DetailView = ({ item, type, onClose, onSave }) => {
  const [formData, setFormData] = useState({ ...item });
  const [catalogs, setCatalogs] = useState({
    genders: [],
    labels: [],
    positions: [],
    departments: [],
    companies: []
  });
  const [openSections, setOpenSections] = useState({
    general: true,
    contact: true,
    identification: true,
    phonetic: false,
    professional: true,
    corporate: true,
    geo: true,
    additional: false
  });
  const [linkingState, setLinkingState] = useState({
    active: false,
    search: '',
    selectedCompany: null,
    positionId: 1,
    deptId: 1
  });

  React.useEffect(() => {
    const loadCatalogs = async () => {
      try {
        const [genders, labels, positions, departments, companies] = await Promise.all([
          catalogService.getGenders(),
          catalogService.getLabels(),
          catalogService.getPositions(),
          catalogService.getDepartments(),
          companyService.list()
        ]);
        setCatalogs({ genders, labels, positions, departments, companies });
      } catch (err) {
        console.error("Error loading catalogs:", err);
      }
    };
    loadCatalogs();
  }, []);

  const toggleSection = (sec) => {
    setOpenSections(prev => ({ ...prev, [sec]: !prev[sec] }));
  };

  const handleFieldChange = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  // Dynamic Contact Handlers
  const addPhone = () => {
    const newPhone = { id: null, local_number: '', label_id: 1, _tempId: Date.now() };
    setFormData(prev => ({ ...prev, phones: [...(prev.phones || []), newPhone] }));
  };

  const updatePhone = (id, field, value) => {
    setFormData(prev => ({
      ...prev,
      phones: prev.phones.map(p => (p.id === id || p._tempId === id) ? { ...p, [field]: value } : p)
    }));
  };

  const removePhone = (id) => {
    setFormData(prev => ({
      ...prev,
      phones: prev.phones.filter(p => p.id !== id && p._tempId !== id)
    }));
  };

  const addEmail = () => {
    const newEmail = { id: null, email_address: '', label_id: 1, _tempId: Date.now() };
    setFormData(prev => ({ ...prev, emails: [...(prev.emails || []), newEmail] }));
  };

  const updateEmail = (id, field, value) => {
    setFormData(prev => ({
      ...prev,
      emails: prev.emails.map(e => (e.id === id || e._tempId === id) ? { ...e, [field]: value } : e)
    }));
  };

  const removeEmail = (id) => {
    setFormData(prev => ({
      ...prev,
      emails: prev.emails.filter(e => e.id !== id && e._tempId !== id)
    }));
  };
  const updateAddress = (id, field, value) => {
    setFormData(prev => ({
      ...prev,
      addresses: prev.addresses.map(a => a.id === id ? { ...a, [field]: value } : a)
    }));
  };

  // UNLINK FUNCTION
  const handleUnlink = async (companyId) => {
    if (!confirm("¿Seguro que desea eliminar el vínculo con esta empresa? La empresa no será borrada.")) return;
    try {
      if (id) {
          await catalogService.unlink(id, companyId);
          // Reload user data to reflect changes
          const updatedUser = await userService.get(id);
          setFormData(updatedUser);
      }
    } catch (err) { alert("Error al desvincular: " + err.message); }
  };

  const handleLinkSubmit = async () => {
    if (!linkingState.selectedCompany) return;
    try {
      await catalogService.link({
        user_id: formData.id,
        company_id: linkingState.selectedCompany.id,
        position_id: linkingState.positionId,
        department_id: linkingState.deptId
      });
      alert("Relación establecida con éxito");
      setLinkingState({ active: false, search: '', selectedCompany: null, positionId: 1, deptId: 1 });
      // We should probably reload the item to show the new link, but App.jsx handles refresh on save
    } catch (err) {
      alert("Error al vincular: " + err.message);
    }
  };

  if (!item) return null;

  const isUser = type === 'users' || (formData.first_name !== undefined && formData.legal_name === undefined);

  const renderField = (label, value, key, placeholder, isTextArea = false) => {
    const displayValue = (value !== null && value !== undefined && value !== '') ? value : '';
    
    return (
      <div className="form-group">
        <label>{label}</label>
        {isTextArea ? (
          <textarea 
            className="form-textarea" 
            value={displayValue} 
            onChange={(e) => handleFieldChange(key, e.target.value)}
            placeholder={placeholder || `Ingrese ${label.toLowerCase()}...`}
          />
        ) : (
          <input 
            type="text" 
            value={displayValue} 
            onChange={(e) => handleFieldChange(key, e.target.value)}
            placeholder={placeholder || `Ingrese ${label.toLowerCase()}...`}
          />
        )}
      </div>
    );
  };

  return (
    <div className="detail-view-container">
      <div className="detail-panel">
        <header className="detail-header">
           <div className="header-left-actions">
             <button className="icon-btn" onClick={onClose}><X size={20} title="Cerrar" /></button>
           </div>
           <div className="header-actions">
             <button className="primary-btn-sm" onClick={() => onSave(formData)}>
               <Save size={18} /> <span>Guardar cambios</span>
             </button>
             <button className="icon-btn danger-text" title="Eliminar definitivamente"><Trash2 size={18} /></button>
           </div>
        </header>

        <div className="detail-body">
          <div className="profile-hero">
            <div className={`avatar hero-avatar ${!isUser ? 'ico-corp' : ''}`}>
              {isUser ? (formData.first_name ? formData.first_name[0] : '?') : (formData.legal_name ? formData.legal_name[0] : 'C')}
            </div>
            <h2 className="profile-name">
              {isUser ? `${formData.first_name || ''} ${formData.last_name || ''}`.trim() || 'Sin nombre' : formData.legal_name || 'Sin Razón Social'}
            </h2>
            <p className="profile-subtitle">{isUser ? (formData.nickname ? `"${formData.nickname}"` : 'Contacto') : (formData.commercial_name || 'Empresa')}</p>
          </div>

          <div className="detail-sections">
            {/* 1. INFORMACIÓN GENERAL */}
            <section className="detail-section">
              <header className="section-header" onClick={() => toggleSection('general')}>
                <div className="section-title">
                  <User size={18} className="icon-muted" />
                  <span>{isUser ? 'Identidad y Nombres' : 'Información Corporativa'}</span>
                </div>
                {openSections.general ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </header>
              {openSections.general && (
                <div className="section-content grid-2">
                  {isUser ? (
                    <>
                      {renderField("Tratamiento / Prefijo", formData.prefix, "prefix", "Ej: Sr., Dr., Ing.")}
                      {renderField("Primer Nombre", formData.first_name, "first_name", "Nombre de pila")}
                      {renderField("Otros Nombres", formData.middle_name, "middle_name", "Nombres adicionales")}
                      {renderField("Apellidos", formData.last_name, "last_name", "Apellidos completos")}
                      {renderField("Sufijo", formData.suffix, "suffix", "Ej: Jr., III, Ph.D")}
                      {renderField("Seudónimo / Apodo", formData.nickname, "nickname", "Nombre informal")}
                      <div className="form-group span-2">
                        {renderField("Archivar como", formData.file_as, "file_as", "Ej: Apellido, Nombre (Para orden alfabético)")}
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="form-group span-2">
                         {renderField("Razón Social (Legal)", formData.legal_name, "legal_name", "Nombre legal de la entidad")}
                      </div>
                      <div className="form-group span-2">
                         {renderField("Nombre Comercial", formData.commercial_name, "commercial_name", "Nombre de marca o fantasía")}
                      </div>
                      <div className="form-group span-2">
                         {renderField("Descripción / Actividad", formData.description, "description", "Describe brevemente a qué se dedica la empresa...", true)}
                      </div>
                    </>
                  )}
                </div>
              )}
            </section>

            {/* 2. IDENTIFICACIÓN FISCAL */}
            <section className="detail-section">
              <header className="section-header" onClick={() => toggleSection('identification')}>
                <div className="section-title">
                  <CreditCard size={18} className="icon-muted" />
                  <span>Identificación Tributaria</span>
                </div>
                {openSections.identification ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </header>
              {openSections.identification && (
                <div className="section-content grid-2">
                   {renderField("RUT / NIT (Cédula/Tax ID)", formData.rut_nit, "rut_nit", "Número base sin puntos ni guiones")}
                   {renderField("Dígito de Verificación (DV)", formData.verification_digit, "verification_digit", "Solo el número final")}
                </div>
              )}
            </section>

            {/* 3. RELACIONES PROFESIONALES */}
            <section className="detail-section">
                <header className="section-header" onClick={() => toggleSection('professional')}>
                  <div className="section-title">
                    {isUser ? <Briefcase size={18} className="icon-muted" /> : <Users size={18} className="icon-muted" />}
                    <span>{isUser ? 'Vínculos Corporativos' : 'Nómina de Empleados'}</span>
                  </div>
                  {openSections.professional ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </header>
                {openSections.professional && (
                  <div className="section-content">
                     {isUser ? (
                      <div className="professional-list">
                        {formData.companies && formData.companies.length > 0 ? formData.companies.map(c => (
                          <div key={c.id} className="address-card">
                            <p style={{fontWeight:500}}><Building size={14} style={{marginRight:8}} /> {c.legal_name}</p>
                            <p className="address-meta">{c.position_name || 'Sin cargo'} • {c.department_name || 'Sin departamento'}</p>
                          </div>
                        )) : <p className="no-data-msg">Este contacto no está vinculado a ninguna empresa registrada.</p>}
                         {!linkingState.active ? (
                           <div style={{marginTop:12}}>
                             <button className="google-pill-button" onClick={() => setLinkingState(prev => ({ ...prev, active: true, search: '', activeCreate: false, selectedCompany: null }))}>
                               <PlusCircle size={16} /> Vincular empresa
                             </button>
                           </div>
                         ) : (
                           <div className="google-outlined-field-group" style={{marginTop:16, padding:16, border:'1px solid var(--border-color)', borderRadius:8}}>
                             {/* LINKING HEADER */}
                             <div style={{display:'flex', justifyContent:'space-between', marginBottom:12}}>
                               <h4 style={{margin:0}}>Vincular a Empresa</h4>
                               <button className="icon-btn-sm" onClick={() => setLinkingState(prev => ({ ...prev, active: false }))}><X size={16}/></button>
                             </div>

                             {/* SEARCH OR CREATE TOGGLE */}
                             {!linkingState.selectedCompany && !linkingState.activeCreate && (
                               <div style={{display:'flex', gap:12, marginBottom:12}}>
                                   <div style={{flex:1, position:'relative'}}>
                                      <Search size={16} style={{position:'absolute', left:12, top:12, color:'var(--text-secondary)'}} />
                                      <input 
                                        type="text" 
                                        placeholder="Buscar empresa..." 
                                        autoFocus
                                        value={linkingState.search}
                                        onChange={(e) => setLinkingState(prev => ({ ...prev, search: e.target.value }))}
                                        className="form-select"
                                        style={{paddingLeft:36}}
                                      />
                                      {/* AUTO-SHOW LIST OR FILTERED RESULTS */}
                                      <div className="search-results-mini">
                                        {catalogs.companies
                                            .filter(c => c.legal_name.toLowerCase().includes(linkingState.search.toLowerCase()))
                                            .slice(0, 8)
                                            .map(c => (
                                          <div key={c.id} className="search-item-mini" onClick={() => setLinkingState(prev => ({ ...prev, selectedCompany: c }))}>
                                            <Building size={14} style={{marginRight:8}}/> {c.legal_name}
                                          </div>
                                        ))}
                                         {catalogs.companies.length === 0 && <div className="search-item-mini">No hay empresas registradas.</div>}
                                      </div>
                                   </div>
                                   <button className="google-pill-button" style={{marginTop:0, whiteSpace:'nowrap'}} onClick={() => setLinkingState(prev => ({ ...prev, activeCreate: true, selectedCompany: { legal_name: linkingState.search } }))}>
                                     Nueva Empresa
                                   </button>
                               </div>
                             )}

                             {/* CREATE NEW COMPANY FORM */}
                             {linkingState.activeCreate && (
                              <div className="link-details-mini animate-fade-in">
                                <p className="selected-tag" style={{alignSelf:'flex-start'}}>Creando Nueva Empresa</p>
                                <div className="google-outlined-input-container">
                                    <label className="google-label-floating">Nombre Legal</label>
                                    <input 
                                      type="text" 
                                      className="google-input-field"
                                      value={linkingState.selectedCompany?.legal_name || ''}
                                      onChange={(e) => setLinkingState(prev => ({ ...prev, selectedCompany: { ...prev.selectedCompany, legal_name: e.target.value } }))}
                                    />
                                </div>
                                <div className="grid-2" style={{gap:12}}>
                                    <div className="google-outlined-input-container">
                                        <label className="google-label-floating">RUT / NIT</label>
                                        <input 
                                          type="text" 
                                          className="google-input-field"
                                          value={linkingState.selectedCompany?.rut_nit || ''}
                                          onChange={(e) => setLinkingState(prev => ({ ...prev, selectedCompany: { ...prev.selectedCompany, rut_nit: e.target.value } }))}
                                        />
                                    </div>
                                    <div className="google-outlined-input-container">
                                        <label className="google-label-floating">Dominio</label>
                                        <input 
                                          type="text" 
                                          className="google-input-field"
                                          value={linkingState.selectedCompany?.domain || ''}
                                          onChange={(e) => setLinkingState(prev => ({ ...prev, selectedCompany: { ...prev.selectedCompany, domain: e.target.value } }))}
                                        />
                                    </div>
                                </div>
                                
                                <div className="row-actions-mini">
                                  <button className="primary-btn-sm" onClick={async () => {
                                    try {
                                      const newComp = await companyService.create(linkingState.selectedCompany);
                                      setLinkingState(prev => ({ ...prev, selectedCompany: { id: newComp.id, legal_name: linkingState.selectedCompany.legal_name }, activeCreate: false, search: '' }));
                                    } catch (err) { alert("Error: " + err.message); }
                                  }}>Guardar y Continuar</button>
                                  <button className="text-btn-sm" onClick={() => setLinkingState(prev => ({ ...prev, activeCreate: false, selectedCompany: null }))}>Cancelar</button>
                                </div>
                              </div>
                            )}

                             {/* POSITION & DEPARTMENT SELECTOR */}
                             {linkingState.selectedCompany && !linkingState.activeCreate && (
                               <div className="link-details-mini animate-fade-in">
                                 <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}> 
                                     <p className="selected-tag">Seleccionada: <b>{linkingState.selectedCompany.legal_name}</b></p>
                                     <button className="text-btn-sm" onClick={() => setLinkingState(prev => ({ ...prev, selectedCompany: null }))}>Cambiar</button>
                                 </div>
                                 <select 
                                   className="form-select"
                                   value={linkingState.position_id}
                                   onChange={(e) => setLinkingState(prev => ({ ...prev, position_id: e.target.value }))}
                                 >
                                   {catalogs.positions.map(p => <option key={p.id} value={p.id}>{p.nombre_cargo || p.position_name}</option>)}
                                 </select>
                                 
                                 <select 
                                   className="form-select"
                                   value={linkingState.department_id}
                                   onChange={(e) => setLinkingState(prev => ({ ...prev, department_id: e.target.value }))}
                                 >
                                   {catalogs.departments.map(d => <option key={d.id} value={d.id}>{d.nombre_departamento || d.department_name}</option>)}
                                 </select>

                                 <div className="row-actions-mini">
                                   <button className="primary-btn-sm" onClick={handleLinkSubmit}>Vincular</button>
                                   <button className="text-btn-sm" onClick={() => setLinkingState(prev => ({ ...prev, active: false }))}>Cancelar</button>
                                 </div>
                               </div>
                             )}
                           </div>
                         )}
                      </div>
                    ) : (
                      <div className="professional-list">
                        {formData.employees && formData.employees.length > 0 ? formData.employees.map(e => (
                          <div key={e.id} className="address-card">
                            <p style={{fontWeight:500}}><User size={14} style={{marginRight:8}} /> {e.first_name} {e.last_name}</p>
                            <p className="address-meta">{e.position_name || 'Sin cargo'} • {e.department_name || 'Sin departamento'}</p>
                          </div>
                        )) : <p className="no-data-msg">No hay empleados registrados vinculados a esta empresa.</p>}
                        <button className="text-btn-sm" onClick={() => alert("Para añadir empleados, diríjase a la ficha del contacto individual y vincúlelo a esta empresa.")}>+ Cómo añadir empleados</button>
                      </div>
                    )}
                  </div>
                )}
            </section>

            {/* 4. CORPORATIVO */}
            {!isUser && (
              <section className="detail-section">
                <header className="section-header" onClick={() => toggleSection('corporate')}>
                  <div className="section-title">
                    <Globe size={18} className="icon-muted" />
                    <span>Indicadores de Negocio</span>
                  </div>
                  {openSections.corporate ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </header>
                {openSections.corporate && (
                  <div className="section-content grid-2">
                    {renderField("Sitio Web / Dominio", formData.domain, "domain", "ejemplo.com")}
                    <div className="form-group">
                      <label>Ingresos Anuales (USD)</label>
                      <input 
                        type="number" 
                        value={formData.revenue || 0} 
                        onChange={(e) => handleFieldChange('revenue', e.target.value)}
                        placeholder="Volumen de ventas" 
                      />
                    </div>
                  </div>
                )}
              </section>
            )}

             {/* 6. CONTACTO DINÁMICO */}
            <section className="detail-section">
              <header className="section-header" onClick={() => toggleSection('contact')}>
                <div className="section-title">
                  <Phone size={18} className="icon-muted" />
                  <span>Medios de Contacto</span>
                </div>
                {openSections.contact ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </header>
             {openSections.contact && (
                <div className="section-content">
                     <div className="contact-list">
                      {formData.phones && formData.phones.length > 0 ? formData.phones.map(p => (
                        <div key={p.id || p._tempId} className="google-outlined-field-group" style={{display:'flex', gap:12, alignItems:'center', marginBottom:12}}>
                           <div style={{display:'flex', alignItems:'center', border:'1px solid var(--border-color)', borderRadius:4, padding:4, height:56}}>
                              <span className="flag-icon">🇨🇴</span>
                              <ChevronDown size={12} className="icon-muted" />
                           </div>
                           <div className="google-outlined-input-container" style={{flex:2}}>
                              <label className="google-label-floating">Teléfono</label>
                              <input 
                                type="text" 
                                className="google-input-field"
                                value={p.local_number} 
                                onChange={(e) => updatePhone(p.id || p._tempId, 'local_number', e.target.value)}
                              />
                           </div>
                           <div className="google-outlined-input-container" style={{flex:1}}>
                              <label className="google-label-floating">Etiqueta</label>
                              <select 
                                className="google-input-field"
                                value={p.label_id || 1}
                                onChange={(e) => updatePhone(p.id || p._tempId, 'label_id', e.target.value)}
                                style={{cursor:'pointer'}}
                              >
                                {catalogs.labels.map(l => (
                                  <option key={l.id} value={l.id}>{l.label_name}</option>
                                ))}
                              </select>
                           </div>
                           <button className="icon-button-danger" onClick={() => removePhone(p.id || p._tempId)}><Trash2 size={18} /></button>
                        </div>
                      )) : <p className="no-data-msg">No hay teléfonos registrados.</p>}
                      <button className="google-pill-button" onClick={addPhone}><PlusCircle size={16} /> Añadir teléfono</button>
                    </div>  
                     <div className="contact-list" style={{marginTop:24}}>
                      <label className="sub-label">Correos Electrónicos</label>
                      {formData.emails && formData.emails.length > 0 ? formData.emails.map(e => (
                        <div key={e.id || e._tempId} className="google-outlined-field-group" style={{display:'flex', gap:12, alignItems:'center', marginBottom:12}}>
                          <div className="google-outlined-input-container" style={{flex:2}}>
                              <label className="google-label-floating">Correo Electrónico</label>
                              <input 
                                type="text" 
                                className="google-input-field"
                                value={e.email_address} 
                                onChange={(ev) => updateEmail(e.id || e._tempId, 'email_address', ev.target.value)}
                              />
                           </div>
                           <div className="google-outlined-input-container" style={{flex:1}}>
                              <label className="google-label-floating">Etiqueta</label>
                              <select 
                                className="google-input-field"
                                value={e.label_id || 1}
                                onChange={(ev) => updateEmail(e.id || e._tempId, 'label_id', ev.target.value)}
                                style={{cursor:'pointer'}}
                              >
                                {catalogs.labels.map(l => (
                                  <option key={l.id} value={l.id}>{l.label_name}</option>
                                ))}
                              </select>
                           </div>
                           <button className="icon-button-danger" onClick={() => removeEmail(e.id || e._tempId)}><Trash2 size={18} /></button>
                        </div>
                      )) : <p className="no-data-msg">No hay correos registrados.</p>}
                      <button className="google-pill-button" onClick={addEmail}><PlusCircle size={16} /> Añadir correo</button>
                    </div>
                </div>
              )}
            </section>

            {/* 7. DIRECCIONES */}
            <section className="detail-section">
              <header className="section-header" onClick={() => toggleSection('geo')}>
                <div className="section-title">
                  <MapPin size={18} className="icon-muted" />
                  <span>Ubicación Física</span>
                </div>
                {openSections.geo ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </header>
              {openSections.geo && (
                <div className="section-content">
                   {formData.addresses && formData.addresses.length > 0 ? formData.addresses.map(a => (
                     <div key={a.id} className="google-outlined-field-group" style={{padding:12, border:'1px solid var(--border-color)', borderRadius:8, marginBottom:12, display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                        <div style={{display:'flex', gap:12, alignItems:'center'}}>
                           <MapPin size={20} className="icon-muted" />
                           <div>
                              <p style={{fontWeight:500, margin:0}}>{a.address_line1 || 'Dirección sin nombre'}</p>
                              <p className="address-meta" style={{margin:0}}>{a.city_name || 'Ciudad'}, {a.country_name || 'País'}</p>
                           </div>
                        </div>
                        <div className="google-outlined-input-container" style={{width:150, height:40}}>
                            <label className="google-label-floating">Etiqueta</label>
                            <select 
                              className="google-input-field"
                              value={a.label_id || 1}
                              onChange={(e) => updateAddress(a.id, 'label_id', e.target.value)}
                              style={{cursor:'pointer', fontSize:13}}
                            >
                              {catalogs.labels.map(l => (
                                <option key={l.id} value={l.id}>{l.label_name}</option>
                              ))}
                            </select>
                        </div>
                     </div>
                   )) : <p className="no-data-msg">No se han registrado direcciones físicas aún.</p>}
                   <button className="text-btn-sm" onClick={() => alert("Módulo de geocodificación en desarrollo (Fase 17)")}>+ Iniciar geocodificación de dirección</button>
                </div>
              )}
            </section>

             {/* 8. ADICIONALES Y NOTAS */}
             <section className="detail-section">
                <header className="section-header" onClick={() => toggleSection('additional')}>
                  <div className="section-title">
                    <BookOpen size={18} className="icon-muted" />
                    <span>Anotaciones y Metadata</span>
                  </div>
                  {openSections.additional ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </header>
                {openSections.additional && (
                  <div className="section-content">
                    <div className="form-group grid-2">
                       {isUser && (
                         <>
                           <div>
                             <label>Fecha de Nacimiento</label>
                             <input 
                                type="date" 
                                value={formData.birthday ? formData.birthday.split('T')[0] : ''} 
                                onChange={(e) => handleFieldChange('birthday', e.target.value)}
                             />
                           </div>
                           <div>
                             <label>Género / Sexo Identificado</label>
                             <select 
                                className="form-select" 
                                value={formData.gender_id || ""}
                                onChange={(e) => handleFieldChange('gender_id', e.target.value)}
                             >
                               <option value="">No especificado</option>
                               {catalogs.genders.map(g => (
                                 <option key={g.id} value={g.id}>{g.gender_name}</option>
                               ))}
                             </select>
                           </div>
                         </>
                       )}
                    </div>
                    {renderField("Notas Privadas", formData.notes, "notes", "Añade detalles internos, historial de contacto, etc.", true)}
                    
                    <div className="custom-fields-area">
                       <button className="outline-btn-sm" onClick={() => alert("Próximamente: Columnas dinámicas")}>
                         <Settings size={14} /> <span>Gestionar campos personalizados (Fase 17)</span>
                       </button>
                    </div>
                  </div>
                )}
              </section>

          </div>
        </div>
      </div>
    </div>
  );
};

export default DetailView;
