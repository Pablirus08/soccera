"""Prueba rápida de conexión a Sofascore."""

import httpx

from soccera.ingestion.providers.costa_rica.client import SofascoreClient, SofascoreError

PATH = "/unique-tournament/11535/seasons"


def probar_http_simple():
    print("1) HTTP simple (httpx) a la portada...")
    try:
        r = httpx.get("https://www.sofascore.com/", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        print(f"   Status: {r.status_code} (403 aquí es normal: bloquean por huella TLS)")
    except Exception as e:
        print(f"   Error: {e}")


def probar_cliente():
    print("\n2) Cliente del proyecto (curl_cffi imitando Chrome)...")
    client = SofascoreClient()
    try:
        temporadas = client.get(PATH).get("seasons", [])
        print(f"   OK: {len(temporadas)} temporadas recibidas")
        for s in temporadas[:3]:
            print(f"     - {s['name']} ({s['year']})")
    except SofascoreError as e:
        print(f"   BLOQUEADO: {e}  -> si persiste, probablemente sea bloqueo de IP")
    finally:
        client.close()


if __name__ == "__main__":
    probar_http_simple()
    probar_cliente()
