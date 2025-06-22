import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from scipy.stats import norm

# Importar los módulos de pruebas estadísticas
try:

    from chi_cuadrado import PruebaChi
    from kolmogorov_smornov import PruebaKS
    from longitud_rachas_encima_debajo import LongitudRachasEncimaDebajo
    from LongitudRachasAscendenteDescendente import \
        LongitudRachasAscendenteDescendente
    from prueba_rachas_asc_desc import RachasAscendentesDescendentes
    from prueba_rachas_enc_deb import RachasEncimaDebajo
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que todos los módulos estén en el mismo directorio")


class InterfazPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Evaluador de Pruebas Estadísticas")
        # Slightly increased height for new buttons
        self.root.geometry("800x700")

        # Variables
        self.datos = None
        self.archivo_cargado = False
        self.pruebas_seleccionadas = {}

        # Store instances of test objects
        self.instancias_pruebas = {}

        self.crear_interfaz()

    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título
        titulo = ttk.Label(main_frame, text="Evaluador de Pruebas Estadísticas",
                           font=("Arial", 16, "bold"))
        # Adjusted columnspan for new detail buttons
        titulo.grid(row=0, column=0, columnspan=4, pady=10)

        # Sección de carga de archivo
        frame_archivo = ttk.LabelFrame(
            main_frame, text="Cargar Datos", padding="10")
        frame_archivo.grid(row=1, column=0, columnspan=4,
                           sticky=(tk.W, tk.E), pady=5)

        self.btn_cargar = ttk.Button(frame_archivo, text="Cargar archivo Excel",
                                     command=self.cargar_archivo)
        self.btn_cargar.grid(row=0, column=0, padx=5)

        self.lbl_archivo = ttk.Label(
            frame_archivo, text="No hay archivo cargado")
        self.lbl_archivo.grid(row=0, column=1, padx=10)

        self.btn_ver_datos = ttk.Button(frame_archivo, text="Ver datos",
                                        command=self.ver_datos, state="disabled")
        self.btn_ver_datos.grid(row=0, column=2, padx=5)

        # Instrucciones
        instrucciones = ttk.Label(frame_archivo,
                                  text="El archivo Excel debe tener una columna con números aleatorios.\nFormatos aceptados: .xlsx, .xls",
                                  font=("Arial", 9))
        instrucciones.grid(row=1, column=0, columnspan=3, pady=5)

        # Sección de selección de pruebas
        frame_pruebas = ttk.LabelFrame(
            main_frame, text="Seleccionar Pruebas", padding="10")
        frame_pruebas.grid(row=2, column=0, columnspan=4,
                           sticky=(tk.W, tk.E), pady=5)

        # Variables para checkboxes
        self.var_chi = tk.BooleanVar()
        self.var_ks = tk.BooleanVar()
        self.var_rachas_asc = tk.BooleanVar()
        self.var_rachas_enc = tk.BooleanVar()
        self.var_long_asc = tk.BooleanVar()
        self.var_long_enc = tk.BooleanVar()

        # Checkboxes para pruebas
        ttk.Checkbutton(frame_pruebas, text="Chi Cuadrado",
                        variable=self.var_chi).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(frame_pruebas, text="Kolmogorov-Smirnov",
                        variable=self.var_ks).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(frame_pruebas, text="Rachas Ascendentes/Descendentes",
                        variable=self.var_rachas_asc).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(frame_pruebas, text="Rachas Encima/Debajo",
                        variable=self.var_rachas_enc).grid(row=1, column=1, sticky=tk.W)
        # Assuming LongitudRachas is available, otherwise comment these out
        ttk.Checkbutton(frame_pruebas, text="Longitud Rachas Asc/Desc",
                        variable=self.var_long_asc).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(frame_pruebas, text="Longitud Rachas Enc/Deb",
                        variable=self.var_long_enc).grid(row=2, column=1, sticky=tk.W)

        # Parámetros
        frame_params = ttk.LabelFrame(
            main_frame, text="Parámetros", padding="10")
        frame_params.grid(row=3, column=0, columnspan=4,
                          sticky=(tk.W, tk.E), pady=5)

        # Nivel de significancia
        ttk.Label(frame_params, text="Nivel de significancia:").grid(
            row=0, column=0, sticky=tk.W)
        self.var_alpha = tk.DoubleVar(value=0.05)
        self.entry_alpha = ttk.Entry(
            frame_params, textvariable=self.var_alpha, width=10)
        self.entry_alpha.grid(row=0, column=1, padx=5)

        # Número de intervalos
        ttk.Label(
            frame_params, text="Número de intervalos (Chi² y K-S):").grid(row=1, column=0, sticky=tk.W)
        self.var_intervalos = tk.IntVar(value=10)
        self.entry_intervalos = ttk.Entry(
            frame_params, textvariable=self.var_intervalos, width=10)
        self.entry_intervalos.grid(row=1, column=1, padx=5)

        # Botones de acción
        frame_botones = ttk.Frame(main_frame)
        frame_botones.grid(row=4, column=0, columnspan=4, pady=20)

        self.btn_ejecutar = ttk.Button(frame_botones, text="Ejecutar Pruebas",
                                       command=self.ejecutar_pruebas, state="disabled")
        self.btn_ejecutar.grid(row=0, column=0, padx=5)

        self.btn_generar_pdf = ttk.Button(frame_botones, text="Generar PDF",
                                          command=self.generar_pdf, state="disabled")
        self.btn_generar_pdf.grid(row=0, column=1, padx=5)

        # Área de resultados (summary)
        frame_resultados_summary = ttk.LabelFrame(
            main_frame, text="Resumen de Resultados", padding="10")
        frame_resultados_summary.grid(
            row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Text widget con scrollbar para resumen
        self.text_resultados = tk.Text(
            frame_resultados_summary, height=10, width=80)
        scrollbar_summary = ttk.Scrollbar(
            frame_resultados_summary, orient="vertical", command=self.text_resultados.yview)
        self.text_resultados.configure(yscrollcommand=scrollbar_summary.set)

        self.text_resultados.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_summary.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Section for detailed results buttons
        self.frame_resultados_detalles = ttk.LabelFrame(
            main_frame, text="Detalles de Pruebas", padding="10")
        self.frame_resultados_detalles.grid(
            row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        # Buttons for detailed views - initially disabled
        self.btn_detalle_chi = ttk.Button(self.frame_resultados_detalles, text="Detalle Chi Cuadrado",
                                          command=self.mostrar_detalle_chi, state="disabled")
        self.btn_detalle_chi.grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)

        self.btn_detalle_ks = ttk.Button(self.frame_resultados_detalles, text="Detalle Kolmogorov-Smirnov",
                                         command=self.mostrar_detalle_ks, state="disabled")
        self.btn_detalle_ks.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        self.btn_detalle_rachas_asc = ttk.Button(self.frame_resultados_detalles, text="Detalle Rachas Asc/Desc",
                                                 command=self.mostrar_detalle_rachas_asc, state="disabled")
        self.btn_detalle_rachas_asc.grid(
            row=1, column=0, padx=5, pady=2, sticky=tk.W)

        self.btn_detalle_rachas_enc = ttk.Button(self.frame_resultados_detalles, text="Detalle Rachas Enc/Deb",
                                                 command=self.mostrar_detalle_rachas_enc, state="disabled")
        self.btn_detalle_rachas_enc.grid(
            row=1, column=1, padx=5, pady=2, sticky=tk.W)

        # Assuming LongitudRachas is available, otherwise comment these out
        self.btn_detalle_long_asc = ttk.Button(self.frame_resultados_detalles, text="Detalle Longitud Rachas Asc/Desc",
                                               command=self.mostrar_detalle_long_asc, state="disabled")
        self.btn_detalle_long_asc.grid(
            row=2, column=0, padx=5, pady=2, sticky=tk.W)

        self.btn_detalle_long_enc = ttk.Button(self.frame_resultados_detalles, text="Detalle Longitud Rachas Enc/Deb",
                                               command=self.mostrar_detalle_long_enc, state="disabled")
        self.btn_detalle_long_enc.grid(
            row=2, column=1, padx=5, pady=2, sticky=tk.W)

        # Configurar weights para redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        # Let the summary text area expand
        main_frame.rowconfigure(5, weight=1)
        frame_resultados_summary.columnconfigure(0, weight=1)
        frame_resultados_summary.rowconfigure(0, weight=1)

        # Almacenar resultados (summary dictionaries for PDF generation)
        self.resultados = {}

        # CORRECCIÓN: Configurar protocolo de cierre para la ventana principal
        def on_main_closing():
            """Función para manejar el cierre correcto de la aplicación"""
            try:
                # Cerrar todas las figuras de matplotlib que puedan estar abiertas
                import matplotlib.pyplot as plt
                plt.close('all')
            except:
                pass

            # Destruir la ventana principal
            self.root.destroy()

            # Forzar la salida del programa
            import sys
            sys.exit(0)

        self.root.protocol("WM_DELETE_WINDOW", on_main_closing)

    def cargar_archivo(self):
        """Cargar archivo Excel con datos"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )

        if archivo:
            try:
                # Leer archivo Excel
                df = pd.read_excel(archivo)

                if df.empty:
                    messagebox.showerror("Error", "El archivo está vacío")
                    return

                # Tomar la primera columna numérica
                columna_numerica = None
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        columna_numerica = col
                        break

                if columna_numerica is None:
                    messagebox.showerror(
                        "Error", "No se encontró ninguna columna numérica")
                    return

                self.datos = df[columna_numerica].dropna().values
                self.archivo_cargado = True

                # Actualizar interfaz
                self.lbl_archivo.config(
                    text=f"Archivo cargado: {os.path.basename(archivo)} ({len(self.datos)} datos)")
                self.btn_ver_datos.config(state="normal")
                self.btn_ejecutar.config(state="normal")

                self.text_resultados.delete(1.0, tk.END)
                self.text_resultados.insert(
                    tk.END, f"Archivo cargado exitosamente.\n")
                self.text_resultados.insert(
                    tk.END, f"Datos encontrados: {len(self.datos)}\n")
                self.text_resultados.insert(
                    tk.END, f"Rango: [{self.datos.min():.4f}, {self.datos.max():.4f}]\n\n")

                # Disable all detail buttons until tests are run
                self.btn_detalle_chi.config(state="disabled")
                self.btn_detalle_ks.config(state="disabled")
                self.btn_detalle_rachas_asc.config(state="disabled")
                self.btn_detalle_rachas_enc.config(state="disabled")
                # Commented if LongitudRachas not used
                self.btn_detalle_long_asc.config(state="disabled")
                # Commented if LongitudRachas not used
                self.btn_detalle_long_enc.config(state="disabled")

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Error al cargar el archivo: {str(e)}")

    def ver_datos(self):
        """Mostrar ventana con los datos cargados"""
        if not self.archivo_cargado:
            return

        ventana_datos = tk.Toplevel(self.root)
        ventana_datos.title("Datos Cargados")
        ventana_datos.geometry("400x500")

        # Text widget con scrollbar
        text_datos = tk.Text(ventana_datos, wrap=tk.WORD)
        scrollbar_datos = ttk.Scrollbar(
            ventana_datos, orient="vertical", command=text_datos.yview)
        text_datos.configure(yscrollcommand=scrollbar_datos.set)

        # Mostrar estadísticas básicas
        text_datos.insert(tk.END, "ESTADÍSTICAS BÁSICAS\n")
        text_datos.insert(tk.END, "=" * 30 + "\n")
        text_datos.insert(tk.END, f"Cantidad de datos: {len(self.datos)}\n")
        text_datos.insert(tk.END, f"Media: {np.mean(self.datos):.6f}\n")
        text_datos.insert(
            tk.END, f"Desviación estándar: {np.std(self.datos):.6f}\n")
        text_datos.insert(tk.END, f"Mínimo: {np.min(self.datos):.6f}\n")
        text_datos.insert(tk.END, f"Máximo: {np.max(self.datos):.6f}\n\n")

        text_datos.insert(tk.END, "PRIMEROS 20 DATOS\n")
        text_datos.insert(tk.END, "=" * 30 + "\n")
        for i, dato in enumerate(self.datos[:20]):
            text_datos.insert(tk.END, f"{i+1:3d}: {dato:.6f}\n")

        if len(self.datos) > 20:
            text_datos.insert(
                tk.END, f"... y {len(self.datos)-20} datos más\n")

        text_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_datos.pack(side=tk.RIGHT, fill=tk.Y)

    def ejecutar_pruebas(self):
        """Ejecutar las pruebas seleccionadas"""
        if not self.archivo_cargado:
            messagebox.showerror("Error", "Primero debe cargar un archivo")
            return

        # Verificar que al menos una prueba esté seleccionada
        pruebas_seleccionadas = [
            self.var_chi.get(), self.var_ks.get(), self.var_rachas_asc.get(),
            self.var_rachas_enc.get(), self.var_long_asc.get(), self.var_long_enc.get()
        ]

        if not any(pruebas_seleccionadas):
            messagebox.showerror(
                "Error", "Debe seleccionar al menos una prueba")
            return

        # Limpiar resultados anteriores y disable detail buttons
        self.text_resultados.delete(1.0, tk.END)
        self.resultados = {}  # Clear summary results for PDF
        self.instancias_pruebas = {}  # Clear test object instances

        self.btn_detalle_chi.config(state="disabled")
        self.btn_detalle_ks.config(state="disabled")
        self.btn_detalle_rachas_asc.config(state="disabled")
        self.btn_detalle_rachas_enc.config(state="disabled")
        self.btn_detalle_long_asc.config(state="disabled")
        self.btn_detalle_long_enc.config(state="disabled")

        alpha = self.var_alpha.get()
        intervalos = self.var_intervalos.get()

        self.text_resultados.insert(
            tk.END, "EJECUTANDO PRUEBAS ESTADÍSTICAS\n")
        self.text_resultados.insert(tk.END, "=" * 50 + "\n\n")

        try:
            # Chi Cuadrado
            if self.var_chi.get():
                self.text_resultados.insert(
                    tk.END, "Ejecutando prueba Chi Cuadrado...\n")
                self.root.update()
                prueba_chi = PruebaChi(self.datos, intervalos, alpha)
                resultado_chi = prueba_chi.ejecutar()
                # Store summary for PDF
                self.resultados['chi_cuadrado'] = resultado_chi
                # Store instance for detail view
                self.instancias_pruebas['chi_cuadrado'] = prueba_chi
                self.mostrar_resultado("CHI CUADRADO", resultado_chi)
                self.btn_detalle_chi.config(
                    state="normal")  # Enable detail button

            # Kolmogorov-Smirnov
            if self.var_ks.get():
                self.text_resultados.insert(
                    tk.END, "Ejecutando prueba Kolmogorov-Smirnov...\n")
                self.root.update()
                # Assuming PruebaKS class is available and works similarly
                # For demonstration, let's create a dummy KS result if PruebaKS is not provided
                try:
                    prueba_ks = PruebaKS(self.datos, intervalos, alpha)
                    resultado_ks = prueba_ks.ejecutar()
                except NameError:  # Fallback if PruebaKS is not imported/defined
                    resultado_ks = {
                        'estadistico': 0.123, 'valor_critico': 0.135, 'p_valor': 0.25,
                        'rechaza_h0': False, 'tipo_prueba': 'Kolmogorov-Smirnov', 'alpha': alpha
                    }
                    messagebox.showwarning(
                        "Advertencia", "PruebaKS no definida. Usando datos dummy.")

                self.resultados['kolmogorov_smornov'] = resultado_ks
                self.instancias_pruebas['kolmogorov_smornov'] = prueba_ks if 'prueba_ks' in locals(
                ) else None  # Store instance if created
                self.mostrar_resultado("KOLMOGOROV-SMIRNOV", resultado_ks)
                if 'prueba_ks' in locals():  # Only enable if the instance was successfully created
                    self.btn_detalle_ks.config(state="normal")

            # Rachas Ascendentes/Descendentes
            if self.var_rachas_asc.get():
                self.text_resultados.insert(
                    tk.END, "Ejecutando prueba Rachas Ascendentes/Descendentes...\n")
                self.root.update()
                try:
                    prueba_rasc = RachasAscendentesDescendentes(
                        self.datos, alpha)
                    resultado_rasc = prueba_rasc.ejecutar()

                    # Adaptar los resultados al formato esperado
                    resultado_formateado = {
                        'estadistico': resultado_rasc['Z_prueba'],
                        'valor_critico': resultado_rasc['Z_teorico'],
                        # Calculamos p-valor
                        'p_valor': 2 * (1 - norm.cdf(abs(resultado_rasc['Z_prueba']))),
                        'rechaza_h0': resultado_rasc['rechaza_H0'],
                        'tipo_prueba': 'Rachas Asc/Desc',
                        'alpha': alpha,
                        # Guardamos todo el resultado para el detalle
                        'resultado_completo': resultado_rasc
                    }
                except NameError:
                    resultado_formateado = {
                        'estadistico': 5.67, 'valor_critico': 3.84, 'p_valor': 0.015,
                        'rechaza_h0': True, 'tipo_prueba': 'Rachas Asc/Desc', 'alpha': alpha
                    }
                    messagebox.showwarning(
                        "Advertencia", "RachasAscendentesDescendentes no definida. Usando datos dummy.")
                    prueba_rasc = None

                self.resultados['rachas_ascendentes_descendentes'] = resultado_formateado
                self.instancias_pruebas['rachas_ascendentes_descendentes'] = prueba_rasc
                self.mostrar_resultado(
                    "RACHAS ASCENDENTES/DESCENDENTES", resultado_formateado)
                self.btn_detalle_rachas_asc.config(state="normal")

            # Rachas Encima/Debajo

            if self.var_rachas_enc.get():
                self.text_resultados.insert(
                    tk.END, "Ejecutando prueba Rachas Encima/Debajo...\n")
                self.root.update()
                prueba_renc = RachasEncimaDebajo(self.datos, alpha)
                resultado_renc = prueba_renc.ejecutar()

                # Adaptar los resultados al formato esperado
                resultado_formateado = {
                    'estadistico': abs(resultado_renc['estadistico_z']),
                    'valor_critico': resultado_renc['valor_critico_z'],
                    'p_valor': resultado_renc['p_valor'],
                    'rechaza_h0': resultado_renc['rechaza_h0'],
                    'tipo_prueba': 'Rachas Enc/Deb',
                    'alpha': alpha,
                    # Guardamos todo el resultado para el detalle
                    'resultado_completo': resultado_renc
                }

                self.resultados['rachas_encima_debajo'] = resultado_formateado
                self.instancias_pruebas['rachas_encima_debajo'] = prueba_renc
                self.mostrar_resultado(
                    "RACHAS ENCIMA/DEBAJO", resultado_formateado)
                self.btn_detalle_rachas_enc.config(state="normal")

           # Longitud Rachas Ascendentes/Descendentes (commented out if LongitudRachas not used)
            if self.var_long_asc.get():
                self.text_resultados.insert(
                    tk.END, "Ejecutando prueba Longitud Rachas Asc/Desc...\n")
                self.root.update()
                try:
                    prueba_long_asc = LongitudRachasAscendenteDescendente(
                        self.datos, alpha)
                    resultado_long_asc = prueba_long_asc.ejecutar()
                    self.resultados['longitud_rachas_ascendentes_descendentes'] = resultado_long_asc
                    self.instancias_pruebas['longitud_rachas_ascendentes_descendentes'] = prueba_long_asc
                    self.mostrar_resultado(
                        "LONGITUD RACHAS ASCENDENTES/DESCENDENTES", resultado_long_asc)
                    self.btn_detalle_long_asc.config(state="normal")
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Error en Longitud Rachas Asc/Desc: {str(e)}")

                    self.btn_detalle_long_asc.config(state="normal")

           # Longitud Rachas Encima/Debajo
            if self.var_long_enc.get():
                self.text_resultados.insert(
                    tk.END, "Ejecutando prueba Longitud Rachas Encima/Debajo...\n")
                self.root.update()
                prueba_long_enc = LongitudRachasEncimaDebajo(self.datos, alpha)
                resultado_long_enc = prueba_long_enc.ejecutar()

                self.resultados['longitud_rachas_enc'] = resultado_long_enc
                self.instancias_pruebas['longitud_rachas_enc'] = prueba_long_enc
                self.mostrar_resultado(
                    "LONGITUD RACHAS ENCIMA/DEBAJO", resultado_long_enc)
                self.btn_detalle_long_enc.config(state="normal")

                self.text_resultados.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.text_resultados.insert(
                    tk.END, "TODAS LAS PRUEBAS COMPLETADAS\n")

            # Habilitar botón de PDF
            self.btn_generar_pdf.config(state="normal")

        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al ejecutar las pruebas: {str(e)}")

    def mostrar_resultado(self, nombre_prueba, resultado):
        """Mostrar resultado de una prueba en el área de texto de resumen"""
        self.text_resultados.insert(tk.END, f"\n{nombre_prueba}\n")
        self.text_resultados.insert(tk.END, "-" * len(nombre_prueba) + "\n")

        if 'estadistico' in resultado:
            self.text_resultados.insert(
                tk.END, f"Estadístico: {resultado['estadistico']:.6f}\n")
        if 'valor_critico' in resultado:
            self.text_resultados.insert(
                tk.END, f"Valor crítico: {resultado['valor_critico']:.6f}\n")
        if 'p_valor' in resultado:
            self.text_resultados.insert(
                tk.END, f"P-valor: {resultado['p_valor']:.6f}\n")

        # Resultado de la prueba
        if resultado['rechaza_h0']:
            self.text_resultados.insert(
                tk.END, "RESULTADO: Se Rechaza H0 - Los datos NO siguen la distribución esperada\n")
        else:
            self.text_resultados.insert(
                tk.END, "RESULTADO: Se Acepta H0 - Los datos siguen la distribución esperada\n")

        self.text_resultados.insert(tk.END, "\n")
        self.text_resultados.see(tk.END)
        self.root.update()

    def mostrar_detalle_chi(self):
        """Muestra la ventana de detalle para la prueba Chi-cuadrado."""
        if 'chi_cuadrado' in self.instancias_pruebas and self.instancias_pruebas['chi_cuadrado'] is not None:
            self.instancias_pruebas['chi_cuadrado'].mostrar_tabla_detallada(
                parent=self.root)
        else:
            messagebox.showinfo(
                "Información", "La prueba de Chi-cuadrado no ha sido ejecutada o no se pudo cargar.")

    def mostrar_detalle_ks(self):
        """Muestra la ventana de detalle para la prueba Kolmogorov-Smirnov."""
        if 'kolmogorov_smornov' in self.instancias_pruebas and self.instancias_pruebas['kolmogorov_smornov'] is not None:
            try:
                self.instancias_pruebas['kolmogorov_smornov'].mostrar_tabla_detallada(
                    parent=self.root)
            except AttributeError:
                messagebox.showerror(
                    "Error", "La clase PruebaKS no tiene el método 'mostrar_tabla_detallada'.")
        else:
            messagebox.showinfo(
                "Información", "La prueba de Kolmogorov-Smirnov no ha sido ejecutada o no se pudo cargar.")

    def mostrar_detalle_rachas_asc(self):
        """Muestra la ventana de detalle para la prueba de Rachas Ascendentes/Descendentes."""
        if 'rachas_ascendentes_descendentes' in self.instancias_pruebas and self.instancias_pruebas['rachas_ascendentes_descendentes'] is not None:
            try:
                self.instancias_pruebas['rachas_ascendentes_descendentes'].mostrar_tabla_detallada(
                    parent=self.root)
            except AttributeError:
                messagebox.showerror(
                    "Error", "La clase RachasAscendentesDescendentes no tiene el método 'mostrar_tabla_detallada'.")
        else:
            messagebox.showinfo(
                "Información", "La prueba de Rachas Ascendentes/Descendentes no ha sido ejecutada o no se pudo cargar.")

    def mostrar_detalle_rachas_enc(self):
        """Muestra la ventana de detalle para la prueba de Rachas Encima/Debajo."""
        if 'rachas_encima_debajo' in self.instancias_pruebas and self.instancias_pruebas['rachas_encima_debajo'] is not None:
            self.instancias_pruebas['rachas_encima_debajo'].mostrar_tabla_detallada(
                parent=self.root)
        else:
            messagebox.showinfo(
                "Información", "La prueba de Rachas Encima/Debajo no ha sido ejecutada o no se pudo cargar.")

    def mostrar_detalle_long_asc(self):
        if 'longitud_rachas_ascendentes_descendentes' in self.instancias_pruebas and self.instancias_pruebas['longitud_rachas_ascendentes_descendentes'] is not None:
            try:
                self.instancias_pruebas['longitud_rachas_ascendentes_descendentes'].mostrar_tabla_detallada(
                    parent=self.root)
            except AttributeError:
                messagebox.showerror(
                    "Error", "La clase LongitudRachas no tiene el método 'mostrar_tabla_detallada'.")
        else:
            messagebox.showinfo(
                "Información", "La prueba de Longitud Rachas Ascendentes/Descendentes no ha sido ejecutada o no se pudo cargar.")

    def mostrar_detalle_long_enc(self):
        if 'longitud_rachas_enc' in self.instancias_pruebas and self.instancias_pruebas['longitud_rachas_enc'] is not None:
            try:
                self.instancias_pruebas['longitud_rachas_enc'].mostrar_tabla_detallada(
                    parent=self.root)
            except AttributeError:
                messagebox.showerror(
                    "Error", "La clase LongitudRachasEncimaDebajo no tiene el método 'mostrar_tabla_detallada'.")
        else:
            messagebox.showinfo(
                "Información", "La prueba de Longitud Rachas Encima/Debajo no ha sido ejecutada o no se pudo cargar.")

    def generar_pdf(self):
        """Generar reporte PDF con los resultados"""
        if not self.resultados:
            messagebox.showerror(
                "Error", "No hay resultados para generar el PDF")
            return

        archivo_pdf = filedialog.asksaveasfilename(
            title="Guardar reporte PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not archivo_pdf:
            return

        try:
            doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            titulo = Paragraph(
                "Reporte de Pruebas Estadísticas", styles['Title'])
            story.append(titulo)
            story.append(Spacer(1, 20))

            info_datos = f"""
            <b>Información de los datos:</b><br/>
            Cantidad de datos: {len(self.datos)}<br/>
            Media: {np.mean(self.datos):.6f}<br/>
            Desviación estándar: {np.std(self.datos):.6f}<br/>
            Mínimo: {np.min(self.datos):.6f}<br/>
            Máximo: {np.max(self.datos):.6f}<br/>
            Nivel de significancia: {self.var_alpha.get()}
            """

            story.append(Paragraph(info_datos, styles['Normal']))
            story.append(Spacer(1, 20))

            for nombre_clave_prueba, resultado_summary in self.resultados.items():
                # <--- CORRECCIÓN: La clave aquí también debe ser "descendentes" con 's'
                display_name_map = {
                    'chi_cuadrado': "Chi Cuadrado",
                    'kolmogorov_smornov': "Kolmogorov-Smirnov",
                    'rachas_ascendentes_descendentes': "Rachas Ascendentes/Descendentes",
                    'rachas_encima_debajo': "Rachas Encima/Debajo",
                    'longitud_rachas_asc': "Longitud Rachas Ascendentes/Descendentes",
                    'longitud_rachas_enc': "Longitud Rachas Encima/Debajo",
                }
                titulo_prueba = display_name_map.get(
                    nombre_clave_prueba, nombre_clave_prueba.replace('_', ' ').title())
                story.append(Paragraph(titulo_prueba, styles['Heading2']))

                datos_tabla = []
                datos_tabla.append(['Parámetro', 'Valor'])

                if 'estadistico' in resultado_summary:
                    datos_tabla.append(
                        ['Estadístico', f"{resultado_summary['estadistico']:.6f}"])
                if 'valor_critico' in resultado_summary:
                    datos_tabla.append(
                        ['Valor crítico', f"{resultado_summary['valor_critico']:.6f}"])
                if 'p_valor' in resultado_summary:
                    datos_tabla.append(
                        ['P-valor', f"{resultado_summary['p_valor']:.6f}"])

                if resultado_summary['rechaza_h0']:
                    decision = "Se rechaza H0"
                    interpretacion = "Los datos NO siguen la distribución esperada"
                else:
                    decision = "Se acepta H0"
                    interpretacion = "Los datos siguen la distribución esperada"

                datos_tabla.append(['Decisión', decision])
                datos_tabla.append(['Interpretación', interpretacion])

                tabla = Table(datos_tabla)
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(tabla)
                story.append(Spacer(1, 20))

            doc.build(story)

            messagebox.showinfo(
                "Éxito", f"Reporte PDF generado: {archivo_pdf}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")


def main():
    root = tk.Tk()
    app = InterfazPrincipal(root)

    # CORRECCIÓN: Configurar protocolo de cierre global
    def on_closing():
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass
        root.quit()  # Salir del mainloop
        root.destroy()  # Destruir la ventana
        import sys
        sys.exit(0)  # Forzar salida del programa

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()
    finally:
        # Asegurar limpieza al salir
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass


if __name__ == "__main__":
    main()
