import re
import io
import pdfplumber

class RUTParsingService:
    @staticmethod
    def extract_text_from_pdf(pdf_bytes):
        """Extracts text by grouping words into lines based on their vertical position."""
        try:
            text_lines = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    words = page.extract_words()
                    if not words: continue
                    
                    # Group words by "top" with a small tolerance
                    # Sort words by top then x0
                    words.sort(key=lambda w: (w['top'], w['x0']))
                    
                    if not words: continue
                    
                    current_line = []
                    last_top = words[0]['top']
                    tolerance = 3 # pixels
                    
                    for w in words:
                        if abs(w['top'] - last_top) > tolerance:
                            # New line
                            text_lines.append(" ".join([x['text'] for x in current_line]))
                            current_line = [w]
                            last_top = w['top']
                        else:
                            current_line.append(w)
                    
                    if current_line:
                        text_lines.append(" ".join([x['text'] for x in current_line]))
            
            return text_lines
        except Exception as e:
            raise ValueError(f"Error al leer el PDF del RUT: {str(e)}")

    def _clean_numeric(self, val):
        if not val: return None
        # Remove ALL non-digit characters
        return re.sub(r'\D', '', str(val))

    def _homologate_city(self, city):
        if not city: return None
        # Normalize: Remove dots, multiple spaces, and uppercase
        city = re.sub(r'\s+', ' ', city.replace('.', '')).strip().upper()
        
        # Homologation logic
        mapping = {
            "BOGOTA D C": "Bogotá",
            "BOGOTA DC": "Bogotá",
            "SANTAFE DE BOGOTA": "Bogotá",
            "BOGOTA": "Bogotá",
            "PEREIRA": "Pereira"
        }
        name = mapping.get(city, city.capitalize())
        # Remove any " D.C." or " D C" from name if not matched in dict
        name = re.sub(r'\s+d\.?c\.?$', '', name, flags=re.IGNORECASE)
        return name.strip()

    def _clean_text(self, text):
        if not text: return None
        # Remove trailing numeric codes common in RUT (e.g., "COLOMBIA 1 6 9" -> "COLOMBIA")
        # Match a space followed by digits at the end of the string
        text = re.sub(r'\s+\d+[\s\d]*$', '', text.strip())
        # Clean text-only fields from any residual single digits used for indexing
        text = re.sub(r'^\d\s+', '', text)
        return text.strip()

    def parse_rut(self, pdf_bytes):
        """Parses a RUT PDF using positional word analysis with label exclusion."""
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page = pdf.pages[0]
                words = page.extract_words()
        except Exception as e:
            raise ValueError(f"Error al leer el PDF del RUT: {str(e)}")

        data = {
            "rut_nit": None,
            "verification_digit": None,
            "legal_name": None,
            "commercial_name": None,
            "country_id": 1, 
            "department_name": None,
            "city_name": None,
            "address": {
                "address_line1": None,
                "label_id": 1 # Trabajo
            },
            "email": None,
            "phones": [],
            "economic_activity_code": None
        }

        # Define Ranges (Horizontal boundaries)
        RANGES = {
            "nit": (80, 185),
            "dv": (188, 202),
            "legal_name": (25, 580),
            "commercial_name": (25, 580),
            "country": (25, 180),
            "dept": (185, 385),
            "city": (390, 580),
            "address": (25, 580),
            "email": (100, 580),
            "phone1": (220, 395),
            "phone2": (400, 585),
            "ciiu": (25, 85)
        }

        # Find Anchor tops
        anchors = {}
        for w in words:
            txt = w['text'].strip()
            # Match strictly box numeric IDs (1_3 digits followed by dot)
            if re.match(r'^\d{1,3}\.$', txt):
                anchors[txt] = w['top']

        # Structural labels to exclude from DATA fields
        # Added Box IDs to stop words to prevent grabbing "31." as part of a name
        STOP_WORDS = {
            "IDENTIFICACIÓN", "UBICACIÓN", "CLASIFICACIÓN", "Razón", "social", "Nombre", 
            "comercial", "Sigla", "Primer", "apellido", "Segundo", "nombre", "Otros", 
            "nombres", "País", "Departamento", "Ciudad/Municipio", "Dirección", 
            "principal", "Correo", "electrónico", "Código", "postal", "Teléfono",
            "Telefono", "Tel.", "Tel", "Actividad", "económica", 
            "Ocupación", "Establecimiento", "DV"
        }

        def get_text_near(anchor_id, x_range, row_offset=11, tolerance=8):
            if anchor_id not in anchors: return None
            target_top = anchors[anchor_id] + row_offset
            relevant = [w for w in words if abs(w['top'] - target_top) < tolerance and x_range[0] <= w['x0'] <= x_range[1]]
            
            filtered = []
            for w in relevant:
                txt = w['text']
                # Skip words that are Box IDs themselves (e.g. "31.")
                if re.match(r'^\d{1,3}\.$', txt): continue
                # Skip words that match our structural labels EXACTLY to avoid stripping digits from data
                if any(sw.lower() == txt.lower() for sw in STOP_WORDS): continue
                filtered.append(w)
            
            # Fallback for some fields where labels and data might be on the same vertical offset
            if not filtered and row_offset != 0:
                return get_text_near(anchor_id, x_range, row_offset=0)
            
            if filtered:
                filtered.sort(key=lambda x: x['x0'])
                parts = [w['text'] for w in filtered]
                # Filter out pure digits from text-only fields (like city/dept) if they are just numerical codes
                if anchor_id in ["39.", "40."]:
                    parts = [p for p in parts if not p.isdigit()]
                return " ".join(parts).strip()
            return None

        # 5. NIT & 6. DV
        raw_nit = get_text_near("5.", RANGES["nit"], row_offset=12)
        if raw_nit: data["rut_nit"] = self._clean_numeric(raw_nit)
        
        raw_dv = get_text_near("6.", RANGES["dv"], row_offset=12)
        if raw_dv: data["verification_digit"] = self._clean_numeric(raw_dv)

        # 35. Razon Social (Prioritized for Companies)
        # Box 35 covers the name for S.A.S. and other entities
        data["legal_name"] = get_text_near("35.", RANGES["legal_name"], row_offset=10)
        
        # 36. Nombre Comercial
        data["commercial_name"] = get_text_near("36.", RANGES["commercial_name"], row_offset=10)

        # 38. Pais
        country_raw = get_text_near("38.", RANGES["country"], row_offset=10)
        if country_raw: data["country_name"] = self._clean_text(country_raw).upper()

        # 39. Depto
        dept_raw = get_text_near("39.", RANGES["dept"], row_offset=10)
        if dept_raw: data["department_name"] = self._clean_text(dept_raw).capitalize()
        
        # 40. Municipio
        city_raw = get_text_near("40.", RANGES["city"], row_offset=10)
        if city_raw: data["city_name"] = self._homologate_city(self._clean_text(city_raw))

        # 41. Direccion
        addr = get_text_near("41.", RANGES["address"], row_offset=10)
        if addr: data["address"]["address_line1"] = addr.upper()

        # 42. Correo
        data["email"] = get_text_near("42.", RANGES["email"], row_offset=0)

        # 44, 45 Phones (with Label 1: Trabajo)
        def clean_phone(p_raw):
            if not p_raw: return None
            # Aggressive cleanup: remove indexing '1' and '2' if they are at the start
            digits = re.sub(r'\D', '', str(p_raw))
            if digits:
                # Discard single digits
                if len(digits) < 3: return None
                # If starts with 1 or 2 and length is 8 or 11, strip it
                if digits[0] in ['1', '2'] and len(digits) in [8, 11]:
                    return digits[1:]
                return digits
            return None

        p1 = get_text_near("44.", RANGES["phone1"], row_offset=0)
        p1_val = clean_phone(p1)
        if p1_val: data["phones"].append({"local_number": p1_val, "label_id": 1})
        
        p2 = get_text_near("45.", RANGES["phone2"], row_offset=0)
        p2_val = clean_phone(p2)
        if p2_val: data["phones"].append({"local_number": p2_val, "label_id": 1})

        # 46. Economic Activity (CIIU)
        ciiu = get_text_near("46.", RANGES["ciiu"], row_offset=14)
        if ciiu: 
            # Extract first 4 digits as per user requirement
            data["economic_activity_code"] = self._clean_numeric(ciiu)[:4]

        return data
