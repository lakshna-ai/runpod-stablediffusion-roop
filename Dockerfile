FROM alpine/git:2.36.2 as download

COPY builder/clone.sh /clone.sh

RUN . /clone.sh stable-diffusion-stability-ai https://github.com/Stability-AI/stablediffusion.git cf1d67a6fd5ea1aa600c4df58e5b47da45f6bdbf && rm -rf assets data/**/*.png data/**/*.jpg data/**/*.gif
RUN . /clone.sh CodeFormer https://github.com/sczhou/CodeFormer.git c5b4593074ba6214284d6acd5f1719b6c5d739af && rm -rf assets inputs
RUN . /clone.sh BLIP https://github.com/salesforce/BLIP.git 48211a1594f1321b00f14c9f7a5b4813144b2fb9
RUN . /clone.sh k-diffusion https://github.com/crowsonkb/k-diffusion.git ab527a9a6d347f364e3d185ba6d714e22d80cb3c
RUN . /clone.sh clip-interrogator https://github.com/pharmapsychotic/clip-interrogator 2cf03aaf6e704197fd0dae7c7f96aa59cf1b11c9
RUN . /clone.sh generative-models https://github.com/Stability-AI/generative-models 45c443b316737a4ab6e40413d7794a7f5657c19f

FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive PIP_PREFER_BINARY=1
RUN --mount=type=cache,target=/var/cache/apt \
  apt-get update && \
  apt-get install -y wget fonts-dejavu-core rsync git jq moreutils aria2 \
  ffmpeg libglfw3-dev libgles2-mesa-dev pkg-config libcairo2 libcairo2-dev build-essential

WORKDIR /
RUN --mount=type=cache,target=/root/.cache/pip \
  wget -O model.safetensors https://civitai.com/api/download/models/126688 && \
  git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git && \
  cd stable-diffusion-webui && \
  git reset --hard 4afaaf8a020c1df457bcf7250cb1c7f609699fa7 && \
  pip install -r requirements_versions.txt && \
  git clone https://github.com/Gourieff/sd-webui-reactor extensions/sd-webui-reactor && \
  git clone https://github.com/lakshna-ai/sd-dynamic-prompts extensions/sd-dynamic-prompts && \
  mkdir -p models/insightface && wget -O models/insightface/inswapper_128.onnx https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx && \
  pip install -r extensions/sd-webui-reactor/requirements.txt && \
  wget -O models/VAE-approx/vaeapprox-sdxl.pt https://github.com/AUTOMATIC1111/stable-diffusion-webui/releases/download/v1.0.0-pre/vaeapprox-sdxl.pt && \
  mkdir -p models/Codeformer && wget -O models/Codeformer/codeformer-v0.1.0.pth https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth && \
  mkdir -p repositories/CodeFormer/weights/facelib && wget -O repositories/CodeFormer/weights/facelib/parsing_parsenet.pth https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/parsing_parsenet.pth && \
  wget -O repositories/CodeFormer/weights/facelib/detection_Resnet50_Final.pth https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth

ENV ROOT=/stable-diffusion-webui

COPY --from=download /repositories/ ${ROOT}/repositories/

RUN mkdir ${ROOT}/interrogate && cp ${ROOT}/repositories/clip-interrogator/clip_interrogator/data/* ${ROOT}/interrogate
RUN --mount=type=cache,target=/root/.cache/pip \
  pip install -r ${ROOT}/repositories/CodeFormer/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
  pip install pyngrok xformers runpod \
  git+https://github.com/TencentARC/GFPGAN.git@8d2447a2d918f8eba5a4a01463fd48e45126a379 \
  git+https://github.com/openai/CLIP.git@d50d76daa670286dd6cacf3bcd80b5e4823fc8e1 \
  git+https://github.com/mlfoundations/open_clip.git@v2.20.0

RUN sed -i 's/in_app_dir = .*/in_app_dir = True/g' /opt/conda/lib/python3.10/site-packages/gradio/routes.py && git config --global --add safe.directory '*'

COPY src/start.sh /start.sh
COPY src/rp_handler.py /rp_handler.py
COPY builder/cache.py /stable-diffusion-webui/cache.py
RUN cd /stable-diffusion-webui && python cache.py --use-cpu=all --ckpt /model.safetensors

# Cleanup section (Worker Template)
RUN apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
      pip install onnxruntime-gpu dynamicprompts send2trash
ADD src/test_input.json .
RUN chmod +x /start.sh
CMD /start.sh
