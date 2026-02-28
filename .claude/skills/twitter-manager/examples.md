# Twitter (X) Manager - Examples

## Basic Usage

### Example 1: Simple Tweet

**User Prompt:**
```
Create a tweet about our new product launch
```

**Claude Action:**
1. Generates content:
   ```
   🚀 BIG NEWS! We just launched something that will save you hours every week.

   Say goodbye to [pain point] and hello to [solution].

   Try it free: [link]

   #ProductLaunch #Innovation
   ```

2. Creates `TWITTER_POST_20260111_180000.md` in `/Pending_Approval/`
3. Notifies user: "Created tweet draft. Review in /Pending_Approval/"

**User Action:**
1. Reviews file
2. Moves to `/Approved/`

**System Action:**
1. `twitter_approval_monitor.py` detects file
2. `twitter_poster.py` posts to Twitter
3. Generates summary in `/Briefings/`
4. Moves file to `/Done/`

---

### Example 2: Reply to Tweet

**User Prompt:**
```
Reply to @elonmusk's tweet about AI
```

**Claude Action:**
1. Generates content:
   ```
   @elonmusk Totally agree! AI is transforming how we work.

   The key is finding the right balance between automation and human creativity.

   What's your take on that?
   ```

2. Creates `TWITTER_REPLY_20260111_180000.md` in `/Pending_Approval/`
   ```yaml
   ---
   type: twitter_post
   reply_to: elonmusk
   ---
   ```

**User Action:**
1. Reviews file
2. Moves to `/Approved/`

**System Action:**
1. `twitter_approval_monitor.py` detects file
2. `twitter_poster.py` posts reply with `--reply-to elonmusk`
3. Generates summary in `/Briefings/`

---

### Example 3: Thread Creation

**User Prompt:**
```
Create a thread about productivity tips for remote workers
```

**Claude Action:**
1. Generates thread:
   ```
   🧵 THREAD: 5 Productivity Tips for Remote Workers

   1/ Working from home? You need these 5 productivity hacks:

   2/ 1. Create a dedicated workspace
   Your brain needs to associate a specific space with work. No working from bed!

   3/ 2. Set clear boundaries
   Start and end times. When you're done, close the laptop and walk away.

   4/ 3. Take real breaks
   Not just scrolling Twitter. Go outside, stretch, grab water.

   5/ 4. Over-communicate
   Your team can't see you. Update them often on progress and blockers.

   6/ 5. Batch similar tasks
   Check email 2-3 times per day. Deep work the rest of the time.

   7/ Want more remote work tips?
   Follow me for daily content! 👋
   ```

2. Creates `TWITTER_THREAD_20260111_180000.md` in `/Pending_Approval/`

**User Action:**
1. Reviews thread
2. Edits if needed
3. Moves to `/Approved/`

**System Action:**
1. Posts each tweet sequentially (future enhancement)
2. Currently: User must manually post thread

---

## Advanced Examples

### Example 4: Content Repurposing

**User Prompt:**
```
Turn our latest blog post into a Twitter thread
```

**Claude Action:**
1. Reads blog post from `/Blog/latest-post.md`
2. Extracts key points
3. Creates thread:
   ```
   🧵 THREAD: [Blog Post Title]

   1/ Just published a deep dive on [topic]. Here's what you need to know:

   2/ [Key point 1 from blog]

   3/ [Key point 2 from blog]

   4/ [Key point 3 from blog]

   5/ [Key point 4 from blog]

   6/ Want to learn more?
   Read the full post: [link]

   7/ [Bonus insight not in blog]
   ```

---

### Example 5: Engaging Question Tweet

**User Prompt:**
```
Create an engaging question tweet about work-life balance
```

**Claude Action:**
1. Generates content:
   ```
   What's the #1 work-life boundary you've set that changed everything?

   I'll start: No email after 7 PM. Game changer. 🙌

   Reply with yours!
   ```

2. Creates `TWITTER_POST_20260111_180000.md` in `/Pending_Approval/`

---

### Example 6: Behind-the- Scenes Tweet

**User Prompt:**
```
Share a behind-the-scenes tweet about our development process
```

**Claude Action:**
1. Generates content:
   ```
   Building in public today 🛠️

   We're working on [feature] and here's our process:
   1. User interviews
   2. Wireframes
   3. Build
   4. Test
   5. Ship

   What's your dev process?
   ```

2. Creates `TWITTER_POST_20260111_180000.md` in `/Pending_Approval/`

---

## Workflow Examples

### Example 7: Daily Content Routine

**User Prompt:**
```
Create today's Twitter content plan
```

**Claude Action:**
1. Generates 3 tweets for the day:
   - Morning: Tip tweet
   - Afternoon: Question tweet
   - Evening: Behind-the-scenes tweet

2. Creates 3 files in `/Pending_Approval/`:
   - `TWITTER_POST_20260111_080000.md` (Morning)
   - `TWITTER_POST_20260111_130000.md` (Afternoon)
   - `TWITTER_POST_20260111_180000.md` (Evening)

3. Notifies user: "Created 3 tweets. Review and approve when ready to post."

---

### Example 8: Event Live-Tweeting

**User Prompt:**
``
I'm at a conference today, create tweets for live updates
```

**Claude Action:**
1. Generates template tweets:
   ```
   📍 Live from [Conference Name]!

   Just saw an amazing talk by [Speaker] about [Topic].

   Key takeaway: [Insight]

   #[ConferenceHashtag]
   ```

2. Creates 5 templates in `/Pending_Approval/`
3. Notifies user: "Created live-tweet templates. Fill in details during event."

---

## Tone Variations

### Example 9: Professional Tone

**User Prompt:**
```
Create a professional tweet about our new partnership
```

**Generated Content:**
```
Excited to announce our partnership with [Company]!

Together, we're bringing [value proposition] to our customers.

Learn more: [link]

#Partnership #Innovation
```

---

### Example 10: Casual Tone

**User Prompt:**
```
Create a casual tweet about our team Friday
```

**Generated Content:**
```
Pizza day at the office! 🍕

Nothing beats team bonding over food. Who else loves team lunches?

#TeamLife #StartupLife
```

---

### Example 11: Excited Tone

**User Prompt:**
```
Create an excited tweet about hitting a milestone
```

**Generated Content:**
```
🎉 WE DID IT!!!

Just hit [10,000] [customers/users/downloads]!

This wouldn't be possible without YOU. Thank you for being on this journey with us! 🙏❤️

#Milestone #Grateful #Growing
```

---

## Troubleshooting Examples

### Example 12: Character Limit Issue

**Problem:** Generated tweet exceeds 280 characters

**User Prompt:**
```
The tweet is too long. Shorten it.
```

**Claude Action:**
1. Analyzes content
2. Splits into thread or shortens
3. Creates new version:
   ```
   Long content → Thread of 2-3 tweets
   OR
   Remove fluff, keep key message
   ```

---

### Example 13: Edit Before Approval

**User Action:**
```
User edits TWITTER_POST_20260111_180000.md before approving
```

**Process:**
1. User opens file in `/Pending_Approval/`
2. Makes edits
3. Saves
4. Moves to `/Approved/`
5. System posts edited version

---

## Integration Examples

### Example 14: Cross-Platform Posting

**User Prompt:**
```
Share this on Twitter, LinkedIn, and Facebook
```

**Claude Action:**
1. Creates 3 files in `/Pending_Approval/`:
   - `TWITTER_POST_20260111_180000.md` (200 chars, hashtags)
   - `LINKEDIN_POST_20260111_180000.md` (300 chars, professional)
   - `META_POST_20260111_180000.md` (Facebook & Instagram)

2. Each file optimized for platform

---

### Example 15: Weekly Twitter Metrics

**User Prompt:**
```
Include Twitter metrics in my weekly briefing
```

**Claude Action:**
1. Reads Twitter post summaries from `/Briefings/`
2. Analyzes engagement (if available)
3. Adds section to weekly briefing:
   ```markdown
   ## Twitter (X) Activity

   ### This Week
   - Tweets posted: 5
   - Replies sent: 3
   - Top performing tweet: [link]

   ### Insights
   - [Engagement insights]
   - [Recommendations for next week]
   ```

---

## Command-Line Examples

### Example 16: Direct Tweet Posting

```bash
# Post a tweet directly
python scripts/social-media/twitter_poster.py "Quick update: Just shipped a new feature! 🚀"

# Post a reply
python scripts/social-media/twitter_poster.py "Thanks for sharing! @user" --reply-to user

# Dry run to test
python scripts/social-media/twitter_poster.py "Test tweet" --dry-run
```

---

### Example 17: Monitor Testing

```bash
# Test the approval monitor in dry-run mode
python scripts/social-media/twitter_approval_monitor.py --vault . --dry-run

# Run monitor for real
python scripts/social-media/twitter_approval_monitor.py --vault .

# Run in background with PM2
pm2 start scripts/social-media/twitter_approval_monitor.py --name twitter-monitor -- --vault .
```

---

## Real-World Scenarios

### Scenario 1: Product Launch Day

**Goal:** Announce product launch on Twitter

**Tweets:**
1. **Morning teaser:** "Something big coming today... 👀"
2. **Launch announcement:** "It's live! [Product] is here. [Link]"
3. **Demo tweet:** "Here's how it works: [Video/gif]"
4. **Social proof:** "Already 100+ users in the first hour! 🎉"
5. **Thank you:** "Thank you to everyone who supported us on this journey! 🙏"

**Timeline:** Post every 2-3 hours

---

### Scenario 2: Thought Leadership

**Goal:** Establish expertise in industry

**Weekly Content:**
- **Monday:** Industry tip
- **Wednesday:** Question to engage
- **Friday:** Behind-the-scenes

**Example Month:**
- Week 1: Productivity tips
- Week 2: Industry trends
- Week 3: Common mistakes
- Week 4: Success stories

---

### Scenario 3: Community Building

**Goal:** Grow engaged following

**Daily Routine:**
- **Morning:** Retweet 3 valuable posts from others
- **Mid-day:** Share original content
- **Afternoon:** Reply to mentions
- **Evening:** Engage with industry conversations

**Results:** 20-30% engagement rate

---

## Quick Reference

### Tweet Templates

```python
# Tip tweet
"[Topic] Tip: [One-line advice]\n\n[Optional context]\n\n#Hashtag"

# Question tweet
"[Question]?\n\n[Optional context]\n\nReply with your answer!"

# News tweet
"[News] + [Your take]\n\n[Optional insight]\n\nLink: [URL]"

# Behind the scenes
"[What you're doing] + [Why it matters]\n\n[Optional process]"
```

### Character Count Tips

```
- Keep it under 240 for easy retweets with comments
- Use link shorteners for long URLs
- Remove unnecessary words
- Use emojis instead of words when appropriate
```

---

*Last Updated: 2026-01-11*
