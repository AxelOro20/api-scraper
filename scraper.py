"""
scraper.py  ─  Lógica de scraping con Playwright
"""

import re
from playwright.sync_api import sync_playwright


TIENDAS_CONFIG = {
    "Mercado Libre": {
        "url":              lambda p: f"https://listado.mercadolibre.com.mx/{p.replace(' ', '%20')}",
        "selector_tarjeta": "div.poly-card, div.ui-search-result__wrapper",
        "selector_titulo":  "h2, a.poly-component__title",
        "selector_precio":  "span.andes-money-amount__fraction",
        "selector_espera":  "div.poly-card",
        "pausa_extra":      0,
    },
    "Amazon": {
        "url":              lambda p: f"https://www.amazon.com.mx/s?k={p.replace(' ', '+')}",
        "selector_tarjeta": 'div[data-component-type="s-search-result"]',
        "selector_titulo":  "h2 span",
        "selector_precio":  "span.a-price > span.a-offscreen",
        "selector_espera":  'div[data-component-type="s-search-result"]',
        "pausa_extra":      0,
    },
    "AliExpress": {
        "url":              lambda p: f"https://es.aliexpress.com/w/wholesale-{p.replace(' ', '-')}.html",
        "selector_tarjeta": '[class*="SearchResults"] [class*="item"], a[class*="search-card-item"]',
        "selector_titulo":  '[class*="title--"]',
        "selector_precio":  '[class*="price--"]',
        "selector_espera":  '[class*="title--"]',
        "pausa_extra":      8000,
    },
    "Shein": {
        "url":              lambda p: f"https://www.shein.com.mx/pdsearch/{p.replace(' ', '%20')}/",
        "selector_tarjeta": '[class*="product-card"], section[class*="product-item"]',
        "selector_titulo":  '[class*="goods-title-link"], [class*="title-inside"]',
        "selector_precio":  '[class*="normal-price-ctn"], [class*="sale-price"]',
        "selector_espera":  '[class*="product-card"]',
        "pausa_extra":      30000,
    },
    "Temu": {
        "url":              lambda p: f"https://www.temu.com/mx/search_result.html?search_key={p.replace(' ', '%20')}",
        "selector_tarjeta": '[class*="goods-item"], [data-testid="goods-item"]',
        "selector_titulo":  '[class*="goods-title"], [class*="item-title"]',
        "selector_precio":  '[class*="price-text"], [class*="sale-price"]',
        "selector_espera":  '[class*="goods-item"]',
        "pausa_extra":      30000,
    },
}


def limpiar_precio(texto: str):
    """Extrae el número de un texto de precio."""
    if not texto or texto == "N/A":
        return None
    limpio = re.sub(r"[^\d.]", "", texto.replace(",", ""))
    try:
        return float(limpio)
    except ValueError:
        return None


def scroll_y_esperar(page, veces=5, pausa_ms=1200):
    for _ in range(veces):
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        page.wait_for_timeout(pausa_ms)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)


def hacer_scraping(producto: str, tienda: str) -> tuple[str, list[dict]]:
    """
    Ejecuta el scraping para un producto y tienda.
    Retorna (url, lista_de_productos).
    """
    if tienda not in TIENDAS_CONFIG:
        raise ValueError(f"Tienda '{tienda}' no soportada. Opciones: {list(TIENDAS_CONFIG.keys())}")

    cfg = TIENDAS_CONFIG[tienda]
    url = cfg["url"](producto)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # headless=True para API (sin ventana)
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="es-MX",
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = context.new_page()
        page.goto(url, timeout=60000)

        if cfg["pausa_extra"] > 0:
            page.wait_for_timeout(4000 + cfg["pausa_extra"])

        if cfg["selector_espera"]:
            try:
                page.wait_for_selector(cfg["selector_espera"], timeout=20000)
            except Exception:
                pass

        scroll_y_esperar(page)

        productos = []
        tarjetas = page.locator(cfg["selector_tarjeta"]).all()

        for tarjeta in tarjetas:
            title_loc = tarjeta.locator(cfg["selector_titulo"]).first
            title = title_loc.inner_text() if title_loc.count() > 0 else "N/A"

            price_loc = tarjeta.locator(cfg["selector_precio"]).first
            price_txt = price_loc.inner_text() if price_loc.count() > 0 else "N/A"

            if title != "N/A" and title.strip():
                productos.append({
                    "tienda":       tienda,
                    "titulo":       title.strip(),
                    "precio_texto": price_txt.strip(),
                    "precio":       limpiar_precio(price_txt.strip()),
                })

        browser.close()
        return url, productos