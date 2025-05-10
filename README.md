pip3 install requests beautifulsoup4 ipwhois playwright
sudo apt-get install whatweb
pip3 install whatweb
pip3 install dnstwist
sudo apt-get install dnstwist
pip3 install dnstwist
python -m playwright install

Funciones del Código
Obtener información de red (IPWhois) (get_ip_info):

Dada una URL, el código obtiene la dirección IP del dominio correspondiente.

Luego, consulta la información WHOIS de la IP para obtener detalles sobre la organización, la ubicación geográfica, el rango de IPs, y más.

Esta información se devuelve en un formato organizado.

Obtener información del servidor (get_server_info):

Realiza una solicitud HTTP para obtener los encabezados de la respuesta del servidor web.

Extrae los encabezados Server y X-Powered-By para identificar qué tipo de servidor web se está utilizando (por ejemplo, Apache, Nginx, etc.) y la tecnología que lo respalda (como PHP).

Ejecutar WhatWeb (run_whatweb):

WhatWeb es una herramienta externa que detecta tecnologías web utilizadas en un sitio (como frameworks, CMS, servidores, etc.).

El programa ejecuta WhatWeb en la URL proporcionada y muestra los resultados sobre las tecnologías detectadas.

Aplicar Google Dorks (apply_google_dorks):

Realiza búsquedas en Google utilizando una lista de Google Dorks predefinidos. Estos son operadores de búsqueda avanzados que pueden ayudar a encontrar información específica y potencialmente sensible en sitios web (como contraseñas o datos privados).

Los resultados son mostrados como URLs de búsqueda en Google.

Enumerar subdominios (enumerate_subdomains):

Utiliza los logs de Transparencia de Certificados de Google (crt.sh) para encontrar subdominios asociados con el dominio principal.

Los subdominios encontrados son listados.

Ejecutar dnstwist (run_dnstwist):

dnstwist es una herramienta que genera posibles variaciones de un dominio (como errores tipográficos o dominios maliciosos) para ayudar a identificar subdominios adicionales.

El programa ejecuta dnstwist para obtener variaciones del dominio y las muestra.

Rastreo del sitio web (crawl_site):

Hace una solicitud HTTP al sitio y analiza el contenido HTML.

Extrae los enlaces de recursos (archivos, imágenes, scripts, etc.) dentro de las categorías definidas (por ejemplo, imágenes, scripts, CSS, etc.).

Organiza estos recursos por tipo de archivo y los muestra.

Imprimir estructura de carpetas (print_folder_tree):

Imprime una estructura tipo árbol de los archivos encontrados en el rastreo, agrupados por su tipo (HTML, CSS, imágenes, videos, etc.).

Obtener enlaces renderizados con JavaScript (fetch_js_rendered_links):

Utiliza Playwright para abrir el sitio web en un navegador real (Chromium) y ejecutar JavaScript para cargar contenido dinámico.

Extrae los enlaces de la página renderizada y los devuelve.
