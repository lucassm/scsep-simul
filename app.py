from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from pyModbusTCP.server import DataBank, ModbusServer
import random
import threading
from time import sleep

# --- CONFIGURATION ---
MODBUS_HOST = "0.0.0.0"
MODBUS_PORT = 8080
WEB_PORT = 5000
ACCESS_CODE = "4251"

REGISTER_NAMES = [
    "Corrente TC 69,0 kV fase A", "Corrente TC 69,0 kV fase B", "Corrente TC 69,0 kV fase C",
    "Tensão TP 69,0 kV fase A", "Tensão TP 69,0 kV fase B", "Tensão TP 69,0 kV fase C",
    "Corrente TC Trafo lado 69,0 kV fase A", "Corrente TC Trafo lado 69,0 kV fase B", "Corrente TC Trafo lado 69,0 kV fase C",
    "Corrente TC Trafo lado 13,8 kV fase A", "Corrente TC Trafo lado 13,8 kV fase B", "Corrente TC Trafo lado 13,8 kV fase C",
    "Corrente TC 13,8 kV fase A", "Corrente TC 13,8 kV fase B", "Corrente TC 13,8 kV fase C",
    "Tensão TP 13,8 kV fase A", "Tensão TP 13,8 kV fase B", "Tensão TP 13,8 kV fase C"
]

# Modbus Setup
my_data_bank = DataBank(coils_size=40, h_regs_size=18)
my_server = ModbusServer(host=MODBUS_HOST, port=MODBUS_PORT, data_bank=my_data_bank, no_block=True)

app = Flask(__name__, static_url_path='/scsep/static')

# Isso é OBRIGATÓRIO para o url_for funcionar com Nginx em VMs separadas
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

@app.route('/scsep/admin')
def index():
    return render_template('index.html', access_code=ACCESS_CODE, register_names=REGISTER_NAMES)

@app.route('/scsep/update_coil', methods=['POST'])
def update_coil():
    data = request.get_json()
    my_data_bank.set_coils(address=int(data['id']), bit_list=[bool(data['value'])])
    return jsonify(success=True)

@app.route('/scsep/view')
def student_view():
    # É fundamental passar o register_names aqui também!
    return render_template('view.html', register_names=REGISTER_NAMES)

@app.route('/scsep/get_system_data')
def get_system_data():
    regs = my_data_bank.get_holding_registers(0, 18) or [0]*18
    coils = my_data_bank.get_coils(0, 40) or [0]*40
    return jsonify(registers=regs, coils=coils)

def background_task():
    while True:
        my_data_bank.set_holding_registers(0, [random.randint(40, 50) for _ in range(0, 3)])
        my_data_bank.set_holding_registers(3, [random.randint(39799, 39899) for _ in range(0, 3)])
        my_data_bank.set_holding_registers(6, [random.randint(40, 50) for _ in range(0, 3)])
        my_data_bank.set_holding_registers(9, [random.randint(150, 160) for _ in range(0, 3)])
        my_data_bank.set_holding_registers(12, [random.randint(150, 160) for _ in range(0, 3)])
        my_data_bank.set_holding_registers(15, [random.randint(7899, 7999) for _ in range(0, 3)])

        sleep(2)

if __name__ == '__main__':
    my_server.start()
    threading.Thread(target=background_task, daemon=True).start()
    app.run(host='0.0.0.0', port=WEB_PORT, debug=False)
