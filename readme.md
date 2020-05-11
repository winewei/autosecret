Autosecret
===
autosecret is a tool running in docker/k8s(recommend).

It will helps [Kubernetes](https://kubernetes.io) operator to create [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) via [`config.json`](config-example.json) when someone creates [Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/), and support multiple secrets in one Namespace 

Required
```
Kubernetes Cluster
config.json
RBAC and serviceAccount
kubeconfig
```

K8s
```
kubectl apply -f https://raw.githubusercontent.com/winewei/autosecret/master/all-in-one.yaml
```
Local
```
docker-compose up
```

Full config `config.json`
```
{
  "matchRole": "project-.*-staging",
  "secrets": [
    {
      "name": "mysqluser",
      "type": "Opaque",
      "data": {
        "username": "root",
        "password": "mypassword"
      }
    },
    {
      "name": "ali-docker-user",
      "type": "kubernetes.io/dockerconfigjson",
      "overwrite": true,
      "data": {
        ".dockerconfigjson": {
          "auths": {
            "registry.cn-hongkong.aliyuncs.com": {
              "Username": "alidockeruser",
              "Password": "123456",
              "Email": "test@test.com"
            },
            "registry.cn-shenzhen.aliyuncs.com": {
              "Username": "alidockeruser2",
              "Password": "7890123",
              "Email": "test@test.com"
            }
          }
        }
      }
    }
  ]
}
```

* support `Opaque`
    ```
    {
      "name": "mysqluser",
      "type": "Opaque",
      "data": {
        "username": "root",
        "password": "mypassword"
      }
    }
    ```
  
* support `docker-registry`
    ```
    {
      "name": "ali-docker-user",
      "type": "kubernetes.io/dockerconfigjson",
      "overwrite": true,
      "data": {
        ".dockerconfigjson": {
          "auths": {
            "registry.cn-hongkong.aliyuncs.com": {
              "Username": "alidockeruser",
              "Password": "123456",
              "Email": "test@test.com"
            },
            "registry.cn-shenzhen.aliyuncs.com": {
              "Username": "alidockeruser2",
              "Password": "7890123",
              "Email": "test@test.com"
            }
          }
        }
      }
    }
    ```
* params
    * `matchRole`
        
        setting namespaces match role [syntax](https://docs.python.org/3/library/re.html?highlight=re#module-re)
        ```
        "matchRole": "project-.*-staging"
        ```
    * `name` secret name
    * `overwrite` 
       - if `true`, autosecret will delete old secret and create a new in namespace
       - if `false`, autosecret will skip old secret
       - usual uses in clusters has been created many projects(or namespace)
    * `type` support `Opaque` and `kubernetes.io/dockerconfigjson`

* docker
    - pristtlt/autosecret:v1.0
    - registry.cn-hongkong.aliyuncs.com/sync-dockerimage/autosecret:v1.0
    