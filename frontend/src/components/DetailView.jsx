import React, { useState } from 'react';
import { 
  X, Save, Trash2, ChevronDown, ChevronUp, User, MapPin, Mail, 
  Phone, Building, Globe, CreditCard, Calendar, Hash, Type, 
  PlusCircle, BookOpen, Settings, Briefcase, Users, Tag, Search,
  RefreshCw, CheckCircle2
} from 'lucide-react';
import { catalogService, userService, companyService, geoService } from '../services/api';

const DetailView = ({ item, type, onClose, onSave, onDelete, onSelectRelated, catalogs, setCatalogs }) => {
  const [formData, setFormData] = useState({ ...item });
  const [geoCache, setGeoCache] = useState({ states: {}, cities: {} });
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
  const [userLinkingState, setUserLinkingState] = useState({
    active: false,
    search: '',
    selectedUser: null,
    relationTypeId: 1,
    customLabel: '',
    isSymmetric: false,
    newTypeName: '',
    newTypeInverse: ''
  });
  const [companyLinkingState, setCompanyLinkingState] = useState({
    active: false,
    search: '',
    selectedCompany: null,
    relationTypeId: "1", // Initial assumed ID
    notes: '',
    isSymmetric: false, // New state
    newTypeName: '',
    newTypeInverse: ''
  });
  const [errors, setErrors] = useState({});
  const [savingError, setSavingError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [showLabelMenu, setShowLabelMenu] = useState(false);
  const [tagSearch, setTagSearch] = useState('');
  const [showManageTypesModal, setShowManageTypesModal] = useState(false);
  const [isRelModalOpen, setIsRelModalOpen] = useState(false); // Controls the main Link Modal
  const [economicActivities, setEconomicActivities] = useState([]);
  const [isSearchingActivities, setIsSearchingActivities] = useState(false);
  const [isParsingRut, setIsParsingRut] = useState(false);
  const [economicSearch, setEconomicSearch] = useState('');

  // Computed Options for Inverse Selection
  const flattenedOptions = React.useMemo(() => {
    if (!(catalogs.company_relation_types || [])) return [];
    return (catalogs.company_relation_types || []).map(ct => {
        // Find the inverse type to display "Emparejado con X"
        // inverse_type_id points to the ID of the paired type
        const inv = (catalogs.company_relation_types || []).find(t => t.id === ct.inverse_type_id);
        const invName = inv ? inv.name : '???';

        return {
            id: ct.id,
            name: ct.name,
            sub: inv ? `Emparejado con ${invName}` : 'Sin inversa definida',
            value: ct.id,
            is_inverse: false // Legacy flag kept for UI logic if needed
        };
    });
  }, [(catalogs.company_relation_types || [])]);

  const handleToggleTag = (tag) => {
    const exists = formData.tags.some(t => t.id === tag.id);
    if (exists) {
      setFormData(prev => ({ ...prev, tags: prev.tags.filter(t => t.id !== tag.id) }));
    } else {
      setFormData(prev => ({ ...prev, tags: [...(prev.tags || []), tag] }));
    }
  };

  const handleCreateTagImpl = async (name) => {
    try {
      const res = await catalogService.createTag({ name });
      const newTag = { id: res.id, name: res.name, color: res.color };
      
      setCatalogs(prev => ({ ...prev, tags: [...prev.tags, newTag] }));
      
      // Update UI state using existing handler (updates visible checks)
      handleToggleTag(newTag);
      
      setTagSearch('');
    } catch (err) {
      console.error("Error creating tag:", err);
      // alert("Error creando etiqueta: " + (err.response?.data?.message || err.message));
    }
  };

  const handleSearchActivities = async (q) => {
    setEconomicSearch(q);
    if (q.length < 2) return;
    setIsSearchingActivities(true);
    try {
      const data = await catalogService.getEconomicActivities(q);
      setEconomicActivities(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearchingActivities(false);
    }
  };

  const handleRutUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setIsParsingRut(true);
    setSavingError(null);
    try {
      const result = await companyService.parseRut(file);
      
      const newFormData = { ...formData };
      
      if (result.rut_nit) newFormData.rut_nit = result.rut_nit;
      if (result.verification_digit) newFormData.verification_digit = parseInt(result.verification_digit);
      if (result.legal_name) newFormData.legal_name = result.legal_name.toUpperCase();
      
      newFormData.commercial_name = result.commercial_name ? result.commercial_name.toUpperCase() : '';
      
      // Helper for normalization
      const norm = (str) => {
        if (!str) return '';
        return str.normalize("NFD")
                  .replace(/[\u0300-\u036f]/g, "")
                  .replace(/[^a-zA-Z0-9\s]/g, "")
                  .toUpperCase()
                  .trim();
      };

      // Discover "Trabajo" Label ID
      let trabajoLabelId = 2; // Default fallback
      if ((catalogs.labels || []) && (catalogs.labels || []).length > 0) {
          const found = (catalogs.labels || []).find(l => norm(l.label_name) === "TRABAJO" || norm(l.label_name) === "BUSINESS");
          if (found) trabajoLabelId = found.id;
          else {
              // If not found by name, and 1 is Personal, maybe 2 is Trabajo
              const is1Personal = (catalogs.labels || []).some(l => l.id === 1 && norm(l.label_name) === "PERSONAL");
              if (is1Personal) trabajoLabelId = 2;
          }
      }

      // Email
      if (result.email) {
        if (!newFormData.emails) newFormData.emails = [];
        const cleanEmail = result.email.toLowerCase();
        const emailId = Date.now() + Math.random();
        if (newFormData.emails.length === 0) {
            newFormData.emails.push({ email_address: cleanEmail, label_id: trabajoLabelId, _tempId: emailId });
        } else {
            newFormData.emails[0].email_address = cleanEmail;
            newFormData.emails[0].label_id = trabajoLabelId;
            if (!newFormData.emails[0].id) newFormData.emails[0]._tempId = emailId;
        }
      }

      // Address & Geography Automation
      if (result.address && result.address.address_line1) {
        if (!newFormData.addresses) newFormData.addresses = [];
        const addrId = Date.now() + Math.random();
        
        let geoData = {
            country_id: 1, // Colombia
            state_id: null,
            city_id: null
        };

        // Automate State/City selection
        try {
            const states = await geoService.getStates(1);
            setGeoCache(prev => ({ ...prev, states: { ...prev.states, 1: states } }));
            
            if (result.department_name) {
                const targetDept = norm(result.department_name);
                const stateMatch = states.find(s => norm(s.state_name).includes(targetDept) || targetDept.includes(norm(s.state_name)));
                
                if (stateMatch) {
                    geoData.state_id = stateMatch.id;
                    const cities = await geoService.getCities(stateMatch.id);
                    setGeoCache(prev => ({ ...prev, cities: { ...prev.cities, [stateMatch.id]: cities } }));
                    
                    if (result.city_name) {
                        const targetCity = norm(result.city_name);
                        const cityMatch = cities.find(c => norm(c.city_name).includes(targetCity) || targetCity.includes(norm(c.city_name)));
                        if (cityMatch) geoData.city_id = cityMatch.id;
                    }
                }
            }
        } catch (e) {
            console.error("Error auto-filling geography:", e);
        }

        if (newFormData.addresses.length === 0) {
            newFormData.addresses.push({ 
                address_line1: result.address.address_line1, 
                label_id: trabajoLabelId,
                ...geoData,
                _tempId: addrId
            });
        } else {
            newFormData.addresses[0].address_line1 = result.address.address_line1;
            newFormData.addresses[0].label_id = trabajoLabelId;
            newFormData.addresses[0].country_id = geoData.country_id;
            newFormData.addresses[0].state_id = geoData.state_id;
            newFormData.addresses[0].city_id = geoData.city_id;
            if (!newFormData.addresses[0].id) newFormData.addresses[0]._tempId = addrId;
        }
      }

      // Phones (Multiple)
      if (result.phones && result.phones.length > 0) {
        if (!newFormData.phones) newFormData.phones = [];
        const filteredPhones = newFormData.phones.filter(p => p.local_number || p.id);
        
        result.phones.forEach((p, idx) => {
            const phoneId = Date.now() + Math.random() + idx;
            if (filteredPhones[idx]) {
                filteredPhones[idx].local_number = p.local_number;
                filteredPhones[idx].label_id = trabajoLabelId;
                if (!filteredPhones[idx].id) filteredPhones[idx]._tempId = phoneId;
            } else {
                filteredPhones.push({ 
                    local_number: p.local_number, 
                    label_id: trabajoLabelId, 
                    country_id: 1,
                    _tempId: phoneId
                });
            }
        });
        newFormData.phones = filteredPhones;
      }

      // Economic Activity
      if (result.economic_activity_code) {
          const codeStr = result.economic_activity_code.toString();
          newFormData.economic_activity_code = parseInt(codeStr);
          try {
            const actData = await catalogService.getEconomicActivities(codeStr);
            if (actData && actData.length > 0) {
                const exact = actData.find(a => a.id.toString() === codeStr) || actData[0];
                setEconomicActivities([exact]);
                setEconomicSearch(`${exact.id} - ${exact.description}`);
            }
          } catch (e) {
            console.error("Error fetching economic activity:", e);
          }
      }
      
      setFormData(newFormData);
      setSavingError(null);
    } catch (err) {
      console.error("Parsing RUT Error:", err);
      setSavingError("No se pudo leer el RUT: " + err.message);
    } finally {
      setIsParsingRut(false);
      event.target.value = null;
    }
  };

  // Use effect to sync economic activity search label if code is loaded/set
  React.useEffect(() => {
    if (formData.economic_activity_code) {
      const loadActivity = async () => {
        try {
          const act = await catalogService.getEconomicActivities(formData.economic_activity_code);
          if (act && act.length > 0) {
              const matched = act.find(a => a.id === formData.economic_activity_code);
              if (matched) setEconomicSearch(`${matched.id} - ${matched.description}`);
          }
        } catch (e) {
          console.error("Error loading activity label:", e);
        }
      };
      loadActivity();
    }
  }, [formData.economic_activity_code]);

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

  const handleAddTag = (tag) => {
    const existing = formData.tags || [];
    if (existing.find(t => t.id === tag.id)) return;
    setFormData(prev => ({ ...prev, tags: [...existing, tag] }));
    setTagInput('');
  };

  const handleRemoveTag = (tagId) => {
    setFormData(prev => ({ ...prev, tags: (formData.tags || []).filter(t => t.id !== tagId) }));
  };

  const handleCreateTag = async (name) => {
    // Aquí podríamos llamar a un servicio para crear la etiqueta si no existe
    // Por ahora simulamos la creación en el frontend o notificamos
    const newTag = { id: Date.now(), name, color: '#e0e0e0' };
    handleAddTag(newTag);
  };
  const updateAddress = (id, field, value) => {
    setFormData(prev => ({
      ...prev,
      addresses: prev.addresses.map(a => (a.id === id || a._tempId === id) ? { ...a, [field]: value } : a)
    }));
  };

  const handleCountryChange = async (addressId, countryId) => {
    updateAddress(addressId, 'country_id', countryId);
    updateAddress(addressId, 'state_id', null);
    updateAddress(addressId, 'city_id', null);
    
    if (countryId && !geoCache.states[countryId]) {
      try {
        const states = await geoService.getStates(countryId);
        setGeoCache(prev => ({ ...prev, states: { ...prev.states, [countryId]: states } }));
      } catch (e) { console.error(e); }
    }
  };

  const handleStateChange = async (addressId, stateId) => {
    updateAddress(addressId, 'state_id', stateId);
    updateAddress(addressId, 'city_id', null);
    
    if (stateId && !geoCache.cities[stateId]) {
      try {
        const cities = await geoService.getCities(stateId);
        setGeoCache(prev => ({ ...prev, cities: { ...prev.cities, [stateId]: cities } }));
      } catch (e) { console.error(e); }
    }
  };

  const addAddress = () => {
    const newAddr = { id: null, address_line1: '', label_id: 1, country_id: 1, _tempId: Date.now() };
    setFormData(prev => ({ ...prev, addresses: [...(prev.addresses || []), newAddr] }));
    if (newAddr.country_id) handleCountryChange(newAddr._tempId, newAddr.country_id);
  };

  const removeAddress = (id) => {
    setFormData(prev => ({
      ...prev,
      addresses: prev.addresses.filter(a => a.id !== id && a._tempId !== id)
    }));
  };

  // UNLINK FUNCTION
  const handleUnlink = async (companyId) => {
    if (!confirm("¿Seguro que desea eliminar el vínculo con esta empresa? La empresa no será borrada.")) return;
    try {
      if (formData.id) {
          await catalogService.unlink(formData.id, companyId);
          // Reload user data to reflect changes
          const updatedUser = await userService.get(formData.id);
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

  const handleUnlinkCompany = async (companyId) => {
    if (!window.confirm("¿Seguro que desea desvincular a este contacto de la empresa?")) return;
    try {
      await userService.unlinkCompany(formData.id, companyId);
      // Reload item
      const updated = await userService.get(formData.id);
      setFormData(updated);
      alert("Vínculo eliminado");
    } catch (err) {
      alert("Error al desvincular: " + err.message);
    }
  };

  const handleUserLinkSubmit = async () => {
    if (!userLinkingState.selectedUser) return;
    try {
      let relTypeId = parseInt(userLinkingState.relationTypeId);
      
      // Handle "Create New" (-1)
      if (relTypeId === -1) {
          const newName = userLinkingState.newTypeName;
          const isSym = userLinkingState.isSymmetric;
          const newInverse = isSym ? null : userLinkingState.newTypeInverse;
          
          if (!newName) { alert("Nombre requerido"); return; }
          if (!isSym && !newInverse) { alert("Nombre Inverso requerido para asimétricas"); return; }

          const res = await catalogService.createUserRelType({ 
              name: newName, 
              inverse_name: newInverse,
              is_symmetric: isSym
          });
          relTypeId = res.id;
          
          // Refresh catalog
          const newTypes = await catalogService.getUserRelationTypes();
          setCatalogs(prev => ({ ...prev, user_relation_types: newTypes }));
      }
      
      await userService.relateUser(formData.id, {
        target_user_id: userLinkingState.selectedUser.id,
        relation_type_id: relTypeId,
        custom_label: userLinkingState.customLabel
      });
      alert("Vínculo entre usuarios establecido");
      // Reset state thoroughly
      setUserLinkingState(prev => ({ 
          ...prev, 
          active: false, 
          search: '', 
          selectedUser: null, 
          relationTypeId: 1, 
          customLabel: '',
          newTypeName: '',
          newTypeInverse: '',
          isSymmetric: false
      }));

      const updated = await userService.get(formData.id);
      setFormData(updated);
    } catch (err) {
      alert("Error al vincular usuarios: " + err.message);
    }
  };

  const handleUnlinkUser = async (targetId) => {
    if (!window.confirm("¿Desea eliminar este vínculo personal/profesional?")) return;
    try {
      await userService.unlinkUser(formData.id, targetId);
      const updated = await userService.get(formData.id);
      setFormData(updated);
      alert("Vínculo eliminado");
    } catch (err) {
      alert("Error al desvincular: " + err.message);
    }
  };

  const handleOpenLinkModal = (existingLink = null) => {
      // If editing, existingLink is the relationship object
      if (existingLink) {
          setCompanyLinkingState({
              active: true,
              isEditing: true, // New Flag
              targetId: existingLink.target_company_id, // Store target ID
              search: existingLink.legal_name,
              selectedCompany: { id: existingLink.target_company_id, legal_name: existingLink.legal_name },
              // In new logic, existingLink.relation_type_id IS the specific bidirectional type
              relationTypeId: existingLink.relation_type_id || 1, 
              notes: existingLink.notes || ''
          });
      } else {
          // New Link
          setCompanyLinkingState(prev => ({ 
              ...prev, 
              active: true, 
              isEditing: false, 
              targetId: null,
              search: '', 
              selectedCompany: null, 
              notes: '' 
          }));
      }
      setIsRelModalOpen(true);
  };

  const handleCompanyLinkSubmit = async () => {
    if (!companyLinkingState.selectedCompany) return;
    try {
      const rawVal = companyLinkingState.relationTypeId.toString();
      let finalRelId = null;

      if (rawVal === "-1") {
          const newName = companyLinkingState.newTypeName;
          const isSym = companyLinkingState.isSymmetric;
          const newInverse = isSym ? null : companyLinkingState.newTypeInverse;
          
          if (!newName) { alert("Nombre requerido"); return; }
          if (!isSym && !newInverse) { alert("Nombre Inverso requerido para relaciones asimétricas"); return; }

          const res = await catalogService.createCompanyRelType({ 
              name: newName, 
              inverse_name: newInverse,
              is_symmetric: isSym
          });
          finalRelId = res.id;
          const newTypes = await catalogService.getCompanyRelationTypes();
          setCatalogs(prev => ({ ...prev, company_relation_types: newTypes }));
      } else {
          finalRelId = parseInt(rawVal);
      }

      const payload = {
        target_company_id: parseInt(companyLinkingState.selectedCompany.id),
        relation_type_id: finalRelId,
        notes: companyLinkingState.notes || '',
        is_inverse: false // Always false now, as we select specific type
      };
      
      if (companyLinkingState.isEditing) {
          await companyService.updateRel(formData.id, companyLinkingState.targetId, payload);
          alert("Relación actualizada");
      } else {
          await companyService.relate(formData.id, payload);
          alert("Relación establecida");
      }
      
      // Close and Reset
      setIsRelModalOpen(false); // Close Modal
      setCompanyLinkingState(prev => ({ ...prev, active: false }));

      // Reload
      const updated = await companyService.get(formData.id);
      setFormData(updated);
    } catch (err) {
      console.error("Link error:", err);
      alert("Error: " + err.message);
    }
  };

  const handleUnlinkCompanyRel = async (targetId) => {
    if (!window.confirm("¿Eliminar esta relación corporativa?")) return;
    try {
      console.log("Unlinking rel:", targetId);
      await companyService.unlinkRel(formData.id, parseInt(targetId));
      const updated = await companyService.get(formData.id);
      setFormData(updated);
      alert("Vínculo eliminado via B2B");
    } catch (err) {
      console.error("Unlink error:", err);
      alert("Error al desvincular B2B: " + err.message);
    }
  };

  if (!item) return null;

  const isUser = type === 'users' || (formData.first_name !== undefined && formData.legal_name === undefined);

  const renderField = (label, value, key, placeholder, isTextArea = false, required = false) => {
    const displayValue = (value !== null && value !== undefined && value !== '') ? value : '';
    const hasError = errors[key];
    
    return (
      <div className={`form-group ${hasError ? 'error' : ''}`}>
        <label>
          {label} 
          {required && <span className="required-star">*</span>}
          {hasError && <span className="error-message-inline"> - Requerido</span>}
        </label>
        {isTextArea ? (
          <textarea 
            className="form-textarea" 
            value={displayValue} 
            onChange={(e) => {
              handleFieldChange(key, e.target.value);
              if (errors[key]) setErrors(prev => {
                  const n = {...prev};
                  delete n[key];
                  return n;
              });
            }}
            placeholder={placeholder || `Ingrese ${label.toLowerCase()}...`}
          />
        ) : (
          <input 
            type="text" 
            value={displayValue} 
            onChange={(e) => {
              handleFieldChange(key, e.target.value);
              if (errors[key]) setErrors(prev => {
                  const n = {...prev};
                  delete n[key];
                  return n;
              });
            }}
            placeholder={placeholder || `Ingrese ${label.toLowerCase()}...`}
          />
        )}
      </div>
    );
  };

  const renderSelect = (label, value, key, options, required = false, config = {}) => {
    const hasError = errors[key];
    const { displayKey = 'name', valueKey = 'id', allowEmpty = true, emptyLabel = '-- Seleccione --', disabled = false } = config;

    return (
        <div className={`form-group ${hasError ? 'error' : ''}`}>
           <label>
               {label}
               {required && <span className="required-star">*</span>}
               {hasError && <span className="error-message-inline"> - Requerido</span>}
           </label>
           <select 
              className={`form-select${disabled ? ' select-disabled' : ''}`}
              value={value || ""}
              disabled={disabled}
              onChange={(e) => {
                  const val = e.target.value;
                  // Auto-convert to numeric ID if it represents a number
                  const finalVal = (val !== "" && !isNaN(val)) ? Number(val) : val;
                  handleFieldChange(key, finalVal);
                  if (errors[key]) setErrors(prev => {
                      const n = {...prev};
                      delete n[key];
                      return n;
                  });
              }}
           >
              {allowEmpty && <option value="">{emptyLabel}</option>}
              {options && Array.isArray(options) ? options.map(opt => (
                  <option key={opt[valueKey]} value={opt[valueKey]}>
                      {opt[displayKey]}
                  </option>
              )) : null}
           </select>
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
             {!isUser && (
                <div className="rut-header-action" style={{marginRight: 8}}>
                  <button 
                    className={`google-pill-button ${isParsingRut ? 'parsing' : ''}`}
                    style={{
                      padding: '6px 14px',
                      background: 'white',
                      border: '1px solid #dadce0',
                      color: '#1a73e8',
                      fontWeight: 500,
                      fontSize: '0.85rem',
                      height: '36px',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                    onClick={() => document.getElementById('header-rut-input').click()}
                    disabled={isParsingRut}
                    title="Importar datos desde PDF del RUT"
                  >
                    {isParsingRut ? <RefreshCw size={16} className="spin" /> : <BookOpen size={16} />}
                    <span>{isParsingRut ? 'Procesando...' : 'Importar RUT'}</span>
                  </button>
                  <input 
                    id="header-rut-input"
                    type="file" 
                    accept="application/pdf" 
                    style={{display:'none'}} 
                    onChange={handleRutUpload} 
                  />
                </div>
             )}
             {/* Tag Selector */}
             <div className="label-management-container">
                  <button 
                    className="icon-btn" 
                    title="Administrar etiquetas"
                    onClick={() => setShowLabelMenu(!showLabelMenu)}
                  >
                    <Tag size={18} />
                  </button>
                  
                  {showLabelMenu && (
                    <div className="label-dropdown-menu">
                      <div className="label-menu-header">Administrar etiquetas</div>
                      <div className="label-menu-search">
                         <input 
                           type="text" 
                           className="label-search-input" 
                           placeholder="Buscar etiqueta" 
                           value={tagSearch}
                           onChange={(e) => setTagSearch(e.target.value)}
                           autoFocus
                           onClick={(e) => e.stopPropagation()}
                         />
                      </div>
                      <div className="label-list-scroll">
                        {catalogs.tags
                          .filter(t => t.name.toLowerCase().includes(tagSearch.toLowerCase()))
                          .map(tag => {
                            const isChecked = formData.tags && formData.tags.some(ft => ft.id === tag.id);
                            return (
                              <div 
                                key={tag.id} 
                                className="label-menu-item"
                                onClick={() => handleToggleTag(tag)}
                              >
                                <div className={`label-checkbox ${isChecked ? 'checked' : ''}`}>
                                  {isChecked && <div style={{width: 8, height: 8, background: 'white'}}></div>}
                                </div>
                                <div className="label-item-icon">
                                  <Tag size={14} />
                                </div>
                                <div className="label-item-text">{tag.name}</div>
                              </div>
                            );
                        })}
                        {catalogs.tags.filter(t => t.name.toLowerCase().includes(tagSearch.toLowerCase())).length === 0 && tagSearch && (
                           <div className="label-menu-item" onClick={(e) => {
                             e.preventDefault();
                             e.stopPropagation();
                             handleCreateTagImpl(tagSearch);
                           }}>
                              <div className="label-item-icon"><PlusCircle size={14} /></div>
                              <div className="label-item-text">Crear "{tagSearch}"</div>
                           </div>
                        )}
                      </div>
                      <button className="label-create-item" onClick={() => {
                          const name = prompt("Nombre de la nueva etiqueta:");
                          if(name) handleCreateTagImpl(name);
                      }}>
                        <PlusCircle size={14} /> Crear etiqueta
                      </button>
                    </div>
                  )}
              </div>
              <button 
                className="primary-btn-sm" 
                disabled={isSaving} 
                onClick={async () => {
                  setSavingError(null);
                  const newErrors = {};
                  if (isUser) {
                    if (!formData.first_name) newErrors.first_name = true;
                    if (!formData.last_name) newErrors.last_name = true;
                    if (!formData.role_id) newErrors.role_id = true;
                    if (!formData.status_id) newErrors.status_id = true;
                  } else {
                    if (!formData.legal_name) newErrors.legal_name = true;
                    if (!formData.rut_nit) newErrors.rut_nit = true;
                    if (!formData.status_id) newErrors.status_id = true;
                  }

                  if (Object.keys(newErrors).length > 0) {
                    setErrors(newErrors);
                    setSavingError("Por favor complete los campos obligatorios marcados en rojo.");
                    
                    // Auto-focus first error
                    setTimeout(() => {
                        const firstErr = document.querySelector('.form-group.error input, .form-group.error select');
                        if (firstErr) {
                            firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            firstErr.focus();
                        }
                    }, 100);
                    return;
                  }

                  const payload = {
                    ...formData,
                    // Numeric field normalization (ensure int or null, vs empty strings)
                    role_id: formData.role_id ? parseInt(formData.role_id) : null,
                    status_id: formData.status_id ? parseInt(formData.status_id) : 1,
                    agent_id: formData.agent_id ? parseInt(formData.agent_id) : null,
                    gender_id: formData.gender_id ? parseInt(formData.gender_id) : null,
                    revenue: formData.revenue ? parseFloat(formData.revenue) : 0,
                    employee_count: formData.employee_count ? parseInt(formData.employee_count) : 0,
                    economic_activity_code: formData.economic_activity_code ? parseInt(formData.economic_activity_code) : null,
                    
                    // Basic string normalization
                    rut_nit: formData.rut_nit ? formData.rut_nit.toString().trim() : '',
                    tag_ids: formData.tags ? formData.tags.map(t => t.id) : [],
                    phones: (formData.phones || []).map(p => ({
                       local_number: p.local_number ? p.local_number.toString().trim() : '',
                       label_id: parseInt(p.label_id) || 1,
                       country_id: parseInt(p.country_id) || 1
                    })),
                    emails: (formData.emails || []).map(e => ({
                       email_address: e.email_address ? e.email_address.toString().trim().toLowerCase() : '',
                       label_id: parseInt(e.label_id) || 1
                    })),
                    addresses: (formData.addresses || []).map(a => ({
                       address_line1: a.address_line1,
                       address_line2: a.address_line2,
                       city_id: a.city_id ? parseInt(a.city_id) : null,
                       state_id: a.state_id ? parseInt(a.state_id) : null,
                       country_id: a.country_id ? parseInt(a.country_id) : 1,
                       label_id: a.label_id ? parseInt(a.label_id) : 1,
                       postal_code: a.postal_code
                    }))
                  };

                  // Map frontend 'rut_nit' to backend 'tax_id' for Users
                  if (type !== 'companies') {
                      payload.tax_id = formData.rut_nit;
                  }

                  setIsSaving(true);
                  try {
                    await onSave(payload);
                    // onSave will close the panel if successful (in App.jsx)
                  } catch (err) {
                    console.error("Save error in DetailView:", err);
                    setSavingError(err.message || "Error inesperado al guardar");
                  } finally {
                    setIsSaving(false);
                  }
                }}
              >
                {isSaving ? <RefreshCw size={18} className="spin" /> : <Save size={18} />} 
                <span>{isSaving ? 'Guardando...' : 'Guardar cambios'}</span>
              </button>
             <button 
               className="icon-btn danger-text" 
               title="Eliminar definitivamente"
               onClick={() => onDelete && onDelete(formData)}
             >
               <Trash2 size={18} />
             </button>
           </div>
        </header>

        <div className="detail-body">
          {savingError && (
            <div className="error-banner">
              <CheckCircle2 size={20} style={{color: '#d93025', transform: 'rotate(180deg)'}} />
              <span>{savingError}</span>
            </div>
          )}
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
                      {renderField("Primer Nombre", formData.first_name, "first_name", "Nombre de pila", false, true)}
                      {renderField("Otros Nombres", formData.middle_name, "middle_name", "Nombres adicionales")}
                      {renderField("Apellidos", formData.last_name, "last_name", "Apellidos completos", false, true)}
                      {renderField("Sufijo", formData.suffix, "suffix", "Ej: Jr., III, Ph.D")}
                      {renderField("Seudónimo / Apodo", formData.nickname, "nickname", "Nombre informal")}
                      <div className="form-group span-2">
                        {renderField("Archivar como", formData.file_as, "file_as", "Ej: Apellido, Nombre (Para orden alfabético)")}
                      </div>

                        {renderSelect("Rol de Acceso", formData.role_id || 4, "role_id", (catalogs.roles || []), true, { displayKey: 'role_name' })}
                        {renderSelect("Estado", formData.status_id || 1, "status_id", (catalogs.statuses || []), true, { displayKey: 'status_name' })}

                      {/* AGENTE RESPONSABLE - visible siempre, editable solo para clientes (IDs 5 y 6) */}
                      {renderSelect("Agente Responsable", formData.agent_id || "", "agent_id", (catalogs.agents || []), false, { emptyLabel: 'Sin asignar...', disabled: ![5, 6].includes(Number(formData.role_id)) })}

                      {/* CONDICIONAL: CREDENCIALES (Si es Admin o Agente 1, 2) */}
                      {(formData.role_id === 1 || formData.role_id === 2) && (
                          <>
                            {renderField("Nombre de Usuario", formData.username, "username", "Para inicio de sesión")}
                            <div className="form-group">
                              <label>Contraseña (Nueva)</label>
                              <input 
                                type="password" 
                                placeholder="Dejar vacío para no cambiar"
                                onChange={(e) => handleFieldChange('plain_password', e.target.value)} 
                              />
                            </div>
                          </>
                      )}
                    </>
                  ) : (
                    <>
                      <div className="form-group span-2">
                         {renderField("Razón Social (Legal)", formData.legal_name, "legal_name", "Nombre legal de la entidad", false, true)}
                      </div>
                      <div className="form-group span-2">
                         {renderField("Nombre Comercial", formData.commercial_name, "commercial_name", "Nombre de marca o fantasía")}
                      </div>
                      
                      <div className="grid-2 span-2">
                          <div className="form-group">
                             {renderField("Sitio Web / Dominio", formData.domain, "domain", "ejemplo.com")}
                          </div>
                          <div className="form-group">
                             {renderField("Ingresos Anuales", formData.revenue, "revenue", "0")}
                          </div>
                      </div>

                      <div className="form-group span-2 grid-2" style={{gap:16}}>
                          {renderSelect("Estado de Empresa", formData.status_id || 1, "status_id", (catalogs.statuses || []), true, { displayKey: 'status_name' })}
                          {renderSelect("Agente Responsable", formData.agent_id || "", "agent_id", (catalogs.agents || []), false, { emptyLabel: 'Seleccione un agente' })}
                      </div>

                      <div className="form-group span-2">
                         {renderField("Descripción / Actividad", formData.description, "description", "Describe brevemente a qué se dedica la empresa...", true)}
                      </div>

                      <div className="form-group span-2">
                          <label>Actividad Económica Principal (CIIU)</label>
                          <div style={{position:'relative'}}>
                              <Search size={16} style={{position:'absolute', left:12, top:10, color:'var(--text-secondary)'}} />
                              <input 
                                  type="text" 
                                  placeholder="Buscar por código o descripción (ej: 2712)..." 
                                  value={economicSearch}
                                  onChange={(e) => handleSearchActivities(e.target.value)}
                                  className="form-select"
                                  style={{paddingLeft:36}}
                              />
                              {isSearchingActivities && <RefreshCw size={14} className="animate-spin" style={{position:'absolute', right:12, top:10}} />}
                              
                              {economicSearch.length >= 2 && economicActivities.length > 0 && !economicSearch.includes(' - ') && (
                                  <div className="search-results-mini" style={{width:'100%', zIndex:100, maxHeight:200, overflowY:'auto'}}>
                                      {economicActivities.map(act => (
                                          <div 
                                              key={act.id} 
                                              className="search-item-mini" 
                                              style={{padding:'8px 12px', cursor:'pointer'}}
                                              onClick={() => {
                                                  handleFieldChange('economic_activity_code', act.id);
                                                  setEconomicSearch(`${act.id} - ${act.description}`);
                                              }}
                                          >
                                              <Hash size={12} style={{marginRight:6, color:'#666'}} />
                                              <b>{act.id}</b> - {act.description}
                                          </div>
                                      ))}
                                  </div>
                              )}
                          </div>
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
                    {renderField("RUT / NIT (Cédula/Tax ID)", formData.rut_nit, "rut_nit", "Número base sin puntos ni guiones", false, true)}
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
                          <div key={c.id} className="address-card" style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
                            <div>
                                <p style={{fontWeight:500}}><Building size={14} style={{marginRight:8}} /> {c.legal_name}</p>
                                <p className="address-meta">{c.position_name || 'Sin cargo'} • {c.department_name || 'Sin departamento'}</p>
                            </div>
                            <button className="icon-btn-sm danger-text" onClick={() => handleUnlinkCompany(c.id)} title="Desvincular">
                                <Trash2 size={16} />
                            </button>
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
                                        {(catalogs.companies || [])
                                            .filter(c => (c.legal_name || '').toLowerCase().includes((linkingState.search || '').toLowerCase()))
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
                                   value={linkingState.positionId}
                                   onChange={(e) => setLinkingState(prev => ({ ...prev, positionId: e.target.value }))}
                                 >
                                   {(catalogs.positions || []).map(p => <option key={p.id} value={p.id}>{p.position_name}</option>)}
                                 </select>
                                 
                                 <select 
                                   className="form-select"
                                   value={linkingState.deptId}
                                   onChange={(e) => setLinkingState(prev => ({ ...prev, deptId: e.target.value }))}
                                 >
                                   {(catalogs.departments || []).map(d => <option key={d.id} value={d.id}>{d.department_name}</option>)}
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
                          <div 
                            key={e.id} 
                            className="address-card clickable-card" 
                            onClick={() => onSelectRelated && onSelectRelated(e.id, 'users')}
                            style={{cursor: 'pointer', transition: 'background 0.2s'}}
                          >
                            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
                              <div>
                                <p style={{fontWeight:500, margin: 0, color: 'var(--google-blue)'}}>
                                  <User size={14} style={{marginRight:8}} /> {e.first_name} {e.last_name}
                                </p>
                                <p className="address-meta" style={{margin: '4px 0 0 22px'}}>
                                  {e.position_name || 'Sin cargo'} • {e.department_name || 'Sin departamento'}
                                </p>
                              </div>
                              <div style={{textAlign: 'right', fontSize: '0.85rem', color: '#666'}}>
                                {e.email && <div style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-end'}}><Mail size={12} style={{marginRight:4}} /> {e.email}</div>}
                                {e.phone && <div style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginTop: 2}}><Phone size={12} style={{marginRight:4}} /> {e.phone}</div>}
                              </div>
                            </div>
                          </div>
                        )) : <p className="no-data-msg">No hay empleados registrados vinculados a esta empresa.</p>}
                        <button className="text-btn-sm" onClick={() => alert("Para añadir empleados, diríjase a la ficha del contacto individual y vincúlelo a esta empresa.")}>+ Cómo añadir empleados</button>
                      </div>
                    )}
                  </div>
                )}
            </section>

            {/* 3.2 VINCULOS CORPORATIVOS (B2B) */}
            {!isUser && (
              <section className="detail-section">
                <header className="section-header" onClick={() => toggleSection('corporate_links')}>
                  <div className="section-title">
                    <Building size={18} className="icon-muted" />
                    <span>Red Corporativa (B2B)</span>
                  </div>
                  {openSections.corporate_links ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </header>
                {openSections.corporate_links && (
                  <div className="section-content">
                    <div className="professional-list">
                      {formData.relationships && formData.relationships.length > 0 ? formData.relationships.map((rel, idx) => (
                          <div key={`${rel.target_company_id}-${rel.relation_type || 'rt'}-${idx}`} className="address-card" style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
                           <div>
                             <p style={{fontWeight:500}}><Building size={14} style={{marginRight:8}} /> {rel.legal_name}</p>
                             <p className="address-meta">
                               <b>{rel.relation_type}:</b> {rel.notes || 'Sin notas'}
                             </p>
                           </div>
                           <div style={{display:'flex', gap:5}}>
                               <button className="icon-btn-sm" onClick={(e) => { e.stopPropagation(); handleOpenLinkModal(rel); }} title="Editar asociación">
                                 <Settings size={16} />
                               </button>
                               <button className="icon-btn-sm danger-text" onClick={(e) => { e.stopPropagation(); handleUnlinkCompanyRel(rel.target_company_id); }} title="Borrar vínculo">
                                 <Trash2 size={16} />
                               </button>
                           </div>
                         </div>
                       )) : <p className="no-data-msg">No hay vínculos con otras empresas.</p>}
 
                       <div style={{marginTop:12}}>
                           <button className="google-pill-button" onClick={() => handleOpenLinkModal(null)}>
                             <PlusCircle size={16} /> Vincular Empresa
                           </button>
                       </div>
 
                       {/* MAIN LINK MODAL (HUBSPOT STYLE) */}
                       {isRelModalOpen && (
                         <div className="modal-overlay" style={{zIndex: 9998}}>
                             <div className="modal-content animate-fade-in" style={{width: 500}}>
                                 <div className="modal-header">
                                     <h3>{companyLinkingState.isEditing ? 'Editar asociación' : 'Vincular a otra Empresa'}</h3>
                                     <button onClick={() => setIsRelModalOpen(false)}><X /></button>
                                 </div>
                                 <div className="modal-body" style={{padding:20}}>
                                     {!companyLinkingState.selectedCompany && !companyLinkingState.isEditing && (
                                       <div style={{marginBottom:15}}>
                                          <Search size={16} style={{position:'absolute', left:32, top:88, color:'#999'}} />
                                          <input 
                                            type="text" 
                                            placeholder="Buscar empresa..." 
                                            autoFocus
                                            value={companyLinkingState.search}
                                            onChange={(e) => setCompanyLinkingState(prev => ({ ...prev, search: e.target.value }))}
                                            className="form-select"
                                            style={{paddingLeft:36}}
                                          />
                                          <div className="search-results-mini">
                                            {(catalogs.companies || [])
                                                .filter(c => c.legal_name.toLowerCase().includes(companyLinkingState.search.toLowerCase()) && c.id !== formData.id)
                                                .slice(0, 8)
                                                .map(c => (
                                              <div key={c.id} className="search-item-mini" onClick={() => setCompanyLinkingState(prev => ({ ...prev, selectedCompany: c }))}>
                                                <Building size={14} style={{marginRight:8}}/> {c.legal_name}
                                              </div>
                                            ))}
                                          </div>
                                       </div>
                                     )}
 
                                     {companyLinkingState.selectedCompany && (
                                       <div className="animate-fade-in">
                                         <div style={{background:'#f5f8fa', padding:10, borderRadius:6, marginBottom:16, borderLeft:'4px solid #1a73e8'}}>
                                             <p style={{margin:0, fontWeight:500, color:'#1a73e8'}}>
                                                 {companyLinkingState.isEditing ? 'Asociado con:' : 'Emparejar con:'}
                                                 <span style={{color:'#333', marginLeft:6}}>{companyLinkingState.selectedCompany.legal_name}</span>
                                             </p>
                                             {!companyLinkingState.isEditing && <button className="text-btn-sm" onClick={() => setCompanyLinkingState(prev => ({ ...prev, selectedCompany: null }))}>Cambiar</button>}
                                         </div>
 
                                         <div className="form-group">
                                            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                                                <label>Etiquetas de asociación (Tipo)</label>
                                                <button 
                                                    className="text-btn-sm" 
                                                    style={{fontSize:'0.75rem', color:'#1a73e8'}}
                                                    onClick={() => setShowManageTypesModal(true)}
                                                >
                                                    <Settings size={12} style={{marginRight:4}} />
                                                    Gestionar
                                                </button>
                                            </div>
                                            <select 
                                              className="form-select"
                                              value={companyLinkingState.relationTypeId}
                                              onChange={(e) => setCompanyLinkingState(prev => ({ ...prev, relationTypeId: e.target.value }))}
                                            >
                                              {flattenedOptions.map(opt => (
                                                  <option key={opt.value} value={opt.value}>
                                                      {opt.name} {opt.is_inverse ? '(Inverso)' : ''} -- {opt.sub}
                                                  </option>
                                              ))}
                                              <option value="-1" style={{fontWeight:'bold', color:'blue'}}>+ Crear Nuevo Tipo...</option>
                                            </select>
                                         </div>
 
                                         {companyLinkingState.relationTypeId === "-1" && (
                                            <div className="new-type-fields animate-fade-in" style={{background:'#f0f4ff', padding:10, borderRadius:6, marginBottom:16}}> 
                                                <div className="form-group" style={{marginBottom:8}}>
                                                  <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                                                      <label style={{fontSize:'0.85em', color:'blue'}}>Nombre Principal</label>
                                                      <label className="checkbox-container" style={{fontSize:'0.8em', display:'flex', alignItems:'center', cursor:'pointer'}}>
                                                          <input 
                                                            type="checkbox" 
                                                            checked={companyLinkingState.isSymmetric} 
                                                            onChange={(e) => setCompanyLinkingState(prev => ({...prev, isSymmetric: e.target.checked}))}
                                                            style={{marginRight:4}}
                                                          /> Enlace Recíproco
                                                      </label>
                                                  </div>
                                                  <input 
                                                      className="form-input" 
                                                      value={companyLinkingState.newTypeName || ''}
                                                      onChange={(e) => setCompanyLinkingState(prev => ({...prev, newTypeName: e.target.value}))}
                                                      placeholder={companyLinkingState.isSymmetric ? "Ej: Socio, Aliado" : "Ej: Contratista"}
                                                  />
                                                </div>
                                                {!companyLinkingState.isSymmetric && (
                                                    <div className="form-group" style={{marginBottom:0}}>
                                                      <label style={{fontSize:'0.85em', color:'blue'}}>Nombre Inverso</label>
                                                      <input 
                                                          className="form-input" 
                                                          value={companyLinkingState.newTypeInverse || ''}
                                                          onChange={(e) => setCompanyLinkingState(prev => ({...prev, newTypeInverse: e.target.value}))}
                                                          placeholder="Ej: Contratante"
                                                      />
                                                    </div>
                                                )}
                                            </div>
                                         )}
 
                                         <div className="form-group">
                                            <label>Notas</label>
                                            <input 
                                              className="form-input" 
                                              placeholder="Ej: Contrato 2024"
                                              value={companyLinkingState.notes}
                                              onChange={(e) => setCompanyLinkingState(prev => ({...prev, notes: e.target.value}))}
                                            />
                                         </div>
                                       </div>
                                     )}
                                 </div>
                                 <div className="modal-footer">
                                     {companyLinkingState.selectedCompany && (
                                         <button className="primary-btn" onClick={handleCompanyLinkSubmit}>
                                             {companyLinkingState.isEditing ? 'Actualizar' : 'Guardar'}
                                         </button>
                                     )}
                                     <button className="text-button" onClick={() => setIsRelModalOpen(false)}>Cancelar</button>
                                 </div>
                             </div>
                         </div>
                       )}
 
                       {/* OLD UI REMOVED - REPLACED BY MODAL ABOVE */}
                    </div>
                  </div>
                )}
              </section>
            )}

            {/* 3.1 RELACIONES PERSONALES / VINCULOS ENTRE USUARIOS */}
            {isUser && (
              <section className="detail-section">
                <header className="section-header" onClick={() => toggleSection('relationships')}>
                  <div className="section-title">
                    <Users size={18} className="icon-muted" />
                    <span>Vínculos entre Usuarios</span>
                  </div>
                  {openSections.relationships ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </header>
                {openSections.relationships && (
                  <div className="section-content">
                    <div className="professional-list">
                      {formData.relationships && formData.relationships.length > 0 ? formData.relationships.map((rel, idx) => (
                        <div key={`${rel.related_user_id}-${rel.relation_type_id}-${idx}`} className="address-card" style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
                          <div>
                            <p style={{fontWeight:500}}><User size={14} style={{marginRight:8}} /> {rel.first_name} {rel.last_name}</p>
                            <p className="address-meta">
                              <b>{rel.relation_type}:</b> {rel.custom_label || 'Sin nota adicional'}
                            </p>
                          </div>
                          <button className="icon-btn-sm danger-text" onClick={(e) => { e.stopPropagation(); handleUnlinkUser(rel.related_user_id); }} title="Borrar vínculo">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      )) : <p className="no-data-msg">No hay vínculos registrados con otros usuarios.</p>}

                      {!userLinkingState.active ? (
                        <div style={{marginTop:12}}>
                          <button className="google-pill-button" onClick={() => setUserLinkingState(prev => ({ ...prev, active: true, search: '', selectedUser: null }))}>
                            <PlusCircle size={16} /> Vincular Usuario
                          </button>
                        </div>
                      ) : (
                        <div className="google-outlined-field-group" style={{marginTop:16, padding:16, border:'1px solid var(--border-color)', borderRadius:8}}>
                           <div style={{display:'flex', justifyContent:'space-between', marginBottom:12}}>
                             <h4 style={{margin:0}}>Vincular a otro Usuario</h4>
                             <button className="icon-btn-sm" onClick={() => setUserLinkingState(prev => ({ ...prev, active: false }))}><X size={16}/></button>
                           </div>

                           {!userLinkingState.selectedUser && (
                             <div style={{position:'relative'}}>
                                <Search size={16} style={{position:'absolute', left:12, top:12, color:'var(--text-secondary)'}} />
                                <input 
                                  type="text" 
                                  placeholder="Buscar por nombre o apellido..." 
                                  autoFocus
                                  value={userLinkingState.search}
                                  onChange={(e) => setUserLinkingState(prev => ({ ...prev, search: e.target.value }))}
                                  className="form-select"
                                  style={{paddingLeft:36}}
                                />
                                <div className="search-results-mini">
                                  {((catalogs.users || []) || [])
                                      .filter(u => `${u.first_name} ${u.last_name}`.toLowerCase().includes(userLinkingState.search.toLowerCase()) && u.id !== formData.id)
                                      .slice(0, 8)
                                      .map(u => (
                                    <div key={u.id} className="search-item-mini" onClick={() => setUserLinkingState(prev => ({ ...prev, selectedUser: u }))}>
                                      <User size={14} style={{marginRight:8}}/> {u.first_name} {u.last_name}
                                    </div>
                                  ))}
                                </div>
                             </div>
                           )}

                           {userLinkingState.selectedUser && (
                             <div className="link-details-mini animate-fade-in">
                               <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}> 
                                   <p className="selected-tag">Vincular con: <b>{userLinkingState.selectedUser.first_name} {userLinkingState.selectedUser.last_name}</b></p>
                                   <button className="text-btn-sm" onClick={() => setUserLinkingState(prev => ({ ...prev, selectedUser: null }))}>Cambiar</button>
                               </div>
                               
                               <label className="google-label-floating" style={{position:'static', marginBottom:4, display:'block', fontSize:'0.8rem'}}>Tipo de relación</label>
                               <select 
                                 className="form-select"
                                 value={userLinkingState.relationTypeId}
                                 onChange={(e) => setUserLinkingState(prev => ({ ...prev, relationTypeId: e.target.value }))}
                               >
                                 {(catalogs.user_relation_types || []) && (catalogs.user_relation_types || []).map(rt => (
                                     <option key={rt.id} value={rt.id}>
                                         {rt.name} {rt.inverse_name ? `-- Emparejado con ${rt.inverse_name}` : '-- Sin inversa definida (Simétrica)'}
                                     </option>
                                 ))}
                                 <option value="-1" style={{fontWeight:'bold', color:'blue'}}>+ Crear Nuevo Tipo...</option>
                               </select>

                               {userLinkingState.relationTypeId === "-1" && (
                                  <div className="new-type-fields animate-fade-in" style={{background:'#f0f4ff', padding:10, borderRadius:6, marginBottom:16, marginTop: 8}}> 
                                      <div className="form-group" style={{marginBottom:8}}>
                                        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                                            <label style={{fontSize:'0.85em', color:'blue'}}>Nombre Principal</label>
                                            <label className="checkbox-container" style={{fontSize:'0.8em', display:'flex', alignItems:'center', cursor:'pointer'}}>
                                                <input 
                                                  type="checkbox" 
                                                  checked={userLinkingState.isSymmetric} 
                                                  onChange={(e) => setUserLinkingState(prev => ({...prev, isSymmetric: e.target.checked}))}
                                                  style={{marginRight:4}}
                                                /> Recíproca
                                            </label>
                                        </div>
                                        <input 
                                            className="form-input" 
                                            value={userLinkingState.newTypeName || ''}
                                            onChange={(e) => setUserLinkingState(prev => ({...prev, newTypeName: e.target.value}))}
                                            placeholder={userLinkingState.isSymmetric ? "Ej: Amigo, Colega" : "Ej: Jefe"}
                                        />
                                      </div>
                                      {!userLinkingState.isSymmetric && (
                                          <div className="form-group" style={{marginBottom:0}}>
                                            <label style={{fontSize:'0.85em', color:'blue'}}>Nombre Inverso</label>
                                            <input 
                                                className="form-input" 
                                                value={userLinkingState.newTypeInverse || ''}
                                                onChange={(e) => setUserLinkingState(prev => ({...prev, newTypeInverse: e.target.value}))}
                                                placeholder="Ej: Empleado"
                                            />
                                          </div>
                                      )}
                                  </div>
                               )}

                               <div className="google-outlined-input-container" style={{marginTop:12}}>
                                   <label className="google-label-floating">Etiqueta personalizada (opcional)</label>
                                   <input 
                                     type="text" 
                                     className="google-input-field"
                                     value={userLinkingState.customLabel}
                                     onChange={(e) => setUserLinkingState(prev => ({ ...prev, customLabel: e.target.value }))}
                                     placeholder="Ej: Cónyuge, Socio, Ref. Personal"
                                   />
                               </div>

                               <div className="row-actions-mini">
                                 <button className="primary-btn-sm" onClick={handleUserLinkSubmit}>Vincular</button>
                                 <button className="text-btn-sm" onClick={() => setUserLinkingState(prev => ({ ...prev, active: false }))}>Cancelar</button>
                               </div>
                             </div>
                           )}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </section>
            )}


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
                    <div className="form-group">
                      <label>Numero de empleados</label>
                      <input 
                        type="number" 
                        value={formData.employee_count || 0} 
                        onChange={(e) => handleFieldChange('employee_count', e.target.value)}
                        placeholder="Cantidad de personal" 
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
                           <div style={{width: 80, marginRight: 8}}>
                              <label className="google-label-floating" style={{zIndex:1, background:'white', padding:'0 4px', left:8, top:-8, fontSize:10, color:'#1a73e8'}}>País</label>
                              <select
                                className="google-input-field"
                                value={p.country_id || 1}
                                onChange={(e) => updatePhone(p.id || p._tempId, 'country_id', e.target.value)}
                                style={{paddingLeft:8, paddingRight:4}}
                              >
                                {(catalogs.countries || []) ? (catalogs.countries || []).map(c => (
                                  <option key={c.id} value={c.id}>{c.phone_code} {c.country_name}</option>
                                )) : <option value={1}>+57 CO</option>}
                              </select>
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
                   {formData.addresses && formData.addresses.map(a => (
                     <div key={a.id || a._tempId} className="address-card" style={{border:'1px solid var(--border-color)', borderRadius:8, padding:12, marginBottom:12}}>
                       <div style={{display:'flex', gap:10, marginBottom:8}}>
                          <select className="google-input-field" value={a.country_id || ''} onChange={(e) => handleCountryChange(a.id || a._tempId, e.target.value)}>
                             <option value="">País...</option>
                             {catalogs.countries.map(c => <option key={c.id} value={c.id}>{c.country_name}</option>)}
                          </select>
                          <select className="google-input-field" value={a.state_id || ''} onChange={(e) => handleStateChange(a.id || a._tempId, e.target.value)}>
                             <option value="">Depto...</option>
                             {((a.country_id && geoCache.states[a.country_id]) || []).map(s => <option key={s.id} value={s.id}>{s.state_name}</option>)}
                          </select>
                          <select className="google-input-field" value={a.city_id || ''} onChange={(e) => updateAddress(a.id || a._tempId, 'city_id', e.target.value)}>
                             <option value="">Ciudad...</option>
                             {((a.state_id && geoCache.cities[a.state_id]) || []).map(city => <option key={city.id} value={city.id}>{city.city_name}</option>)}
                          </select>
                       </div>
                       <div style={{display:'flex', gap:10}}>
                            <input className="google-input-field" placeholder="Dirección (Calle/Carrera...)" value={a.address_line1 || ''} onChange={(e) => updateAddress(a.id || a._tempId, 'address_line1', e.target.value)} style={{flex:2}} />
                             <select className="google-input-field" value={a.label_id || 1} onChange={(e) => updateAddress(a.id || a._tempId, 'label_id', e.target.value)} style={{flex:1}}>
                                {catalogs.labels.map(l => <option key={l.id} value={l.id}>{l.label_name}</option>)}
                             </select>
                            <button className="icon-button-danger" onClick={() => removeAddress(a.id || a._tempId)}><Trash2 size={18} /></button>
                       </div>
                     </div>
                   ))}
                   <button className="google-pill-button" onClick={addAddress}><PlusCircle size={16} /> Agregar Dirección</button>
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
                           {renderSelect("Género / Sexo Identificado", formData.gender_id, "gender_id", (catalogs.genders || []), false, { emptyLabel: 'No especificado' })}
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
