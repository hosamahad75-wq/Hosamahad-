# Backend compiler pipeline for HUS DSL (5-stage)
from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import re
from datetime import datetime

@dataclass
class ASTNode:
    type: str
    name: Optional[str]
    body: Dict[str, Any]

class CompilerError(Exception):
    pass

class BootStage:
    """Initial sanity checks and environment normalization."""
    def run(self, source: str) -> str:
        if not source or not source.strip():
            raise CompilerError("Empty source provided to compiler Boot stage")
        # Normalize line endings and remove BOM
        normalized = source.replace('\r\n', '\n').lstrip('\ufeff')
        return normalized

class ParserStage:
    """Parses a tiny DSL into a minimal AST.

    DSL format supported (minimal, deterministic):
      contract <name> {
        key: value
        flag: true
      }

    Values are strings, numbers, booleans. Nested objects are not supported in this minimal parser
    but the AST is expressive enough to extend later.
    """
    CONTRACT_RE = re.compile(r"contract\s+(?P<name>[A-Za-z0-9_\-]+)\s*\{(?P<body>.*?)\}", re.S)
    ASSIGN_RE = re.compile(r"^(?P<key>[A-Za-z0-9_\-]+)\s*:\s*(?P<val>.+)$")

    def run(self, source: str) -> List[ASTNode]:
        matches = list(self.CONTRACT_RE.finditer(source))
        if not matches:
            raise CompilerError("No contract blocks found in source")
        ast_nodes: List[ASTNode] = []
        for m in matches:
            name = m.group("name")
            body_raw = m.group("body").strip()
            body: Dict[str, Any] = {}
            for line in body_raw.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                am = self.ASSIGN_RE.match(line)
                if not am:
                    raise CompilerError(f"Invalid assignment line in contract {name}: '{line}'")
                key = am.group("key")
                val = am.group("val").strip()
                # coerce types
                if val.lower() in ("true", "false"):
                    value: Any = val.lower() == "true"
                else:
                    try:
                        if '.' in val:
                            value = float(val)
                        else:
                            value = int(val)
                    except Exception:
                        # strip quotes if present
                        value = val.strip().strip('"').strip("'")
                body[key] = value
            ast_nodes.append(ASTNode(type="contract", name=name, body=body))
        return ast_nodes

class ValidatorStage:
    """Validates AST nodes against basic rules."""
    REQUIRED_FIELDS = ("version",)

    def run(self, ast: List[ASTNode]) -> List[ASTNode]:
        for node in ast:
            if node.type != "contract":
                raise CompilerError(f"Unsupported node type: {node.type}")
            # enforce required fields exist
            for rf in self.REQUIRED_FIELDS:
                if rf not in node.body:
                    raise CompilerError(f"Contract '{node.name}' missing required field: {rf}")
            # simple semantic check: version must be positive number
            try:
                v = float(node.body.get("version"))
                if v <= 0:
                    raise CompilerError(f"Contract '{node.name}' has non-positive version: {v}")
            except Exception:
                raise CompilerError(f"Contract '{node.name}' has invalid version value: {node.body.get('version')}")
        return ast

class ResolverStage:
    """Resolves references / placeholders inside AST bodies.

    Supports placeholders like ${env.SOME_VAR} provided via a context dict.
    """
    PLACEHOLDER_RE = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        self.context = context or {}

    def _resolve_value(self, val: Any) -> Any:
        if isinstance(val, str):
            def _repl(m):
                key = m.group(1)
                return str(self.context.get(key, ""))
            return self.PLACEHOLDER_RE.sub(_repl, val)
        return val

    def run(self, ast: List[ASTNode]) -> List[ASTNode]:
        for node in ast:
            new_body: Dict[str, Any] = {}
            for k, v in node.body.items():
                new_body[k] = self._resolve_value(v)
            node.body = new_body
        return ast

class ContractInjectorStage:
    """Attaches runtime metadata and contract wrappers to AST nodes."""
    def run(self, ast: List[ASTNode]) -> List[Dict[str, Any]]:
        enriched: List[Dict[str, Any]] = []
        for node in ast:
            meta = {
                "__contract": node.name,
                "__type": node.type,
                "__generated_at": datetime.utcnow().isoformat() + "Z",
                "body": node.body,
            }
            # Example contract injection: ensure 'stamps' field exists
            if "stamps" not in meta["body"]:
                meta["body"]["stamps"] = {"creator": "compiler", "ts": meta["__generated_at"]}
            enriched.append(meta)
        return enriched

# Public API
def compile_hus(source: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    boot = BootStage()
    parser = ParserStage()
    validator = ValidatorStage()
    resolver = ResolverStage(context=context)
    injector = ContractInjectorStage()

    s = boot.run(source)
    ast = parser.run(s)
    ast = validator.run(ast)
    ast = resolver.run(ast)
    contracts = injector.run(ast)
    return contracts

# Simple CLI utility for manual debugging
if __name__ == "__main__":
    sample = """
    contract sample_contract {
      version: 1
      name: "Example"
      owner: ${env.OWNER}
    }
    """
    out = compile_hus(sample, context={"env.OWNER": "Hussam"})
    import json
    print(json.dumps(out, indent=2))
