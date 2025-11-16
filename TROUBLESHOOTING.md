# Troubleshooting Guide

## Frontend Shows "Error fetching data"

### Step 1: Check Environment Variable in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Verify `NEXT_PUBLIC_API_URL` is set to your Railway backend URL
   - Should be: `https://your-app-name.up.railway.app`
   - **Important:** No trailing slash!
4. Make sure it's set for **Production**, **Preview**, and **Development** environments
5. **Redeploy** after adding/updating the variable

### Step 2: Check Browser Console

1. Open your deployed Vercel site
2. Open browser DevTools (F12)
3. Go to **Console** tab
4. Look for:
   - `Fetching from: [URL]` - This shows what URL it's trying to fetch
   - Any CORS errors
   - Network errors

### Step 3: Test Backend API Directly

1. Open your Railway backend URL in a browser: `https://your-app.up.railway.app/api/v1/correlation`
2. You should see JSON data
3. If you get an error, the backend has an issue

### Step 4: Check CORS Configuration in Railway

1. Go to Railway dashboard
2. Navigate to your project → **Variables**
3. Check `CORS_ORIGINS` includes your Vercel URL:
   ```
   https://your-vercel-app.vercel.app,http://localhost:3000
   ```
4. **Important:** 
   - Must include `https://` protocol
   - No trailing slashes
   - Comma-separated if multiple origins
5. Redeploy backend after updating

### Step 5: Verify API Endpoint

Test these endpoints directly:

- `https://your-railway-app.up.railway.app/` - Should return API info
- `https://your-railway-app.up.railway.app/health` - Should return `{"status":"healthy"}`
- `https://your-railway-app.up.railway.app/api/v1/correlation` - Should return correlation data

### Common Issues

#### Issue: "API URL is not configured"
**Solution:** Set `NEXT_PUBLIC_API_URL` in Vercel environment variables

#### Issue: CORS Error in Browser Console
**Solution:** 
1. Add your Vercel URL to Railway's `CORS_ORIGINS`
2. Make sure it starts with `https://`
3. Redeploy backend

#### Issue: 404 Not Found
**Solution:** 
1. Check the Railway URL is correct
2. Make sure the endpoint path is `/api/v1/correlation`
3. Test the endpoint directly in browser

#### Issue: 500 Internal Server Error
**Solution:**
1. Check Railway logs for backend errors
2. Verify all dependencies are in `requirements.txt`
3. Check if Kalshi API is accessible

#### Issue: Network Error / Timeout
**Solution:**
1. Check Railway service is running
2. Verify the Railway URL is accessible
3. Check Railway logs for any startup errors

### Debug Checklist

- [ ] `NEXT_PUBLIC_API_URL` is set in Vercel
- [ ] Railway backend is running (check Railway dashboard)
- [ ] `CORS_ORIGINS` includes your Vercel URL
- [ ] Backend URL is accessible (test in browser)
- [ ] No trailing slashes in URLs
- [ ] Environment variables are set for correct environments (Production/Preview)
- [ ] Both services have been redeployed after env var changes

### Testing Locally

To test if everything works locally:

1. **Backend:** Run `python main.py` in backend directory
2. **Frontend:** Create `frontend/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Run `npm run dev` in frontend directory
4. Should work the same as production

### Getting More Details

The updated error message now shows:
- The API URL being used
- More detailed error information
- Console logs for debugging

Check the browser console for detailed error messages.

