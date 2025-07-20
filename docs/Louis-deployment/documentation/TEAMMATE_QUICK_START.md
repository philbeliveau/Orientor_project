# ⚡ Teammate Quick Start Guide

## 🎯 Goal: Deploy Orientor Platform Frontend in 10 Minutes

Your teammate needs to deploy the frontend to Vercel. The backend is already running on Railway.

## 🚀 Super Quick Deployment (5 Minutes)

### Step 1: Get Access (1 minute)
1. Ensure access to: `https://github.com/philbeliveau/Orientor_project`
2. Create Vercel account at: [vercel.com](https://vercel.com)

### Step 2: Deploy (2 minutes)
1. Go to [vercel.com/new](https://vercel.com/new)
2. Click **"Import Git Repository"**
3. Select **"Orientor_project"**
4. Click **"Deploy"** (use default settings)

### Step 3: Verify (2 minutes)
1. Visit the Vercel URL when build completes
2. Test login at: `[your-url]/login`
3. Verify API works (should connect to existing backend)

**Done!** The `vercel.json` file already has all the correct configuration.

## 🔧 Configuration (Already Done)

The repository already includes:

### ✅ `vercel.json` (Pre-configured)
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next", 
  "framework": "nextjs",
  "installCommand": "cd frontend && npm install",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://orientor-backend-production-7c13.up.railway.app/$1"
    }
  ]
}
```

### ✅ Environment Variables (Pre-configured)
- `NEXT_PUBLIC_API_URL=/api`
- `NEXT_PUBLIC_BACKEND_URL=https://orientor-backend-production-7c13.up.railway.app`

## 🧪 Testing Checklist

After deployment, test these URLs:

- [ ] **Homepage:** `https://[your-vercel-url].vercel.app/`
- [ ] **Login:** `https://[your-vercel-url].vercel.app/login`
- [ ] **Registration:** `https://[your-vercel-url].vercel.app/register`
- [ ] **Dashboard:** `https://[your-vercel-url].vercel.app/dashboard` (after login)

## 🆘 If Something Goes Wrong

### Build Fails?
- Check build logs in Vercel dashboard
- Ensure repository access is correct
- Try deploying again (sometimes it's a temporary issue)

### Site Loads but API Doesn't Work?
- Check browser console for errors
- Verify backend is running: `https://orientor-backend-production-7c13.up.railway.app/health`
- Check that Vercel rewrite rules are working

### Can't Access Repository?
- Contact repository owner for collaborator access
- Ensure GitHub account has proper permissions

## 📞 Need Help?

1. **Check the detailed guide:** `VERCEL_DEPLOYMENT_GUIDE.md`
2. **Vercel Support:** [vercel.com/support](https://vercel.com/support)
3. **Test backend directly:** 
   ```bash
   curl https://orientor-backend-production-7c13.up.railway.app/health
   ```

## ✅ Success Criteria

Your deployment works when:
- ✅ Login page loads without errors
- ✅ Can create new account
- ✅ Can login with existing account
- ✅ Dashboard shows user information

**That's it!** The backend handles all the heavy lifting - your teammate just needs to deploy the frontend interface.

---

**Estimated Time:** 5-10 minutes for experienced developers, 15-30 minutes for beginners.