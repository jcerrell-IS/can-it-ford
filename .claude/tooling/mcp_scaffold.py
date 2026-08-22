"""Minimal MCP stdio server, zero dependencies, Python 3.9 safe.

Written for can-it-ford because the Mac has no `mcp` package and no numpy
(see memory: mac-has-no-numpy-python). Implements only what Claude Code needs:
initialize, tools/list, tools/call, and the initialized notification.

Protocol: JSON-RPC 2.0, newline-delimited JSON on stdin/stdout. Every log line
goes to stderr so it can never corrupt the protocol stream.
"""
import json
import sys
import traceback

PROTOCOL_VERSION = "2024-11-05"


def log(msg):
    sys.stderr.write("[mcp] %s\n" % msg)
    sys.stderr.flush()


class Server(object):
    def __init__(self, name, version="1.0.0"):
        self.name = name
        self.version = version
        self._tools = {}

    def tool(self, name, description, schema):
        """Decorator. schema is a JSON Schema dict for the arguments."""
        def deco(fn):
            self._tools[name] = {
                "name": name,
                "description": description,
                "inputSchema": schema,
                "_fn": fn,
            }
            return fn
        return deco

    # ---- protocol -------------------------------------------------------
    def _tools_list(self):
        return {"tools": [
            {k: v for k, v in t.items() if k != "_fn"}
            for t in self._tools.values()
        ]}

    def _tools_call(self, params):
        name = params.get("name")
        args = params.get("arguments") or {}
        t = self._tools.get(name)
        if t is None:
            return {"content": [{"type": "text", "text": "unknown tool: %s" % name}],
                    "isError": True}
        try:
            out = t["_fn"](**args)
        except Exception as e:
            log("tool %s raised: %s" % (name, traceback.format_exc()))
            return {"content": [{"type": "text",
                                 "text": "%s: %s" % (type(e).__name__, e)}],
                    "isError": True}
        if not isinstance(out, str):
            out = json.dumps(out, indent=2, default=str)
        return {"content": [{"type": "text", "text": out}]}

    def _handle(self, req):
        m = req.get("method")
        if m == "initialize":
            return {"protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": self.name, "version": self.version}}
        if m == "tools/list":
            return self._tools_list()
        if m == "tools/call":
            return self._tools_call(req.get("params") or {})
        if m == "ping":
            return {}
        return None  # unknown -> method not found

    def run(self):
        log("%s starting, %d tools" % (self.name, len(self._tools)))
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except ValueError:
                continue
            # notifications have no id and expect no reply
            if "id" not in req:
                continue
            try:
                result = self._handle(req)
            except Exception:
                log(traceback.format_exc())
                result = None
            if result is None:
                resp = {"jsonrpc": "2.0", "id": req["id"],
                        "error": {"code": -32601, "message": "method not found"}}
            else:
                resp = {"jsonrpc": "2.0", "id": req["id"], "result": result}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
