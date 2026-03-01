# LOCAL RUN INSTRUCTIONS (for reproducible verification)

Run from repo root (`/workspace/General` equivalent).

## 1) Capability probes
```bash
echo PROBE_OK
python3 --version
sqlite3 --version
unzip -l concept_pack_v0.2.zip | head
```

## 2) Zip unpack/pack probe
```bash
rm -rf /tmp/caps_zip_test && mkdir -p /tmp/caps_zip_test
unzip -o -q concept_pack_v0.2.zip -d /tmp/caps_zip_test
(cd /tmp/caps_zip_test && zip -qr /tmp/caps_repack.zip .)
ls -l /tmp/caps_repack.zip
```

## 3) Input integrity checks
```bash
sha256sum AGENT_PROMPT_v3_7_FULL_PACKAGE.zip concept_pack_v0.2.zip AGENT_PROMPT_PACKAGE/AGENT_PROMPT_v3_7.md
```

Expected: non-empty SHA256 hashes and successful exit codes.
