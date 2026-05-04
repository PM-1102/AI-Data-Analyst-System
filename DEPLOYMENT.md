# Streamlit Deployment Guide - DataSense AI

## Quick Deployment to Streamlit Cloud

### Prerequisites
- GitHub account (with this repo pushed)
- Streamlit account (free at streamlit.io)
- Groq API key

### Step 1: Prepare Your Repository

1. **Initialize Git (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: DataSense AI ready for deployment"
   ```

2. **Create a GitHub repository:**
   - Go to github.com and create a new repository
   - Copy the repository URL

3. **Push code to GitHub:**
   ```bash
   git remote add origin YOUR_GITHUB_REPO_URL
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit https://share.streamlit.io
   - Click "New app"

2. **Configure deployment:**
   - **GitHub repo**: Select your repository
   - **Branch**: main
   - **File path**: `streamlit_app.py`

3. **Click Deploy**

### Step 3: Set Environment Variables

1. **After deployment starts:**
   - Click on "Advanced settings" or go to your app settings
   - Go to "Secrets" tab

2. **Add your Groq API key:**
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   GROQ_MODEL = "llama-3.1-8b-instant"
   ENVIRONMENT = "production"
   DEBUG = false
   LOG_LEVEL = "INFO"
   ```

3. **Save secrets** - Streamlit will restart your app

### Step 4: Verify Deployment

1. Check the app logs for any errors
2. Test the full workflow:
   - Upload a CSV/Excel file
   - Click "Clean & Prepare Data"
   - Navigate to KPI and Dashboard tabs
   - Test AI Chat functionality

---

## Alternative: Deploy to Other Platforms

### Heroku Deployment

1. **Install Heroku CLI**
2. **Create Procfile:**
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Create runtime.txt:**
   ```
   python-3.10.12
   ```

4. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

### AWS / Google Cloud / DigitalOcean

- Use Docker containerization
- Set environment variables in your platform's console
- Reference the Streamlit documentation for your platform

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Required: Your Groq API key |
| `GROQ_MODEL` | llama-3.1-8b-instant | AI model to use |
| `ENVIRONMENT` | production | Deployment environment |
| `DEBUG` | false | Enable debug logging |
| `LOG_LEVEL` | INFO | Logging level |
| `MAX_FILE_SIZE_MB` | 100 | Max upload file size |
| `MAX_ROWS_FOR_FULL_ANALYSIS` | 100000 | Max rows to process |

---

## Troubleshooting

### App won't load
- Check Streamlit Cloud logs
- Verify all dependencies in `requirements.txt`
- Ensure `streamlit_app.py` exists in root

### Missing API key error
- Verify GROQ_API_KEY is set in Secrets
- Wait 2-3 minutes after setting secrets for restart
- Check that the key is valid and has proper permissions

### File upload fails
- Check `maxUploadSize` in config.toml
- Increase if needed (max 200 MB)
- Verify disk space on server

### Memory issues
- Reduce `MAX_ROWS_FOR_FULL_ANALYSIS`
- Use smaller sample data for testing
- Consider upgrading Streamlit plan

---

## Security Best Practices

1. **Never commit secrets:**
   - `.streamlit/secrets.toml` is in `.gitignore` ✓
   - Use Streamlit's Secrets management only

2. **Keep dependencies updated:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Use environment-specific configs:**
   - Development: Local `.env` file
   - Production: Streamlit Secrets

4. **Monitor logs:**
   - Check Streamlit Cloud logs regularly
   - Set up alerts for errors

---

## Performance Tips

1. **Cache expensive operations:**
   ```python
   @st.cache_data
   def expensive_function():
       return result
   ```

2. **Optimize data loading:**
   - Use `pd.read_csv()` with `dtype` parameter
   - Load only needed columns

3. **Limit initial data processing:**
   - Lazy load tabs
   - Process on-demand

---

## Monitoring & Maintenance

### Regular checks:
- [ ] Monitor resource usage
- [ ] Review error logs weekly
- [ ] Update dependencies monthly
- [ ] Test full workflow periodically
- [ ] Collect user feedback

### Update process:
1. Test changes locally
2. Commit to GitHub
3. Streamlit Cloud auto-deploys
4. Monitor logs for issues

---

## Support & Documentation

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud:** https://streamlit.io/cloud
- **Groq API:** https://console.groq.com/docs
- **GitHub:** https://github.com

---

## Production Checklist

- [ ] Requirements.txt has all dependencies
- [ ] .gitignore excludes sensitive files
- [ ] streamlit_app.py exists at root
- [ ] Config.toml is optimized for production
- [ ] Groq API key is working
- [ ] All paths are relative (for cross-platform)
- [ ] Error handling is comprehensive
- [ ] Logging is configured
- [ ] README has usage instructions
- [ ] Code is tested locally before push

---

**Happy Deploying! 🚀**
