#!flask/bin/python
from flask import Flask, request, logging
from KNX import *
import logging

app = Flask(__name__)

@app.route('/store/<int:floor_id>/<int:store_id>', methods=['POST'], strict_slashes=False)
def setStore(floor_id, store_id):
    # Example values: 200 2 2 3/4/1
    content = request.get_json()
    value = int(int(content['value']) * 255 / 100)
    size = int(content['size']) #'2'
    acpi = '2'
    group = '3/' + str(floor_id) + '/' + str(store_id)
    res = process(value, size, acpi, group)
    return res

@app.route('/radiator/<int:floor_id>/<int:radiator_id>', methods=['POST'], strict_slashes=False)
def setRadiator(floor_id, radiator_id):
    # 200 2 2 3/4/1
    content = request.get_json()
    value = int(int(content['value']) * 255 / 100)
    size = int(content['size'])#'2'
    acpi = '2'
    group = '0/' + str(floor_id) + '/' + str(radiator_id)
    res = process(value, size, acpi, group)
    return res

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('hello')
    app.run(host='::', debug=True, port=5500)
