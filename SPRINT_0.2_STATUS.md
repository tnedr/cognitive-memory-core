# Sprint 0.2.0 Status

## ✅ Completed (0. lépés - Alap környezet)

- [x] UV package manager telepítve és konfigurálva
- [x] Dependencies telepítve (`uv pip install -e .`)
- [x] Unit tesztek futnak (9/9 PASSED)
- [x] Docker Compose fájl javítva (version mező eltávolítva)
- [x] SETUP.md dokumentáció létrehozva
- [x] pytest e2e marker regisztrálva

## 🚧 In Progress (1. lépés - E2E tesztek)

- [x] E2E teszt fájl létrehozva (`tests/test_e2e.py`)
- [x] Docker Compose fixture implementálva
- [x] Tesztek skip-elhetők Docker nélkül
- [ ] **TODO**: Docker Desktop indítása és E2E tesztek validálása
- [ ] **TODO**: E2E tesztek hibák javítása
- [ ] **TODO**: CI-ben kötelezővé tenni az E2E teszteket

### E2E Tesztek Listája

1. ✅ `test_end_to_end_ingest_encode_link_context` - Teljes workflow
2. ✅ `test_autolink_workflow` - Automatikus linkelés
3. ✅ `test_vector_search_accuracy` - Vektor keresés pontossága
4. ✅ `test_graph_traversal` - Gráf bejárás
5. ✅ `test_docker_services_available` - Docker szolgáltatások ellenőrzése

### E2E Tesztek Futtatása

```bash
# Docker szolgáltatások indítása
cd docker
docker-compose up -d
# Várj ~10-15 másodpercet

# E2E tesztek futtatása
cd ..
uv run pytest tests/test_e2e.py -v -m e2e

# Vagy skip Docker nélkül
SKIP_DOCKER_TESTS=1 uv run pytest tests/test_e2e.py -v
```

## 📋 Next Steps

### 1. E2E tesztek lezárása (1. lépés)
- [ ] Indítsd a Docker Desktop-ot
- [ ] Futtasd az E2E teszteket: `uv run pytest tests/test_e2e.py -v -m e2e`
- [ ] Javítsd a hibákat, amíg zöld nem lesz
- [ ] Tedd kötelezővé a CI-ben

### 2. LLM Reflection (2. lépés)
- [ ] Branch: `feature/llm-reflection`
- [ ] LangChain integráció
- [ ] Prompt template (`templates/reflect.jinja`)
- [ ] `reflect()` implementáció
- [ ] Unit tesztek mockolt LLM-mel

### 3. Token-aware Compress (3. lépés)
- [ ] Branch: `feature/compress-rag`
- [ ] Tiktoken integráció
- [ ] RAG összegzés
- [ ] `materialize_context()` integráció

### 4. Decay Policy (4. lépés)
- [ ] Branch: `feature/decay-scheduler`
- [ ] `last_access` tracking
- [ ] Archiválás implementáció
- [ ] Scheduler (APScheduler/Celery)

### 5. File Watcher (5. lépés)
- [ ] Branch: `feature/fs-watch`
- [ ] Watchdog integráció
- [ ] Debounced re-encode
- [ ] Törlés/átnevezés kezelés

### 6. REST/GraphQL API (6. lépés)
- [ ] Branch: `api/rest-graphql`
- [ ] FastAPI alkalmazás
- [ ] CLI parancsok endpointokká
- [ ] Swagger UI

### 7. CI/CD bővítés (7. lépés)
- [ ] Branch: `infra/gha-pipeline`
- [ ] Test matrix (Py 3.10-3.12) ✅ (már kész)
- [ ] Codecov integráció ✅ (már kész)
- [ ] Docker build-push
- [ ] Pre-commit checks

## 📊 Progress

- **0. lépés**: ✅ 100% (Alap környezet)
- **1. lépés**: 🚧 80% (E2E tesztek - Docker validálás hiányzik)
- **2. lépés**: ⏳ 0% (LLM Reflection)
- **3. lépés**: ⏳ 0% (Compress)
- **4. lépés**: ⏳ 0% (Decay)
- **5. lépés**: ⏳ 0% (File Watcher)
- **6. lépés**: ⏳ 0% (API)
- **7. lépés**: ✅ 70% (CI/CD - Docker build hiányzik)

## 🎯 Milestone: v0.2.0

**Target Date**: TBD
**Status**: In Progress (20% complete)

**Blockers**:
- Docker Desktop indítása E2E tesztekhez
- LLM API kulcs beállítása (reflection feature-hez)

**Next Actions**:
1. Indítsd a Docker Desktop-ot
2. Futtasd az E2E teszteket
3. Kezdj el dolgozni a `feature/llm-reflection` branch-en

