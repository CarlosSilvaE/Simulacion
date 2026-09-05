import math
import tkinter as tk
from tkinter import ttk

from DB import conectar_edificios


class MedirDistancia:
    def __init__(self, root):
        self.root = root
        self.root.title("Medición de Distancias")
        self.root.geometry("1200x600")

        self.lbl_title = tk.Label(
            self.root,
            text="Análisis de edificios escolares y colonias",
            font=("Helvetica", 16, "bold")
        )
        self.lbl_title.pack(pady=10)

        self.lbl_stats = tk.Label(
            self.root,
            text="Edificios revisados: 0 | Distancias calculadas: 0",
            font=("Helvetica", 12, "bold")
        )
        self.lbl_stats.pack()

        self.lbl_subtitle = tk.Label(
            self.root,
            text="Edificios encontrados a 10 km o más de su código postal",
            font=("Helvetica", 12)
        )
        self.lbl_subtitle.pack(pady=10)

        self.lbl_count = tk.Label(
            self.root,
            text="Edificios a 10 km o más: 0",
            font=("Helvetica", 20, "bold")
        )
        self.lbl_count.pack()

        self.crear_tabla()

        self.cargar_datos()


    def crear_tabla(self):
        columnas = (
            "cct",
            "nombre",
            "codigo_postal",
            "lat_edificio",
            "lon_edificio",
            "lat_cp",
            "lon_cp",
            "distancia"
        )

        self.tabla = ttk.Treeview(
            self.root,
            columns=columnas,
            show="headings"
        )

        self.tabla.heading("cct", text="CCT")
        self.tabla.heading("nombre", text="Edificio")
        self.tabla.heading("codigo_postal", text="CP")
        self.tabla.heading("lat_edificio", text="Lat. Edificio")
        self.tabla.heading("lon_edificio", text="Lon. Edificio")
        self.tabla.heading("lat_cp", text="Lat. CP")
        self.tabla.heading("lon_cp", text="Lon. CP")
        self.tabla.heading("distancia", text="Distancia (km)")

        self.tabla.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )


    def haversine(self, lat1, lon1, lat2, lon2):
        r = 6371

        diferencia_lat = math.radians(lat2 - lat1)
        diferencia_lon = math.radians(lon2 - lon1)

        h = (
            math.sin(diferencia_lat / 2) ** 2
            +
            math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(diferencia_lon / 2) ** 2
        )
        h = max(0, min(1, h))

        c = 2 * math.atan2(
            math.sqrt(h),
            math.sqrt(1 - h)
        )

        return r * c


    def coordenadas_validas(self, lat, lon):
        try:
            lat = float(lat)
            lon = float(lon)

            if not (-90 <= lat <= 90):
                return None

            if not (-180 <= lon <= 180):
                return None

            return lat, lon

        except (ValueError, TypeError):
            return None


    def codigo_postal_valido(self, codigo_postal):
        if codigo_postal is None:
            return False

        cp = str(codigo_postal).strip()

        if cp == "":
            return False

        if cp == "00000":
            return False

        try:
            return int(cp) != 0
        except ValueError:
            return True


    def cargar_datos(self):
        conn = conectar_edificios()
        cursor = conn.cursor()

        consulta = """
            SELECT
                e.cct,
                e.nombre,
                e.codigo_postal,
                e.latitud,
                e.longitud,
                c.lat,
                c.lon
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
            ;
        """

        cursor.execute(consulta)
        registros = cursor.fetchall()
        distancias_calculadas = 0

        for registro in registros:

            cct = registro[0]
            nombre = registro[1]
            codigo_postal = registro[2]

            if not self.codigo_postal_valido(codigo_postal):
                continue

            coordenada_edificio = self.coordenadas_validas(
                registro[3],
                registro[4]
            )

            coordenada_cp = self.coordenadas_validas(
                registro[5],
                registro[6]
            )

            # Si alguna coordenada es inválida, no se procesa
            if coordenada_edificio is None or coordenada_cp is None:
                continue

            lat_edificio, lon_edificio = coordenada_edificio
            lat_cp, lon_cp = coordenada_cp

            distancia = self.haversine(
                lat_edificio,
                lon_edificio,
                lat_cp,
                lon_cp
            )
            distancias_calculadas += 1

            if distancia >= 10:
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        cct,
                        nombre,
                        codigo_postal,
                        lat_edificio,
                        lon_edificio,
                        lat_cp,
                        lon_cp,
                        f"{distancia:.2f}"
                    )
                )

        self.lbl_stats.config(
            text=f"Edificios revisados: {len(registros)} | Distancias calculadas: {distancias_calculadas}"
        )
        self.lbl_count.config(
            text=f"Edificios a 10 km o más: {len(self.tabla.get_children())}"
        )

        cursor.close()
        conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = MedirDistancia(root)
    root.mainloop()