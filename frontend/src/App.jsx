
import React, { useState, useEffect } from 'react'
import { 
  Users, 
  Building2, 
  Trash2, 
  Settings,
  Menu, 
  Globe, 
  Search, 
  Moon, 
  Sun,
  Plus,
  RefreshCw,
  Star,
  Printer,
  Upload,
  MoreVertical,
  CheckCircle2,
  Settings2,
  FileDown
} from 'lucide-react'
import { userService, companyService, hygieneService } from './services/api'
import UserRow from './components/UserRow'
import DetailView from './components/DetailView'

function App() {
  const [darkMode, setDarkMode] = useState(false)
  const [activeTab, setActiveTab] = useState('users')
  const [users, setUsers] = useState([])
  const [companies, setCompanies] = useState([])
  const [trash, setTrash] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedItem, setSelectedItem] = useState(null)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [selectedIds, setSelectedIds] = useState([])

  // Theme effect
  useEffect(() => {
    if (darkMode) {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
  }, [darkMode])

  // Data fetching
  const fetchData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'users') {
        const data = await userService.list()
        setUsers(data)
      } else if (activeTab === 'companies') {
        const data = await companyService.list()
        setCompanies(data)
      } else if (activeTab === 'trash') {
        const data = await hygieneService.getTrash('users') // Default to users for now
        setTrash(data)
      }
    } catch (error) {
      console.error("Error fetching data:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const handleDeleteUser = async (id) => {
    if (window.confirm('¿Mover este contacto a la papelera?')) {
      try {
        await userService.delete(id)
        await fetchData() // Refresh all lists
      } catch (error) {
        console.error("Delete failed:", error)
        alert("Error al eliminar registro")
      }
    }
  }

  const menuItems = [
    { id: 'users', label: 'Contactos', icon: Users },
    { id: 'companies', label: 'Empresas', icon: Building2 },
    { id: 'import', label: 'Importar', icon: Upload }, // Reemplazado Geografía
    { id: 'config', label: 'Configuración', icon: Settings },
    { id: 'trash', label: 'Papelera', icon: Trash2 },
  ]

  return (
    <div className="layout">
      {/* Header */}
      <header className="main-header">
        <div className="header-left">
          <button className="icon-btn" onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}>
            <Menu size={20} />
          </button>
          <img src="/vite.svg" alt="Logo" className="logo" />
          <span className="app-title">CRM Industrial</span>
        </div>
        
        <div className="search-container">
          <div className="search-bar">
            <Search size={18} className="search-icon" />
            <input type="text" placeholder="Buscar contactos..." />
          </div>
        </div>

        <div className="header-right">
          <button 
            className="icon-btn theme-toggle" 
            onClick={() => setDarkMode(!darkMode)}
            title="Cambiar tema"
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <div className="user-avatar">J</div>
        </div>
      </header>

      <div className="main-container">
        {/* Sidebar */}
        <aside className={`sidebar ${isSidebarCollapsed ? 'collapsed' : ''}`}>
          <button className="create-btn">
            <Plus size={24} />
            {!isSidebarCollapsed && <span>Crear contacto</span>}
          </button>
          
          <nav className="side-nav">
            {menuItems.map(item => (
              <button 
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => {
                  setActiveTab(item.id)
                  setSelectedItem(null)
                }}
                title={isSidebarCollapsed ? item.label : ''}
              >
                <item.icon size={20} />
                {!isSidebarCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </nav>
        </aside>

        {/* Content Area */}
        <main className="content">
          {selectedItem ? (
            <DetailView 
              key={selectedItem.id}
              item={selectedItem} 
              type={selectedItem.legal_name ? 'companies' : 'users'}
              onClose={() => setSelectedItem(null)}
              onSave={async (updated) => {
                try {
                  if (updated.legal_name) {
                    await companyService.update(updated.id, updated);
                  } else {
                    await userService.update(updated.id, updated);
                  }
                  setSelectedItem(null);
                  fetchData();
                } catch (err) {
                  console.error("Error saving updates:", err);
                  alert("Error al guardar los cambios: " + err.message);
                }
              }}
            />
          ) : (
            <>
              <div className="content-header">
                <div className="title-area">
                  <h1>
                    {menuItems.find(i => i.id === activeTab)?.label}
                    {activeTab === 'users' && users.length > 0 && <span className="entity-count">({users.length})</span>}
                    {activeTab === 'companies' && companies.length > 0 && <span className="entity-count">({companies.length})</span>}
                  </h1>
                  {activeTab === 'trash' && <span className="badge">Papelera Global</span>}
                </div>
                <div className="header-actions-bar">
                  <button className="icon-btn-ghost" title="Imprimir"><Printer size={20} /></button>
                  <button className="icon-btn-ghost" title="Exportar"><FileDown size={20} /></button>
                  <button className="icon-btn-ghost" title="Configurar columnas"><Settings2 size={20} /></button>
                  <button className="icon-btn" onClick={fetchData} title="Refrescar">
                    <RefreshCw size={20} className={loading ? 'spin' : ''} />
                  </button>
                </div>
              </div>
              
              <div className="data-table">
                <div className="table-header">
                  <div className="user-col checkbox"><input type="checkbox" /></div>
                  <div className="user-col star"></div>
                  {activeTab === 'companies' ? (
                    <>
                      <div className="user-col name">Razón Social</div>
                      <div className="user-col comercial">Nombre Comercial</div>
                      <div className="user-col rut">RUT / NIT</div>
                      <div className="user-col web">Sitio Web</div>
                      <div className="user-col revenue">Ingresos</div>
                    </>
                  ) : (
                    <>
                      <div className="user-col name">Nombre</div>
                      <div className="user-col email">Correo electrónico</div>
                      <div className="user-col phone">Número de teléfono</div>
                      <div className="user-col company">Cargo y empresa</div>
                      <div className="user-col labels">Etiquetas</div>
                    </>
                  )}
                  <div className="user-col actions"></div>
                </div>

                <div className="table-body">
                  {activeTab === 'users' && users.map(u => (
                    <div key={u.id} onClick={async (e) => {
                      if (e.target.type !== 'checkbox') {
                        setLoading(true);
                          try {
                          const detail = await userService.get(u.id);
                          console.log("Detail loaded:", detail);
                          setSelectedItem(detail);
                        } catch (err) {
                          console.error("Error fetching user detail:", err);
                          setSelectedItem(null); 
                        } finally {
                          setLoading(false);
                        }
                      }
                    }}>
                      <UserRow user={u} onDelete={handleDeleteUser} />
                    </div>
                  ))}
                  
                  {activeTab === 'companies' && companies.map(c => (
                    <div key={c.id} className="user-row" onClick={async () => {
                      setLoading(true);
                      try {
                        const detail = await companyService.get(c.id);
                        setSelectedItem(detail);
                      } catch (err) {
                        setSelectedItem(c);
                      } finally {
                        setLoading(false);
                      }
                    }}>
                       <div className="user-col checkbox"><input type="checkbox" /></div>
                       <div className="user-col star"><Star size={18} className="icon-muted" /></div>
                       <div className="user-col name">
                         <div className="avatar ico-corp"><Building2 size={18} /></div>
                         <span>{c.legal_name}</span>
                       </div>
                       <div className="user-col comercial">{c.commercial_name || '-'}</div>
                       <div className="user-col rut">{c.rut_nit || '-'}</div>
                       <div className="user-col web">{c.domain || '-'}</div>
                       <div className="user-col revenue">{c.revenue ? `$${c.revenue.toLocaleString()}` : '-'}</div>
                       <div className="user-col actions">
                          <button className="icon-btn-sm"><MoreVertical size={16} /></button>
                       </div>
                    </div>
                  ))}

                  {activeTab === 'trash' && trash.map(item => (
                    <div key={item.id} className="user-row deleted">
                       <div className="user-col checkbox"><input type="checkbox" /></div>
                       <div className="user-col star"><Trash2 size={18} className="icon-muted" /></div>
                       <div className="user-col name">
                         <span>{item.first_name || item.company_name}</span>
                       </div>
                       <div className="user-col email">-</div>
                       <div className="user-col phone">-</div>
                       <div className="user-col company">-</div>
                       <div className="user-col labels">-</div>
                       <div className="user-col actions">
                         <button className="primary-btn-sm">Restaurar</button>
                       </div>
                    </div>
                  ))}

                  {((activeTab === 'users' && users.length === 0) || 
                    (activeTab === 'companies' && companies.length === 0) || 
                    (activeTab === 'trash' && trash.length === 0)) && !loading && (
                    <div className="empty-state">
                      <img src="https://ssl.gstatic.com/social/contactsui/images/emptyview/empty_contacts_light.png" alt="Empty" />
                      <p>Aún no hay registros en {activeTab}</p>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
