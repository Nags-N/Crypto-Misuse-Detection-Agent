# Hard Cases Dataset

This directory contains synthetically crafted, difficult samples designed to challenge simple rule-based and statistical ML models, while evaluating the reasoning capabilities of Agentic AI models.

## Sample Schemas
Standard JSONL with `metadata`, `label` ("secure" or "insecure") and `code_snippet` (Java source).

## Included Scenarios:
1. **IndirectKeyHardcoding**: Key bytes are hardcoded but stored safely in another class, dodging simple regex proximity rules.
2. **SecureECBLookalike**: A false-positive trap. The string "ECB" is in the code (as a variable or unrelated constant), but the actual cipher instantiated is "GCM".
3. **CompositeMisuse_StaticIV**: The algorithm and mode are secure (AES/CBC), but the IV is hardcoded repeatedly.
4. **WeakPRNG_Disguised**: Uses `java.util.Random` for key generation directly array manipulation, which bypasses naive API checks for `SecureRandom`.
5. **ProperPBKDF2**: Good instantiation with safely parameterized iteration counts.
