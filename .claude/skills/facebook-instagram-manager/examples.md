# Facebook & Instagram Manager - Examples

This document provides practical examples of using the Facebook & Instagram Manager skill.

---

## EXAMPLE 1: Quick Facebook Post

**User Request:**
> "Post to Facebook about our new product launch"

**What Happens:**

1. **Claude generates content:**
   ```python
   python .claude/skills/facebook-instagram-manager/scripts/generate_fb_content.py \
       --vault . \
       --topic "Our new AI-powered analytics tool is now live!" \
       --tone professional
   ```

2. **Creates file:** `/Pending_Approval/FACEBOOK_POST_20260111_143000.md`

3. **Content generated:**
   ```
   🚀 We're excited to share...

   Our new AI-powered analytics tool is now live!

   Learn more in the link below.

   Let us know your thoughts in the comments!

   #ProductLaunch #NewFeatures #Innovation
   ```

4. **User reviews** the file in `/Pending_Approval/`

5. **User edits** if needed (adds link, adjusts hashtags)

6. **User moves file to `/Approved/`**

7. **Meta approval monitor** detects the file and posts to Facebook

8. **File moved to `/Done/`**

9. **Summary generated** in `/Briefings/Meta_Post_Summary_*.md`

---

## EXAMPLE 2: Instagram Post with Image

**User Request:**
> "Create an Instagram post about our team event, use this image: team.jpg"

**What Happens:**

1. **Claude generates content:**
   ```python
   python .claude/skills/facebook-instagram-manager/scripts/generate_insta_content.py \
       --vault . \
       --topic "Amazing team building day at the office!" \
       --tone fun \
       --image ./images/team.jpg
   ```

2. **Creates file:** `/Pending_Approval/INSTAGRAM_POST_20260111_143500.md`

3. **Content generated:**
   ```
   ✨ Guess what?!

   Amazing team building day at the office!

   Tap the link in our bio for more! 📱

   #CompanyNews #BehindTheScenes #TeamWork #TeamCulture
   ```

4. **Image attached** to the approval file

5. **User reviews** and moves to `/Approved/`

6. **Posted to Instagram** with the image

---

## EXAMPLE 3: Cross-Platform Post

**User Request:**
> "Post to both Facebook and Instagram about our upcoming webinar"

**What Happens:**

1. **Claude creates TWO approval files:**

   **Facebook version:**
   - File: `FACEBOOK_POST_20260111_144000.md`
   - Longer content (200 chars)
   - Link to registration page
   - 3-5 hashtags

   **Instagram version:**
   - File: `INSTAGRAM_POST_20260111_144100.md`
   - Shorter content (100 chars)
   - "Link in bio" call-to-action
   - 15 hashtags
   - Image required

2. **User reviews both files**

3. **User can:**
   - Approve both (move both to `/Approved/`)
   - Approve only one
   - Edit content before approving

4. **Both posted** to their respective platforms

---

## EXAMPLE 4: Weekly Content Planning

**User Request:**
> "Generate content ideas for this week on Facebook and Instagram"

**What Happens:**

1. **Claude analyzes:**
   - Business goals from `Business_Goals.md`
   - Upcoming events from `Calendar/`
   - Past performance from `Briefings/`

2. **Generates content calendar:**
   ```python
   python .claude/skills/facebook-instagram-manager/scripts/generate_meta_calendar.py \
       --vault . \
       --week 2026-W02
   ```

3. **Creates:** `/Plans/Content_Calendar_2026-W02.md`

4. **Calendar includes:**
   - Monday: Company news (Facebook)
   - Tuesday: Product tip (Instagram + Story)
   - Wednesday: Behind-the-scenes (both)
   - Thursday: Customer testimonial (Facebook)
   - Friday: Team spotlight (Instagram)

5. **User reviews** and approves topics

6. **Claude generates** individual approval files for each post

---

## EXAMPLE 5: Performance Review

**User Request:**
> "How did our Facebook posts perform last week?"

**What Happens:**

1. **Claude reads:** All `Meta_Post_Summary_*.md` files from last week

2. **Analyzes metrics:**
   - Posts published: 5
   - Total engagement: 234 likes, 45 comments, 12 shares
   - Best performing post: "Product launch announcement" (89 likes)
   - Best posting time: Tuesday 2:00 PM

3. **Generates insights:**
   - "Product-related posts get 2x more engagement"
   - "Posts with images perform 40% better"
   - "Tuesday/Wednesday are best days"

4. **Recommendations:**
   - "Post more product features content"
   - "Always include high-quality images"
   - "Schedule important posts for Tuesday/Wednesday"

---

## EXAMPLE 6: A/B Testing

**User Request:**
> "Test two different headlines for this post on Facebook"

**What Happens:**

1. **Claude creates TWO approval files:**

   **Option A:** `FACEBOOK_POST_Test_A_20260111.md`
   ```
   🚀 New Feature Alert!

   We've just launched our latest integration...
   ```

   **Option B:** `FACEBOOK_POST_Test_B_20260111.md`
   ```
   💡 Save 2 Hours Every Day

   Our new automation feature just launched...
   ```

2. **User posts Option A** on Monday

3. **User posts Option B** on Tuesday (similar time)

4. **After 48 hours**, compare performance

5. **Claude analyzes** and recommends winner for future posts

---

## EXAMPLE 7: Story Integration

**User Request:**
> "Create Instagram Stories to accompany the product launch post"

**What Happens:**

1. **Claude generates Story sequence:**

   **Story 1 (Teaser - 2 hours before):**
   ```
   Something big is coming... 🚀
   #ComingSoon
   ```

   **Story 2 (At post time):**
   ```
   IT'S HERE! Check our latest post! 👆
   ```

   **Story 3 (Behind the scenes):**
   ```
   Behind the scenes of our development process 🛠️
   ```

   **Story 4 (Engagement):**
   ```
   What feature do you want next?
   [Poll sticker]
   ```

   **Story 5 (Call to action):**
   ```
   Tap the link in our bio to learn more! 🔗
   ```

2. **Creates approval file** with Story sequence

3. **User approves** and posts Stories throughout the day

---

## EXAMPLE 8: Crisis Management

**User Request:**
> "Post a clarification about the service outage"

**What Happens:**

1. **Claude detects urgency** (priority: high)

2. **Generates content** with:
   - Professional, apologetic tone
   - Clear explanation
   - ETA for resolution
   - Regular updates commitment

3. **Content:**
   ```
   ⚠️ Service Update

   We're currently experiencing an outage affecting [service].
   Our team is working hard to resolve this.

   We expect to be back online within [timeframe].
   We'll keep you updated here.

   Thank you for your patience. 🙏

   #ServiceUpdate #StatusUpdate
   ```

4. **User reviews and approves** immediately

5. **Posted to both platforms** simultaneously

6. **Follow-up posts** scheduled automatically

---

## EXAMPLE 9: User-Generated Content

**User Request:**
> "Share this customer review on Instagram, they posted about us"

**What Happens:**

1. **Claude creates repost approval file:**

2. **Content includes:**
   - Credit to original poster (@username)
   - Permission statement
   - Brand comment
   - Relevant hashtags

3. **Content:**
   ```
   🙌 Look at this amazing review from @customername!

   We love seeing our community thrive!

   Reposted with permission ✅

   #CustomerLove #Community #Repost
   ```

4. **User ensures** they have permission to repost

5. **Posted** with appropriate credit

---

## EXAMPLE 10: Seasonal Campaign

**User Request:**
> "Create a New Year campaign for both platforms"

**What Happens:**

1. **Claude generates campaign plan:**

   **Theme:** "New Year, New Tools"

   **Posts:**
   - Dec 31: Reflection post
   - Jan 1: Welcome message + goals
   - Jan 2: Feature spotlight (New Year focused)
   - Jan 3: Customer success story
   - Jan 4: Team predictions for industry
   - Jan 5: Productivity tips for the year

2. **Creates 6 approval files** (one per day)

3. **Visual consistency** across all posts

4. **Campaign hashtag:** #NewYearNewTools

5. **User reviews** entire campaign

6. **Schedules posts** across the week

---

## 🎯 BEST PRACTICES FROM EXAMPLES

### ✅ DO:
- Always review content before approving
- Include clear calls-to-action
- Use platform-specific content (don't copy-paste)
- Post consistently (3-5 times per week)
- Respond to engagement within 24 hours
- Use analytics to refine strategy
- Test different content types

### ❌ DON'T:
- Skip the approval process
- Post the exact same content to both platforms
- Ignore comments and messages
- Post at random times
- Over-post (max 2-3 per day per platform)
- Buy followers or engagement

---

## 📊 METRICS TO TRACK

Based on the examples above, track:

1. **Engagement rate:** (likes + comments + shares) / reach
2. **Best posting times:** When does your audience engage most?
3. **Content types:** Which topics perform best?
4. **Hashtag performance:** Which hashtags drive reach?
5. **Follower growth:** Are you gaining followers consistently?
6. **Click-through rate:** Are people visiting your website?

---

*For more information, see SKILL.md*
