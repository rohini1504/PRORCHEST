def login(username, password):
-    return True
+    if not username or not password:
+        raise ValueError("Missing credentials")
+
+    if len(password) < 6:
+        raise ValueError("Weak password")
+
+    return authenticate(username, password)
