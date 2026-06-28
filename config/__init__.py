import os
import json
import base64
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
# FUNCTII PENTRU IMAGINI
# ============================================================

def generate_image(client, model_cfg, prompt, size="1024x1024", n=1):
    response = client.images.generate(
        model=model_cfg["model_id"],
        prompt=prompt,
        size=size,
        n=n,
        response_format="b64_json"
    )
    return [img.b64_json for img in response.data]


def edit_image(client, model_cfg, image_path, prompt, mask_path=None):
    with open(image_path, "rb") as img_file:
        if mask_path:
            with open(mask_path, "rb") as mask_file:
                response = client.images.edit(
                    model=model_cfg["model_id"],
                    image=img_file,
                    mask=mask_file,
                    prompt=prompt,
                    response_format="b64_json"
                )
        else:
            response = client.images.edit(
                model=model_cfg["model_id"],
                image=img_file,
                prompt=prompt,
                response_format="b64_json"
            )
    return [img.b64_json for img in response.data]


def b64_to_image(b64_string):
    return base64.b64decode(b64_string)

def create_image_mask(image_path, mask_path=None):
    """
    Creează o mască alb-negru pentru editare imagine.
    Dacă nu se specifică mask_path, returnează doar imaginea.
    """
    from PIL import Image
    import numpy as np
    
    img = Image.open(image_path).convert("RGBA")
    
    if mask_path and os.path.exists(mask_path):
        mask = Image.open(mask_path).convert("L")
        return img, mask
    
    # Mască implicită transparentă (editează tot)
    mask = Image.new("L", img.size, 255)
    return img, mask


def resize_image_for_api(image_path, max_size=1024):
    """
    Redimensionează imaginea pentru API (limită de dimensiune).
    """
    from PIL import Image
    
    img = Image.open(image_path)
    
    # Păstrează aspect ratio
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    
    # Salvează temporar
    temp_path = image_path.replace(".", "_resized.")
    img.save(temp_path, format="PNG")
    
    return temp_path
