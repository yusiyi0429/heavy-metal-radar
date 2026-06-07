import sys, os, time, subprocess, json, urllib.request, urllib.error

BASE = "http://127.0.0.1:5001"
passed = 0
failed = 0

def test(method, path, body=None, check=None):
    global passed, failed
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        result = json.loads(resp.read())
        if check:
            ok = check(result)
            if ok:
                passed += 1
                print(f"  PASS {method} {path}")
            else:
                failed += 1
                print(f"  FAIL {method} {path}: check returned False")
        else:
            passed += 1
            print(f"  PASS {method} {path}")
        return result
    except Exception as e:
        failed += 1
        print(f"  FAIL {method} {path}: {e}")
        return None

proc = subprocess.Popen(
    [".venv/bin/python3", "-m", "backend.server"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(2)

print("Test suite:")
test("GET", "/api/health")
test("GET", "/api/config", check=lambda d: "keywords" in d and "cities" in d)
test("PUT", "/api/config", body={"enable_push": False})
test("GET", "/api/config", check=lambda d: d.get("enable_push") == False)
test("PUT", "/api/config", body={"enable_push": True})
test("GET", "/api/shows", check=lambda d: d.get("total", 0) >= 0)
test("GET", "/api/shows?city=%E5%8C%97%E4%BA%AC", check=lambda d: isinstance(d.get("shows"), list))
test("GET", "/api/shows?keyword=Arch", check=lambda d: isinstance(d.get("shows"), list))
test("POST", "/api/notify")
test("POST", "/api/reset")
test("POST", "/api/fetch")
test("PUT", "/api/config", body={"keywords": ["金属","死核","Arch Enemy"], "cities": ["北京"]})
test("GET", "/api/config", check=lambda d: len(d["keywords"]) == 3 and len(d["cities"]) == 1)

proc.kill()
proc.wait()
print(f"\n{passed}/{passed+failed} passed")
sys.exit(0 if failed == 0 else 1)
