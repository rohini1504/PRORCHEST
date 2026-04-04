def authenticate_user(token):
   if token == "valid":
-        return True
-    return False
+    try:
+        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
+        return payload.get("user_id") is not None
+    except Exception as e:
+        print("JWT Error:", e)
+        return False
