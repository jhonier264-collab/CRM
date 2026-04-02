import os

def clean_sql(file_path):
    tables_to_clean = [
        '`addresses`', '`companies`', '`company_activities`', 
        '`company_associations`', '`emails`', '`phones`', 
        '`user_companies`', '`user_user_relations`', '`user_tags`', 
        '`users`', '`audit_logs`'
    ]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for line in lines:
        # Reset AUTO_INCREMENT in CREATE TABLE
        if ") ENGINE=InnoDB" in line and "AUTO_INCREMENT=" in line:
            line = line.split("AUTO_INCREMENT=")[0] + "DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;\n"
            if not line.endswith(";\n"):
                line = line.strip() + ";\n"

        # Detect start of data dumping
        if any(f"Dumping data for table {t}" in line for t in tables_to_clean):
            skip = True
        
        # Detect end of data dumping (next table or end of file)
        if skip and line.startswith("-- Table structure for table"):
            skip = False
        
        if not skip:
            new_lines.append(line)
            
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    clean_sql(os.path.join(backend_dir, "database", "core_template.sql"))
