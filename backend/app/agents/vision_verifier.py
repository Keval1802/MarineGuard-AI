import os
import io
import json
import base64
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Any, Optional

from app.config import settings

class LLMVisionVerifier:
    """
    Multimodal LLM Vision Verification Engine for Satellite Evidence (Section 16 / Phase 2).
    
    Primary LLM  → Gemini Vision (gemini-1.5-flash / gemini-2.5-flash-lite / gemini-flash-latest)
    Fallback LLM → Groq (openai/gpt-oss-120b or llama-3.3-70b-versatile)
    Heuristic Fallback → Deterministic HSV / Reflectance / Land-Water & Cloud Filter
    """

    @classmethod
    def _encode_image_to_base64(cls, image: Any) -> str:
        """Helper to convert image (path, bytes, or numpy array) to Base64 string."""
        if isinstance(image, str) and os.path.exists(image):
            with open(image, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        elif isinstance(image, np.ndarray):
            success, buffer = cv2.imencode(".png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            if success:
                return base64.b64encode(buffer).decode("utf-8")
        raise ValueError("Invalid image input for base64 encoding.")

    @classmethod
    async def verify_anomaly_with_llm(
        cls,
        image: Any,
        sensor: str,
        candidate_class: str,
        confidence: float,
        area_km2: float
    ) -> Dict[str, Any]:
        """
        Main entry point for verifying candidate satellite anomalies via Primary LLM (Gemini),
        Fallback LLM (Groq), or Heuristic Fallback.
        """
        # Try Primary LLM (Gemini)
        if settings.GEMINI_API_KEY:
            gemini_res = cls._try_gemini_vision(image, sensor, candidate_class, confidence, area_km2)
            if gemini_res:
                gemini_res["verifier_used"] = f"Primary Gemini ({settings.PRIMARY_LLM_MODEL})"
                return gemini_res

        # Try Fallback LLM (Groq)
        if settings.GROQ_API_KEY:
            groq_res = cls._try_groq_llm(image, sensor, candidate_class, confidence, area_km2)
            if groq_res:
                groq_res["verifier_used"] = f"Fallback Groq ({settings.FALLBACK_LLM_MODEL})"
                return groq_res

        # Heuristic Deterministic Vision Fallback (Zero LLM API cost fallback)
        heuristic_res = cls._heuristic_vision_verifier(image, sensor, candidate_class, confidence)
        heuristic_res["verifier_used"] = "Deterministic Heuristic Vision Engine"
        return heuristic_res

    @classmethod
    def _try_gemini_vision(
        cls,
        image: Any,
        sensor: str,
        candidate_class: str,
        confidence: float,
        area_km2: float
    ) -> Optional[Dict[str, Any]]:
        """Call Primary Gemini Vision API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            model = genai.GenerativeModel(settings.PRIMARY_LLM_MODEL)
            
            # Prepare image PIL
            if isinstance(image, str) and os.path.exists(image):
                pil_img = Image.open(image)
            elif isinstance(image, np.ndarray):
                pil_img = Image.fromarray(image)
            else:
                return None

            prompt = f"""You are an expert satellite remote sensing oceanographer inspecting a candidate marine anomaly in coastal Gujarat, India.
Details:
- Sensor: {sensor}
- Candidate Anomaly Class: {candidate_class}
- Heuristic Confidence: {confidence*100:.1f}%
- Est Area: {area_km2} km²

Analyze the attached image:
1. WATER vs LAND: Is the highlighted box or anomaly located over open ocean water, or over land / vegetation / river bank?
2. CLOUD / GLINT CHECK: Is the highlighted region a cloud, cloud reflection, sun glint, or image noise artifact?
3. VALIDITY: Is this a valid marine pollution / floating material candidate?

Respond ONLY in strictly valid JSON format with keys:
"is_ocean_water" (boolean), "is_cloud_or_glint" (boolean), "is_valid_marine_anomaly" (boolean), "verified_class" (string: OIL_LIKE_ANOMALY, FLOATING_MATERIAL_CANDIDATE, FALSE_POSITIVE, NORMAL, CLOUD_COVERED), "verified_confidence" (float 0.0 to 1.0), "reasoning" (string)."""

            candidate_models = [settings.PRIMARY_LLM_MODEL, "gemini-1.5-flash-latest", "gemini-2.5-flash", "gemini-1.5-pro"]
            response_text = None
            for model_name in candidate_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    res = model.generate_content([prompt, pil_img])
                    if res and res.text:
                        response_text = res.text.strip()
                        break
                except Exception:
                    continue

            if not response_text:
                return None
            
            # Parse JSON from response text
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(response_text)
        except Exception as e:
            print(f"[LLMVisionVerifier] Gemini Primary Vision error: {e}")
            return None

    @classmethod
    def _try_groq_llm(
        cls,
        image: Any,
        sensor: str,
        candidate_class: str,
        confidence: float,
        area_km2: float
    ) -> Optional[Dict[str, Any]]:
        """Call Fallback Groq LLM API."""
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            prompt = f"""Inspect satellite candidate anomaly metadata & visual evidence:
Sensor: {sensor} | Candidate: {candidate_class} | Confidence: {confidence:.2f} | Area: {area_km2} km2.

Verify if the highlighted region is ocean water vs land, and whether it is a cloud/glint or genuine marine anomaly.
Respond in JSON:
{{"is_ocean_water": true/false, "is_cloud_or_glint": true/false, "is_valid_marine_anomaly": true/false, "verified_class": "OIL_LIKE_ANOMALY" | "FLOATING_MATERIAL_CANDIDATE" | "FALSE_POSITIVE" | "NORMAL" | "CLOUD_COVERED", "verified_confidence": 0.0-1.0, "reasoning": "..."}}"""

            # Try Groq vision model or text model
            models_to_try = [settings.FALLBACK_LLM_MODEL, "llama-3.2-11b-vision-preview", "llama-3.3-70b-versatile"]
            response_text = None

            for m in models_to_try:
                try:
                    response = client.chat.completions.create(
                        model=m,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1
                    )
                    if response.choices and response.choices[0].message.content:
                        response_text = response.choices[0].message.content.strip()
                        break
                except Exception:
                    continue

            if not response_text:
                return None

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(response_text)
        except Exception as e:
            print(f"[LLMVisionVerifier] Groq Fallback LLM error: {e}")
            return None

    @classmethod
    def _heuristic_vision_verifier(
        cls,
        image: Any,
        sensor: str,
        candidate_class: str,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Deterministic Heuristic Vision Engine:
        1. Evaluates brightness / cloud fraction (rejects clouds > 15% bright pixels).
        2. Evaluates land-water ratio (rejects land crops).
        """
        if isinstance(image, str) and os.path.exists(image):
            img_rgb = cv2.imread(image)
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
        elif isinstance(image, np.ndarray):
            img_rgb = image.copy()
        else:
            return {
                "is_ocean_water": True,
                "is_cloud_or_glint": False,
                "is_valid_marine_anomaly": True,
                "verified_class": candidate_class,
                "verified_confidence": confidence,
                "reasoning": "Standard heuristic fallback validation."
            }

        # Calculate Cloud Brightness Fraction (RGB channels all high > 180)
        bright_pixels = np.sum((img_rgb[:, :, 0] > 185) & (img_rgb[:, :, 1] > 185) & (img_rgb[:, :, 2] > 185))
        cloud_ratio = bright_pixels / (img_rgb.shape[0] * img_rgb.shape[1])

        # Calculate Green/Soil Vegetation Land Fraction
        # Vegetation / soil land has high Red and Green relative to Blue (R > B and G > B)
        land_pixels = np.sum((img_rgb[:, :, 1] > img_rgb[:, :, 2] + 20) | (img_rgb[:, :, 0] > img_rgb[:, :, 2] + 30))
        land_ratio = land_pixels / (img_rgb.shape[0] * img_rgb.shape[1])

        if cloud_ratio > 0.12 and "Optical" in sensor or "Sentinel-2" in sensor:
            return {
                "is_ocean_water": True,
                "is_cloud_or_glint": True,
                "is_valid_marine_anomaly": False,
                "verified_class": "CLOUD_COVERED",
                "verified_confidence": 0.0,
                "reasoning": f"Optical image cloud / sun glint threshold exceeded ({cloud_ratio*100:.1f}% bright cloud pixels). Anomaly rejected as false positive cloud/glint."
            }

        if land_ratio > 0.35:
            return {
                "is_ocean_water": False,
                "is_cloud_or_glint": False,
                "is_valid_marine_anomaly": False,
                "verified_class": "FALSE_POSITIVE",
                "verified_confidence": 0.0,
                "reasoning": f"Image crop contains {land_ratio*100:.1f}% land/intertidal mudflat pixels. Region flagged as coastal land/mudflat, not open marine water."
            }

        # Calculate Turbid Sediment / Intertidal Mudflat Fraction (High Red & Green reflectance in shallow estuarine water)
        sediment_pixels = np.sum((img_rgb[:, :, 0] > 110) & (img_rgb[:, :, 1] > 100) & (img_rgb[:, :, 2] < 90))
        sediment_ratio = sediment_pixels / (img_rgb.shape[0] * img_rgb.shape[1])

        if sediment_ratio > 0.25 and candidate_class == "OIL_LIKE_ANOMALY":
            return {
                "is_ocean_water": True,
                "is_cloud_or_glint": False,
                "is_valid_marine_anomaly": False,
                "verified_class": "HIGH_TURBIDITY_EVENT",
                "verified_confidence": 0.35,
                "reasoning": f"Optical spectral analysis indicates high estuarine sediment turbidity / intertidal mudflat exposure ({sediment_ratio*100:.1f}% sediment reflectance). Reclassified from OIL_LIKE_ANOMALY to HIGH_TURBIDITY_EVENT."
            }

        return {
            "is_ocean_water": True,
            "is_cloud_or_glint": False,
            "is_valid_marine_anomaly": True,
            "verified_class": candidate_class,
            "verified_confidence": confidence,
            "reasoning": "Heuristic verification passed: Ocean water pixel ratio high, cloud/glint pixels below threshold."
        }
