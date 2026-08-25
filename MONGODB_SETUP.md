# MongoDB Setup Guide for Nexus AIOps

## Option 1: MongoDB Atlas (Recommended for Production/Render)

### Step 1: Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" or Sign Up
3. Create a new organization and project
4. Select "Build a Cluster"
5. Choose Free Tier (M0, 512MB storage)
6. Select your region (same as Render for best performance)
7. Create the cluster (takes 5-10 minutes)

### Step 2: Set Up Database User
1. In Atlas, go to "Database Access"
2. Click "Add New Database User"
3. Username: `aiops_user`
4. Password: Generate a secure password (save it!)
5. Built-in Roles: Select "readWriteAnyDatabase"
6. Click "Add User"

### Step 3: Allow Network Access
1. In Atlas, go to "Network Access"
2. Click "Add IP Address"
3. For Render: Click "Allow Access from Anywhere" (0.0.0.0/0)
4. For Local: Add your IP address
5. Click "Confirm"

### Step 4: Get Connection String
1. Go to "Clusters" and click "Connect"
2. Select "Connect your application"
3. Choose Node.js driver
4. Copy the connection string
5. Replace `<username>` and `<password>` with your credentials
6. Replace `<database>` with `nexus_aiops`

Example format:
```
mongodb+srv://aiops_user:PASSWORD@cluster0.xxxxx.mongodb.net/nexus_aiops?retryWrites=true&w=majority
```

### Step 5: Set Environment Variable in Render
1. Go to https://dashboard.render.com
2. Select your `aiops-mvp` service
3. Go to "Environment"
4. Add new variable:
   - Name: `MONGODB_URI`
   - Value: Your connection string from Step 4
5. Click "Save"
6. Service will automatically redeploy

## Option 2: Local MongoDB (Development Only)

### macOS:
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux (Ubuntu):
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Windows:
1. Download from https://www.mongodb.com/try/download/community
2. Run installer
3. Start MongoDB service or run `mongod`

### Local Connection String:
```
mongodb://localhost:27017/nexus_aiops
```

## Testing Your Connection

### Python Test Script:
```python
from pymongo import MongoClient

uri = "your_mongodb_uri_here"
client = MongoClient(uri)
db = client['nexus_aiops']

# Test connection
try:
    client.admin.command('ping')
    print("✓ Connected to MongoDB successfully!")
    print(f"Collections: {db.list_collection_names()}")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Using MongoDB Compass (GUI):
1. Download from https://www.mongodb.com/products/compass
2. Paste your connection string
3. Connect and browse databases/collections

## Collections Created Automatically

The Nexus AIOps app creates these collections on first run:
- `incidents` - Problem incidents from CSV data
- `responses` - Incident response actions
- `users` - User accounts and authentication
- `audit_log` - All system actions and approvals
- `actions` - Executed remediation actions
- `approvals` - Approval requests and statuses

## Troubleshooting

### "Connection refused" error
- Local MongoDB: Ensure `mongod` is running
- Atlas: Check that your IP is whitelisted in Network Access
- Check MONGODB_URI environment variable is set correctly

### "Authentication failed"
- Verify username and password in connection string
- Check that database user exists in Atlas
- Ensure special characters in password are URL-encoded

### Slow connections
- If using Render + Atlas, select same region as Render
- Consider upgrading from M0 to M2 free tier if performance issues

## Monitoring

### View Database Usage
1. Go to Atlas Dashboard
2. Click on your cluster
3. View "Database" tab for collections and data
4. Check "Metrics" for performance stats

### Export Data
1. In Atlas, go to "Clusters"
2. Click "..." → "Export Collection"
3. Choose format (CSV, JSON)
4. Download backup

## Support

- MongoDB Atlas Support: https://docs.mongodb.com/manual/
- Nexus AIOps Issues: Check GitHub issues
- Render Support: https://render.com/docs
