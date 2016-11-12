 # -*- coding: utf-8 -*-
import numpy as np
import cv2
import math

class Detector(object):
	"""Clase que permite detectar figuras de colores. Puede retornar
	el centroide de la misma."""
	# Constructor
	def __init__(self):
		super(Detector, self).__init__()
		pass

	def detectar(self, imagen, hLow, sLow, vLow, hHi, sHi, vHi, mostrar_mascara):
		""" Detecta el centro de la figura del color dentro del rango """
		# Realiza un desenfoque gaussiano para reducir ruido
		blur = cv2.GaussianBlur(imagen, (3, 3),1)
		# Cambia de BGR a HSV
		hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
		lowerColor = np.array([hLow, sLow, vLow])
		upperColor = np.array([hHi, sHi, vHi])

		# Devuelve una mascara con los pixeles dentro del rango
		mask = cv2.inRange(hsv, lowerColor, upperColor)

		mask = cv2.dilate(mask, np.ones((8,8),np.uint8), 3)

		# Desenfoca la mascara
		bmask = cv2.GaussianBlur(mask, (5,5),0)
		bmask = cv2.erode(bmask, np.ones((8,8),np.uint8), 3)

		"""
		# Calcula los momentos y el centroide
		moments = cv2.moments(bmask)

		m00 = moments['m00']
		centroid_x, centroid_y = None, None

		if m00 > 25000:
			centroid_x = int(moments['m10']/m00)
			centroid_y = int(moments['m01']/m00)
			ctr = (centroid_x, centroid_y)
			exito = True
		else:
			ctr = (-1,-1)
			exito = False
		"""


		# Crea una instancia de detector MSER y busca las regiones
		detector = cv2.MSER_create()
		regiones = detector.detect(bmask)

		cv2.drawKeypoints(imagen, regiones, np.array([]), (255,255,255))
		regiones.sort(key = lambda x: -x.size)

		circulos = [region for region in regiones if not self.suprimir(region, regiones)]

		# Dibuja circulos sobre la region de mayor area
		if len(circulos) != 0:
			exito = True
			ctr = (int(circulos[0].pt[0]), int(circulos[0].pt[1]))
			cv2.circle(imagen, (int(circulos[0].pt[0]), int(circulos[0].pt[1])), int(circulos[0].size/2), (150, 55, 65), 2, cv2.LINE_AA)
			cv2.circle(imagen, (int(circulos[0].pt[0]), int(circulos[0].pt[1])), int(circulos[0].size/2), (250, 200, 200), 1, cv2.LINE_AA)
		else:
			exito = False
			ctr = (-1, -1)

		if mostrar_mascara is True:
			cv2.imshow("Mascara", bmask)
		return exito, ctr

	def suprimir(self, regionAEvaluar, regiones):
		""" Criterio de supresion de regiones. Si las regiones estan cerca de
		las otras grandes, se eliminan."""
		for region in regiones:
			distx = region.pt[0] - regionAEvaluar.pt[0]
			disty = region.pt[1] - regionAEvaluar.pt[1]
			dist = math.sqrt(distx  * distx + disty * disty)
			if (region.size > regionAEvaluar.size) and (dist < region.size / 2):
					return True

	def calcular_distancia(self, puntoRef, punto):
		""" Calcula la distancia en el plano entre la referencia y un punto"""
		x1 = puntoRef[0]
		y1 = puntoRef[1]
		x2 = punto[0]
		y2 = punto[1]

		distancia = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
		if x1 > x2:
			distancia = -distancia
		return distancia

	def distancia_x(self, puntoRef, punto):
		""" Calcula la distancia lineal entre la referencia y un punto"""
		x1 = puntoRef[0]
		x2 = punto[0]
		return  x1 - x2
