#!flask/bin/python
from flask import Flask, request
from KNX import *

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/store/<int:store_id>', methods=['POST'], strict_slashes=False)
def setStores(store_id):
    #200 2 2 3/4/1
    content = request.get_json()
    if all(item in content.keys() for item in ['value']):
        value = int(content['value']) * 255/100
        size = 2
        acpi = 2
        group = '3/4/' + store_id
        command = value + ' ' + size + ' ' + acpi + ' ' + group
        process(command)
    return 'wrong input'

#######################################################################################################################
############# BEACONS #################################################################################################
#######################################################################################################################
### THESE METHODS WERE SPECIALLY MADE FOR BEACONS ################################################################
#######################################################################################################################

"""
@api {get} /beacon/<node_id>  get_beacon_devices
@apiName get_beacon_devices
@apiGroup Beacon


@apiParam {Number} major_id Beacon's major ID


@apiSuccess {String} Network_Home_ID Network's ID

@apiSuccess {JSON} Node_<Number> A JSON containing node's information (for each node). See below

@apiSuccess {boolean} Is_Ready Node status

@apiSuccess {String[]} Neighbours Node's neighbours

@apiSuccess {Number} Node_ID Node's ID

@apiSuccess {String} Node_location Node's location

@apiSuccess {String} Node_name Node's name

@apiSuccess {String} Product_name Node's product name

@apiSuccess {String} Query_stage Node object's readiness stage. Once it's at "Complete" stage, the Node object is ready to be used.

@apiSuccess {Number} Query_stage_(%)  Node object's readiness stage (pourcentage). Once it's at 100%, the Node object is ready to be used.





@apiSuccessExample {json} Example of result in case of success:
{
"Network Home ID": "0xe221b13f",
"Node 1": {
    "Is Ready": true,
    "Neighbours": "2",
    "Node ID": "1",
    "Node location": "",
    "Node name": "",
    "Product name": "Z-Stick Gen5",
    "Query Stage": "Complete",
    "Query Stage (%)": "100 %"
  },
"Node 2": {
    "Is Ready": true,
    "Neighbours": "1",
    "Node ID": "2",
    "Node location": "",
    "Node name": "",
    "Product name": "MultiSensor 6",
    "Query Stage": "Complete",
    "Query Stage (%)": "100 %"
  }
}



@apiDescription Gets information about the Z-Wave network in a JSON format
"""

'''
@app.route('/beacon/<int:major_id>', strict_slashes=False)
def get_beacon_devices(major_id):
    return beacons.get_beacon_devices(major_id)
'''

if __name__ == '__main__':
    app.run(debug=True, port='5500')

