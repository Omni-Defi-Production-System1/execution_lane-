from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Protocol, Any

# === token_universe.py ===
@dataclass(frozen=True)
class TokenUniverse:
    groups: Dict[str, List[str]]

    @staticmethod
    def polygon_core() -> "TokenUniverse":
        return TokenUniverse(groups={
            "stables": ["USDC", "USDT", "DAI", "FRAX"],
            "majors":  ["POL", "WMATIC", "WETH", "WBTC"],
            "defi":    ["AAVE", "CRV", "BAL", "SUSHI", "LINK", "UNI", "YFI", "SNX", "LDO"],
            "alts":    ["AVAX", "FTM"]
        })

    def all_symbols(self) -> List[str]:
        seen = []
        for syms in self.groups.values():
            for s in syms:
                if s not in seen:
                    seen.append(s)
        return seen

# === scanner_base.py ===
SourceType = Literal["onchain", "protocol", "bridge", "static"]

@dataclass
class ScanResult:
    source: str
    chain_id: int
    added: int
    updated: int
    blocked: int
    errors: List[str]

class Scanner(Protocol):
    def name(self) -> str: ...
    def source_type(self) -> SourceType: ...
    def scan(self, chain_id: int) -> List["TokenMeta"]: ...

# === verifier.py ===
@dataclass
class VerifyIssue:
    level: str
    code: str
    message: str

class TokenVerifier:
    def verify(self, chain_id: int, meta: 'TokenMeta') -> List[VerifyIssue]:
        issues: List[VerifyIssue] = []
        if not (isinstance(meta.address, str) and meta.address.startswith("0x") and len(meta.address) == 42):
            issues.append(VerifyIssue("ERROR", "BAD_ADDRESS", f"{meta.symbol} bad address: {meta.address}"))
        if not isinstance(meta.decimals, int) or not (0 <= meta.decimals <= 255):
            issues.append(VerifyIssue("ERROR", "BAD_DECIMALS", f"{meta.symbol} bad decimals: {meta.decimals}"))
        if meta.native and meta.wrapped:
            issues.append(VerifyIssue("ERROR", "NATIVE_WRAPPED_CONFLICT", f"{meta.symbol} native cannot be wrapped"))
        if meta.origin_chain and meta.origin_chain != chain_id:
            if not meta.bridge or meta.canonical is None:
                issues.append(VerifyIssue("ERROR", "BRIDGED_MISSING_META", f"{meta.symbol} missing bridge/canonical"))
            if meta.canonical is True:
                issues.append(VerifyIssue("ERROR", "BRIDGED_CANONICAL_CONFLICT", f"{meta.symbol} bridged cannot be canonical=True"))
        if meta.wrapped and not isinstance(meta.wrapped, str):
            issues.append(VerifyIssue("ERROR", "WRAP_UNDERLYING_INVALID", f"{meta.symbol} wrapped underlying invalid"))
        return issues

# === risk.py ===
RiskTier = Literal["LOW", "MEDIUM", "HIGH", "BLOCKED"]

@dataclass
class RiskDecision:
    tier: RiskTier
    reasons: List[str]

class RiskEngine:
    def __init__(self, trusted_bridges: List[str], block_untrusted_bridge: bool = True):
        self.trusted_bridges = trusted_bridges
        self.block_untrusted_bridge = block_untrusted_bridge
        self.map: Dict[str, RiskTier] = {
            "NATIVE": "LOW",
            "WRAPPED": "LOW",
            "CANONICAL_ERC20": "MEDIUM",
            "BRIDGED": "HIGH",
            "UNKNOWN": "BLOCKED"
        }

    def assess(self, assessment: 'TokenAssessment') -> RiskDecision:
        tier = self.map.get(assessment.token_class, "BLOCKED")
        reasons = list(assessment.reasons)
        if assessment.token_class == "BRIDGED":
            bridge = next((r.split("=", 1)[1] for r in assessment.reasons if r.startswith("bridge=")), None)
            if self.block_untrusted_bridge and bridge and bridge not in self.trusted_bridges:
                return RiskDecision("BLOCKED", reasons + [f"untrusted_bridge={bridge}"])
        return RiskDecision(tier, reasons)

# === exports.py ===
def export_token_registry(intel: 'TokenIntelligence', chain_id: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for sym, meta in intel.all_tokens(chain_id).items():
        assessment = intel.classify(chain_id, sym)
        out[sym] = {
            "address": meta.address,
            "decimals": meta.decimals,
            "class": assessment.token_class,
            "reasons": assessment.reasons
        }
    return out
