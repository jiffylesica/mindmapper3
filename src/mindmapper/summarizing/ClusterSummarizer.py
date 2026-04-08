import json
import os
from typing import Iterable
import cohere

from utils.env_get_helper import get_env_var

COHERE_API_KEY_ENV = "COHERE_API_KEY"
COHERE_SUMMARY_MODEL_ENV = "COHERE_SUMMARY_MODEL"
SUMMARY_MODEL_NAME = os.getenv(COHERE_SUMMARY_MODEL_ENV, "command-r-08-2024")
MAX_CHUNKS_PER_CLUSTER = 8
MAX_CHARS_PER_CHUNK = 700


class ClusterSummarizer:
    def __init__(self):
        self.co = cohere.ClientV2(api_key=get_env_var(COHERE_API_KEY_ENV))

    def summarize_clusters(self, cluster_chunks: dict[int, list[str]]) -> dict[int, str]:
        if not cluster_chunks:
            return {}

        prompt = self._build_prompt(cluster_chunks)
        fallback = {
            cluster_id: f"Cluster {cluster_id}: Summary unavailable."
            for cluster_id in cluster_chunks.keys()
        }

        try:
            response = self.co.chat(
                model=SUMMARY_MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        except Exception:
            return fallback

        response_text = self._extract_response_text(response)
        if not response_text:
            return fallback

        parsed = self._parse_summary_json(response_text)
        if not parsed:
            return fallback

        output: dict[int, str] = {}
        for cluster_id in cluster_chunks.keys():
            summary = parsed.get(str(cluster_id)) or parsed.get(cluster_id)
            if isinstance(summary, str) and summary.strip():
                output[cluster_id] = summary.strip()
            else:
                output[cluster_id] = fallback[cluster_id]
        return output

    def _build_prompt(self, cluster_chunks: dict[int, list[str]]) -> str:
        sections: list[str] = []
        for cluster_id in sorted(cluster_chunks.keys()):
            chunks = cluster_chunks[cluster_id]
            trimmed_chunks = self._trim_chunks(chunks)
            chunk_lines = "\n".join(
                [f"- Chunk {index + 1}: {chunk}" for index, chunk in enumerate(trimmed_chunks)]
            )
            section = (
                f"Cluster {cluster_id}\n"
                f"Chunks:\n{chunk_lines if chunk_lines else '- (no chunks)'}"
            )
            sections.append(section)

        cluster_payload = "\n\n".join(sections)

        return (
            "You are summarizing clustered text chunks. For each cluster, produce a concise"
            " thematic summary in at most 3 sentences.\n\n"
            "Return ONLY valid JSON (no markdown, no extra text) where keys are cluster IDs"
            " as strings and values are summaries.\n"
            "Example: {\"0\": \"...\", \"1\": \"...\"}\n\n"
            f"Cluster data:\n{cluster_payload}"
        )

    def _trim_chunks(self, chunks: Iterable[str]) -> list[str]:
        trimmed: list[str] = []
        for chunk in list(chunks)[:MAX_CHUNKS_PER_CLUSTER]:
            chunk_text = chunk.strip()
            if not chunk_text:
                continue
            if len(chunk_text) > MAX_CHARS_PER_CHUNK:
                chunk_text = f"{chunk_text[:MAX_CHARS_PER_CHUNK]}..."
            trimmed.append(chunk_text)
        return trimmed

    def _extract_response_text(self, response) -> str:
        # Cohere responses can differ by SDK version; normalize safely.
        try:
            message = getattr(response, "message", None)
            content = getattr(message, "content", None)
            if content and isinstance(content, list):
                text_parts: list[str] = []
                for item in content:
                    text = getattr(item, "text", None)
                    if isinstance(text, str):
                        text_parts.append(text)
                if text_parts:
                    return "\n".join(text_parts)
        except Exception:
            pass

        # Fallback to best-effort string conversion.
        try:
            return str(response)
        except Exception:
            return ""

    def _parse_summary_json(self, raw_text: str) -> dict:
        text = raw_text.strip()

        # Handle accidental fenced output.
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 3:
                text = "\n".join(lines[1:-1]).strip()

        # Attempt direct JSON parse first.
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        # Attempt to extract first JSON object region.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return {}

        return {}
