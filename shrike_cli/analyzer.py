import json
import re
from typing import Dict, Any, Optional
from shrike_cli.rules import STRIPE_RULES

# Try importing the Gemini SDK, fallback if missing
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

class StripeDiagnosticEngine:
    def __init__(self, gemini_api_key: Optional[str] = None):
        if HAS_GENAI and gemini_api_key:
            self.client = genai.Client(api_key=gemini_api_key)
        else:
            self.client = None

    def analyze(self, raw_text: str) -> Dict[str, Any]:
        """
        Main pipeline execution.
        Step 1: Fast-path deterministic rule matching.
        Step 2: Fallback to LLM analysis if no rules hit.
        """
        # Step 1: Sweep for deterministic rules
        deterministic_results = self._scan_rules(raw_text)
        if deterministic_results:
            return {"issues": deterministic_results}
            
        # Step 2: Fallback to LLM if configured
        if self.client:
            llm_result = self._llm_fallback(raw_text)
            return {"issues": [llm_result]}
            
        return {
            "issues": [{
                "issue_type": "UNKNOWN_ERROR",
                "severity": "LOW",
                "confidence": 0,
                "root_cause": "No deterministic rules matched the logs, and LLM fallback is disabled.",
                "impact": "Unknown",
                "minimal_patch": "N/A",
                "verification_steps": ["[ ] Provide clear logs for analysis."],
                "evidence": []
            }]
        }

    def _scan_rules(self, raw_text: str) -> list:
        # returns a list of matched rules, sorted by severity and confidence
        text_to_search = raw_text
        matches = []
        
        for issue_type, rule in STRIPE_RULES.items():
            hits = 0
            matched_triggers = []
            
            for trigger in rule["regex_triggers"]:
                # Using DOTALL and IGNORECASE to catch multiline contextual anomalies
                if re.search(trigger, text_to_search, re.IGNORECASE | re.DOTALL):
                    hits += 1
                    matched_triggers.append(trigger)
            
            if hits > 0:
                adjusted_confidence = rule["base_confidence"]
                    
                matches.append({
                    "issue_type": issue_type,
                    "severity": rule["severity"],
                    "confidence": adjusted_confidence,
                    "root_cause": rule["root_cause"],
                    "impact": rule["impact"],
                    "minimal_patch": rule["minimal_patch"],
                    "verification_steps": rule["verification_steps"],
                    "evidence": matched_triggers
                })
                
        severity_value = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        matches.sort(key=lambda x: (severity_value.get(x["severity"], 0), x["confidence"]), reverse=True)
        return matches

    def _llm_fallback(self, raw_text: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the following server log/payload specifically for Stripe integration errors.
        You must strictly diagnose the root cause and provide a patch.
        
        Log Data:
        {raw_text[:3000]} # Trim to fit context safely
        
        Respond with a JSON object strictly adhering to this schema:
        {{
            "issue_type": "UPPERCASE_SNAKE_CASE_SUMMARY",
            "severity": "CRITICAL, HIGH, MEDIUM, or LOW",
            "confidence": <integer between 50 and 85>,
            "root_cause": "Detailed technical explanation",
            "impact": "Business/architectural impact",
            "minimal_patch": "Code snippet resolving the issue",
            "verification_steps": ["List of steps to verify fix"]
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            data = json.loads(response.text)
            
            # Ensure AI confidence is capped since it's an anomaly reading
            if data.get("confidence", 100) > 85:
                data["confidence"] = 85
                
            return {
                "issue_type": data.get("issue_type", "AI_DIAGNOSIS_UNSTRUCTURED"),
                "severity": data.get("severity", "MEDIUM"),
                "confidence": data.get("confidence", 70),
                "root_cause": data.get("root_cause", "Anomaly detected, context unclear."),
                "impact": data.get("impact", "Requires manual review."),
                "minimal_patch": data.get("minimal_patch", "# Review integration logic"),
                "verification_steps": data.get("verification_steps", ["[ ] Manually audit code execution."]),
                "evidence": ["LLM Inference logic executed due to lack of deterministic matches."]
            }
        except Exception as e:
            return {
                "issue_type": "LLM_ANALYSIS_FAILED",
                "severity": "MEDIUM",
                "confidence": 0,
                "root_cause": f"Failed to execute LLM fallback: {e}",
                "impact": "System degraded to deterministic rules only.",
                "minimal_patch": "N/A",
                "verification_steps": [],
                "evidence": []
            }
