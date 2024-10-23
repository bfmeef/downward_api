# downward_api


### 과제: Downward API 를 사용하여 POD 생성

#### 과정

1. github에 신규 repository 생성 (해당 repository)

2. flask 사용하는 python을 생성한다.
* app.py
```
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def get_env_vars():
    pod_name = os.getenv('POD_NAME', 'Unknown POD')
    node_name = os.getenv('NODE_NAME', 'Unknown NODE')
    namespace = os.getenv('POD_NAMESPACE', 'Unknown NAMESPACE')
    return jsonify({
        "pod_name": pod_name,
        "node_name": node_name,
        "namespace": namespace
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

3. Dockerfile 생성
```
FROM python:3.8-slim

# curl 모듈 설치
RUN apt-get update && apt-get install -y curl

# 작업 디렉터리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt requirements.txt
COPY app.py app.py

# Flask 설치
RUN pip install -r requirements.txt

# 앱 실행
CMD ["python", "app.py"]
```

4. Github Action으로 github에 이미지 push (multi platform 지원)
```
name: Publish Docker Multi Platform GitHub image

on:
  workflow_dispatch:
    inputs:
      name:
        description: "Docker TAG"
        required: true
        default: "master"

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Setup QEMU
        uses: docker/setup-qemu-action@v2

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v2  # Buildx 설정 추가

      - name: Install cosign
        if: github.event_name != 'pull_request'
        uses: sigstore/cosign-installer@v3.7.0

      - name: Log into registry ${{ env.REGISTRY }}
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: ${{ github.event.inputs.name }}

      - name: Build and push Docker image
        id: build-and-push
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          platforms: linux/amd64,linux/arm64  # 다중 플랫폼 지원
```

워크플로우 실행하면 프로필 - 패키지에 이미지가 생성됨


5. downward_api.yaml 작성

github에 생성된 도커 이미지로 default namespace에 배포

```
apiVersion: v1
kind: Pod
metadata:
  name: downward-env
spec:
  containers:
  - name: main
    imagePullPolicy: Always
    image: ghcr.io/bfmeef/downward_api:master
    env:
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    ports:
    - containerPort: 5000
```

아래 명령어로 Pod 생성
` kubectl apply -f downward_api.yaml `


6. 결과 확인
` kubectl exec -it downward-env -- curl localhost:5000 `

{"namespace":"default","node_name":"docker-desktop","pod_name":"downward-env"}

이렇게 실행된다.



