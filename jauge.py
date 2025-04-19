import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget
from math import cos, sin, radians


class CircularGauge(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jauge circulaire - Style Montre")
        self.setGeometry(100, 100, 400, 400)
        self.value = 0  # Valeur initiale de la jauge
        self.timer = QTimer(self)                                   # Associer un timer à ce widget (important)
        self.timer.timeout.connect(self.update_value)               # Met à jour toutes les 100 ms.
        self.timer.start(100)  # Mettre à jour toutes les 100 ms

        self.background_image = QPixmap("D:/Alain/ps2.png")

        if self.background_image.isNull():
            print(
                "Erreur : L'image 'cadran.png' n'a pas été trouvée. Placez cette image dans le répertoire indiqué ci-dessus.")
            sys.exit(1)

    def update_value(self):
        """Met à jour la valeur de la jauge."""
        if self.value != 70:
            self.value = 0

        self.update()  # Redessiner la jauge (très important avec QPainter)

    def paintEvent(self, event):
        """Redessiner la jauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Activer un rendu fluide

        # Dessiner l'image de fond (cadran)
        background_resized = self.background_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(
            (self.width() - background_resized.width()) // 2,
            (self.height() - background_resized.height()) // 2,
            background_resized
        )

        # Définir les dimensions et le centre
        rect = self.rect()  # Obtenir le rectangle entourant le widget
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        radius = min(center_x, center_y) - 20  # Rayon de la jauge

        # Dessiner le cercle de fond (arrière-plan)
        pen = QPen(Qt.gray, 15)  # Créer un stylo de couleur grise et épaisseur
        painter.setPen(pen)
        painter.drawEllipse(center_x - radius, center_y - radius, 2 * radius, 2 * radius)

        # Dessiner la progression (comme une découpe circulaire)
        pen.setColor(Qt.green)  # Couleur de la progression
        painter.setPen(pen)
        painter.drawArc(
            center_x - radius, center_y - radius, 2 * radius, 2 * radius,
            200 * 16, -int(self.value * 50//16)  # Progression circulaire en fonction de value
        )

        # Ajouter une aiguille (facultatif)
        painter.setPen(QPen(Qt.red, 10))  # Créer un stylo rouge pour l'aiguille
        angle = radians(360 * (self.value / 360) - 215)  # Calculer l'angle
        x2 = center_x + int(radius * cos(angle))  # Coordonnées x de l'aiguille
        y2 = center_y + int(radius  * sin(angle))  # Coordonnées y de l'aiguille
        painter.drawLine(center_x, center_y, x2, y2)  # Dessiner l'aiguille

"""
        # Dessiner le texte au centre de la montre
        painter.setPen(QPen(Qt.black))  # Couleur noire pour le texte
        painter.drawText(rect, Qt.AlignCenter, f"{self.value} %")  # Afficher la valeur
"""

if __name__ == "__main__":
    # Initialiser l'application Qt
    app = QApplication(sys.argv)

    # Créer et afficher la jauge circulaire
    window = CircularGauge()
    window.show()

    # Exécuter la boucle d'événements
    sys.exit(app.exec_())
