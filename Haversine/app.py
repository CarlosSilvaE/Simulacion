import math

from flask import Flask, jsonify, render_template

from DB import conectar_edificios

app = Flask(__name__)


def haversine(lat1, lon1, lat2, lon2):
    radio = 6371
    diferencia_lat = math.radians(lat2 - lat1)
    diferencia_lon = math.radians(lon2 - lon1)

    h = (
        math.sin(diferencia_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(diferencia_lon / 2) ** 2
    )
    h = max(0, min(1, h))

    c = 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))
    return radio * c


def coordenadas_validas(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)

        if not (-90 <= lat <= 90):
            return None
        if not (-180 <= lon <= 180):
            return None

        return lat, lon
    except (TypeError, ValueError):
        return None


def codigo_postal_valido(codigo_postal):
    if codigo_postal is None:
        return False

    cp = str(codigo_postal).strip()
    if cp == "" or cp == "00000":
        return False

    try:
        return int(cp) != 0
    except ValueError:
        return True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/edificios")
def api_edificios():
    conn = conectar_edificios()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            e.cct,
            e.nombre,
            e.codigo_postal,
            e.latitud,
            e.longitud,
            c.lat AS lat_cp,
            c.lon AS lon_cp
        FROM edificios_escolares.edificios_escolares AS e
        LEFT JOIN (
            SELECT DISTINCT
                cve_codpost,
                lat,
                lon
            FROM cat_colonias.cat_colonias
            WHERE
                cve_codpost IS NOT NULL
                AND TRIM(cve_codpost) <> ''
                AND TRIM(cve_codpost) <> '00000'
                AND lat IS NOT NULL
                AND lon IS NOT NULL
                AND TRIM(lat) <> ''
                AND TRIM(lon) <> ''
        ) AS c
            ON e.codigo_postal = c.cve_codpost
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    resultados = []
    for row in rows:
        if not codigo_postal_valido(row.get("codigo_postal")):
            continue

        coordenada_edificio = coordenadas_validas(row.get("latitud"), row.get("longitud"))
        coordenada_cp = coordenadas_validas(row.get("lat_cp"), row.get("lon_cp"))

        if coordenada_edificio is None or coordenada_cp is None:
            continue

        lat_edificio, lon_edificio = coordenada_edificio
        lat_cp, lon_cp = coordenada_cp

        distancia = haversine(lat_edificio, lon_edificio, lat_cp, lon_cp)
        if distancia < 10:
            continue

        resultados.append(
            {
                "cct": row.get("cct"),
                "nombre": row.get("nombre"),
                "codigo_postal": row.get("codigo_postal"),
                "edificio_lat": round(lat_edificio, 7),
                "edificio_lon": round(lon_edificio, 7),
                "cp_lat": round(lat_cp, 7),
                "cp_lon": round(lon_cp, 7),
                "distancia_km": round(distancia, 2),
                "google_maps": (
                    f"https://www.google.com/maps/dir/?api=1&origin={lat_edificio},{lon_edificio}"
                    f"&destination={lat_cp},{lon_cp}"
                ),
            }
        )

    resultados.sort(key=lambda item: item["distancia_km"], reverse=True)
    cursor.close()
    conn.close()

    return jsonify({"count": len(resultados), "results": resultados})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
