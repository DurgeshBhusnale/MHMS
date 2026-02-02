# CRPF MHMS - Deployment Security Checklist

**Version:** Emergency Security Patch v1.0
**Date:** 2026-02-02
**Status:** Minimum viable security for deployment

---

## Pre-Deployment Checklist

### 1. Required Environment Variables

The following environment variables **MUST** be set before starting the application:

```bash
# CRITICAL - Generate a secure secret key (REQUIRED)
SECRET_KEY=<generate-with-command-below>

# Database Configuration (REQUIRED)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=3306
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Security Fixes Applied (This Patch)

| Fix | Status | Description |
|-----|--------|-------------|
| Admin Authorization | COMPLETE | All 22 admin endpoints now require authentication |
| SECRET_KEY Validation | COMPLETE | App fails to start with insecure/missing key |
| SQL Injection Fix | COMPLETE | DELETE statements use parameterized queries |
| Credential Logging | COMPLETE | Database details no longer logged to stdout |
| Register Endpoint | COMPLETE | Soldier registration now requires admin auth |

### 3. Firewall Recommendations

For on-premise deployment, configure firewall rules:

```bash
# Allow frontend to backend communication (internal only)
Allow: Internal Network -> Backend:5000

# Block external access to backend API
Deny: External -> Backend:5000

# Allow frontend web access
Allow: Internal Network -> Frontend:3000
```

---

## Known Limitations (Post-Patch)

The following issues remain and should be addressed after deployment:

### HIGH Priority (Address within 1 week)

1. **No Rate Limiting**
   - Login endpoints can be brute-forced
   - Recommendation: Implement `flask-limiter`

2. **No Connection Pooling**
   - Each request creates new DB connection
   - May cause issues under high load (>100 concurrent users)

3. **N+1 Query Problem**
   - Soldiers report endpoint makes 301+ queries for 100 soldiers
   - Performance degrades with user count

4. **Zero Test Coverage**
   - No automated tests to verify functionality
   - Manual testing required before deployment

### MEDIUM Priority (Address within 2 weeks)

5. **No CSRF Protection**
   - Cross-site request forgery attacks possible
   - Recommendation: Implement `flask-wtf`

6. **Bare Exception Handlers**
   - 13+ instances of `except:` swallow errors
   - Makes debugging difficult

7. **HTTPS Not Enforced**
   - Credentials transmitted in plain text if HTTPS not configured
   - Ensure reverse proxy (nginx) handles HTTPS

---

## Verification Steps

After deployment, verify security fixes:

### 1. Test Authorization

```bash
# Should return 401 Unauthorized
curl http://localhost:5000/api/admin/soldiers-report

# Should return 401 Unauthorized (no session)
curl http://localhost:5000/api/admin/dashboard-stats
```

### 2. Test SECRET_KEY Validation

```bash
# Unset SECRET_KEY and try to start
unset SECRET_KEY
python app.py
# Expected: ValueError - SECRET_KEY required
```

### 3. Verify No Credential Logging

```bash
# Start the app and check output
python app.py 2>&1 | grep -i "password\|DB_USER\|connecting"
# Expected: No database credentials in output
```

---

## Post-Deployment Roadmap

| Week | Task | Priority |
|------|------|----------|
| 1 | Add rate limiting to auth endpoints | HIGH |
| 1 | Implement connection pooling | HIGH |
| 2 | Fix N+1 queries in soldiers-report | HIGH |
| 2 | Add CSRF protection | MEDIUM |
| 3 | Add basic test coverage (auth, survey) | HIGH |
| 4 | Security audit and penetration testing | HIGH |

---

## Emergency Contacts

If security incident occurs:
1. Disconnect system from network immediately
2. Preserve logs for forensic analysis
3. Contact security team

---

## Changelog

### v1.0 (2026-02-02) - Emergency Security Patch
- Added `@require_admin` decorator to all admin endpoints
- Made SECRET_KEY required with validation
- Fixed SQL injection in DELETE statements
- Removed database credentials from logs
- Protected `/register` endpoint with admin auth
