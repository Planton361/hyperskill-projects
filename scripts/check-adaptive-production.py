#!/usr/bin/env python3
"""Read-only verification of the adopted adaptive release and protected inputs."""
import json
from pathlib import Path
from knowledge_atlas.production_guard import verify_release

if __name__ == '__main__':
    print(json.dumps(verify_release(Path(__file__).resolve().parents[1]), indent=2))
