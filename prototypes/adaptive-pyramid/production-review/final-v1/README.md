# Exact adaptive Production review

Open view/ through a localhost server. Review Current Production, Target My Knowledge,
Target Global, Target Course and Target Project. The page displays the exact source,
target and manifest fingerprints and the changed-file count.

NO STATE / KNOWLEDGE / GENERATION CHANGE. Local geometry remains derived.
This package grants no approval itself. Real Production has not been replaced.

After separate explicit human approval only, the operator command is:

python3 -B scripts/update-knowledge-atlas.py --apply-adaptive-production /absolute/path/to/apply-manifest.json --reviewed-fingerprint EXACT_MANIFEST_FINGERPRINT --confirm-production-replacement

Copy manifest_fingerprint from apply-manifest.json or the review page. No environment
bypass exists. Any change to the source bindings, implementation or package requires
a new review. Do not run the legacy --production command to publish this candidate.
The transient publication journal is outside State; no durable State is introduced.
Canonical identity uses UTF-8 sorted compact JSON, without timestamps. Manifest identity
hashes all fields except manifest_fingerprint. Package identity hashes all package files
except apply-manifest.json, avoiding self-reference. Inventories bind relative paths to
file SHA256; Production inventories use docs/knowledge-map/ prefixes.
