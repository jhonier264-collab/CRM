# Project Directory Structure

```
├── .env
├── .env.example
├── .gitignore
├── **start_dev.bat** (Script de inicio automatizado del ecosistema)
├── backend/ (FastAPI Server)
│   ├── api_server.py
│   ├── data/
│   │   └── headers.txt
│   ├── logs/
│   │   ├── backend_log.txt
│   │   ├── debug_payload.txt
│   │   ├── debug_run.log
│   │   ├── qa_output.log
│   │   ├── qa_traceback.log
│   │   └── startup_error.log
│   ├── main.py
│   ├── requirements.txt
│   ├── src/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── database_interface.py
│   │   │   ├── database_manager.py
│   │   │   ├── exceptions.py
│   │   │   ├── mysql_repository.py
│   │   │   ├── responses.py
│   │   │   └── serializers.py
│   │   ├── lib/
│   │   │   └── shared_auth/
│   │   │       ├── interfaces.py
│   │   │       ├── recovery_provider.py
│   │   │       ├── security.py
│   │   │       └── services.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   ├── modules/
│   │   │   └── business_pipeline/
│   │   │       ├── __init__.py
│   │   │       ├── models.py
│   │   │       ├── repositories.py
│   │   │       └── services.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── auth_repository.py
│   │   │   └── repository.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── address_intelligence_service.py
│   │       ├── auth_service.py
│   │       ├── contact_normalization_service.py
│   │       ├── data_hygiene_service.py
│   │       ├── identity_hygiene_service.py
│   │       ├── provisioning_service.py
│   │       ├── schema_manager.py
│   │       └── services.py
│   ├── tests/
│   │   ├── integration/
│   │   │   ├── check_interfaces.py
│   │   │   ├── clean_sql.py
│   │   │   ├── repro_error.py
│   │   │   ├── test_b2b_b2c.py
│   │   │   ├── test_company_create.py
│   │   │   ├── test_company_delete.py
│   │   │   ├── test_company_read.py
│   │   │   ├── test_relations_google.py
│   │   │   ├── test_trash_hygiene.py
│   │   │   ├── test_update_audit.py
│   │   │   ├── test_user_create.py
│   │   │   ├── test_user_delete.py
│   │   │   ├── test_user_extended.py
│   │   │   ├── test_user_read.py
│   │   │   └── verify_api.py
│   │   ├── manual/
│   │   │   ├── cli_manager.py
│   │   │   ├── flows.py
│   │   │   ├── schemas.py
│   │   │   ├── test_contacts_flow.py
│   │   │   ├── test_lookups.py
│   │   │   ├── test_results.log
│   │   │   ├── test_service_refactor.py
│   │   │   └── ui_utils.py
│   │   ├── qa/
│   │   │   ├── qa_broadcast.py
│   │   │   ├── qa_frontend_integration.py
│   │   │   ├── qa_provisioning.py
│   │   │   ├── qa_rollback.py
│   │   │   └── qa_security.py
│   │   └── unit/
│   │       └── test_validation.py
│   └── tools/
│       ├── check_db_state.py
│       ├── debug_tenant.py
│       ├── init_master_db.py
│       ├── inspect_schema.py
│       ├── migrate_schema.py
│       ├── migrate_tenant.py
│       ├── read_log.py
│       ├── seed_duplicates.py
│       ├── test_api_flow.py
│       ├── verify_company.py
│       └── verify_fix.py
├── database/
│   ├── core_template.sql
│   ├── dumps/
│   │   ├── CRM.sql
│   │   └── CRM_English.sql
│   ├── master_db.sql
│   ├── modules/
│   │   ├── broken_module.sql
│   │   └── business_pipeline.sql
│   └── scripts/
│       └── crm_hygiene_setup.sql
├── docs/
│   ├── DEPENDENCIES.md
│   ├── DIAGRAMAS
│   ├── MANUAL_MAESTRO_CRM.md
│   ├── README.md
│   └── REPORTE_ESTABILIDAD_CRM.md
├── frontend/
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── public/
│   ├── src/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── DetailView.jsx
│   │   │   └── UserRow.jsx
│   │   ├── config/
│   │   │   ├── api_config.js
│   │   │   └── runtime_config.js
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   ├── AuthPage.css
│   │   │   └── AuthPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   │       ├── global.css
│   │       └── themes.css
│   └── vite.config.js
```
