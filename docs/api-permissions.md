# Meta Graph API Permissions

This document explains what each permission Satori requests actually does — and what breaks without it.

---

## Required Permissions

### `instagram_basic`
**What it does:** Allows reading your Instagram account's basic information — username, bio, follower count, media count, and the list of your posts (media objects).

**What breaks without it:** Nothing works. This is the foundation. All API calls fail.

**Privacy note:** Read-only. Cannot post, send messages, or modify anything.

---

### `instagram_manage_insights`
**What it does:** Unlocks access to analytics data — reach, impressions, saves, shares, engagement rate, story views, audience demographics, and online follower activity by hour.

**What breaks without it:** You can see your posts but not their performance metrics. Most of Satori's value comes from this permission.

**Privacy note:** Read-only analytics only. No ability to publish or interact.

---

### `pages_read_engagement`
**What it does:** Allows reading the Facebook Page that is connected to your Instagram Business account. Required because the Instagram Business Account is linked through a Page.

**What breaks without it:** The API cannot resolve your Instagram Business Account ID from your Page ID. Account ID lookup fails.

**Privacy note:** Read-only. Cannot post to your Page.

---

### `pages_show_list`
**What it does:** Allows listing all Facebook Pages managed by your account. Used to find which Page is connected to your Instagram account during the account ID discovery step.

**What breaks without it:** The `/me/accounts` call returns empty. You cannot find your Instagram Business Account ID automatically.

---

## Optional Permissions

These are not requested by default but unlock additional capabilities:

### `instagram_manage_comments`
**What it does:** Allows reading comments on your posts (including commenter usernames).

**When to add:** If you want Satori to analyze comment sentiment and recurring questions. Without it, Satori can still read basic comment counts but not comment text.

### `ads_read` (Meta Marketing API)
**What it does:** Allows reading Meta advertising data — campaign performance, ROAS, CPM, ad spend.

**When to add:** If you run Instagram ads and want to correlate organic content performance with paid amplification.

---

## What Satori Cannot Do

Regardless of permissions, Satori **cannot**:
- Post content to Instagram on your behalf (Meta's publishing API requires app review)
- Read direct messages
- Access other users' private data
- Follow, unfollow, like, or comment as you
- Access data from accounts you don't own

All data access is **read-only** and **limited to your own account**.

---

## Permission Scope in the Access Token

When you generate a token in the Graph API Explorer, the token encodes the permissions you selected. You can verify what permissions your token has by calling:

```
GET https://graph.facebook.com/v18.0/me/permissions?access_token={token}
```

The response lists each permission and whether it was granted or declined.
