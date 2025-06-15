import os
import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import socket
import subprocess
from ipwhois import IPWhois
from pathlib import Path
from playwright.sync_api import sync_playwright
import tldextract

FILE_EXTENSIONS = {
    "html": [".html", ".htm"],
    "php": [".php"],
    "css": [".css"],
    "js": [".js"],
    "images": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
    "video": [".mp4", ".webm"],
    "audio": [".mp3", ".ogg"],
    "sql": [".sql"]
}

COMMON_INDEX_DIRS = [
    "/", "/backup/", "/files/", "/logs/", "/uploads/", 
    "/data/", "/web/", "/webdav/", "/ftp/", "/pub/",
    "/wp-content/uploads/", "/wp-content/uploads/branding/"
]

GOOGLE_DORKS = [
    ("2024-08-23", "site:github.com \"BEGIN OPENSSH PRIVATE KEY\"", "Files Containing Passwords", "kstrawn0"),
    ("2024-07-04", "intitle:\"SSL Network Extender Login\" -checkpoint.com", "Vulnerable Servers", "Everton Hydd3n"),
    ("2024-05-13", "\"START test_database\" ext:log", "Files Containing Usernames", "Nadir Boulacheb (RubX)"),
    ("2024-05-01", "intitle:\"GlobalProtect Portal\"", "Files Containing Juicy Info", "Javier Bernardo"),
    ("2024-04-19", "inurl:pastebin intitle:mastercard", "Files Containing Juicy Info", "Soriful Islam")
]

def get_ip_info(domain):
    ip = socket.gethostbyname(domain)
    whois = IPWhois(ip)
    info = whois.lookup_rdap()
    return {
        "ip": ip,
        "range": info.get('network', {}).get('cidr', 'N/A'),
        "organization": info.get('network', {}).get('name', 'Desconocido'),
        "description": info.get('network', {}).get('remarks', [''])[0] if info.get('network', {}).get('remarks') else 'N/A',
        "country": info.get('network', {}).get('country', 'Desconocido'),
        "asn_type": info.get('asn_description', 'N/A'),
        "location_link": f"https://ipinfo.io/{ip}",
        "is_static": "Indeterminado (consultar proveedor)"
    }

def get_server_info(url):
    headers = requests.get(url, timeout=10).headers
    return {
        "server": headers.get("Server", "No identificado"),
        "powered_by": headers.get("X-Powered-By", "No informado")
    }

def run_whatweb(url):
    try:
        result = subprocess.check_output(["whatweb", url], text=True)
        return result.strip()
    except Exception as e:
        return f"Error al ejecutar WhatWeb: {e}"

def apply_google_dorks(domain):
    print("\n🔍 Aplicando Google Dorks a la URL proporcionada...")
    for date, query, category, author in GOOGLE_DORKS:
        search_query = query.replace("site:", f"site:{domain}")
        search_url = f"https://www.google.com/search?q={search_query}"
        print(f"\n[Google Dork] {date}: {search_query}")
        print(f"    Resultado: {search_url}")

def fetch_js_rendered_links(url):
    links = set()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle")
            anchors = page.query_selector_all("a")
            for a in anchors:
                href = a.get_attribute("href")
                if href:
                    links.add(urljoin(url, href))
        except Exception:
            pass
        browser.close()
    return links

def crawl_site(url):
    resources = {k: [] for k in FILE_EXTENSIONS}
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.find_all(["a", "link", "script", "img", "source", "audio", "video"]):
            attr = tag.get("href") or tag.get("src")
            if attr:
                full_url = urljoin(url, attr)
                for key, exts in FILE_EXTENSIONS.items():
                    if any(full_url.lower().endswith(ext) for ext in exts):
                        resources[key].append(full_url)
    except Exception as e:
        print(f"Error al rastrear el sitio: {e}")
    return resources

def print_folder_tree(resources):
    print("\n📂 Diagrama de estructura del sitio:")
    for category, links in resources.items():
        print(f"\n📁 {category.upper()} ({len(links)} archivos)")
        for url in sorted(set(links)):
            print(f"  └── {url}")

def enumerate_subdomains(domain):
    print("\n🌐 Subdominios encontrados mediante Certificate Transparency Logs (crt.sh):")
    try:
        response = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            subdomains = sorted({entry["name_value"] for entry in data})
            for sub in subdomains:
                print(f"  └── {sub}")
        else:
            print("  ❌ No se pudo obtener subdominios.")
    except Exception as e:
        print(f"  ⚠️ Error al consultar subdominios: {e}")

def run_dnstwist(domain):
    print("\n🔎 Ejecutando dnstwist para obtener posibles subdominios...")
    try:
        result = subprocess.check_output(["dnstwist", domain], text=True)
        print(result)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar dnstwist: {e}")

def check_index_of(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        title_text = soup.title.string if soup.title else ""
        found_index_of = "Index of" in title_text or "Index of" in response.text

        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and not href.startswith("?") and href not in ("../", "/", "#"):
                full_url = urljoin(url, href)
                links.append(full_url)

        if found_index_of or (len(links) >= 5 and "<pre>" in response.text):
            print(f"\n📂 Index of detectado en: {url}")
            for file_url in sorted(set(links)):
                print(f"  └── {file_url}")
            return True
    except Exception as e:
        print(f"  ⚠️ Error al verificar '{url}': {e}")
    return False

def extract_base_domain(domain):
    # Usamos tldextract para obtener dominio base sin subdominios
    ext = tldextract.extract(domain)
    return ext.domain

def search_common_index_dirs(base_url):
    print("\n📁 Obteniendo posibles directorios 'Index of'...")
    parsed = urlparse(base_url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    base_domain = extract_base_domain(parsed.netloc)
    for path in COMMON_INDEX_DIRS:
        test_url = urljoin(domain, path)
        check_index_of(test_url)
    
    # Mostrar búsqueda rápida con Google Dork usando sólo el nombre base del dominio
    dork_query = f'intitle:"index of" /{base_domain}'
    dork_url = f"https://www.google.com/search?q={requests.utils.quote(dork_query)}"
    print("\n🔎 Búsqueda rápida de Google Dork para 'Index of':")
    print(f"  {dork_query}")
    print(f"  {dork_url}")

def main():
    start_url = input("Introduce la URL del sitio: ").strip()
    if not start_url.startswith(("http://", "https://")):
        start_url = "https://" + start_url

    parsed = urlparse(start_url)
    domain = parsed.netloc or parsed.path

    print("\n🔍 Obteniendo información de red...")
    ip_info = get_ip_info(domain)
    for k, v in ip_info.items():
        print(f"{k.capitalize()}: {v}")

    print("\n🛰️ Información del servidor...")
    server_info = get_server_info(start_url)
    for k, v in server_info.items():
        print(f"{k.capitalize()}: {v}")

    print("\n🔎 Tecnologías detectadas por WhatWeb...")
    print(run_whatweb(start_url))

    apply_google_dorks(domain)

    enumerate_subdomains(domain)

    print("\n⛏️ CRAWLING del sitio...")
    resources = crawl_site(start_url)
    print_folder_tree(resources)

    print("\n📁 Buscando directorios 'Index of'...")
    search_common_index_dirs(start_url)

    print("\n🔍 Ejecutando dnstwist...")
    run_dnstwist(domain)

    print("\n✅ Análisis completo.")

if __name__ == "__main__":
    main()
