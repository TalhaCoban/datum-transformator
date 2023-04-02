import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QSizePolicy,
                             QComboBox, QLineEdit, QPushButton, QListWidget, QGroupBox, QLabel)
from PyQt5.QtGui import QFont


paramaters = {
    "wgs84_to_itrf96" : {
        "dx" : 0.072,
        "dy" : 0.092,
        "dz" : 0.093,
        "ex" : 0.000094,
        "ey" : 0.000092,
        "ez" : 0.000032,
        "ppm" : -0.000007
    },
    "ed50_to_itrf96" : {
        "dx" : 0.039,
        "dy" : 0.092,
        "dz" : 0.057,
        "ex" : 0.000036,
        "ey" : 0.000033,
        "ez" : 0.000064,
        "ppm" : 0.000001
    }
}


def helmert_transformation(x, y, z, datums, inverse=False):

    if inverse:
        # Invert the sign of the parameters for the inverse transformation
        dx = -paramaters[datums]["dx"]
        dy = -paramaters[datums]["dy"]
        dz = -paramaters[datums]["dz"]
        ex = -paramaters[datums]["ex"]
        ey = -paramaters[datums]["ey"]
        ez = -paramaters[datums]["ez"]
        ppm = -paramaters[datums]["ppm"]
    else:
        # Set the transformation parameters
        dx = paramaters[datums]["dx"]
        dy = paramaters[datums]["dy"]
        dz = paramaters[datums]["dz"]
        ex = paramaters[datums]["ex"]
        ey = paramaters[datums]["ey"]
        ez = paramaters[datums]["ez"]
        ppm = paramaters[datums]["ppm"]
    
    # Perform the translation
    x_trans = x + dx
    y_trans = y + dy
    z_trans = z + dz
    
    # Perform the rotation
    x_rot = x_trans - ex * y_trans + ey * z_trans
    y_rot = ex * x_trans + y_trans - ez * z_trans
    z_rot = -ey * x_trans + ez * y_trans + z_trans
    
    # Perform the scale adjustment
    x_scaled = x_rot + ppm * x_rot
    y_scaled = y_rot + ppm * y_rot
    z_scaled = z_rot + ppm * z_rot

    return x_scaled, y_scaled, z_scaled




class DatumTransformWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up the UI
        self.setWindowTitle('Helmert Datum Transformer')
        
        self.combo_box = QComboBox()
        self.combo_box.addItem('WGS84 to ITRF96')
        self.combo_box.addItem('ITRF96 to WGS84')
        self.combo_box.addItem('ED50 to ITRF96')
        self.combo_box.addItem('ITRF96 to ED50')
        self.combo_box.setMaximumWidth(200)
        self.combo_box.setFont(QFont('Times', 9))

        self.x_label = QLabel('X : ')
        self.x_label.setFont(QFont('Times', 10))
        self.y_label = QLabel('Y : ')
        self.y_label.setFont(QFont('Times', 10))
        self.z_label = QLabel('Z : ')
        self.z_label.setFont(QFont('Times', 10))

        self.x_edit = QLineEdit()
        self.x_edit.setMaximumWidth(150)
        self.x_edit.setFont(QFont('Times', 9))
        self.y_edit = QLineEdit()
        self.y_edit.setMaximumWidth(150)
        self.y_edit.setFont(QFont('Times', 9))
        self.z_edit = QLineEdit()
        self.z_edit.setMaximumWidth(150)
        self.z_edit.setFont(QFont('Times', 9))

        self.clear_button = QPushButton('clear')
        self.clear_button.setMaximumWidth(100)
        self.clear_button.setFont(QFont('Times', 9))
        self.button = QPushButton('Transform')
        self.button.setMaximumWidth(100)
        self.button.setFont(QFont('Times', 9))
        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(250)
        self.list_widget.setMaximumHeight(150)
        self.list_widget.setFont(QFont('Times', 10))

        combobox_layout = QHBoxLayout()
        combobox_layout.addStretch()
        combobox_layout.addWidget(self.combo_box)
        combobox_layout.addStretch()
        combo_group = QGroupBox('datums')
        combo_group.setLayout(combobox_layout)
        
        # Set up the input group box
        input_layout_X = QHBoxLayout()
        input_layout_Y = QHBoxLayout()
        input_layout_Z = QHBoxLayout()
        
        input_layout_X.addStretch()
        input_layout_X.addWidget(self.x_label)
        input_layout_X.addWidget(self.x_edit)
        input_layout_X.addStretch()
        input_layout_Y.addStretch()
        input_layout_Y.addWidget(self.y_label)
        input_layout_Y.addWidget(self.y_edit)
        input_layout_Y.addStretch()
        input_layout_Z.addStretch()
        input_layout_Z.addWidget(self.z_label)
        input_layout_Z.addWidget(self.z_edit)
        input_layout_Z.addStretch()

        input_layout = QVBoxLayout()
        input_layout.addStretch()
        input_layout.addLayout(input_layout_X)
        input_layout.addLayout(input_layout_Y)
        input_layout.addLayout(input_layout_Z)
        input_layout.addStretch()

        input_group = QGroupBox('Input coordinates')
        input_group.setLayout(input_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.button)
        buttons_layout.addStretch()

        list_layout = QHBoxLayout()
        list_layout.addStretch()
        list_layout.addWidget(self.list_widget)
        list_layout.addStretch()
        list_group = QGroupBox("Output_coordinates")
        list_group.setLayout(list_layout)

        # Add the widgets to the layout
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(combo_group)
        layout.addWidget(input_group)
        layout.addLayout(buttons_layout)
        layout.addWidget(list_group)
        layout.addStretch()
        
        # Set the layout and make the widget resizable
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Connect the button's clicked signal to the transform function
        self.button.clicked.connect(self.transform)
        self.clear_button.clicked.connect(self.clear)
    

    def clear(self):

        self.x_edit.clear()
        self.y_edit.clear()
        self.z_edit.clear()
        self.list_widget.clear()


    def transform(self):
        """
        Perform the selected transformation on the input coordinates and display the result in the list widget.
        """
        # Get the selected transformation and input coordinates
        transform = self.combo_box.currentText()
        try:
            x = float(self.x_edit.text())
            y = float(self.y_edit.text())
            z = float(self.z_edit.text())
        except:
            self.list_widget.clear()
            self.list_widget.addItem("Please, write correct inputs")
            return
        
        # Perform the transformation and display the result
        if transform == 'WGS84 to ITRF96':
            x_trans, y_trans, z_trans = helmert_transformation(x, y, z, "wgs84_to_itrf96")
        elif transform == 'ITRF96 to WGS84':
            x_trans, y_trans, z_trans = helmert_transformation(x, y, z, "wgs84_to_itrf96", inverse=True)
        elif transform == 'ED50 to ITRF96':
            x_trans, y_trans, z_trans = helmert_transformation(x, y, z, "ed50_to_itrf96")
        elif transform == 'ITRF96 to ED50':
            x_trans, y_trans, z_trans = helmert_transformation(x, y, z, "ed50_to_itrf96", inverse=True)
        else:
            return
       
        result = f'X: {x_trans:.6f}\nY: {y_trans:.6f}\nZ: {z_trans:.6f}'
        self.list_widget.clear()
        self.list_widget.addItem(result)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = DatumTransformWidget()
    widget.show()
    sys.exit(app.exec_())
