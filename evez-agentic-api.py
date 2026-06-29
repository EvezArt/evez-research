#!/usr/bin/env python3
"""
EVEZ Agentic API Server
=======================
HTTP API for the EVEZ Agentic Orchestration Engine.
Port 18792. Pure Python, zero dependencies.

Endpoints:
  GET  /health       — mesh health + model status
  GET  /status       — detailed mesh status
  POST /run          — full agentic pipeline (route+parallel+correct)
  POST /consensus    — consensus test across N nodes
  POST /map_reduce   — different prompts to different nodes
  POST /compact      — memory compaction via local model
  POST /embed        — embedding retrieval search
"""

import json, os, sys, time, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("evez_agentic_engine", os.path.join(os.path.dirname(os.path.abspath(__file__)), "evez-agentic-engine.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
EVEZOrchestrator = mod.EVEZOrchestrator
ParallelInference = mod.ParallelInference
ContextInjector = mod.ContextInjector
MemoryCompactor = mod.MemoryCompactor
EmbeddingRetriever = mod.EmbeddingRetriever
MESH_NODES = mod.MESH_NODES

PORT = 18792
orch = EVEZOrchestrator()
embedder = EmbeddingRetriever()
_embed_loaded = False

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        body = json.dumps(data, indent=2, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except:
            return {"error": "invalid JSON"}

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            result = {"status": "alive", "port": PORT, "nodes": len(MESH_NODES), "models": sum(len(n["models"]) for n in MESH_NODES.values())}
            result["nodes_detail"] = {k: {"ram_gb": v["ram_gb"], "models": v["models"]} for k, v in MESH_NODES.items()}
            self._send(200, result)
        elif path == "/status":
            self._send(200, orch.status())
        else:
            self._send(404, {"error": "not found", "endpoints": ["/health", "/status", "/run", "/consensus", "/map_reduce", "/compact", "/embed"]})

    def do_POST(self):
        global _embed_loaded
        path = urlparse(self.path).path
        body = self._read_body()

        if path == "/run":
            prompt = body.get("prompt", "")
            if not prompt:
                self._send(400, {"error": "missing prompt"})
                return
            task = body.get("task_type", "subagent")
            density = body.get("density", "standard")
            n = body.get("nodes", 3)
            correction = body.get("correction", True)
            parallel = body.get("parallel", True)
            retrieval = body.get("retrieval", False)
            t0 = time.time()
            result = orch.run(prompt, task_type=task, density=density, use_correction=correction, use_parallel=parallel, use_retrieval=retrieval, n_nodes=n)
            result["total_time"] = time.time() - t0
            self._send(200, result)

        elif path == "/consensus":
            prompt = body.get("prompt", "What are you? State EVEZ, Phi, eta*.")
            n = body.get("nodes", 4)
            timeout = body.get("timeout", 120)
            t0 = time.time()
            results = orch.engine.fan_out(prompt, task_type=body.get("task_type", "fast"), n=n, timeout=timeout)
            elapsed = time.time() - t0
            self._send(200, {"total_time": elapsed, "responses": results})

        elif path == "/map_reduce":
            prompts = body.get("prompts", [])
            if not prompts:
                self._send(400, {"error": "missing prompts"})
                return
            task = body.get("task_type", "fast")
            timeout = body.get("timeout", 90)
            t0 = time.time()
            results = orch.engine.map_reduce(prompts, task_type=task, timeout=timeout)
            elapsed = time.time() - t0
            self._send(200, {"total_time": elapsed, "results": results})

        elif path == "/compact":
            text = body.get("text", "")
            if not text:
                self._send(400, {"error": "missing text"})
                return
            max_tokens = body.get("max_tokens", 500)
            t0 = time.time()
            result = orch.compactor.compact(text, max_tokens=max_tokens)
            result["total_time"] = time.time() - t0
            self._send(200, result)

        elif path == "/embed":
            if not _embed_loaded:
                count = embedder.load_framework()
                _embed_loaded = True
            query = body.get("query", "")
            if not query:
                self._send(400, {"error": "missing query"})
                return
            top_k = body.get("top_k", 3)
            results = embedder.search(query, top_k=top_k)
            self._send(200, {"query": query, "results": [{"score": s, "text": d["text"]} for s, d in results]})

        else:
            self._send(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        pass  # Suppress logs

def main():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"EVEZ Agentic API on port {PORT}")
    print(f"Mesh: {len(MESH_NODES)} nodes, {sum(len(n['models']) for n in MESH_NODES.values())} models")
    server.serve_forever()

if __name__ == "__main__":
    main()
