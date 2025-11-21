# PersonaGym Green Agent - Quick Start Guide

**Get up and running in 10 minutes!**

---

## Step 1: Clone and Setup (2 minutes)

```bash
# Clone your repository
git clone https://github.com/christine1117/agentic-ai.git
cd agentic-ai

# Make setup script executable (Mac/Linux only)
chmod +x setup.sh

# Run automated setup
./setup.sh

# On Windows, run these commands instead:
# python -m venv venv
# venv\Scripts\activate
# pip install -r requirements.txt
```

---

## Step 2: Configure API Keys (1 minute)

**Create a `.env` file:**

```bash
# Create .env file
cat > .env << 'EOL'
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
EOL
```

**Or set environment variables:**

```bash
# Mac/Linux
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"  # Optional

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-openai-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"  # Optional
```

---

## Step 3: Get Your Public IP (1 minute)

**If deploying to cloud:**
```bash
# On your cloud server (AWS, GCP, Azure)
curl ifconfig.me
```

**If testing locally:**
```bash
# Install ngrok
brew install ngrok  # Mac
# or download from https://ngrok.com/

# In terminal 1:
ngrok http 8001

# In terminal 2:
ngrok http 8002

# Use the ngrok URLs in your agent card
```

---

## Step 4: Update Configuration (2 minutes)

**Edit `green_agent_card.toml`:**

```toml
[agent]
name = "EmpaTeam PersonaGym Evaluator"  # Change to your team name
url = "http://YOUR_PUBLIC_IP:8001"      # ← Replace with your IP

[launcher]
url = "http://YOUR_PUBLIC_IP:8002"      # ← Replace with your IP
```

**Example with actual IP:**
```toml
url = "http://54.123.45.67:8001"
```

---

## Step 5: Test Locally (2 minutes)

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate    # Windows

# Run a test evaluation
python green_agent.py
```

You should see:
```
==========================================
PersonaGym Mental Health Evaluation
...
PersonaScore: 4.2/5.0
==========================================
```

---

## Step 6: Deploy to AgentBeats (2 minutes)

```bash
python agentbeats_runner.py green_agent_card.toml \
  --launcher_host 54.123.45.67 \
  --launcher_port 8002 \
  --agent_host 54.123.45.67 \
  --agent_port 8001 \
  --model_type openai \
  --model_name gpt-4o
```

**Replace `54.123.45.67` with your actual public IP!**

---

## Step 7: Register on AgentBeats (2 minutes)

1. Go to https://agentbeats.org
2. Sign in / Create account
3. Navigate to "Register Agent"
4. Fill in:
   - **Agent URL**: `http://YOUR_IP:8001`
   - **Launcher URL**: `http://YOUR_IP:8002`
   - **Agent Name**: Your team name
   - **Agent Type**: Green (Evaluator)
5. Click "Register"
6. Verify agent shows as "Online" ✓

---

## Step 8: Create Your First Battle! (1 minute)

1. Go to "Create Battle"
2. Select your green agent
3. Select purple agent(s) to evaluate
4. Click "Launch Battle"
5. Watch evaluation run in real-time!

---

## 🎉 Done!

You now have a fully functional PersonaGym green agent evaluating LLMs on mental health scenarios!

---

## Quick Commands Reference

```bash
# Setup
./setup.sh

# Activate environment
source venv/bin/activate

# Test locally
python green_agent.py

# Deploy
python agentbeats_runner.py green_agent_card.toml \
  --launcher_host YOUR_IP --launcher_port 8002 \
  --agent_host YOUR_IP --agent_port 8001 \
  --model_type openai --model_name gpt-4o

# Run in background (production)
nohup python agentbeats_runner.py green_agent_card.toml \
  --launcher_host YOUR_IP --launcher_port 8002 \
  --agent_host YOUR_IP --agent_port 8001 \
  --model_type openai --model_name gpt-4o \
  > agent.log 2>&1 &

# Check logs
tail -f agent.log

# Stop background process
ps aux | grep agentbeats_runner
kill <PID>
```

---

## Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API key not set"
```bash
export OPENAI_API_KEY="your-key"  # Mac/Linux
$env:OPENAI_API_KEY="your-key"    # Windows
```

### "Connection refused"
- Check firewall allows ports 8001 and 8002
- Verify agent is running: `ps aux | grep agentbeats`
- Test port: `curl http://YOUR_IP:8001/health`

### "Agent offline on platform"
- Verify public IP is correct
- Check agent is running
- Ensure ports aren't blocked by firewall/security group

---

## Cost Estimate

**Per evaluation run (7 personas, 5 questions each):**
- ~$2.50 in API costs (GPT-4o)
- ~5-10 minutes runtime

**Monthly (100 evaluations):**
- ~$250 in API costs
- Consider using GPT-4o-mini for 90% cost reduction during development

---

## Next Steps

✅ You're all set! Now you can:

1. **Customize personas** - Edit `green_agent.py` to add your own personas
2. **Tune evaluation** - Adjust rubrics and weights for your use case
3. **Analyze results** - Check `./evaluation_results/` for detailed reports
4. **Submit to competition** - Enter the AgentX-AgentBeats competition!

---

## Need Help?

- 📖 **Full docs**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- 🐛 **Issues**: Open an issue on GitHub
- 💬 **Questions**: Contact the team
- 📚 **Resources**: 
  - AgentBeats: https://docs.agentbeats.org
  - PersonaGym: https://personagym.com

---

**Happy Evaluating! 🚀**

*EmpaTeam - Making AI safer for mental health applications*