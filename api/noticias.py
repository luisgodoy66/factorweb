import requests
import json

class NoticieroFactoring:
    def __init__(self, news_api_key):
        self.news_api_key = news_api_key
        self.base_url = "https://newsdata.io/api/1/latest"

    def buscar_noticias_ecuador(self, empresa_query, ruc_empresa):
        """
        Busca noticias en fuentes ecuatorianas sobre una empresa específica.
        """
        params = {
            'apikey': self.news_api_key,
            'country': 'ec',           # ISO Code para Ecuador
            'language': 'es',
            'removeduplicate': '1',
            'category': 'business,top,breaking,politics,technology'
            # 'q': f'"{empresa_query}" , "{ruc_empresa}"', # Comillas para búsqueda exacta
            # 'prioritydomain': 'top',
            # 'sort': 'relevancy',

        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return self._formatear_resultados(data.get('results', []))
        
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return []

    def _formatear_resultados(self, resultados):
        noticias_limpias = []
        for art in resultados:
            noticias_limpias.append({
                'titular': art.get('title'),
                'fuente': art.get('source_id'),
                'fecha': art.get('pubDate'),
                'link': art.get('link'),
                'contenido': art.get('description') or art.get('content'),
                'id': art.get('article_id'),
                'url_imagen': art.get('image_url'),
                'icono_fuente': art.get('source_icon'),
            })
        return noticias_limpias

def generar_prompt_riesgo(empresa, lista_noticias):
    noticias_texto = "\n".join([f"- {n['titular']}: {n['contenido']}" for n in lista_noticias])
    
    prompt = f"""
    Eres un experto en gestión de riesgos de factoring en Ecuador.
    Analiza las siguientes noticias sobre la empresa "{empresa}":
    
    {noticias_texto}
    
    TAREA:
    1. Clasifica el riesgo de la operación de 1 (Seguro) a 10 (Crítico).
    2. Identifica si hay menciones a: Leyes, Deudas, Huelgas o Intervenciones Estatales.
    3. Responde estrictamente en formato JSON con las llaves: 'score', 'resumen_critico', 'banderas_rojas'.
    """
    return prompt

# --- EJEMPLO DE USO ---

API_KEY_NOTICIAS = "pub_781334009b194ecaa1b83135b87756ad"
monitor = NoticieroFactoring(API_KEY_NOTICIAS)

# Supongamos que un cliente quiere negociar una factura de "Corporación Favorita"
# (Usa nombres específicos para evitar falsos positivos)
deudor = "Corporación Favorita"
ruc_deudor = "0993379806001"
noticias_encontradas = monitor.buscar_noticias_ecuador(deudor, ruc_deudor)

if noticias_encontradas:
    print(f"--- Alertas encontradas para {deudor} ---")
    for idx, noticia in enumerate(noticias_encontradas, 1):
        print(f"{idx}. {noticia['titular']} (Fuente: {noticia['fuente']}) Link: {noticia['link']}")
else:
    print(f"No se encontraron alertas recientes para {deudor}.")

# {"status":"success","totalResults":1
#  ,"results":[{"article_id":"3e3887cae4e453e95e2db6a9f29e434c"
#               ,"link":"https://eluniverso.com/noticias/economia/byd-ecuador-taxis-crecimiento-ventas-nuevos-modelos-nota/"
#                 ,"title":"BYD acelera en Ecuador y entra en el transporte comercial con un modelo para taxis"
#                 ,"description":"Primer lote de 150 unidades. A nivel general, Andor Corp., que comercializa carros de esta marca china, busca pasar de 2.916 a 7.000 unidades vendidas."
#                 ,"content":"SOLO DISPONIBLE EN PLANES DE PAGO"
#                 ,"keywords":["china","ecuador","transporte","vehículos","automóviles","no_premium"]
#                 ,"creator":["vanessa silva cruz"],"language":"spanish","country":["ecuador"]
#                 ,"category":["business"],"datatype":"news","pubDate":"2026-03-31 15:00:00","pubDateTZ":"UTC"
#                 ,"fetched_at":"2026-03-31 15:06:44"
#                   ,"image_url":"https://eluniverso.com/resizer/9rypkWjzrtP04OiMbT9xdIth4Is=/cloudfront-us-east-1.images.arcpublishing.com/eluniverso/HY3SLAYLWFAM3AUNZEFHYEFAGA.jpg"
#                 ,"video_url":null,"source_id":"eluniverso","source_name":"Eluniverso","source_priority":31547
#                 ,"source_url":"https://www.eluniverso.com","source_icon":"https://n.bytvi.com/eluniverso.png"
#                 ,"sentiment":"SOLO DISPONIBLE EN PLANES PROFESIONALES Y CORPORATIVOS"
#                 ,"sentiment_stats":"SOLO DISPONIBLE EN PLANES PROFESIONALES Y CORPORATIVOS"
#                 ,"ai_tag":"SOLO DISPONIBLE EN PLANES PROFESIONALES Y CORPORATIVOS"
#                 ,"ai_region":"SOLO DISPONIBLE EN PLANES CORPORATIVOS","ai_org":"SOLO DISPONIBLE EN PLANES CORPORATIVOS"
#                 ,"ai_summary":"SOLO DISPONIBLE EN PLANES DE PAGO","duplicate":false}],"nextPage":null}