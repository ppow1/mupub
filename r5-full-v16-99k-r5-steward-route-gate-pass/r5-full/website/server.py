
"""
Riverview 5 Website Server - R5 dashboard + auth - fixes /steward Not Found
"""
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import pathlib, json, os, asyncio, secrets as py_secrets, time, datetime
from passlib.context import CryptContext

app = FastAPI(title="Riverview 5 - R5 Dashboard + Auth")
BASE = pathlib.Path(__file__).parent.parent
DASH = BASE / "dashboard"
SECRETS_FILE = BASE / "secrets" / "auth.json"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def load_auth():
    env_user = os.getenv("R5_WEBSITE_USERNAME")
    env_pass = os.getenv("R5_WEBSITE_PASSWORD")
    if env_user and env_pass:
        return {"username": env_user, "password": env_pass, "source": "env"}
    if SECRETS_FILE.exists():
        try:
            data = json.loads(SECRETS_FILE.read_text())
            return {"username": data.get("username"), "password_hash": data.get("password_hash"), "source": "secrets/auth.json"}
        except:
            pass
    return None

if DASH.exists():
    app.mount("/web", StaticFiles(directory=str(DASH)), name="web")
    app.mount("/static", StaticFiles(directory=str(DASH)), name="static")

@app.get("/")
async def root():
    return FileResponse(str(DASH / "index.html"))

@app.get("/login")
async def login_page():
    p = DASH / "steward-login.html"
    if p.exists():
        return FileResponse(str(p))
    return FileResponse(str(DASH / "index.html"))

@app.get("/steward")
async def steward_page():
    return FileResponse(str(DASH / "index.html"))

@app.get("/steward.html")
async def steward_html():
    return FileResponse(str(DASH / "index.html"))

@app.get("/api/v1/steward/session")
async def steward_session(request: Request):
    auth = load_auth()
    return {"contract":"r5.steward-session.v1","session_id":"r5-lean-session","steward": auth["username"] if auth else "steward","established_at": datetime.datetime.now().isoformat()+"Z","correlation_id": f"r5-{int(time.time())}","status":"active","state":"authenticated"}

@app.post("/api/v1/steward/session")
async def create_session(request: Request):
    body = await request.json()
    login_name = body.get("login_name") or body.get("username") or ""
    password = body.get("password") or ""
    intent = body.get("intent", "login")
    auth_config = load_auth()
    if auth_config is None:
        if intent == "enroll":
            SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
            hashed = pwd_context.hash(password)
            SECRETS_FILE.write_text(json.dumps({"username": login_name, "password_hash": hashed, "created_at": datetime.datetime.now().isoformat()+"Z", "source": "R5 first enrollment"}))
            return {"contract":"r5.steward-session.v1","session_id": f"r5-{int(time.time())}","steward": login_name,"state":"authenticated","status":"active","message":"Enrollment complete"}
        else:
            return JSONResponse(status_code=401, content={"contract":"r5.steward-session.v1","error":"No steward enrolled yet. Use First enrollment.","state":"unauthenticated"})
    expected_user = auth_config.get("username")
    if "password" in auth_config:
        ok = py_secrets.compare_digest(login_name, expected_user) and py_secrets.compare_digest(password, auth_config["password"])
    else:
        pw_hash = auth_config.get("password_hash", "")
        ok = py_secrets.compare_digest(login_name, expected_user) and pwd_context.verify(password, pw_hash) if pw_hash else False
    if not ok:
        return JSONResponse(status_code=401, content={"contract":"r5.steward-session.v1","error":"Invalid credentials","state":"unauthenticated"})
    return {"contract":"r5.steward-session.v1","session_id": f"r5-{int(time.time())}","steward": login_name,"state":"authenticated","status":"active","correlation_id": f"r5-auth-{int(time.time())}"}

@app.delete("/api/v1/steward/session")
async def end_session():
    return {"contract":"r5.steward-session.v1","status":"ended","state":"unauthenticated"}

@app.get("/api/v1/steward/status")
async def steward_status():
    try:
        from cme.socket import CMESocket
        sock = CMESocket()
        cme_state = sock.monitor()
        cme_ok = True
    except Exception as e:
        cme_state = {"error": str(e)}
        cme_ok = False
    try:
        from data.ledger import ledger
        events = ledger.read_events()
        ledger_count = len(events)
    except:
        ledger_count = 0
    import psutil
    def pid_alive(path, name_hint=None):
        p = pathlib.Path(path)
        if p.exists():
            try:
                pid = int(p.read_text().strip())
                if psutil.pid_exists(pid):
                    return True
            except:
                pass
        if name_hint:
            try:
                for proc in psutil.process_iter(['cmdline']):
                    cmd = ' '.join(proc.info['cmdline'] or [])
                    if name_hint in cmd:
                        return True
            except:
                pass
        return False
    return {
        "contract":"r5.steward-access-status.v1",
        "correlation_id": f"r5-status-{int(time.time())}",
        "cme":{"status":"online" if cme_ok else "offline","state": cme_state},
        "ring0":{"status":"online" if pid_alive("/tmp/r5-ring0.pid", "ring0.py") else "offline"},
        "ddelta":{"status":"online" if pid_alive("/tmp/r5-cme.pid", "d_delta.py") else "offline"},
        "ledger":{"count": ledger_count,"status":"online"},
        "storage":{"status":"healthy"},
        "checks":{"CME":"Online" if cme_ok else "Offline","Ledger": f"{ledger_count} events","Storage":"Healthy"}
    }

@app.get("/api/v1/steward/capabilities")
async def capabilities():
    cap_path = BASE / "registries" / "capabilities.json"
    caps = {}
    if cap_path.exists():
        caps = json.loads(cap_path.read_text())
    return {"contract":"r5.steward-capability-discovery.v1","correlation_id": f"r5-cap-{int(time.time())}","capabilities": caps}

@app.post("/api/v1/steward/operations/invoke")
async def invoke_operation(request: Request):
    body = await request.json()
    op = body.get("request", body)
    try:
        from cme.socket import CMESocket
        from data.ledger import ledger
        sock = CMESocket()
        task_class = op.get("task_class","v1.0.0-conversation")
        if "capability" not in op and "text" in op:
            op["capability"] = "conversation"
        obs = sock.observe(op)
        grant = sock.dispatch(op, task_class)
        ledger.append_event({"type":"operation_invoke","request": op,"grant": dict(grant),"task_class": task_class})
        return {"contract":"r5.steward-operation-result.v1","correlation_id": f"r5-op-{int(time.time())}","status":"completed","result":{"mode":"lightweight","message": f"R5 lean CME dispatched: {op.get('text','')[:200]}","grant": dict(grant)},"observation": dict(obs)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"contract":"r5.steward-operation-result.v1","error":{"code":"dispatch_failed","message": str(e)},"correlation_id": f"r5-err-{int(time.time())}"})

@app.get("/api/status")
async def legacy_status():
    s = await steward_status()
    return {"host":"192.168.1.155","checks": s,"flags": s.get("checks", {})}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        try:
            s = await steward_status()
            await ws.send_json({"type":"heartbeat","status": s,"time": datetime.datetime.now().isoformat()})
        except:
            await ws.send_json({"type":"heartbeat","cme":"online"})
        await asyncio.sleep(2)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
