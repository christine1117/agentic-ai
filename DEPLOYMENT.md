# PersonaGym Green Agent Deployment Guide

**Team: EmpaTeam**  
**Project: Evaluating LLMs Capability in Roleplaying with PersonaGym Benchmark**

## Overview

This guide walks you through deploying the PersonaGym Mental Health Green Agent to AgentBeats platform for evaluating LLMs' mental health role-playing capabilities.

---

## Prerequisites

### 1. System Requirements
- Python >= 3.11
- Public IP address or cloud server (AWS, GCP, Azure, etc.)
- Stable internet connection
- 8GB+ RAM recommended

### 2. API Keys
You need API keys for LLM evaluation:
- **Required**: OpenAI API key (for GPT-4o evaluator)
- **Optional**: Anthropic API key (for Claude evaluator in ensemble)

Get your keys:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### 3. AgentBeats Account
- Create account at: https://agentbeats.org
- Familiarize yourself with the platform interface

---

## Step 1: Environment Setup

### Clone Your Repository
```bash
git clone https://github.com/christine1117/agentic-ai.git
cd agentic-ai
```

### Create Virtual Environment
```bash
# Create virtual environment (requires Python >= 3.11)
python3.11 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\activate

# On Windows (CMD):
venv\Scripts\activate.bat
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 2: Configure Agent

### Set Environment Variables

**On Linux/Mac (bash/zsh):**
```bash
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"  # Optional
```

**On Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-openai-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"  # Optional
```

**Persistent Environment Variables (Recommended):**

Create a `.env` file in your project root:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

Then install and use python-dotenv:
```bash
pip install python-dotenv
```

### Update Agent Card

Edit `green_agent_card.toml`:

```toml
[agent]
name = "EmpaTeam PersonaGym Evaluator"  # Your team name
url = "http://YOUR_PUBLIC_IP:8001"     # Your server IP

[launcher]
url = "http://YOUR_PUBLIC_IP:8002"     # Same server IP
```

**Finding Your Public IP:**
```bash
# On cloud servers:
curl ifconfig.me

# Or check your cloud provider's dashboard
# AWS: EC2 instance details
# GCP: VM instance external IP
# Azure: Virtual machine public IP
```

---

## Step 3: Deploy to Cloud (Recommended)

### Option A: AWS EC2

1. **Launch EC2 Instance:**
   - Instance type: t3.medium or larger
   - AMI: Ubuntu 22.04 LTS
   - Storage: 20GB+
   - Security Group: Open ports 8001 and 8002

2. **Configure Security Group:**
   ```
   Type: Custom TCP
   Port Range: 8001
   Source: 0.0.0.0/0
   
   Type: Custom TCP
   Port Range: 8002
   Source: 0.0.0.0/0
   ```

3. **SSH into instance:**
   ```bash
   ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
   ```

4. **Install dependencies on EC2:**
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv git
   
   # Clone your repo
   git clone https://github.com/christine1117/agentic-ai.git
   cd agentic-ai
   
   # Setup as described in Step 1
   ```

### Option B: Google Cloud Platform

1. **Create VM Instance:**
   - Machine type: e2-standard-2
   - Boot disk: Ubuntu 22.04 LTS, 20GB
   - Firewall: Allow HTTP/HTTPS traffic

2. **Configure firewall rules:**
   ```bash
   gcloud compute firewall-rules create allow-agentbeats \
     --allow tcp:8001,tcp:8002 \
     --source-ranges 0.0.0.0/0
   ```

3. **SSH and setup:**
   ```bash
   gcloud compute ssh your-instance-name
   # Follow Step 1 installation
   ```

### Option C: Local Development (Testing Only)

⚠️ **Warning:** Local deployment requires:
- Port forwarding on your router
- Static IP or dynamic DNS
- Not recommended for production

Use ngrok for testing:
```bash
# Install ngrok
brew install ngrok  # Mac
# or download from https://ngrok.com/

# Expose ports
ngrok http 8001  # In one terminal
ngrok http 8002  # In another terminal

# Use ngrok URLs in agent card
```

---

## Step 4: Run the Agent

### Validate Configuration
```bash
python agentbeats_runner.py green_agent_card.toml \
  --launcher_host YOUR_PUBLIC_IP \
  --launcher_port 8002 \
  --agent_host YOUR_PUBLIC_IP \
  --agent_port 8001 \
  --model_type openai \
  --model_name gpt-4o \
  --validate-only
```

### Start the Agent
```bash
python agentbeats_runner.py green_agent_card.toml \
  --launcher_host YOUR_PUBLIC_IP \
  --launcher_port 8002 \
  --agent_host YOUR_PUBLIC_IP \
  --agent_port 8001 \
  --model_type openai \
  --model_name gpt-4o
```

**Example with actual IP:**
```bash
python agentbeats_runner.py green_agent_card.toml \
  --launcher_host 54.123.45.67 \
  --launcher_port 8002 \
  --agent_host 54.123.45.67 \
  --agent_port 8001 \
  --model_type openai \
  --model_name gpt-4o
```

### Run in Background (Production)

Using `screen`:
```bash
screen -S personagym-agent
python agentbeats_runner.py green_agent_card.toml ...
# Press Ctrl+A then D to detach

# Reattach later:
screen -r personagym-agent
```

Using `nohup`:
```bash
nohup python agentbeats_runner.py green_agent_card.toml \
  --launcher_host YOUR_PUBLIC_IP \
  --launcher_port 8002 \
  --agent_host YOUR_PUBLIC_IP \
  --agent_port 8001 \
  --model_type openai \
  --model_name gpt-4o \
  > agent.log 2>&1 &

# Check logs:
tail -f agent.log
```

Using `systemd` (best for production):
```bash
# Create service file
sudo nano /etc/systemd/system/personagym-agent.service
```

```ini
[Unit]
Description=PersonaGym Green Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/agentic-ai
Environment="OPENAI_API_KEY=your-key"
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/home/ubuntu/agentic-ai/venv/bin/python agentbeats_runner.py green_agent_card.toml --launcher_host YOUR_IP --launcher_port 8002 --agent_host YOUR_IP --agent_port 8001 --model_type openai --model_name gpt-4o
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable personagym-agent
sudo systemctl start personagym-agent

# Check status
sudo systemctl status personagym-agent

# View logs
sudo journalctl -u personagym-agent -f
```

---

## Step 5: Register on AgentBeats

1. **Login to AgentBeats:**
   - Go to https://agentbeats.org
   - Sign in with your account

2. **Register Your Agent:**
   - Navigate to agent registration page
   - Fill in the form:
     ```
     Agent Name: EmpaTeam PersonaGym Evaluator
     Agent Type: Green (Evaluator)
     Agent URL: http://YOUR_PUBLIC_IP:8001
     Launcher URL: http://YOUR_PUBLIC_IP:8002
     Description: Evaluates LLM mental health role-playing using PersonaGym
     ```

3. **Verify Agent:**
   - Platform will send health check to your agent
   - Confirm agent appears as "Online" in dashboard

4. **Create Evaluation Battle:**
   - Go to "Create Battle" section
   - Select your green agent as orchestrator
   - Select purple agents (LLMs to evaluate)
   - Configure evaluation parameters:
     - Number of personas: 7 (default mental health personas)
     - Questions per persona: 5
     - Evaluation dimensions: All 7 dimensions
   - Launch battle!

---

## Step 6: Monitor and Collect Results

### View Live Evaluation
- Watch battle progress on AgentBeats dashboard
- See real-time scores and evaluations
- Monitor for any errors or issues

### Access Results
Results are saved in multiple locations:

1. **Local Files:**
   ```bash
   # Evaluation results
   ls -la ./evaluation_results/
   
   # View latest result
   cat ./evaluation_results/evaluation_*.json | jq
   ```

2. **AgentBeats Platform:**
   - View leaderboard rankings
   - Download detailed reports
   - Compare across purple agents

3. **Result Structure:**
   ```json
   {
     "evaluation_type": "PersonaGym Mental Health",
     "average_persona_score": 4.2,
     "aggregate_dimension_scores": {
       "expected_action": 4.5,
       "empathy": 4.3,
       "support": 4.1,
       ...
     },
     "individual_results": [...]
   }
   ```

---

## Troubleshooting

### Agent Won't Start

**Check Python version:**
```bash
python --version  # Must be 3.11+
```

**Verify dependencies:**
```bash
pip list | grep agentbeats
pip list | grep openai
```

**Check environment variables:**
```bash
echo $OPENAI_API_KEY  # Should print your key
```

### Connection Issues

**Test ports are open:**
```bash
# From another machine
curl http://YOUR_PUBLIC_IP:8001/health
curl http://YOUR_PUBLIC_IP:8002/health
```

**Check firewall:**
```bash
# Ubuntu
sudo ufw status
sudo ufw allow 8001
sudo ufw allow 8002

# Check cloud security groups
```

**Verify agent is listening:**
```bash
netstat -tuln | grep 8001
netstat -tuln | grep 8002
```

### API Key Issues

**Test OpenAI key:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Test Anthropic key:**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### Evaluation Errors

**Check logs:**
```bash
tail -f agent.log
# or
sudo journalctl -u personagym-agent -f
```

**Common issues:**
- Rate limiting: Add delays between API calls
- Token limits: Reduce question length
- Model unavailable: Check API status pages

### Platform Registration Issues

**Agent not showing as online:**
- Verify URLs are publicly accessible
- Check agent is actually running
- Ensure ports aren't blocked

**Battle won't start:**
- Confirm both green and purple agents are online
- Check agent compatibility
- Review error messages in platform

---

## Performance Optimization

### Reduce Evaluation Time
```python
# In green_agent.py, reduce questions per persona
num_questions_per_persona = 3  # Default is 5
```

### Use Caching
```python
# Implement response caching for repeated questions
import functools

@functools.lru_cache(maxsize=100)
def cached_evaluate(question_hash):
    # Your evaluation logic
    pass
```

### Batch API Calls
```python
# Evaluate multiple dimensions in parallel
import asyncio

async def parallel_evaluate(dimensions):
    tasks = [evaluate_dimension(d) for d in dimensions]
    return await asyncio.gather(*tasks)
```

---

## Cost Estimation

### API Costs per Evaluation

**Per persona evaluation (~5 questions):**
- Question generation: ~$0.05 (GPT-4o)
- Response evaluation (7 dimensions × 5 questions): ~$0.30
- Total per persona: ~$0.35

**Full evaluation (7 personas):**
- Estimated cost: ~$2.50 per purple agent
- Monthly (100 evaluations): ~$250

**Cost reduction strategies:**
- Use GPT-4o-mini for some tasks: 90% cheaper
- Implement caching for repeated evaluations
- Batch API requests
- Use fewer questions during development

---

## Security Best Practices

### Protect API Keys
```bash
# Never commit keys to git
echo ".env" >> .gitignore
echo "*.log" >> .gitignore

# Use environment variables, not hardcoded keys
# Rotate keys regularly
```

### Secure Your Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8001/tcp
sudo ufw allow 8002/tcp

# Install fail2ban
sudo apt install fail2ban -y
```

### Monitor for Abuse
```bash
# Set up rate limiting in your agent
# Monitor API usage in OpenAI/Anthropic dashboards
# Set up billing alerts
```

---

## Next Steps

### Phase 1: Development (Completed)
✅ Green agent implementation  
✅ PersonaGym integration  
✅ Mental health persona evaluation  
✅ Deployment configuration  

### Phase 2: Testing
- [ ] Run pilot evaluations with test personas
- [ ] Validate scoring against human judgments
- [ ] Tune evaluation prompts and rubrics
- [ ] Test edge cases and safety scenarios

### Phase 3: Production
- [ ] Deploy to production server
- [ ] Register on AgentBeats leaderboard
- [ ] Evaluate multiple purple agents
- [ ] Collect and analyze results
- [ ] Write evaluation report

### Phase 4: Publication
- [ ] Document findings
- [ ] Create demo video
- [ ] Submit to AgentX competition
- [ ] Share results with community

---

## Support & Resources

### Documentation
- AgentBeats Docs: https://docs.agentbeats.org
- PersonaGym Paper: https://arxiv.org/abs/2407.18416
- A2A Protocol: https://ai.google.dev/gemini-api/docs/a2a

### Team Contact
- Team: EmpaTeam
- GitHub: https://github.com/christine1117/agentic-ai
- Project Lead: [Your Email]

### Get Help
1. Check troubleshooting section above
2. Review AgentBeats documentation
3. Search GitHub issues
4. Ask on AgentBeats Discord/Slack
5. Email course staff

---

## Appendix: Quick Reference

### Essential Commands
```bash
# Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
export OPENAI_API_KEY="your-key"
nano green_agent_card.toml  # Update IPs

# Run
python agentbeats_runner.py green_agent_card.toml \
  --launcher_host YOUR_IP \
  --launcher_port 8002 \
  --agent_host YOUR_IP \
  --agent_port 8001 \
  --model_type openai \
  --model_name gpt-4o

# Monitor
tail -f agent.log
sudo systemctl status personagym-agent
```

### Port Reference
- **8001**: Agent endpoint (A2A protocol communication)
- **8002**: Launcher endpoint (receives reset signals)

### File Structure
```
agentic-ai/
├── green_agent_card.toml       # Agent configuration
├── green_agent.py              # Main evaluation logic
├── agentbeats_runner.py        # Platform integration
├── requirements.txt            # Python dependencies
├── evaluation_results/         # Output directory
│   └── evaluation_*.json       # Evaluation results
├── .env                        # API keys (gitignored)
└── DEPLOYMENT.md              # This file
```

---

**Good luck with your evaluation! 🚀**

*For questions or issues, refer to the Support section or contact the team.*