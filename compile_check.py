import py_compile, traceback
files = ['threat_detector.py','entity_extractor.py','translations.py']
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"Compiled OK: {f}")
    except Exception:
        print(f"Compile failed: {f}")
        traceback.print_exc()
