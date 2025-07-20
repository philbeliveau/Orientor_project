# 👥 Repository Setup Guide for Teammate Access

## 🎯 Overview

This guide helps you prepare the repository so your teammate can independently deploy the Orientor platform frontend to Vercel.

## 🔐 Step 1: Grant Repository Access

### GitHub Collaborator Access
1. Go to your repository: `https://github.com/philbeliveau/Orientor_project`
2. Click **Settings** tab
3. Click **Manage access** (left sidebar)
4. Click **Invite a collaborator**
5. Enter your teammate's GitHub username or email
6. Select permission level: **Write** (allows deployment)
7. Click **Add [username] to this repository**

### Required Permissions
Your teammate needs **Write** access to:
- ✅ Read repository code
- ✅ Access deployment configurations
- ✅ Connect to Vercel (if needed)
- ✅ View project documentation

## 📋 Step 2: Verify Repository State

### Essential Files (Already Present)
Confirm these files exist in your repository:

```
✅ vercel.json                    # Vercel deployment configuration
✅ frontend/package.json          # Frontend dependencies  
✅ frontend/src/app/login/        # Login page
✅ frontend/src/app/register/     # Registration page
✅ frontend/src/app/dashboard/    # Dashboard page
✅ frontend/src/services/api.ts   # API configuration
```

### Configuration Check
Verify `vercel.json` contains correct backend URL:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://orientor-backend-production-7c13.up.railway.app/$1"
    }
  ]
}
```

## 🔧 Step 3: Prepare Documentation

### Share These Files with Your Teammate
1. **Quick Start:** `docs/mapping/deploy-louis/TEAMMATE_QUICK_START.md`
2. **Detailed Guide:** `docs/mapping/deploy-louis/VERCEL_DEPLOYMENT_GUIDE.md`
3. **This Setup Guide:** `docs/mapping/deploy-louis/REPOSITORY_SETUP_GUIDE.md`

### Test Credentials (Optional)
If you want your teammate to test login functionality, provide:
```
Test User Email: [existing-user-email]
Test Password: [password]
```

## 🌐 Step 4: Backend Verification

### Confirm Backend is Running
Before your teammate deploys, verify the backend works:

```bash
# Test health endpoint
curl https://orientor-backend-production-7c13.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "message": "Phase 2 Minimal - Fallback endpoints operational",
  "version": "2.1.0-minimal",
  "platform": "minimal_fallback_endpoints"
}
```

### Test Critical Endpoints
```bash
# Test login endpoint (should work)
curl -X POST https://orientor-backend-production-7c13.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Expected: Either success response or 401 (both indicate endpoint is working)
```

## 📞 Step 5: Communication Checklist

### Information to Share with Teammate

#### Repository Access
- [ ] **GitHub Repository:** `https://github.com/philbeliveau/Orientor_project`
- [ ] **Collaborator Invitation:** Sent and accepted
- [ ] **Documentation:** Shared quick start guide

#### Deployment Info
- [ ] **Backend URL:** `https://orientor-backend-production-7c13.up.railway.app`
- [ ] **Current Status:** Backend is running and healthy
- [ ] **Expected Result:** Frontend will connect automatically to backend

#### Support Resources
- [ ] **Documentation Location:** `docs/mapping/deploy-louis/`
- [ ] **Contact Info:** How to reach you if issues arise
- [ ] **Timeline:** When they need deployment completed

## 🔍 Step 6: Pre-Deployment Testing

### Local Test (Optional but Recommended)
Your teammate can test locally before deploying:

```bash
# Clone repository
git clone https://github.com/philbeliveau/Orientor_project.git
cd Orientor_project

# Install and run frontend
cd frontend
npm install
npm run dev

# Test at: http://localhost:3000
```

### Expected Local Behavior
- ✅ Login page loads at `http://localhost:3000/login`
- ✅ API calls go to Railway backend (check Network tab)
- ✅ Registration/login should work if backend is healthy

## 🚨 Troubleshooting Preparation

### Common Issues and Solutions

#### "Repository not found"
- **Cause:** Teammate doesn't have access
- **Solution:** Check collaborator invitation was accepted

#### "Build failed" on Vercel
- **Cause:** Missing dependencies or configuration
- **Solution:** Verify `package.json` and `vercel.json` are correct

#### "API calls fail"
- **Cause:** Backend is down or URL is wrong
- **Solution:** Check Railway backend health

### Emergency Contacts
Prepare this info for your teammate:
- **Your Contact Info:** [email/phone]
- **Railway Dashboard:** [login info if needed]
- **Vercel Account:** [if you have specific requirements]

## ✅ Ready to Deploy Checklist

Before your teammate starts:
- [ ] Repository access granted and confirmed
- [ ] Backend is running and healthy
- [ ] Documentation shared
- [ ] Test credentials provided (if applicable)
- [ ] Support contact info shared
- [ ] Expected timeline communicated

## 📈 Success Metrics

Your teammate's deployment is successful when:
- ✅ **Vercel deployment completes** without build errors
- ✅ **Frontend loads** at their Vercel URL
- ✅ **Login page works** (form submits to backend)
- ✅ **Registration works** (can create new accounts)
- ✅ **Dashboard loads** after successful login
- ✅ **No console errors** in browser developer tools

## 🔄 Post-Deployment

### After Your Teammate Deploys
1. **Test their deployment** at their Vercel URL
2. **Verify API connectivity** between their frontend and your backend
3. **Update documentation** with their deployment URL if needed
4. **Confirm handoff** is complete and working

### Optional: Multiple Deployments
If you want multiple team members to deploy:
- Each person gets their own Vercel URL (e.g., `teammate1.vercel.app`, `teammate2.vercel.app`)
- All connect to the same Railway backend
- No conflicts or issues with multiple frontend deployments

---

**Note:** Your teammate only deploys the frontend. The backend stays on Railway under your control, so there's no risk of them affecting the core platform infrastructure.