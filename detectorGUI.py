 # -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import errorthread
from main import configuracion
import threading
import json
import time

class VentanaPrincipal(QtGui.QMainWindow):
	""" Ventana principal """
	# Constructor
	def __init__(self):
		super(VentanaPrincipal, self).__init__()
		self.initGUI()

	def closeEvent(self, event):
		event.ignore()
		self.cerrar_aplicacion(soloPreguntar = True)
		event.accept()

	def initGUI(self):
		""" Inicializa los widgets y layouts """
		# Propiedades de la ventana principal
		self.setGeometry(50, 50, 600, 400)
		self.setWindowTitle("Ball and Beam | Electrónica Industrial I - UTN FRA")
		self.setWindowIcon(QtGui.QIcon("imagenes/iconoVentana.png"))

		self.crear_barra_herramientas()
		self.crear_widget_principal()
		self.crear_widget_configuracion()
		self.crear_widget_calibrar_referencia_1()
		self.crear_widget_calibrar_referencia_2()
		self.crear_widget_calibrar_objetivo()

		# Contenedor de los diferentes layouts
		self.stacked_layout = QtGui.QStackedLayout()
		# Agrega los widgets de las secciones al contenedor
		self.stacked_layout.addWidget(self.widget_principal)
		self.stacked_layout.addWidget(self.widget_configuracion)
		self.stacked_layout.addWidget(self.widget_calibrar_referencia_1)
		self.stacked_layout.addWidget(self.widget_calibrar_referencia_2)
		self.stacked_layout.addWidget(self.widget_calibrar_objetivo)

		self.widget_central = QtGui.QWidget()
		self.widget_central.setLayout(self.stacked_layout)
		self.setCentralWidget(self.widget_central)
		self.show()

		# Inicia deteccion
		errorthread.iniciar_deteccion()

	def crear_barra_herramientas(self):
		""" Crea la barra de herramientas """
		self.barra_herramientas = self.addToolBar("Barra de Herramientas")

		# Crea las acciones para la Barra de Herramientas
		accion_salir = QtGui.QAction(QtGui.QIcon("./imagenes/iconoSalir.png"), "Salir de la aplicación", self)
		accion_salir.triggered.connect(self.cerrar_aplicacion)
		accion_salir.setShortcut("Ctrl+X")

		accion_objetivo = QtGui.QAction(QtGui.QIcon("./imagenes/iconoObjetivo.png"), "Calibrar objetivo", self)
		accion_objetivo.triggered.connect(self.ir_calibrar_objetivo)

		accion_configuracion = QtGui.QAction(QtGui.QIcon("./imagenes/iconoConfiguracion.png"), "Configuración", self)
		accion_configuracion.triggered.connect(self.ir_configuracion)

		accion_referencia_1 = QtGui.QAction(QtGui.QIcon("./imagenes/iconoReferencia1.png"), "Calibrar referencia 1", self)
		accion_referencia_1.triggered.connect(self.ir_calibrar_referencia_1)

		accion_referencia_2 = QtGui.QAction(QtGui.QIcon("./imagenes/iconoReferencia2.png"), "Calibrar referencia 2", self)
		accion_referencia_2.triggered.connect(self.ir_calibrar_referencia_2)

		accion_correr = QtGui.QAction(QtGui.QIcon("./imagenes/iconoCorrer.png"), "Iniciar correción", self)
		accion_correr.triggered.connect(lambda: self.cambiar_bandera('corregir_error', True))
		accion_correr.setShortcut("Ctrl+C")

		accion_parar = QtGui.QAction(QtGui.QIcon("./imagenes/iconoParar.png"), "Detener correción", self)
		accion_parar.triggered.connect(lambda: self.cambiar_bandera('corregir_error', False))
		accion_parar.setShortcut("Ctrl+D")

		self.barra_herramientas.addAction(accion_correr)
		self.barra_herramientas.addAction(accion_parar)
		self.barra_herramientas.addAction(accion_objetivo)
		self.barra_herramientas.addAction(accion_referencia_1)
		#self.barra_herramientas.addAction(accion_referencia_2)
		self.barra_herramientas.addAction(accion_configuracion)
		self.barra_herramientas.addAction(accion_salir)

	def crear_widget_principal(self):
		""" Crea el widget de la seccion principal """
		layout_principal = QtGui.QHBoxLayout()
		label = QtGui.QLabel()
		pixmap = QtGui.QPixmap('imagenes/logo.png')
		label.setPixmap(pixmap)
		layout_principal.addWidget(label)
		self.widget_principal = QtGui.QWidget()
		self.widget_principal.setLayout(layout_principal)

	def crear_widget_configuracion(self):
		""" Crea el widget de la seccion configuracion """
		configuracion_titulo = QtGui.QLabel()
		configuracion_titulo.setText("Configuración")
		configuracion_titulo.setStyleSheet("font-size: 17px")

		definir_region_interes_checkbox = QtGui.QCheckBox("Definir zona de deteccion")
		definir_region_interes_checkbox.setChecked(False)
		definir_region_interes_checkbox.stateChanged.connect(lambda: self.cambiar_bandera('definir_region_interes', definir_region_interes_checkbox.isChecked()))

		# Etiqueta y slider para el brillo de la camara
		self.camara_brillo_label, self.camara_brillo_slider = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
															minimo = 0,
															maximo = 100,
															valor = configuracion['sistema']['camara']['brillo'],
															etiqueta = 'Brillo de camara: ')


		self.camara_brillo_slider.valueChanged.connect(lambda: self.cambiar_bandera('actualizar_camara', True))

		# Etiqueta y slider para el contraste de la camara
		self.camara_contraste_label, self.camara_contraste_slider = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
															minimo = 0,
															maximo = 100,
															valor = configuracion['sistema']['camara']['contraste'],
															etiqueta = 'Contraste de camara: ')


		self.camara_contraste_slider.valueChanged.connect(lambda: self.cambiar_bandera('actualizar_camara', True))

		# Etiqueta y slider para la saturacion de la camara
		self.camara_saturacion_label, self.camara_saturacion_slider = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
															minimo = 0,
															maximo = 100,
															valor = configuracion['sistema']['camara']['saturacion'],
															etiqueta = 'Saturacion de camara: ')
													
		self.camara_saturacion_slider.valueChanged.connect(lambda: self.cambiar_bandera('actualizar_camara', True))


		layout_configuracion = QtGui.QVBoxLayout()
		# Titulo
		layout_configuracion.addWidget(configuracion_titulo)
		# Definir region de interes
		layout_configuracion.addWidget(definir_region_interes_checkbox)
		layout_configuracion.addWidget(self.lineaH())
		# Controles de camara
		layout_configuracion.addWidget(self.camara_brillo_label)
		layout_configuracion.addWidget(self.camara_brillo_slider)
		layout_configuracion.addWidget(self.camara_contraste_label)
		layout_configuracion.addWidget(self.camara_contraste_slider)
		layout_configuracion.addWidget(self.camara_saturacion_label)
		layout_configuracion.addWidget(self.camara_saturacion_slider)
		
		# Multiplicadores de constantes de control
		# Grupos de botones multiplicadores de constantes de control
		self.grupo_kp = QtGui.QButtonGroup(self.widget_principal)
		widget_grupo_kp = QtGui.QWidget(self)
		layout_grupo_kp = QtGui.QHBoxLayout()
		widget_grupo_kp.setLayout(layout_grupo_kp)

		widget_grupo_ki = QtGui.QWidget(self)
		layout_grupo_ki = QtGui.QHBoxLayout()
		widget_grupo_ki.setLayout(layout_grupo_ki)

		widget_grupo_kd = QtGui.QWidget(self)
		layout_grupo_kd = QtGui.QHBoxLayout()
		widget_grupo_kd.setLayout(layout_grupo_kd)
		
		self.grupo_ki = QtGui.QButtonGroup(self.widget_principal)
		self.grupo_kd = QtGui.QButtonGroup(self.widget_principal)

		# Botones multiplicadores de constantes de control
		# KP
		grupo_kp_label = QtGui.QLabel()
		grupo_kp_label.setText("Multiplicador de Kp")
		layout_grupo_kp.addWidget(grupo_kp_label)
		self.kp_0_radio = QtGui.QRadioButton("0%")
		self.kp_0_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 0.0))
		layout_grupo_kp.addWidget(self.kp_0_radio)
		self.kp_20_radio = QtGui.QRadioButton("20%")
		self.kp_20_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 0.2))
		layout_grupo_kp.addWidget(self.kp_20_radio)
		self.kp_50_radio = QtGui.QRadioButton("50%")
		self.kp_50_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 0.5))
		layout_grupo_kp.addWidget(self.kp_50_radio)
		self.kp_100_radio = QtGui.QRadioButton("100%")
		self.kp_100_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 1.0))
		self.kp_100_radio.setChecked(True)
		layout_grupo_kp.addWidget(self.kp_100_radio)
		self.kp_120_radio = QtGui.QRadioButton("120%")
		self.kp_120_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 1.2))
		layout_grupo_kp.addWidget(self.kp_120_radio)
		self.kp_150_radio = QtGui.QRadioButton("150%")
		self.kp_150_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 1.5))
		layout_grupo_kp.addWidget(self.kp_150_radio)
		self.kp_200_radio = QtGui.QRadioButton("200%")
		self.kp_200_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kp', 2.0))
		layout_grupo_kp.addWidget(self.kp_200_radio)		
		# Agrega los botones al grupo
		self.grupo_kp.addButton(self.kp_0_radio)
		self.grupo_kp.addButton(self.kp_20_radio)
		self.grupo_kp.addButton(self.kp_50_radio)
		self.grupo_kp.addButton(self.kp_100_radio)
		self.grupo_kp.addButton(self.kp_120_radio)
		self.grupo_kp.addButton(self.kp_150_radio)
		self.grupo_kp.addButton(self.kp_200_radio)
		layout_configuracion.addWidget(self.lineaH())
		layout_configuracion.addWidget(widget_grupo_kp)

		# Ki
		grupo_ki_label = QtGui.QLabel()
		grupo_ki_label.setText("Multiplicador de Ki")
		layout_grupo_ki.addWidget(grupo_ki_label)
		self.ki_0_radio = QtGui.QRadioButton("0%")
		self.ki_0_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 0.0))
		layout_grupo_ki.addWidget(self.ki_0_radio)
		self.ki_20_radio = QtGui.QRadioButton("20%")
		self.ki_20_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 0.2))
		layout_grupo_ki.addWidget(self.ki_20_radio)
		self.ki_50_radio = QtGui.QRadioButton("50%")
		self.ki_50_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 0.5))
		layout_grupo_ki.addWidget(self.ki_50_radio)
		self.ki_100_radio = QtGui.QRadioButton("100%")
		self.ki_100_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 1.0))
		self.ki_100_radio.setChecked(True)
		layout_grupo_ki.addWidget(self.ki_100_radio)
		self.ki_120_radio = QtGui.QRadioButton("120%")
		self.ki_120_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 1.2))
		layout_grupo_ki.addWidget(self.ki_120_radio)
		self.ki_150_radio = QtGui.QRadioButton("150%")
		self.ki_150_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 1.5))
		layout_grupo_ki.addWidget(self.ki_150_radio)
		self.ki_200_radio = QtGui.QRadioButton("200%")
		self.ki_200_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_ki', 2.0))
		layout_grupo_ki.addWidget(self.ki_200_radio)		
		# Agrega los botones al grupo
		self.grupo_ki.addButton(self.ki_0_radio)
		self.grupo_ki.addButton(self.ki_20_radio)
		self.grupo_ki.addButton(self.ki_50_radio)
		self.grupo_ki.addButton(self.ki_100_radio)
		self.grupo_ki.addButton(self.ki_120_radio)
		self.grupo_ki.addButton(self.ki_150_radio)
		self.grupo_ki.addButton(self.ki_200_radio)
		layout_configuracion.addWidget(self.lineaH())
		layout_configuracion.addWidget(widget_grupo_ki)

		# Kd
		grupo_kd_label = QtGui.QLabel()
		grupo_kd_label.setText("Multiplicador de Kd")
		layout_grupo_kd.addWidget(grupo_kd_label)
		self.kd_0_radio = QtGui.QRadioButton("0%")
		self.kd_0_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 0.0))
		layout_grupo_kd.addWidget(self.kd_0_radio)
		self.kd_20_radio = QtGui.QRadioButton("20%")
		self.kd_20_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 0.2))
		layout_grupo_kd.addWidget(self.kd_20_radio)
		self.kd_50_radio = QtGui.QRadioButton("50%")
		self.kd_50_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 0.5))
		layout_grupo_kd.addWidget(self.kd_50_radio)
		self.kd_100_radio = QtGui.QRadioButton("100%")
		self.kd_100_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 1.0))
		self.kd_100_radio.setChecked(True)
		layout_grupo_kd.addWidget(self.kd_100_radio)
		self.kd_120_radio = QtGui.QRadioButton("120%")
		self.kd_120_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 1.2))
		layout_grupo_kd.addWidget(self.kd_120_radio)
		self.kd_150_radio = QtGui.QRadioButton("150%")
		self.kd_150_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 1.5))
		layout_grupo_kd.addWidget(self.kd_150_radio)
		self.kd_200_radio = QtGui.QRadioButton("200%")
		self.kd_200_radio.clicked.connect(lambda: self.cambiar_bandera('actualizar_multiplicador_kd', 2.0))
		layout_grupo_kd.addWidget(self.kd_200_radio)		
		# Agrega los botones al grupo
		self.grupo_kd.addButton(self.kd_0_radio)
		self.grupo_kd.addButton(self.kd_20_radio)
		self.grupo_kd.addButton(self.kd_50_radio)
		self.grupo_kd.addButton(self.kd_100_radio)
		self.grupo_kd.addButton(self.kd_120_radio)
		self.grupo_kd.addButton(self.kd_150_radio)
		self.grupo_kd.addButton(self.kd_200_radio)
		layout_configuracion.addWidget(self.lineaH())
		layout_configuracion.addWidget(widget_grupo_kd)


		layout_configuracion.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
		self.widget_configuracion = QtGui.QWidget()
		self.widget_configuracion.setLayout(layout_configuracion)

	def crear_widget_calibrar_referencia_1(self):
		titulo_seccion = QtGui.QLabel()
		titulo_seccion.setText("Calibrar la referencia 1")
		titulo_seccion.setStyleSheet("font-size: 17px")
		# Crea los sliders con sus etiquetas
		self.r1_label_H_low, self.r1_slider_H_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 180,
												valor = configuracion['colores']['colorReferencia1']['H_low'],
												etiqueta = 'Hue bajo')
		self.r1_slider_H_low.valueChanged.connect(self.actualizar_colores)

		self.r1_label_S_low, self.r1_slider_S_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia1']['S_low'],
												etiqueta = 'Saturation bajo')
		self.r1_slider_S_low.valueChanged.connect(self.actualizar_colores)

		self.r1_label_V_low, self.r1_slider_V_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia1']['V_low'],
												etiqueta = 'Value bajo')
		self.r1_slider_V_low.valueChanged.connect(self.actualizar_colores)

		self.r1_label_H_hi, self.r1_slider_H_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 180,
												valor = configuracion['colores']['colorReferencia1']['H_hi'],
												etiqueta = 'Hue alto')
		self.r1_slider_H_hi.valueChanged.connect(self.actualizar_colores)

		self.r1_label_S_hi, self.r1_slider_S_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia1']['S_hi'],
												etiqueta = 'Saturation alto')
		self.r1_slider_S_hi.valueChanged.connect(self.actualizar_colores)

		self.r1_label_V_hi, self.r1_slider_V_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia1']['V_hi'],
												etiqueta = 'Value alto')
		self.r1_slider_V_hi.valueChanged.connect(self.actualizar_colores)

		mostrar_mascara = QtGui.QCheckBox("Mostrar máscara")
		mostrar_mascara.setChecked(False)
		mostrar_mascara.stateChanged.connect(lambda: self.cambiar_bandera('calibrar_referencia_1', mostrar_mascara.isChecked()))

		# Crea el layout y le agrega los widgets
		layout_calibrar_referencia_1 = QtGui.QVBoxLayout()
		layout_calibrar_referencia_1.addWidget(titulo_seccion)
		layout_calibrar_referencia_1.addWidget(mostrar_mascara)
		layout_calibrar_referencia_1.addWidget(self.r1_label_H_low)
		layout_calibrar_referencia_1.addWidget(self.r1_slider_H_low)
		layout_calibrar_referencia_1.addWidget(self.r1_label_S_low)
		layout_calibrar_referencia_1.addWidget(self.r1_slider_S_low)
		layout_calibrar_referencia_1.addWidget(self.r1_label_V_low)
		layout_calibrar_referencia_1.addWidget(self.r1_slider_V_low)
		layout_calibrar_referencia_1.addWidget(self.r1_label_H_hi)
		layout_calibrar_referencia_1.addWidget(self.r1_slider_H_hi)
		layout_calibrar_referencia_1.addWidget(self.r1_label_S_hi)
		layout_calibrar_referencia_1.addWidget(self.r1_slider_S_hi)
		layout_calibrar_referencia_1.addWidget(self.r1_label_V_hi)
		layout_calibrar_referencia_1.addWidget(self.r1_slider_V_hi)

		layout_calibrar_referencia_1.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignVCenter)
		self.widget_calibrar_referencia_1 = QtGui.QWidget()
		self.widget_calibrar_referencia_1.setLayout(layout_calibrar_referencia_1)

	def crear_widget_calibrar_referencia_2(self):
		titulo_seccion = QtGui.QLabel()
		titulo_seccion.setText("Calibrar la referencia 2")
		titulo_seccion.setStyleSheet("font-size: 17px")

		layout_calibrar_referencia_2 = QtGui.QHBoxLayout()
		# Crea los sliders con sus etiquetas
		self.r2_label_H_low, self.r2_slider_H_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 180,
												valor = configuracion['colores']['colorReferencia2']['H_low'],
												etiqueta = 'Hue bajo')
		self.r2_slider_H_low.valueChanged.connect(self.actualizar_colores)

		self.r2_label_S_low, self.r2_slider_S_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia2']['S_low'],
												etiqueta = 'Saturation bajo')
		self.r2_slider_S_low.valueChanged.connect(self.actualizar_colores)

		self.r2_label_V_low, self.r2_slider_V_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia2']['V_low'],
												etiqueta = 'Value bajo')
		self.r2_slider_V_low.valueChanged.connect(self.actualizar_colores)

		self.r2_label_H_hi, self.r2_slider_H_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 180,
												valor = configuracion['colores']['colorReferencia2']['H_hi'],
												etiqueta = 'Hue alto')
		self.r2_slider_H_hi.valueChanged.connect(self.actualizar_colores)

		self.r2_label_S_hi, self.r2_slider_S_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia2']['S_hi'],
												etiqueta = 'Saturation alto')
		self.r2_slider_S_hi.valueChanged.connect(self.actualizar_colores)

		self.r2_label_V_hi, self.r2_slider_V_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorReferencia2']['V_hi'],
												etiqueta = 'Value alto')
		self.r2_slider_V_hi.valueChanged.connect(self.actualizar_colores)

		mostrar_mascara = QtGui.QCheckBox("Mostrar máscara")
		mostrar_mascara.setChecked(False)
		mostrar_mascara.stateChanged.connect(lambda: self.cambiar_bandera('calibrar_referencia_2', mostrar_mascara.isChecked()))

		# Crea el layout y le agrega los widgets
		layout_calibrar_referencia_2.addWidget(titulo_seccion)
		layout_calibrar_referencia_2 = QtGui.QVBoxLayout()
		layout_calibrar_referencia_2.addWidget(titulo_seccion)
		layout_calibrar_referencia_2.addWidget(mostrar_mascara)
		layout_calibrar_referencia_2.addWidget(self.r2_label_H_low)
		layout_calibrar_referencia_2.addWidget(self.r2_slider_H_low)
		layout_calibrar_referencia_2.addWidget(self.r2_label_S_low)
		layout_calibrar_referencia_2.addWidget(self.r2_slider_S_low)
		layout_calibrar_referencia_2.addWidget(self.r2_label_V_low)
		layout_calibrar_referencia_2.addWidget(self.r2_slider_V_low)
		layout_calibrar_referencia_2.addWidget(self.r2_label_H_hi)
		layout_calibrar_referencia_2.addWidget(self.r2_slider_H_hi)
		layout_calibrar_referencia_2.addWidget(self.r2_label_S_hi)
		layout_calibrar_referencia_2.addWidget(self.r2_slider_S_hi)
		layout_calibrar_referencia_2.addWidget(self.r2_label_V_hi)
		layout_calibrar_referencia_2.addWidget(self.r2_slider_V_hi)

		layout_calibrar_referencia_2.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignVCenter)

		self.widget_calibrar_referencia_2 = QtGui.QWidget()
		self.widget_calibrar_referencia_2.setLayout(layout_calibrar_referencia_2)

	def crear_widget_calibrar_objetivo(self):
		titulo_seccion = QtGui.QLabel()
		titulo_seccion.setText("Calibrar el objetivo")
		titulo_seccion.setStyleSheet("font-size: 17px")
		layout_calibrar_objetivo = QtGui.QHBoxLayout()
		layout_calibrar_objetivo.addWidget(titulo_seccion)

		# Crea los sliders con sus etiquetas
		self.objetivo_label_H_low, self.objetivo_slider_H_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 180,
												valor = configuracion['colores']['colorObjetivo']['H_low'],
												etiqueta = 'Hue bajo')
		self.objetivo_slider_H_low.valueChanged.connect(self.actualizar_colores)

		self.objetivo_label_S_low, self.objetivo_slider_S_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorObjetivo']['S_low'],
												etiqueta = 'Saturation bajo')
		self.objetivo_slider_S_low.valueChanged.connect(self.actualizar_colores)

		self.objetivo_label_V_low, self.objetivo_slider_V_low = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorObjetivo']['V_low'],
												etiqueta = 'Value bajo')
		self.objetivo_slider_V_low.valueChanged.connect(self.actualizar_colores)

		self.objetivo_label_H_hi, self.objetivo_slider_H_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 180,
												valor = configuracion['colores']['colorObjetivo']['H_hi'],
												etiqueta = 'Hue alto')
		self.objetivo_slider_H_hi.valueChanged.connect(self.actualizar_colores)

		self.objetivo_label_S_hi, self.objetivo_slider_S_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorObjetivo']['S_hi'],
												etiqueta = 'Saturation alto')
		self.objetivo_slider_S_hi.valueChanged.connect(self.actualizar_colores)

		self.objetivo_label_V_hi, self.objetivo_slider_V_hi = self.crear_slider(orientacion = QtCore.Qt.Horizontal,
												minimo = 0,
												maximo = 255,
												valor = configuracion['colores']['colorObjetivo']['V_hi'],
												etiqueta = 'Value alto')
		self.objetivo_slider_V_hi.valueChanged.connect(self.actualizar_colores)

		mostrar_mascara = QtGui.QCheckBox("Mostrar máscara")
		mostrar_mascara.setChecked(False)
		mostrar_mascara.stateChanged.connect(lambda: self.cambiar_bandera('calibrar_objetivo', mostrar_mascara.isChecked()))

		# Crea el layout y le agrega los widgets
		layout_calibrar_objetivo.addWidget(titulo_seccion)
		layout_calibrar_objetivo = QtGui.QVBoxLayout()
		layout_calibrar_objetivo.addWidget(titulo_seccion)
		layout_calibrar_objetivo.addWidget(mostrar_mascara)
		layout_calibrar_objetivo.addWidget(self.objetivo_label_H_low)
		layout_calibrar_objetivo.addWidget(self.objetivo_slider_H_low)
		layout_calibrar_objetivo.addWidget(self.objetivo_label_S_low)
		layout_calibrar_objetivo.addWidget(self.objetivo_slider_S_low)
		layout_calibrar_objetivo.addWidget(self.objetivo_label_V_low)
		layout_calibrar_objetivo.addWidget(self.objetivo_slider_V_low)
		layout_calibrar_objetivo.addWidget(self.objetivo_label_H_hi)
		layout_calibrar_objetivo.addWidget(self.objetivo_slider_H_hi)
		layout_calibrar_objetivo.addWidget(self.objetivo_label_S_hi)
		layout_calibrar_objetivo.addWidget(self.objetivo_slider_S_hi)
		layout_calibrar_objetivo.addWidget(self.objetivo_label_V_hi)
		layout_calibrar_objetivo.addWidget(self.objetivo_slider_V_hi)

		layout_calibrar_objetivo.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignVCenter)

		self.widget_calibrar_objetivo = QtGui.QWidget()
		self.widget_calibrar_objetivo.setLayout(layout_calibrar_objetivo)

	def ir_configuracion(self):
		""" Cambia a la seccion configuracion """
		self.stacked_layout.setCurrentIndex(1)

	def ir_calibrar_referencia_1(self):
		""" Cambia la seccion de calibracion de referencia 1 """
		self.stacked_layout.setCurrentIndex(2)

	def ir_calibrar_referencia_2(self):
		""" Cambia la seccion calibracion de referencia 2 """
		self.stacked_layout.setCurrentIndex(3)

	def ir_calibrar_objetivo(self):
		""" Cambia la seccion calibracion de objetivo """
		self.stacked_layout.setCurrentIndex(4)

	def crear_slider(self, orientacion, minimo, maximo, valor, etiqueta):
		slider = QtGui.QSlider(orientacion)
		slider.setMinimum(minimo)
		slider.setMaximum(maximo)
		slider.setValue(valor)
		slider.setTickPosition(QtGui.QSlider.TicksBelow)
		slider.setTickInterval(2)
		label = QtGui.QLabel()
		label.setText(etiqueta + " " + str(valor))
		return label, slider

	def lineaH(self):
		linea = QtGui.QFrame()
		linea.setFrameShape(QtGui.QFrame.HLine)
		linea.setFrameShadow(QtGui.QFrame.Sunken)
		return linea

	def actualizar_colores(self):
		# Referencia 1
		configuracion['colores']['colorReferencia1']['H_low'] = self.r1_slider_H_low.value()
		configuracion['colores']['colorReferencia1']['S_low'] = self.r1_slider_S_low.value()
		configuracion['colores']['colorReferencia1']['V_low'] = self.r1_slider_V_low.value()
		configuracion['colores']['colorReferencia1']['H_hi'] = self.r1_slider_H_hi.value()
		configuracion['colores']['colorReferencia1']['S_hi'] = self.r1_slider_S_hi.value()
		configuracion['colores']['colorReferencia1']['V_hi'] = self.r1_slider_V_hi.value()

		# Referencia 2
		configuracion['colores']['colorReferencia2']['H_low'] = self.r2_slider_H_low.value()
		configuracion['colores']['colorReferencia2']['S_low'] = self.r2_slider_S_low.value()
		configuracion['colores']['colorReferencia2']['V_low'] = self.r2_slider_V_low.value()
		configuracion['colores']['colorReferencia2']['H_hi'] = self.r2_slider_H_hi.value()
		configuracion['colores']['colorReferencia2']['S_hi'] = self.r2_slider_S_hi.value()
		configuracion['colores']['colorReferencia2']['V_hi'] = self.r2_slider_V_hi.value()

		# Objetivo
		configuracion['colores']['colorObjetivo']['H_low'] = self.objetivo_slider_H_low.value()
		configuracion['colores']['colorObjetivo']['S_low'] = self.objetivo_slider_S_low.value()
		configuracion['colores']['colorObjetivo']['V_low'] = self.objetivo_slider_V_low.value()
		configuracion['colores']['colorObjetivo']['H_hi'] = self.objetivo_slider_H_hi.value()
		configuracion['colores']['colorObjetivo']['S_hi'] = self.objetivo_slider_S_hi.value()
		configuracion['colores']['colorObjetivo']['V_hi'] = self.objetivo_slider_V_hi.value()

		self.r1_label_H_low.setText("Hue bajo " + str(self.r1_slider_H_low.value()))
		self.r1_label_S_low.setText("Saturation bajo " + str(self.r1_slider_S_low.value()))
		self.r1_label_V_low.setText("Value bajo " + str(self.r1_slider_V_low.value()))
		self.r1_label_H_hi.setText("Hue alto " + str(self.r1_slider_H_hi.value()))
		self.r1_label_S_hi.setText("Saturation alto " + str(self.r1_slider_S_hi.value()))
		self.r1_label_V_hi.setText("Value alto " + str(self.r1_slider_V_hi.value()))

		self.r2_label_H_low.setText("Hue bajo " + str(self.r2_slider_H_low.value()))
		self.r2_label_S_low.setText("Saturation bajo " + str(self.r2_slider_S_low.value()))
		self.r2_label_V_low.setText("Value bajo " + str(self.r2_slider_V_low.value()))
		self.r2_label_H_hi.setText("Hue alto " + str(self.r2_slider_H_hi.value()))
		self.r2_label_S_hi.setText("Saturation alto " + str(self.r2_slider_S_hi.value()))
		self.r2_label_V_hi.setText("Value alto " + str(self.r2_slider_V_hi.value()))

		self.objetivo_label_H_low.setText("Hue bajo " + str(self.objetivo_slider_H_low.value()))
		self.objetivo_label_S_low.setText("Saturation bajo " + str(self.objetivo_slider_S_low.value()))
		self.objetivo_label_V_low.setText("Value bajo " + str(self.objetivo_slider_V_low.value()))
		self.objetivo_label_H_hi.setText("Hue alto " + str(self.objetivo_slider_H_hi.value()))
		self.objetivo_label_S_hi.setText("Saturation alto " + str(self.objetivo_slider_S_hi.value()))
		self.objetivo_label_V_hi.setText("Value alto " + str(self.objetivo_slider_V_hi.value()))

	def cambiar_bandera(self, bandera, valor):
		""" Actualiza los valores de las banderas globales"""
		if bandera == 'calibrar_referencia_1':
			errorthread.r1_mostrar_mascara = valor
			# Llama a esta funcion para cerrar las ventanas muertas
			errorthread.reiniciar_ventanas()
		elif bandera == 'calibrar_referencia_2':
			errorthread.r2_mostrar_mascara = valor
			# Llama a esta funcion para cerrar las ventanas muertas
			errorthread.reiniciar_ventanas()
		elif bandera == 'calibrar_objetivo':
			errorthread.objetivo_mostrar_mascara = valor
			# Llama a esta funcion para cerrar las ventanas muertas
			errorthread.reiniciar_ventanas()
		elif bandera == 'definir_region_interes':
			errorthread.definir_region_interes = valor
		elif bandera == 'corregir_error':
			errorthread.corregir_error = valor
		elif bandera == 'actualizar_camara':
			# Actualiza los valores de configuracion de la camara
			errorthread.actualizar_camara = valor
			configuracion['sistema']['camara']['brillo'] = self.camara_brillo_slider.value()
			configuracion['sistema']['camara']['contraste'] = self.camara_contraste_slider.value()
			configuracion['sistema']['camara']['saturacion'] = self.camara_saturacion_slider.value()
			self.camara_brillo_label.setText("Brillo de camara: " + str(self.camara_brillo_slider.value()))
			self.camara_contraste_label.setText("Contraste de camara: " + str(self.camara_contraste_slider.value()))
			self.camara_saturacion_label.setText("Saturacion de camara: " + str(self.camara_saturacion_slider.value()))
		elif bandera == 'actualizar_multiplicador_kp':
			# Actualiza el multiplicador de kp
			print("Cambiando multiplicador Kp a " + str(valor))
			errorthread.multiplicador_kp = valor
		elif bandera == 'actualizar_multiplicador_ki':
			# Actualiza el multiplicador de ki
			print("Cambiando multiplicador Ki a " + str(valor))
			errorthread.multiplicador_ki = valor
		elif bandera == 'actualizar_multiplicador_kd':
			# Actualiza el multiplicador de kd
			print("Cambiando multiplicador Kd a " + str(valor))
			errorthread.multiplicador_kd = valor



	def cerrar_aplicacion(self, soloPreguntar):
		""" Presenta un popup preguntando si se quiere salir de la aplicacion """
		pregunta = QtGui.QMessageBox.question(self, 'Salir', "Realmente desea salir?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if pregunta == QtGui.QMessageBox.Yes:
			# Guarda la configuracion
			with open('config.json', 'w') as archivo_salida:
				json.dump(configuracion, archivo_salida, indent=4)
			threadsActivos = threading.enumerate()
			print("Cerrando threads activos")
			for thread in threadsActivos:
				if  getattr(thread, "finalizar", None):
					thread.finalizar()
					thread.join(1)

			if soloPreguntar is not True:
				sys.exit(0)


def main():
	app = QtGui.QApplication(sys.argv)
	ventanaPrincipal = VentanaPrincipal()
	#sys.exit(app.exec_())
	app.exec_()

if __name__ == '__main__':
	main()
