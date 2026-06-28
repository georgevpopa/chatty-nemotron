import os
import json
import base64
import requests
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "providers.json")


def load_providers_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_available_models(config):
    available = []
    for provider in config["providers"]:
        api_key = os.getenv(provider["env_key"])
        if not api_key:
            continue

        provider_type = provider.get("type", "openai")

        for model in provider["models"]:
            model_cfg = {
                "provider": provider["name"],
                "provider_type": provider_type,
                "model_id": model["id"],
                "label": model["label"],
                "description": model.get("description", ""),
                "base_url": provider["base_url"],
                "env_key": provider["env_key"],
                "api_key": api_key,
                "stream_parser": model.get("stream_parser", "standard"),
                "features": model.get("features", []),
            }
            model_cfg["default_params"] = provider.get("default_params", {}).copy()
            model_cfg["default_params"].update(model.get("default_params", {}))
            available.append(model_cfg)
    return available


def get_client_for_model(model_config):
    return OpenAI(
        base_url=model_config["base_url"],
        api_key=model_config["api_key"]
    )


def build_chat_params(model_cfg, messages, **overrides):
    params = {
        "model": model_cfg["model_id"],
        "messages": messages,
        "stream": True,
    }

    defaults = model_cfg.get("default_params", {})
    params.update(defaults)

    for key, val in overrides.items():
        if val is not None:
            params[key] = val

    if "extra_body" in overrides and "extra_body" in defaults:
        merged = defaults["extra_body"].copy()
        merged.update(overrides["extra_body"])
        params["extra_body"] = merged
    elif "extra_body" in overrides:
        params["extra_body"] = overrides["extra_body"]

    return params


def stream_chat(client, model_cfg, messages, **overrides):
    params = build_chat_params(model_cfg, messages, **overrides)
    completion = client.chat.completions.create(**params)
    parser = model_cfg.get("stream_parser", "standard")

    for chunk in completion:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        if parser == "reasoning":
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                yield ("reasoning", reasoning)

        content = getattr(delta, "content", None)
        if content:
            yield ("content", content)


def get_fallback_chain(available_models, selected_label):
    if selected_label == "Auto (Fallback automat)":
        return available_models

    for m in available_models:
        if m["label"] == selected_label or m["model_id"] == selected_label:
            return [m]

    return available_models


# ============================================================
# FUNCTII PENTRU IMAGINI - NVIDIA NIM OPENAI-COMPATIBLE API
# ============================================================
# Endpoint: https://integrate.api.nvidia.com/v1/images/generations
# Endpoint edit: https://integrate.api.nvidia.com/v1/images/edits
# Documentatie: https://docs.nvidia.com/nim/visual-genai/latest/getting-started.html

def generate_image(model_cfg, prompt, size="1024x1024", n=1):
    """
    Genereaza imagini folosind NVIDIA NIM OpenAI-compatible API.
    Endpoint: POST https://integrate.api.nvidia.com/v1/images/generations
    Suporta: FLUX.1-schnell, FLUX.1-dev, Stable Diffusion XL, etc.
    """

    model_id = model_cfg["model_id"]
    api_key = model_cfg["api_key"]

    # Endpoint OpenAI-compatible pentru generare imagini
    endpoint = "https://integrate.api.nvidia.com/v1/images/generations"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Parseaza dimensiunea
    width, height = map(int, size.split("x"))

    # Payload OpenAI-compatible
    payload = {
        "model": model_id,
        "prompt": prompt,
        "n": n,
        "response_format": "b64_json",
        "seed": 0
    }

    # Adauga parametri specifici modelului in extra_body
    extra = {}
    defaults = model_cfg.get("default_params", {})

    # FLUX.1-schnell: steps=4 (implicit)
    # FLUX.1-dev: steps=50, guidance_scale=3.5
    if "schnell" in model_id:
        extra["steps"] = 4
    elif "dev" in model_id:
        extra["steps"] = defaults.get("steps", 50)
        extra["guidance_scale"] = defaults.get("guidance_scale", 3.5)

    if extra:
        payload["extra_body"] = extra

    # Request
    response = requests.post(endpoint, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        raise Exception(f"Image generation failed: {response.status_code} - {response.text[:500]}")

    result = response.json()

    # Extrage base64 din format OpenAI (data[0].b64_json)
    images_b64 = []
    if "data" in result:
        for item in result["data"]:
            if "b64_json" in item:
                images_b64.append(item["b64_json"])
    elif "artifacts" in result:
        for artifact in result["artifacts"]:
            if "base64" in artifact:
                images_b64.append(artifact["base64"])

    return images_b64


def edit_image(model_cfg, image_path, prompt, mask_path=None):
    """
    Editeaza imagine folosind NVIDIA NIM OpenAI-compatible API.
    Endpoint: POST https://integrate.api.nvidia.com/v1/images/edits
    NOTA: Editarea nu e suportata de toate modelele.
    """

    model_id = model_cfg["model_id"]
    api_key = model_cfg["api_key"]

    # Endpoint OpenAI-compatible pentru editare imagini
    endpoint = "https://integrate.api.nvidia.com/v1/images/edits"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    # Pentru editare, folosim multipart/form-data (OpenAI format)
    files = {
        "image": open(image_path, "rb")
    }

    data = {
        "model": model_id,
        "prompt": prompt,
        "n": 1,
        "response_format": "b64_json",
        "seed": 0
    }

    if mask_path:
        files["mask"] = open(mask_path, "rb")

    try:
        response = requests.post(endpoint, headers=headers, data=data, files=files, timeout=120)

        if response.status_code != 200:
            raise Exception(f"Image editing failed: {response.status_code} - {response.text[:500]}")

        result = response.json()

        images_b64 = []
        if "data" in result:
            for item in result["data"]:
                if "b64_json" in item:
                    images_b64.append(item["b64_json"])
        elif "artifacts" in result:
            for artifact in result["artifacts"]:
                if "base64" in artifact:
                    images_b64.append(artifact["base64"])

        return images_b64
    finally:
        for f in files.values():
            f.close()


def b64_to_image(b64_string):
    return base64.b64decode(b64_string)


def create_image_mask(image_path, mask_path=None):
    """
    Creeaza o masca alb-negru pentru editare imagine.
    """
    from PIL import Image
    import numpy as np

    img = Image.open(image_path).convert("RGBA")

    if mask_path and os.path.exists(mask_path):
        mask = Image.open(mask_path).convert("L")
        return img, mask

    # Masca implicita transparenta (editeaza tot)
    mask = Image.new("L", img.size, 255)
    return img, mask


def resize_image_for_api(image_path, max_size=1024):
    """
    Redimensioneaza imaginea pentru API (limita de dimensiune).
    """
    from PIL import Image

    img = Image.open(image_path)

    # Pastreaza aspect ratio
    img.thumbnail((max_size, max_size), Image.LANCZOS)

    # Salveaza temporar
    temp_path = image_path.replace(".", "_resized.")
    img.save(temp_path, format="PNG")

    return temp_path
