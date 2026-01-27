# Standard Operating Procedures (SOPs)

## Daily Operations

### Morning Routine (Every Day)
**Time Required**: 15 minutes

1. **Check System Status**
   ```bash
   # Check if all services are running
   python examples/test_connections.py
   ```

2. **Review Logs**
   ```bash
   # Check for overnight errors
   tail -n 100 logs/video_toolkit.log
   
   # Check upload logs
   tail -n 50 logs/multi_platform_upload.json
   ```

3. **Monitor Quotas**
   - Check YouTube API quota
   - Check TikTok API limits
   - Review upload counts
   - Verify storage space

4. **Review Performance**
   - Check video views/engagement
   - Review trending topics
   - Analyze successful content
   - Identify improvements

---

### Video Production Procedure

#### Procedure 1: Manual Single Video Creation
**Time Required**: 30-60 minutes

**Step 1: Research (5 min)**
```bash
python main.py --research-only
```
- Review output in `output/trends/`
- Select most promising topic
- Note topic score and source

**Step 2: Deep Research (10 min)**
```bash
python -c "
import asyncio
from agents.deep_research_agent import DeepResearchAgent
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

agent = DeepResearchAgent(config)
research = asyncio.run(agent.research_topic('YOUR_TOPIC_HERE'))
agent.save_research(research)
"
```
- Review research output
- Verify key points
- Check video angles

**Step 3: Generate Video (15 min)**
```bash
python examples/basic_workflow.py
```
- Monitor generation progress
- Check for errors
- Review generated video

**Step 4: Edit Video (10 min)**
```bash
python -c "
from agents.video_editing_agent import VideoEditingAgent

config = {'video_generation': {'output_directory': 'output/videos'}}
agent = VideoEditingAgent(config)

edits = {
    'color_grade': 'vibrant',
    'trim': {'start': 0, 'duration': 60}
}

edited = agent.edit_video('output/videos/YOUR_VIDEO.mp4', edits)
short = agent.create_short_form(edited, duration=60)
print(f'Short form: {short}')
"
```
- Apply color grading
- Trim to optimal length
- Create short versions

**Step 5: Review & Approve (5 min)**
- Watch full video
- Check quality
- Verify no errors
- Approve for upload

**Step 6: Upload (5 min)**
- Prepare metadata
- Select platforms
- Schedule upload
- Monitor status

---

#### Procedure 2: Automated Batch Production
**Time Required**: 2-3 hours (mostly automated)

**Step 1: Configure Batch**
Edit `config/config.yaml`:
```yaml
workflow:
  auto_generate: true
  auto_upload: false  # Review before upload
  batch_size: 5
```

**Step 2: Start Batch Production**
```bash
python crews/video_production_crew.py
```

**Step 3: Monitor Progress**
```bash
# In separate terminal
watch -n 30 'ls -lh output/videos/ | tail -10'
```

**Step 4: Review Outputs**
- Check each video
- Review metadata
- Approve quality
- Flag issues

**Step 5: Bulk Upload**
```bash
# After review, enable auto-upload
python -c "
import asyncio
from agents.multiplatform_upload_agent import MultiPlatformUploadAgent
import glob

config = {'upload': {'platforms': ['youtube_shorts', 'tiktok']}}
agent = MultiPlatformUploadAgent(config)

videos = glob.glob('output/videos/short_*.mp4')
for video in videos:
    metadata = {
        'title': 'AI Generated Content',
        'description': 'Automated video',
        'tags': ['AI', 'Automated']
    }
    results = asyncio.run(agent.upload_to_all_platforms(video, metadata))
    print(f'Uploaded: {video}')
"
```

---

#### Procedure 3: Emergency Content Creation
**Time Required**: 15 minutes (fast response to breaking topics)

**Use Case**: Trending topic breaks, need quick content

**Step 1: Quick Research (2 min)**
```bash
python -c "
import asyncio
from agents.trending_topics_agent import TrendingTopicsAgent

config = {'research': {'sources': ['reddit', 'twitter']}}
agent = TrendingTopicsAgent(config)
trends = asyncio.run(agent.research())
print(trends[0])  # Get top trending
"
```

**Step 2: Generate Short Form (8 min)**
```bash
python -c "
import asyncio
from crews.video_production_crew import ShortFormCrew
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

crew = ShortFormCrew(config)
result = asyncio.run(crew.create_short_form('BREAKING_TOPIC', duration=30))
print(result)
"
```

**Step 3: Quick Upload (5 min)**
- Verify video quality
- Add breaking/trending hashtags
- Upload to all platforms
- Share immediately

---

### Weekly Maintenance

#### Monday: Strategy Review
**Time Required**: 30 minutes

1. **Analyze Previous Week**
   - Review view counts
   - Check engagement rates
   - Identify top performers
   - Note failures

2. **Update Content Calendar**
   - Plan week's topics
   - Schedule productions
   - Set goals

3. **Optimize Settings**
   - Adjust prompts
   - Update templates
   - Refine workflows

#### Wednesday: Technical Check
**Time Required**: 20 minutes

1. **Update Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Check Disk Space**
   ```bash
   df -h
   du -sh output/*
   ```

3. **Clean Temporary Files**
   ```bash
   rm -rf temp/*
   find output/ -name "*.tmp" -delete
   ```

4. **Backup Important Files**
   ```bash
   tar -czf backup_$(date +%Y%m%d).tar.gz config/ workflows/ output/trends/
   ```

#### Friday: Performance Optimization
**Time Required**: 30 minutes

1. **Review Logs**
   ```bash
   grep ERROR logs/video_toolkit.log | tail -50
   ```

2. **Analyze Upload Success Rate**
   ```bash
   python -c "
   import json
   with open('logs/multi_platform_upload.json') as f:
       logs = json.load(f)
   
   total = len(logs)
   successful = sum(1 for log in logs if log['status'] == 'success')
   print(f'Success rate: {successful/total*100:.1f}%')
   "
   ```

3. **Update Trending Sources**
   - Add new content sources
   - Remove low-quality sources
   - Adjust scoring weights

4. **Optimize Prompts**
   - Test new prompt variations
   - Update based on results
   - Document improvements

---

### Monthly Tasks

#### First Week: Deep Analysis
1. **Monthly Report**
   - Total videos created
   - Total views across platforms
   - Engagement metrics
   - Top performing content
   - ROI analysis

2. **Strategy Adjustment**
   - Update content types
   - Adjust posting schedule
   - Modify platform focus
   - Update target audience

#### Second Week: System Maintenance
1. **Update Models**
   ```bash
   ollama pull llama2
   ollama pull mistral
   ```

2. **Update ComfyUI**
   ```bash
   cd ComfyUI
   git pull
   pip install -r requirements.txt
   ```

3. **Security Audit**
   - Rotate API keys
   - Update credentials
   - Review access logs
   - Check for vulnerabilities

#### Third Week: Content Refresh
1. **Update Templates**
   - Refresh intro/outro
   - Update color schemes
   - Modify transitions
   - Test new effects

2. **Update Music Library**
   - Add new background tracks
   - Remove unused music
   - Check licensing

3. **Refresh Workflows**
   - Test new ComfyUI nodes
   - Update workflow JSONs
   - Document changes

#### Fourth Week: Training & Documentation
1. **Document Learnings**
   - What worked well
   - What didn't work
   - New techniques discovered
   - Process improvements

2. **Update Documentation**
   - Update README
   - Improve guides
   - Add examples
   - Fix errors

---

## Emergency Procedures

### Procedure: System Down
**Severity**: High
**Response Time**: Immediate

1. **Assess Impact**
   - Which services are down?
   - Are uploads affected?
   - Is data safe?

2. **Check Logs**
   ```bash
   tail -n 200 logs/video_toolkit.log
   journalctl -u ollama -n 100
   ```

3. **Restart Services**
   ```bash
   # Restart Ollama
   pkill ollama
   ollama serve &
   
   # Restart ComfyUI
   cd ComfyUI
   pkill -f "python main.py"
   python main.py &
   ```

4. **Verify Recovery**
   ```bash
   python examples/test_connections.py
   ```

5. **Document Incident**
   - What happened
   - What was affected
   - How it was fixed
   - How to prevent

---

### Procedure: Upload Failures
**Severity**: Medium
**Response Time**: 1 hour

1. **Check API Status**
   - YouTube API status
   - TikTok API status
   - Instagram API status

2. **Verify Credentials**
   - Check API keys
   - Refresh OAuth tokens
   - Test authentication

3. **Check Rate Limits**
   ```bash
   python -c "
   from agents.multiplatform_upload_agent import MultiPlatformUploadAgent
   import yaml
   
   with open('config/config.yaml') as f:
       config = yaml.safe_load(f)
   
   agent = MultiPlatformUploadAgent(config)
   print(agent.get_upload_stats())
   "
   ```

4. **Retry Failed Uploads**
   - Get list of failed uploads
   - Retry manually
   - Log results

---

### Procedure: Quality Issues
**Severity**: Medium
**Response Time**: 2 hours

1. **Identify Problem**
   - Video quality poor
   - Audio issues
   - Generation failures
   - Consistency problems

2. **Adjust Settings**
   - Increase resolution
   - Change models
   - Modify prompts
   - Adjust parameters

3. **Test Changes**
   - Generate test video
   - Review quality
   - Compare to baseline
   - Document changes

4. **Update Templates**
   - Save successful settings
   - Update configurations
   - Document parameters

---

## Checklist Templates

### Pre-Launch Checklist
- [ ] All services running
- [ ] API keys configured
- [ ] Models downloaded
- [ ] Storage space available
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Documentation reviewed
- [ ] Test run successful

### Video Quality Checklist
- [ ] Resolution correct
- [ ] Audio clear
- [ ] No artifacts
- [ ] Color good
- [ ] Length appropriate
- [ ] Subtitles accurate
- [ ] Branding consistent
- [ ] Meets platform specs

### Upload Checklist
- [ ] Metadata complete
- [ ] Hashtags optimized
- [ ] Title compelling
- [ ] Description detailed
- [ ] Thumbnail created
- [ ] Tags added
- [ ] Platform requirements met
- [ ] Schedule set

### Daily Monitoring Checklist
- [ ] Services status
- [ ] Error logs reviewed
- [ ] Uploads successful
- [ ] Quotas checked
- [ ] Performance metrics
- [ ] Engagement reviewed
- [ ] Issues logged
- [ ] Actions taken

---

## Contact & Escalation

### Issue Severity Levels

**P0 - Critical**
- Complete system down
- Data loss
- Security breach
- Response: Immediate

**P1 - High**
- Upload failures
- Generation failures
- Service degradation
- Response: 1 hour

**P2 - Medium**
- Quality issues
- Performance degradation
- Minor bugs
- Response: 1 day

**P3 - Low**
- Feature requests
- Documentation
- Optimization
- Response: 1 week

---

**Document Version**: 1.0
**Last Updated**: 2024-01-27
**Next Review**: 2024-02-27
