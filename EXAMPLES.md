# RankBot Usage Examples

## Initial Setup
1. Run the bot: `python bot.py` (with DISCORD_BOT_TOKEN set)
2. In your Discord server, run: `!setup #problems-channel #mods-only #leaderboard @Moderator`

## Example Commands

### For Moderators:

**Post a Problem:**
```
!post_problem "Array Sorting Challenge" This problem requires implementing an efficient sorting algorithm.
```
(Attach a PDF file to this message)

**Score a PDF Solution:**
```
!score_solution 1 85
```
(Scores solution ID 1 with 85 points out of 100)

**Score a Code Submission:**
```
!score_submission 3 8 7 9
```
(Scores submission ID 3: 8/10 completeness, 7/10 elegance, 9/10 speed = 24/30 total)

**View Review Queue:**
```
!review_queue
```

### For Users:

**Submit Code Solution:**
```
!submit python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
```

**Submit PDF Solution:**
Tag the bot in the problems channel with a PDF attachment:
```
@RankBot Here's my solution for problem 1
```
(Attach PDF and include problem ID at the end)

**View Leaderboard:**
```
!leaderboard
```

## Scoring System

### PDF Solutions (0-100 points)
- Simple single score for overall solution quality
- Assigned by moderators using !score_solution

### Code Submissions (0-30 points total)
- **Completeness (0-10)**: Does it solve the problem completely?
- **Elegance (0-10)**: Is the code clean, readable, and well-structured?
- **Speed (0-10)**: Is the algorithm efficient and optimized?

## Channel Setup

The bot uses three main channels:
- **Problems Channel**: Where problems are posted and PDF solutions submitted
- **Moderator Channel**: Private channel where submissions appear for review
- **Leaderboard Channel**: Public channel showing current rankings
