# Riverview 5 - Lean Estate OS

R3 Alpha closed: 383 commits 372 files 55,334 lines. R5 is lean in spirit, not code save.

## Structure
- cme/socket.py 1,954 bytes <15KB - 3 methods Observe/Dispatch/Monitor
- cme/loop.py - 10 stages from waterwheel tile as registry lookups
- registries/resources.json - hardware: OctoMiner1 4xP100->8x 16GB 80B MoE, OctoMiner2 30B vision 7.5s, Camarillo N95 15W 0.6B autonomic
- registries/capabilities.json - Local CAD text-to-STL proven, manifest r3a.module-manifest.v1@1.0.0
- registries/environments.json - 8 castle realms + Undercurrent veil Evelyn+Gray Man + Grace AA USB no PG residue
- hr/security_levels.json - Helen Waite holds whitelist/blacklist/budget, Ingrid firewall reads
- residents/13 json - Alyssa time shield, Grace #1 owns workflow, Chloe Chief Architect hybrid, Jessica Chief Character affinity crush, Vicky Eng uses CAD not owns, etc.
- tools/modularity-gate.py <5KB CI - fails if BLOCKED/bounded/demo hardcoded returns
- dashboard/index.html - lean replica of your 4 panorama images

## Install tomorrow AM
```
unzip r5-full.zip
cd r5-full
python -m tools.modularity-gate
python -c "from cme.socket import CMESocket; print(CMESocket().dispatch({'task':'hi'}, 'v1.0.0-conversation'))"
open dashboard/index.html
```

## Fixes from R3
- Vicky hiring stall + Grace conversation block: task_class v1.0.0-conversation ["respond helpfully"] bypasses authority_grades store + acceptance envelope
- Scrape: cme.py 197KB 18 BLOCKED, grace_module.py 85KB 36 BLOCKED, db.py 113KB 23 BLOCKED -> registry lookups
- Interconnection: db becomes dumb ledger, cme becomes router, grace reads registries

## Dashboard
Your images: four_variations_labeled_landmarks.png + waterwheel_dashboard_map_labels.png + panorama_dashboard_resident_location_cards.png + panorama_dashboard_system_flags.png + modern_dashboard_left_navigation.png + modern_dashboard_estate_status.png + waterwheel_dashboard_cme_waterwheel.png + waterwheel_dashboard_bottom_collapsible_tiles.png are the spec.

Bottom tiles: PROJECT & WORK, KNOWLEDGE & MEMORY, COMMUNICATION BUS, POLICY & ACCESS (was GOVERNANCE), RESOURCE & CAPACITY, OBSERVABILITY & HEALTH, DATA & STATE
