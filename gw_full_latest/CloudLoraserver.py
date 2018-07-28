#!/usr/bin/env python2

import base64
import json
import os
import subprocess
import sys

import key_Loraserver


gwconf_filename = "gateway_conf.json"

with open(os.path.expanduser(gwconf_filename), "r") as f:
    gw_json_array = json.loads(f.read())


def main(ldata, pdata, rdata, tdata, gwid):
    arr = map(int, pdata.split(','))
    dst = arr[0]
    ptype = arr[1]
    src = arr[2]
    seq = arr[3]
    datalen = arr[4]
    snr = arr[5]
    rssi = arr[6]

    arr = map(int, rdata.split(','))
    bw = arr[0]
    cr = arr[1]
    sf = arr[2]

    rx_topic = 'gateway/{gwid}/rx'.format(gwid=gwid)
    stats_topic = 'gateway/{gwid}/stats'.format(gwid=gwid)

    rx_data = {'rxInfo': {
                    'mac': gwid,
                    'time': tdata,
                    #'timestamp': 0,  # TODO
                    'frequency': gw_json_array['radio_conf']['freq'],
                    'channel': gw_json_array['radio_conf']['ch'],
                    'rfChain': 1,
                    'crcStatus': 1,
                    'codeRate': "4/{}".format(cr),
                    'rssi': rssi,
                    'loRaSNR': snr,
                    'size': datalen,
                    'dataRate': {'modulation': 'LORA', 'spreadFactor': sf, 'bandwidth': bw},
                    'board': 0,
                    'antenna': 0
                },
                'phyPayload': base64.b64encode(ldata)
              }  # NOQA

    p = subprocess.Popen(['mosquitto_pub', '-h', key_Loraserver.MQTT_server, '-t', rx_topic, '-m', json.dumps(rx_data)])
    p.communicate()

    if p.returncode != 0:
        sys.exit(1)

    gateway_data = {'mac': gwid,
                    'time': tdata,
                    'altitude': -1,
                    'rxPacketsReceived': 1,
                    'rxPacketsReceivedOK': 1,  # TODO
                    'txPacketsReceived': 0,  # TODO
                    'txPacketsEmitted': 0
                    }
    try:
        gw_lat = float(gw_json_array['gateway_conf']['ref_latitude'])
        gw_lon = float(gw_json_array['gateway_conf']['ref_longitude'])

        gateway_data['latitude'] = gw_lat
        gateway_data['longitude'] = gw_lon

    except ValueError:
        pass

    p = subprocess.Popen(['mosquitto_pub', '-h', key_Loraserver.MQTT_server, '-t', stats_topic, '-m', json.dumps(gateway_data)])
    p.communicate()

    if p.returncode != 0:
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
