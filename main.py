# encoding: utf-8
from kubernetes import client, config, watch
import logging, json, base64, time, re

VERSION=1.1

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

# base64 encode secrets values.
for secret in configdata["secrets"]:
    for k in secret["data"]:
        if k == ".dockerconfigjson":
            secret["data"][k] = base64.b64encode(json.dumps(secret["data"][k]).encode("utf-8")).decode("utf-8")
        else:
            secret["data"][k] = base64.b64encode(secret["data"][k].encode("utf-8")).decode("utf-8")

def main():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config('~/.kube/config')

    v1 = client.CoreV1Api()
    watch_ns = watch.Watch()

    logging.info("Autosecret started.")
    # k8s watch api will limits responses, is's 3.
    for event in watch_ns.stream(v1.list_namespace):
        if event["type"] == "ADDED":
            time.sleep(0.05)
            sec_namespace = event["object"].metadata.name
            # matchRole is a py Regular syntax, will matchs namespaces.
            if configdata.get("matchRole") and re.match(pattern=configdata.get("matchRole"), string=sec_namespace):
                logging.info("Fetch a new namespace: %s" % sec_namespace)
                for secret in configdata["secrets"]:
                    logging.info("Take Secret: %s in config file" % secret.get("name"))
                    secret_instance = client.CoreV1Api()
                    sec = client.V1Secret()
                    sec.metadata = client.V1ObjectMeta(name=secret.get("name"))
                    sec.type = secret.get("type")
                    sec.data = secret.get("data")

                    # when secret setting `overwrite: true` , that will try to delete old secrets in each namespaces
                    if secret.get("overwrite"):
                        # Delete old secret
                        try:
                            secret_instance.delete_namespaced_secret(namespace=sec_namespace, name=secret["name"])
                            logging.info("Delete old Secret: %s in namesapce: %s success!" % (secret["name"], sec_namespace))
                        except client.rest.ApiException as e:
                            logging.error("%s in namespace: %s" % (json.loads(e.body)['message'], sec_namespace))
                    try:
                        secret_instance.create_namespaced_secret(namespace=sec_namespace, body=sec)
                        logging.info("Create Secret: %s in namespace: %s success!" % (secret["name"], sec_namespace))
                    except client.rest.ApiException as e:
                        logging.error("%s in namespace: %s" % (json.loads(e.body)['message'], sec_namespace))

if __name__ == "__main__":
    main()