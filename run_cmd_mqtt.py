import os
import json
import paho.mqtt.client as mqtt


def load_config(file_name="config.json"):
    with open(file_name, "r") as fp:
        config_file = json.load(fp)
    return config_file


config = load_config()
cmd_exe_sub_topic = config["cmd_sub_topic"]
cmd_exe_pub_topic = config["cmd_pub_topic"]

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect(host=config["broker"], port=int(config["port"]), keepalive=60)


class CommandExecutionMQTT:
    def __init__(self):
        pass

    @staticmethod
    def on_connect(client, userdata, flag, rc):
        print("Result from connect: {}".format(mqtt.connack_string(rc)))
        client.subscribe(cmd_exe_sub_topic, qos=2)

    @staticmethod
    def on_subscribe(client, userdata, mid, granted_qos):
        print("Subscribed with QoS: {}".format(granted_qos[0]))

    def on_message(self, client, userdata, msg):
        self.cmd = str(msg.payload.decode("utf-8", "ignore"))
        print("Message received. Topic: {}. Payload: {}".format(msg.topic, self.cmd))
        self.run_cmd(self.cmd)

    @staticmethod
    def run_cmd(command):
        stream = os.popen(command)
        output = stream.read()
        client.publish(cmd_exe_pub_topic, output)
        print("Message: {}\nSuccessfully Published.".format(output))


if __name__ == '__main__':
    cmdExeMQTT = CommandExecutionMQTT()
    client.on_connect = cmdExeMQTT.on_connect
    client.on_subscribe = cmdExeMQTT.on_subscribe
    client.on_message = cmdExeMQTT.on_message
    while True:
        client.loop_forever()
