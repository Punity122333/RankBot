# RankBot - Discord Competition Bot

A Discord bot for managing programming competitions with PDF problem distribution, solution submissions, and automated scoring/leaderboards.

## Features

### PDF & CP Problem Management

- Moderators can post **math** problems (PDF) and **CP** problems (URL) using interactive commands
- Problems are automatically posted in the dedicated problem channel selected via `/setup`
- Problems are assigned unique IDs for reference
- Users submit solutions by tagging the bot with PDF attachments (math) or using the interactive dropdown/code modal (CP)

### Code Submission System

- Users can submit code solutions using the `/submit` slash command
- Supports multiple programming languages
- Solutions appear in a private moderator channel for review

### Scoring System

- PDF solutions: Simple 0-100 point scoring
- Code submissions: Multi-criteria scoring (Completeness, Elegance, Speed - each 0-10 points)
- Automatic leaderboard updates when scores are assigned

### Leaderboard

- Real-time leaderboard combining scores from both submission types  
- Displays top 10 users with medal emojis for top 3
- Auto-updates in designated leaderboard channel

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a Discord application and bot at <https://discord.com/developers/applications>

3. Set your bot token as an environment variable:

```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
```

4. Invite the bot to your server with the following permissions:
   - Send Messages
   - Read Message History
   - Attach Files
   - Use Slash Commands
   - Manage Messages (for moderators)

5. Run the bot:

```bash
python bot.py
```

## Configuration

Use the `/setup` command to configure channels:

```
/setup #problems #moderators #leaderboard @ModeratorRole
```

**Note:** Both math and CP problems are posted in the problem channel you select here. Posting is automatic when a moderator uses the interactive post command.

## Commands

### Moderator Commands

- `/setup <problem_channel> <moderator_channel> <leaderboard_channel> [moderator_role]` - Initial bot setup
- `/post` - Interactive post command (choose Math or CP, then fill out modal)
- `/score_solution <solution_id> <score>` - Score a PDF solution (0-100)
- `/score_submission <submission_id> <completeness> <elegance> <speed>` - Score code submission (0-10 each)
- `/review_queue` - View pending submissions awaiting review

### User Commands

- `/submit` - Interactive solution submission (choose Math or CP, then select problem from dropdown)
- `/leaderboard` - View current rankings
- Tag the bot with PDF attachment and problem ID to submit PDF solution (in problem channel)

## File Structure

- `bot.py` - Main bot code (loads cogs)
- `database.py` - Database logic
- `cogs/` - Bot features split into cogs:
  - `admin.py`, `problems.py`, `submissions.py`, `scoring.py`, `leaderboard.py`
- `utils/config.py` - Configuration and permissions
- `rankbot.db` - SQLite database (auto-created)
- `config.json` - Channel/role configuration (auto-created)
- `requirements.txt` - Python dependencies

## Database Schema

### Problems Table

- id, title, pdf_url, posted_by, posted_at

### Solutions Table (PDF submissions)

- id, problem_id, user_id, pdf_url, submitted_at, score, reviewed

### Submissions Table (Code submissions)  

- id, user_id, code, language, submitted_at, score, reviewed, completeness_score, elegance_score, speed_score
