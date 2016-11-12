import argparse
import serial
import cv2
import numpy as np
import math
import threading
import time
import detectorGUI
import detectorClass
from collections import deque
from PyQt4 import QtGui, QtCore
import sys
from main import configuracion

r1_mostrar_mascara = False
r2_mostrar_mascara = False
objetivo_mostrar_mascara = False
definir_region_interes = False
actualizar_camara = False
corregir_error = False
multiplicador_kp = 1
multiplicador_ki = 1
multiplicador_kd = 1

################################################################################
class errorThread(threading.Thread):
	""" Clase que crea un thread para detectar el error entre el objetivo y la
	referencia. Depende de la clase Detector para ubicarlos."""
	def __init__(self, captura, debug):
		""" Constructor del thread de calculo de error."""
		threading.Thread.__init__(self)
		self.captura = captura
		self.threadActiva = True
		self.errorAcumulado = 0
		self.errorAnterior = 0
		self.mouse_suelto = True
		self.fps = 0
		self.cuadros = 0
		self.pasadas = 0
		self.tiempoAnalisis = 0
		self.referenciaAcumulada = 0
		self.duty = configuracion['control']['dutyCen']
		# Region de interes para el calculo de error
		self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0

		self.posicionCero = +100
		self.debug = debug

		# Lee una vez para detectar las dimensiones
		_, cuadro = self.captura.read()

		# Inicializa el thread para calcular FPS
		self.fps_thread()

		# Al comienzo evalua toda la imagen
		self.x1 = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH) - 1)
		self.y1 = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT) - 1)

		print("X1: " + str(self.x1) + " Y1: " + str(self.y1))
		cv2.namedWindow('Detectado')
		# Interrupcion de mouse
		cv2.setMouseCallback('Detectado', self.mouse_callback)

	def fps_thread(self):
		"Thread para calcular los FPS de la captura de la camara"
		t = threading.Timer(1.0, self.fps_thread)
		t.daemon = True
		t.start()
		self.fps = self.cuadros
		self.cuadros = 0

	def run(self):
		""" Codigo que se corre al ejecutar la tarea."""
		global actualizar_camara
		global corregir_error
		global multiplicador_kd
		global multiplicador_ki
		global multiplicador_kp
		# Si esta en modo debug, no abre el puerto serie
		if self.debug is not True:
			# Crea una instancia de serie
			try:
				serie = serial.Serial(port = configuracion['sistema']['serialPort'], baudrate = configuracion['sistema']['baudRate'], stopbits = serial.STOPBITS_ONE)
				print('Se esta usando el puerto: ' + serie.name)
			except Exception:
				print('Error al abrir el puerto serie')
				exit()

		# Crea una instancia del detector
		self.detector = detectorClass.Detector()

		while self.threadActiva is True and self.captura.isOpened():

			if actualizar_camara == True:
				actualizar_camara = False
				self.realizar_actualizacion_camara()

			# Intenta leer un cuadro de la camara
			exito, self.cuadro = self.captura.read()
			#self.cuadro = self.normalizar_color(self.cuadro)
			self.cuadro = self.ecualizar_histograma(self.cuadro)

			if exito is True:
				# Para calcular el tiempo de cada ciclo
				tiempoComienzo = time.time()
				self.pasadas += 1
				self.cuadros += 1
				self.region_interes = self.cuadro[self.y0:self.y1, self.x0:self.x1]

				# Calcula el error y aplica el control
				if self.debug is not True:
					self.calcular_error(serie)
				else:
					self.calcular_error(None)

				if definir_region_interes is True:
					cv2.rectangle(self.cuadro, (self.x0, self.y0), (self.x1, self.y1), (255, 255, 255), 2)

				tiempoFin = time.time()
				self.tiempoAnalisis += tiempoFin - tiempoComienzo
				# Actualiza la ventana que muestra la camara
				cv2.imshow("Detectado", self.cuadro)
				# Interrupcion de mouse
				cv2.setMouseCallback('Detectado', self.mouse_callback)

				print("Tiempo promedio del ciclo %f, pasadas %d, FPS: %d" %(self.tiempoAnalisis / self.pasadas, self.pasadas, self.fps))

				k = cv2.waitKey(1)
				if k == 27:
					break
			else:
				# En caso de no poder acceder a la camara, sale
				print('Error al leer fuente de video')
				break

		print("Cerrrando thread de calculo de error")
		self.captura.release()
		cv2.destroyAllWindows()

	def calcular_error(self, serie):
		""" Funcion que toma el cuadro actual e intenta localizar las referencias
		y el objetivo. Calcula el error en distancia, aplica el PID y lo envia
		por puerto serie si corresponde."""
		# Si logra obtener un cuadro, busca el objeto
		exitoObjeto, centroObjeto = self.detector.detectar(self.region_interes,
												configuracion['colores']['colorObjetivo']['H_low'],
												configuracion['colores']['colorObjetivo']['S_low'],
												configuracion['colores']['colorObjetivo']['V_low'],
												configuracion['colores']['colorObjetivo']['H_hi'],
												configuracion['colores']['colorObjetivo']['S_hi'],
												configuracion['colores']['colorObjetivo']['V_hi'],
												mostrar_mascara = objetivo_mostrar_mascara)
		if exitoObjeto is True:
			centroObjeto = (centroObjeto[0] + self.x0, centroObjeto[1] + self.y0)
			# Si encuentra el objeto, dibuja un punto
			cv2.circle(self.cuadro, centroObjeto, 4, (0, 0, 255), -1)

		# Intenta buscar la referencia
		exitoReferencia1, centroReferencia1 = self.detector.detectar(self.region_interes,
												configuracion['colores']['colorReferencia1']['H_low'],
												configuracion['colores']['colorReferencia1']['S_low'],
												configuracion['colores']['colorReferencia1']['V_low'],
												configuracion['colores']['colorReferencia1']['H_hi'],
												configuracion['colores']['colorReferencia1']['S_hi'],
												configuracion['colores']['colorReferencia1']['V_hi'],
												mostrar_mascara = r1_mostrar_mascara)
		"""
		exitoReferencia2, centroReferencia2 = self.detector.detectar(self.region_interes,
												configuracion['colores']['colorReferencia2']['H_low'],
												configuracion['colores']['colorReferencia2']['S_low'],
												configuracion['colores']['colorReferencia2']['V_low'],
												configuracion['colores']['colorReferencia2']['H_hi'],
												configuracion['colores']['colorReferencia2']['S_hi'],
												configuracion['colores']['colorReferencia2']['V_hi'],
												mostrar_mascara = r2_mostrar_mascara)

		if exitoReferencia2 is True:
			centroReferencia2 = (centroReferencia2[0] + self.x0, centroReferencia2[1] + self.y0)
			# Si encuentra la referencia, dibuja un punto
			cv2.circle(self.cuadro, centroReferencia2, 4, (0, 255, 0), -1)
		"""
		if exitoReferencia1 is True:
			centroReferencia1 = (centroReferencia1[0] + self.x0, centroReferencia1[1] + self.y0)
			self.referenciaAcumulada += centroReferencia1[0]
			cv2.circle(self.cuadro, centroReferencia1, 4, (255, 0, 0), -1)

		if exitoReferencia1 is True and exitoObjeto is True:
			# Calcula el error y dibuja la linea de distancia horizontal
			error = self.detector.distancia_x(puntoRef = (centroReferencia1[0] + self.posicionCero, centroReferencia1[1]), punto = centroObjeto) - 100
			cv2.line(self.cuadro, centroReferencia1, (centroObjeto[0], centroReferencia1[1]), (255, 0, 0), thickness = 3)
			cv2.putText(self.cuadro, "Error: " + str(round(error)), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 0), 2)

			# Aplica el control PID
			self.duty = self.pid(error = error, Kp = configuracion['control']['Kp'] * multiplicador_kp, Ki = configuracion['control']['Ki'] * multiplicador_ki, Kd = configuracion['control']['Kd'] * multiplicador_kd)
			print ("Duty: %d Error: %d Error Acumulado: %d x0: %d y0: %d x1: %d y1: %d" % (int(self.duty), error, self.errorAcumulado, self.x0, self.y0, self.x1, self.y1))
			print("Constantes de control -> Kp: %f | Kd: %f | Ki: %f" %(configuracion['control']['Kp'] * multiplicador_kp, configuracion['control']['Ki'] * multiplicador_ki, configuracion['control']['Kd'] * multiplicador_kd))

			if self.debug is not True and corregir_error is True:
				# Si no es debug, envia el duty por el puerto serie
				self.enviarDuty(int(self.duty), serie)

	def mouse_callback(self, evento, x, y, flags, parametros):
		if evento == cv2.EVENT_LBUTTONDOWN:
			if definir_region_interes is True:
				self.mouse_suelto = False
				# Inicio de la region de interes
				self.x0, self.y0 = x, y
				self.x1, self.y1 = x + 5, y + 5
			else:
				pass

		elif evento == cv2.EVENT_MOUSEMOVE:
			if (definir_region_interes is True) and (self.mouse_suelto is False):
				if x < self.x0:
					self.x1 = self.x0
					self.x0 = x
				elif x == self.x0:
					self.x0 -= 5
					self.x1 = x
				else:
					self.x1 = x

				if y < self.y0:
					self.y1 = self.y0
					self.y0 = y
				elif y == self.y0:
					self.y0 -= 5
					self.y1 = y
				else:
					self.y1 = y

		elif evento == cv2.EVENT_LBUTTONUP:
			self.mouse_suelto = True

	def pid(self, error, Kp, Ki, Kd):
		""" Aplica el algoritmo de PID dado un error, retorna el ciclo de actividad
		que debe aplicarse en el actuador para conseguir un angulo de correcion.
		"""
		self.errorAcumulado += error

		if self.errorAcumulado > configuracion['control']['acumuladoMax']:
			self.errorAcumulado = configuracion['control']['acumuladoMax']
		elif self.errorAcumulado < configuracion['control']['acumuladoMin']:
			self.errorAcumulado = configuracion['control']['acumuladoMin']

		if abs(error) > 200:
			duty = configuracion['control']['dutyCen'] + 3.0 * Kp * error + 1.0 * Kd * (error - self.errorAnterior) + 0 * Ki * self.errorAcumulado
			if duty < configuracion['control']['dutyMin']:
				duty = configuracion['control']['dutyMin']
			if duty > configuracion['control']['dutyMax']:
				duty = configuracion['control']['dutyMax']
			self.errorAnterior = error
		elif 50 <= abs(error) <= 200 :
			duty = configuracion['control']['dutyCen'] + 10.0 * Kp * error + 1.5 * Kd * (error - self.errorAnterior) + 1.0 * Ki * self.errorAcumulado
			if duty < configuracion['control']['dutyMin']:
				duty = configuracion['control']['dutyMin']
			if duty > configuracion['control']['dutyMax']:
				duty = configuracion['control']['dutyMax']
			self.errorAnterior = error
		elif 2 < abs(error) < 50:
			duty = configuracion['control']['dutyCen'] + 2.0 * Kp * error + 2.0 * Kd * (error - self.errorAnterior) + 2.0 * Ki * self.errorAcumulado
			if duty < configuracion['control']['dutyMin'] + 100:
				duty = configuracion['control']['dutyMin'] + 100
			if duty > configuracion['control']['dutyMax']:
				duty = configuracion['control']['dutyMax']
			self.errorAnterior = error
		else:
			duty = configuracion['control']['dutyCen']
		return duty

	def enviarDuty(self, duty, serie):
		""" Envia el ciclo de actividad recibido como parametro por el puerto serie,
		dividiendo el dato en dos bytes, primero el byte bajo y luego el alto.
		"""
		dutyBytes = duty.to_bytes(2, byteorder = 'little', signed = True)
		print("Actualizando duty. Alto: " + str(dutyBytes[0]) + " Bajo: " + str(dutyBytes[1]))
		serie.write(dutyBytes)

	def realizar_actualizacion_camara(self):
		"""Actualiza los valores de configuracion de la camara."""
		self.captura.set(cv2.CAP_PROP_BRIGHTNESS, configuracion['sistema']['camara']['brillo'])
		self.captura.set(cv2.CAP_PROP_CONTRAST, configuracion['sistema']['camara']['contraste'])
		self.captura.set(cv2.CAP_PROP_SATURATION, configuracion['sistema']['camara']['saturacion'])

	def ecualizar_histograma(self, cuadro):
		img_yuv = cv2.cvtColor(cuadro, cv2.COLOR_BGR2YUV)
		img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
		return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

	def normalizar_color(self, cuadro):
		norm=np.zeros((480,640,3),np.float32)
		norm_rgb=np.zeros((480,640,3),np.uint8)

		b=cuadro[:,:,0]
		g=cuadro[:,:,1]
		r=cuadro[:,:,2]

		sum=b+g+r

		norm[:,:,0]=b/sum*255.0
		norm[:,:,1]=g/sum*255.0
		norm[:,:,2]=r/sum*255.0

		norm_rgb=cv2.convertScaleAbs(norm)
		return norm_rgb

	def finalizar(self):
		self.threadActiva = False
################################################################################

def iniciar_deteccion():
	""" Inicializa la captura y el thread de deteccion."""

	# Parser de argumentos de linea de comandos
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', action = 'store_true', help = 'Activa el modo debug')
	parser.add_argument('-t', '--test', action= 'store_true', help = 'Usa como fuente un video de prueba')

	test = parser.parse_args().test
	debug = parser.parse_args().debug

	if test is True:
		# Inicia una captura desde un video
		captura = cv2.VideoCapture('test.avi')
	else:
		# Inicia una captura desde la camara
		captura = cv2.VideoCapture(configuracion["sistema"]["camara"]["numero"])

	tareaError = errorThread(captura, debug)
	# Inicia la tarea que calcula el error al objetivo
	tareaError.setDaemon(True)
	tareaError.start()

def reiniciar_ventanas():
	""" Cierra todas las ventanas."""
	cv2.destroyAllWindows()

# Calibraciones
def calibrar_objetivo():
	pass

def calibrar_referencia_1():
	pass

def calibrar_referencia_2():
	pass
