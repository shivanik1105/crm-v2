# 🔴 REAL-TIME System - Complete Implementation

## ✅ **Good News: WebSocket Backend Already Exists!**

Your system already has:
- ✅ WebSocket endpoints (`/ws` and `/ws/{channel}`)
- ✅ WebSocket manager service
- ✅ FastAPI with WebSocket support

## 🚀 **What We Need to Add:**

### **1. Emit Real-Time Events When Emails Are Processed**

Update `backend/app/routers/ingest.py` to broadcast events:

```python
# Add at the top
from app.services.websocket_manager import ws_manager

# After email is saved and classified (around line 140):
async def process_email_async(db: AsyncSession, email_data: EmailIngest):
    # ... existing code ...
    
    # At the end, after db.commit():
    
    # Broadcast new email event
    await ws_manager.broadcast("global", {
        "type": "new_email",
        "data": {
            "id": str(email_record.id),
            "sender": email_record.sender,
            "subject": email_record.subject,
            "category": email_record.category,
            "urgency": email_record.urgency,
            "sentiment_score": email_record.sentiment_score,
            "timestamp": email_record.timestamp.isoformat()
        }
    })
    
    # If escalation, send alert
    if email_record.requires_human:
        await ws_manager.broadcast("global", {
            "type": "escalation_alert",
            "data": {
                "email_id": str(email_record.id),
                "sender": email_record.sender,
                "reason": classification.escalation_reason,
                "urgency": email_record.urgency
            }
        })
    
    return str(email_record.id)
```

---

### **2. Frontend WebSocket Client**

Create `frontend/src/hooks/useWebSocket.js`:

```javascript
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  useEffect(() => {
    function connect() {
      // Use WSL IP or localhost based on environment
      const wsUrl = url.replace('http://', 'ws://').replace('https://', 'wss://');
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket Connected');
        setIsConnected(true);
        if (reconnectTimeout.current) {
          clearTimeout(reconnectTimeout.current);
        }
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket Disconnected');
        setIsConnected(false);
        // Reconnect after 3 seconds
        reconnectTimeout.current = setTimeout(connect, 3000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket Error:', error);
      };
    }

    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, lastMessage, sendMessage };
}
```

---

### **3. Update Inbox Component for Real-Time**

In `frontend/src/components/Inbox.jsx`:

```javascript
import { useWebSocket } from '../hooks/useWebSocket';

function Inbox() {
  // ... existing state ...
  
  // Add WebSocket connection
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const WS_URL = `${API_BASE}/ws`.replace('http', 'ws');
  const { isConnected, lastMessage } = useWebSocket(WS_URL);
  
  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;
    
    if (lastMessage.type === 'new_email') {
      // Add new email to the top of the list
      setEmails(prev => [lastMessage.data, ...prev]);
      setFilteredEmails(prev => [lastMessage.data, ...prev]);
      
      // Show toast notification
      console.log('New email received:', lastMessage.data.subject);
    }
    
    if (lastMessage.type === 'escalation_alert') {
      // Show urgent notification
      console.log('ESCALATION:', lastMessage.data);
    }
  }, [lastMessage]);
  
  return (
    <div className="space-y-4">
      {/* Connection indicator */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Mission Control Inbox</h2>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
            isConnected 
              ? 'bg-green-100 text-green-700' 
              : 'bg-red-100 text-red-700'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            {isConnected ? 'Live' : 'Disconnected'}
          </div>
          {/* ... existing refresh button ... */}
        </div>
      </div>
      
      {/* Rest of inbox component */}
    </div>
  );
}
```

---

### **4. Update Analytics for Real-Time**

In `frontend/src/components/Analytics.jsx`:

```javascript
import { useWebSocket } from '../hooks/useWebSocket';

function Analytics() {
  // ... existing state ...
  
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const WS_URL = `${API_BASE}/ws`.replace('http', 'ws');
  const { isConnected, lastMessage } = useWebSocket(WS_URL);
  
  // Handle real-time updates
  useEffect(() => {
    if (!lastMessage) return;
    
    if (lastMessage.type === 'new_email') {
      // Refresh stats
      const fetchData = async () => {
        try {
          const statsRes = await api.getDashboardStats();
          setStats(statsRes.data);
          
          const perfRes = await api.getAgentPerformance();
          if (perfRes.data) {
            setAgentPerf(perfRes.data);
          }
        } catch (error) {
          console.error('Error fetching updated stats:', error);
        }
      };
      fetchData();
    }
  }, [lastMessage]);
  
  return (
    <div className="space-y-6">
      {/* Connection indicator */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-indigo-50 rounded-lg">
          <Activity size={24} className="text-indigo-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
        <div className={`ml-auto flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
          isConnected 
            ? 'bg-green-100 text-green-700' 
            : 'bg-gray-100 text-gray-500'
        }`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
          {isConnected ? 'Real-time Active' : 'Polling Mode'}
        </div>
      </div>
      
      {/* Rest of analytics */}
    </div>
  );
}
```

---

### **5. Add Toast Notifications (Optional but Nice)**

Install: `npm install react-hot-toast` (in frontend)

Then wrap your App with:

```javascript
import { Toaster, toast } from 'react-hot-toast';

function App() {
  return (
    <>
      <Toaster position="top-right" />
      {/* Your app content */}
    </>
  );
}
```

Use in Inbox when new email arrives:

```javascript
if (lastMessage.type === 'new_email') {
  toast.success(`New email from ${lastMessage.data.sender}`, {
    icon: '📧',
    duration: 3000
  });
}

if (lastMessage.type === 'escalation_alert') {
  toast.error(`⚠️ Escalation: ${lastMessage.data.reason}`, {
    duration: 5000
  });
}
```

---

## 🎯 **Implementation Steps (30 minutes):**

1. **Update ingest router** (10 min)
   - Add ws_manager imports
   - Add broadcast calls after email processing

2. **Create WebSocket hook** (5 min)
   - Create `frontend/src/hooks/useWebSocket.js`

3. **Update Inbox** (5 min)
   - Add WebSocket connection
   - Handle new email messages
   - Add connection indicator

4. **Update Analytics** (5 min)
   - Add WebSocket connection
   - Auto-refresh on new emails
   - Add live indicator

5. **Test** (5 min)
   - Run simulation
   - Watch emails appear in real-time
   - Check connection status

---

## 🧪 **Testing Real-Time:**

```bash
# Terminal 1: Watch backend logs
docker compose logs backend -f

# Terminal 2: Run slow simulation
docker compose exec backend python /app/scripts/simulate_stream.py --file /app/email-data-advanced.json --speed 1

# Browser: Open http://localhost:5173
# Watch emails appear one by one
# See "Live" indicator
# Get notifications for escalations
```

---

## 📊 **What This Gives You:**

✅ **Instant Updates**: Emails appear without refresh  
✅ **Live Connection**: Green "Live" badge when connected  
✅ **Escalation Alerts**: Toast notifications for urgent emails  
✅ **Real-Time Analytics**: Stats update automatically  
✅ **Production Ready**: Automatic reconnection on disconnect  
✅ **Scalable**: WebSocket can handle hundreds of connections  

---

## 🎓 **For Demo:**

"The system uses WebSockets for real-time updates. Watch as I simulate incoming emails - they appear instantly without refreshing. The green 'Live' indicator shows we're connected. When a GDPR request comes in, you'll see an immediate escalation alert."

**Start simulation at speed 1, let evaluator watch emails populate live!** 🚀

---

## ⚡ **Extra Credit: Add Sound Notifications**

```javascript
// In Inbox, when critical email arrives:
if (lastMessage.data.urgency === 'Critical') {
  const audio = new Audio('/notification.mp3');
  audio.play().catch(e => console.log('Audio play failed:', e));
}
```

---

**This makes your system production-grade with real-time capabilities!** 🎯
