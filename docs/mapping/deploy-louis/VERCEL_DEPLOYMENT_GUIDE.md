# 🚀 Vercel Deployment Guide for Teammates

## 📋 Overview

This guide enables your teammate to deploy the Orientor platform frontend to Vercel independently. The frontend connects to the existing Railway backend that's already configured and running.

## 🎯 Prerequisites

### Required Accounts
- **GitHub Account** with access to the repository
- **Vercel Account** (free tier sufficient)
- **Repository Access** to `https://github.com/philbeliveau/Orientor_project`

### Required Information
- **Backend URL:** `https://orientor-backend-production-7c13.up.railway.app`
- **Repository:** `https://github.com/philbeliveau/Orientor_project`
- **Branch:** `main`

## 🚀 Step-by-Step Deployment

### Step 1: Access the Repository
1. Ensure your teammate has **collaborator access** to the GitHub repository
2. They should be able to view: `https://github.com/philbeliveau/Orientor_project`
3. Verify they can see the `frontend/` directory and `vercel.json` file

### Step 2: Connect to Vercel

#### Option A: Import from GitHub (Recommended)
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"**
3. Click **"Import Git Repository"**
4. Find and select **"Orientor_project"** repository
5. Click **"Import"**

#### Option B: Deploy with Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Clone repository
git clone https://github.com/philbeliveau/Orientor_project.git
cd Orientor_project

# Deploy to Vercel
vercel --prod
```

### Step 3: Configure Deployment Settings

When importing, Vercel will detect Next.js automatically. Configure these settings:

#### Project Settings
- **Framework Preset:** Next.js
- **Root Directory:** `./` (project root, not `./frontend`)
- **Build Command:** `cd frontend && npm run build`
- **Output Directory:** `frontend/.next`
- **Install Command:** `cd frontend && npm install`

#### Environment Variables
Set these in Vercel dashboard under Project Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_BACKEND_URL=https://orientor-backend-production-7c13.up.railway.app
```

### Step 4: Verify Configuration Files

Ensure these files exist in the repository root (they should already be there):

#### `vercel.json` (Already Configured)
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "installCommand": "cd frontend && npm install",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://orientor-backend-production-7c13.up.railway.app/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "/api",
    "NEXT_PUBLIC_BACKEND_URL": "https://orientor-backend-production-7c13.up.railway.app"
  }
}
```

### Step 5: Deploy and Verify

1. **Trigger Deployment**
   - Push to `main` branch triggers automatic deployment
   - Or click "Deploy" in Vercel dashboard

2. **Monitor Build Process**
   - Watch build logs in Vercel dashboard
   - Build should complete in 2-3 minutes

3. **Test Deployment**
   - Visit the provided Vercel URL (e.g., `yourproject.vercel.app`)
   - Test login/registration functionality
   - Verify API calls work properly

## 🔧 Project Structure

Your teammate should understand this structure:

```
Orientor_project/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/
│   │   │   ├── login/        # Login page
│   │   │   ├── register/     # Registration page
│   │   │   └── dashboard/    # Main dashboard
│   │   ├── services/
│   │   │   └── api.ts        # API configuration
│   │   └── components/       # React components
│   ├── package.json          # Frontend dependencies
│   └── next.config.js        # Next.js configuration
├── vercel.json               # Vercel deployment config
└── README.md                 # Project documentation
```

## 🌐 Domain Configuration (Optional)

### Custom Domain Setup
If you want a custom domain instead of `*.vercel.app`:

1. **In Vercel Dashboard:**
   - Go to Project Settings → Domains
   - Click "Add Domain"
   - Enter your domain (e.g., `orientor.yourcompany.com`)

2. **DNS Configuration:**
   - Add CNAME record pointing to `cname.vercel-dns.com`
   - Or follow Vercel's specific DNS instructions

## 🔍 Troubleshooting Common Issues

### Build Failures

#### Issue: "Module not found" errors
```bash
# Solution: Verify package.json exists in frontend/
# Check that all dependencies are listed
cd frontend && npm install
```

#### Issue: "Build command failed"
```bash
# Solution: Check build logs for specific errors
# Ensure Next.js version compatibility
# Verify all TypeScript files compile
```

### Runtime Issues

#### Issue: API calls returning 404
```bash
# Check: Vercel rewrite rules in vercel.json
# Verify: Backend URL is correct
# Test: Backend health endpoint directly
curl https://orientor-backend-production-7c13.up.railway.app/health
```

#### Issue: Environment variables not working
```bash
# Solution: Check Vercel dashboard Environment Variables
# Ensure variables start with NEXT_PUBLIC_ for client-side
# Redeploy after changing environment variables
```

## 📊 Deployment Checklist

### Pre-Deployment
- [ ] Repository access confirmed
- [ ] Vercel account created
- [ ] Backend URL verified as working
- [ ] `vercel.json` configuration reviewed

### During Deployment  
- [ ] Project imported successfully
- [ ] Build settings configured correctly
- [ ] Environment variables set
- [ ] Build completes without errors

### Post-Deployment
- [ ] Site loads at Vercel URL
- [ ] Login page accessible
- [ ] Registration page accessible  
- [ ] API calls work (check browser network tab)
- [ ] Dashboard displays after login

## 🔐 Security Considerations

### Environment Variables
- **Never commit API keys** to the repository
- **Use Vercel dashboard** for sensitive environment variables
- **NEXT_PUBLIC_*** variables are **visible to users**

### API Security
- All API calls go through Vercel proxy to Railway
- CORS is handled by the backend
- Authentication tokens stored in localStorage

## 🚨 Emergency Procedures

### If Deployment Fails
1. **Check build logs** in Vercel dashboard
2. **Verify repository access** and file permissions
3. **Test locally** first: `cd frontend && npm run dev`
4. **Contact original developer** if backend issues suspected

### If Site is Down
1. **Check Vercel status**: [status.vercel.com](https://status.vercel.com)
2. **Test backend**: `curl https://orientor-backend-production-7c13.up.railway.app/health`
3. **Check recent deployments** in Vercel dashboard
4. **Rollback if needed** to previous working deployment

## 📞 Support Resources

### Documentation
- **Vercel Docs:** [vercel.com/docs](https://vercel.com/docs)
- **Next.js Docs:** [nextjs.org/docs](https://nextjs.org/docs)
- **Project Docs:** `docs/mapping/deploy-louis/DEPLOYMENT_DOCUMENTATION.md`

### Quick Commands
```bash
# Test frontend locally
cd frontend && npm run dev

# Check build locally  
cd frontend && npm run build

# Deploy manually
vercel --prod

# Check deployment logs
vercel logs [deployment-url]
```

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Site loads at Vercel URL without errors
- ✅ Login page works (`/login`)
- ✅ Registration page works (`/register`)
- ✅ Dashboard loads after authentication (`/dashboard`)
- ✅ All API calls return data (check browser network tab)
- ✅ No console errors in browser developer tools

## 📋 Handoff Checklist

For the original developer to prepare for teammate deployment:

- [ ] **Repository Access:** Add teammate as collaborator
- [ ] **Vercel Account:** Ensure teammate has Vercel account
- [ ] **Documentation:** Share this guide
- [ ] **Backend Status:** Verify Railway backend is running
- [ ] **Test Credentials:** Provide test user credentials if needed
- [ ] **Domain Info:** Share any custom domain requirements
- [ ] **Environment Secrets:** Share any required API keys securely

---

**Note:** This deployment connects to the existing Railway backend. Your teammate does NOT need to deploy or configure the backend - only the frontend on Vercel.