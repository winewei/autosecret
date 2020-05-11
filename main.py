from kubernetes import client, config, watch
import logging, json, base64, time, re
from pprint import pprint as print

# 1, watch 每个namespace的事件，发现有创建ns时就在这个ns中自动添加一个指定的secret, 比如添加一个docker-registy
# 2.

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s",
                    datefmt = '%Y-%m-%d  %H:%M:%S %a')

try:
    f = open('config.json', 'r')
    configdata = json.loads(f.read())
except:
    logging.info("Load json or file error")
    raise
finally:
    f.close()

for secret in configdata["secrets"]:
    for k in secret["data"]:
        if k == ".dockerconfigjson":
            secret["data"][k] = base64.b64encode(json.dumps(secret["data"][k]).encode()).decode()
        else:
            secret["data"][k] = base64.b64encode(secret["data"][k].encode("utf-8")).decode("utf-8")

def main():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config('~/.kube/config')

    v1 = client.CoreV1Api()
    watch_ns = watch.Watch()
    for event in watch_ns.stream(v1.list_namespace):
        if event["type"] == "ADDED":
            time.sleep(0.05)
            sec_namespace = event["object"].metadata.name
            if configdata.get("matchRole") and re.match(pattern=configdata.get("matchRole"), string=sec_namespace):
                logging.info("Fetch a new namespace: %s" % sec_namespace)
                for secret in configdata["secrets"]:
                    logging.info("Take Secret: %s in config file" % secret.get("name"))

                    secret_instance = client.CoreV1Api()
                    sec = client.V1Secret()
                    sec.metadata = client.V1ObjectMeta(name=secret.get("name"))
                    sec.type = secret.get("type")
                    sec.data = secret.get("data")

                    if secret.get("overwrite"):
                        # Delete old secret
                        try:
                            logging.info("Delete old Secret: %s in namesapce: %s" % (secret["name"], sec_namespace))
                            secret_instance.delete_namespaced_secret(namespace=sec_namespace, name=secret["name"])
                        except:
                            logging.error("Delete old Secret: %s in namespace: %s error!" % (secret["name"], sec_namespace))
                            pass
                    try:
                        logging.info("Create Secret: %s in namespace: %s" % (secret["name"], sec_namespace))
                        secret_instance.create_namespaced_secret(namespace=sec_namespace, body=sec)
                    except:
                        logging.error("Create Secret: %s in namespace: %s error!" % (secret["name"], sec_namespace))
                        continue

if __name__ == "__main__":
    main()