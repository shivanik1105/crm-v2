# 🌐 Application Access URLs

## Issue: localhost:5173 Not Working from Windows

The services are running in Docker/WSL, so you need to access them using the WSL IP address instead of `localhost`.

## ✅ Working URLs (Access from Windows Browser)

### Option 1: WSL IP Address (Recommended)
- **Frontend:** http://172.30.27.231:5173
- **Backend API:** http://172.30.27.231:8000
- **API Docs:** http://172.30.27.231:8000/docs

### Option 2: Access from WSL Browser
If you have a browser in WSL/Linux:
- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:8000/docs

## 🔍 If WSL IP Doesn't Work

### Method 1: Use Docker Desktop Port Forwarding
Docker Desktop should automatically forward ports. Try:
- http://127.0.0.1:5173
- http://0.0.0.0:5173

### Method 2: Find Current WSL IP
The WSL IP can change. To find the current IP:

```powershell
# In PowerShell (Windows)
wsl hostname -I
```

Use the first IP address in the output (e.g., 172.30.27.231)

### Method 3: Port Forwarding from Windows
```powershell
# In PowerShell (as Administrator)
netsh interface portproxy add v4tov4 listenport=5173 listenaddress=0.0.0.0 connectport=5173 connectaddress=172.30.27.231
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=172.30.27.231
```

Then access:
- http://localhost:5173
- http://localhost:8000/docs

To remove port forwarding later:
```powershell
netsh interface portproxy delete v4tov4 listenport=5173 listenaddress=0.0.0.0
netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0
```

## 🐛 Troubleshooting

### Check Services are Running
```bash
cd /mnt/f/shivani/VSCode/projects/crm
docker compose ps
```

All services should show "Up" status.

### Check Frontend Logs
```bash
docker compose logs frontend --tail=20
```

Should show: `VITE v5.4.21 ready in XXX ms`

### Check Backend Logs
```bash
docker compose logs backend --tail=20
```

Should show: `Application startup complete.`

### Restart Services
```bash
docker compose restart frontend backend
sleep 5
docker compose ps
```

## 📊 Quick Test - Backend is Working

From Windows PowerShell, test the backend:
```powershell
# Test with WSL IP
curl http://172.30.27.231:8000/docs

# Or from WSL
wsl curl http://localhost:8000/docs
```

## 🚀 Alternative: Access from WSL Terminal Browser

If you have `w3m` or `lynx` in WSL:
```bash
w3m http://localhost:5173
# or
lynx http://localhost:5173
```

## 💡 Best Solution for Development

### Option A: VS Code Port Forwarding
If using VS Code with WSL extension:
1. Open Command Palette (Ctrl+Shift+P)
2. Search "Forward a Port"
3. Forward ports 5173 and 8000
4. Access via the forwarded URLs

### Option B: Use Windows Hosts File
Add to `C:\Windows\System32\drivers\etc\hosts`:
```
172.30.27.231    crm.local
```

Then access:
- http://crm.local:5173
- http://crm.local:8000/docs

## ✅ Current Status

Your services are running at:
- Frontend: **http://172.30.27.231:5173** ← Try this first!
- Backend: **http://172.30.27.231:8000/docs** ← Try this too!

The backend is fully operational - we successfully processed 60 emails!
