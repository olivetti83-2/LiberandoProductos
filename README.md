# PRACTICA FINAL LIBERANDO PRODUCTOS

## Necesario:
 * Python (version => `3.8.5`) - https://python.org/downloads/release/python-385
 * VirtualEnv:

    ```sh
    pip3 install virtualenv || sudo apt-get update && sudo apt-get install -y python3.8-venv
    ```
 
 * Docker: https://docs.docker.com/get-docker


## Servidor:

### Servidor con Python:

 * Instalación: 
   * Obtener versión python: 
    
      ```sh
      python3 --version
      ```

   * Crear VirtualEnv en la raíz: (versión python comando anterior) 

      ```sh
      python3.8 -m venv venv
      ```

 * Activar VirtualEnv: 

    ```sh
    source venv/bin/activate
    ```

 * Instalar librerías (`requirements.txt`):

    ```sh
    pip3 install -r requirements.txt
    ```

 * Arrancar Servidor:

    ```sh
    python3 src/app.py
    ```
 * Mostrará una URL para que puedas acceder:
  
    ```sh
    Running on http://0.0.0.0:8081 (CTRL + C to quit)
    ```

### Servidor con Docker:

 * Creamos imagen Docker:

    ```sh
    docker build -t server:0.0.1
    ```

 * Arrancamos la imagen construída (necesitamos mapear los puertos de FastApi y Prometheus)

    ```sh
    docker run -d -p 8000:8000 -p 8081:8081 --name server server:0.0.1

 * Ejecuta `docker logs -f server` y te aparecerá la URL a la que puedes acceder:

     ```sh
    Running on http://0.0.0.0:8081 (CTRL + C to quit)
    ```

## Para correr los Tests:

 * Corre todos los test:
   
   ```sh
   pytest
   ``` 

 * Corre los test mostrando cobertura:
   
   ```sh
   pytest --cov
   ```

 * Corre los test generando un reporte de cobertura html:

   ```sh
   pytest --cov --cov-report=html
   ```

## Monitorización:

### Prometheus:
#### Software Necesario:
 * Minikube - https://minikube.sigs.k8s.io/docs/
 * Kubectl - https://kubernetes.io/docs/reference/kubectl/kubectl
 * Helm - https://helm.sh

 * Para ver las métricas necesitamos Prometheus que a su vez necesita `minikube`:
   ```sh
   minikube start --kubernetes-version=`v1.21.1` --memory=4096 -p liberando-productos-practica
   ```

 * Añadir repositorio helm
   ```sh
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   ```

 * Desplegar chart Prometheus
   ```sh
   helm -n monitorin upgrade --install prometheus prometheus-community/kube-prometheus-stack -f ./helm/kube-prometheus-stack/custom_values_prometheus.yaml --create-namespace --wait --version 34.1.1

 * Port-forward al service de prometheus - http://localhost:9090
   ```sh
   kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090
   ```

 * Port-forward al service de grafana - http://localhost:3000
   ```sh
   kubectl -n monitoring port-forward svc/prometheus-grafana 3000:80
   ```
 
 * Instalar metrics server
   ```sh
   minikube addons enable metrics-server -p liberando-productos-practica
   ```

 * Añadir repositorio helm bitnami:
   ```sh
   helm repo add bitnami https://charts.bitnami.com/bitnami
   helm repo update
   ```

 * Descargar dependencias:
   ```sh
   helm dep up ./
   ```

 * Desplegar app con helm:
   ```sh
   helm -n liberando-productos-practica upgrade --install my-app --create-namespace --wait helm/fast-api-webapp
   ```
#### Alerta consumo

 * En el yaml de Prometheus en mychart/prometheus está la configuración para la alerta que se lanzará en el canal #pruebas, en mi caso... lo puedes configurar modificando los siguientes valores:

   ```yaml
   receivers:
    - name: 'null'
    - name: 'slack'
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/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' # <--- AÑADIR EN ESTA LÍNEA EL WEBHOOK CREADO
        send_resolved: true
        channel: '#pruebas' # <--- AÑADIR EN ESTA LÍNEA EL CANAL
        title: '[{{ .Status | toUpper }}{{ if eq .Status "firing" }}:{{ .Alerts.Firing | len }}{{ end }}] Monitoring Event Notification'
   ```

##### Funcionamiento de la alerta:

 * Para la comprobación se necesita desactiva HPA, porque sino no funcionará
   ```sh
   helm -n liberando-productos-practica upgrade --install my-app --create-namespace --wait helm/fast-api-webapp --set autoscaling.enabled=false
   ```
 * Obtener el POD
   ```sh
   export POD_NAME=$(kubectl get pods --namespace liberando-productos-practica -l "app.kubernetes.io/name=fast-api-webapp,app.kubernetes.io/instance=my-app" -o jsonpath="{.items[0].metadata.name}")
   ```

 * Nos conectamos al POD
   ```sh
   kubectl -n liberando-productos-practica exec -it $POD_NAME -- /bin/sh
   ```
   * Dentro del POD
      * Instalamos software
         ```sh
         apk update && apk add git go
         ```
      * Descargamos software para prueba de estrés
         ```sh
         git clone https://github.com/jaeg/NodeWrecker.git
         cd NodeWrecker
         go build -o estres main.go
         ```
      * Ejecutamos binario
         ```sh
         ./estres -abuse-memory -escalate -max-duration 10000000
         ```
 *  Primero llega la alerta y después la recuperación:
      (./img/alerta.jpg)

### Grafana

 * Lo primero será importar el dashboard con el archivo liberando_productos_dashboard.yaml en la siguiente dirección http://localhost:3000/dashboard/import

 * Una vez importado se verán las métricas utilizadas

  * Healthcheck
  * Main
  * Agur
  * Total requests
  * Status: con el que obtienes el número de inicios de la app

  * Se verá un dashboard similar a este:
      (./img/grafana.jpg)


















después de esto:
helm -n liberando-productos-practica upgrade --install my-app --create-namespace --wait mychart/fast-api-webapp

1
export POD_NAME=$(kubectl get pods --namespace liberando-productos-practica -l "app.kubernetes.io/name=fast-api-webapp,app.kubernetes.io/instance=my-app" -o jsonpath="{.items[0].metadata.name}")

2
export CONTAINER_PORT=$(kubectl get pod --namespace liberando-productos-practica $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")

3
kubectl --namespace liberando-productos-practica port-forward $POD_NAME 8080:$CONTAINER_PORT