# Connecting Your Instagram Account

This is the one-time setup. It takes about 5 minutes and you'll never need to repeat it (unless your token expires after ~60 days of not using Satori).

**You don't need to be technical.** Follow each step exactly as written and you'll be done.

---

## Before you start

Your Instagram account needs to be a **Professional account** (Business or Creator) — not a personal one.

**How to check:** Open Instagram → tap your profile → tap the three lines (☰) → Settings → Account.
- If you see "Switch to Professional Account" → tap it, choose **Creator** or **Business**, and come back here.
- If you already see "Account type and tools" or similar → you're good, keep going.

Your Instagram also needs to be **linked to a Facebook Page.**
- If you haven't done this: Settings → Account → Linked Accounts → Facebook → follow the prompts.
- If you're not sure, just continue — you'll find out in Step 2.

---

## Step 1 — Create a free Meta developer app

Think of this as giving Satori a private key to read your Instagram data — nothing gets posted, nothing gets changed.

1. Go to **[developers.facebook.com](https://developers.facebook.com)** and log in with your regular Facebook account.

2. Click **My Apps** in the top right.
   > You'll land on a page showing your apps (probably empty).

3. Click the **Create App** button.

4. You'll be asked "What do you want your app to do?" — scroll down and select **Other**, then click Next.

5. On the next screen, select **Business** and click Next.

6. Give it a name — anything works, like `My Satori` — and click **Create App**. You may be asked to enter your Facebook password.
   > You'll land on a dashboard with a list of products.

7. Find **Instagram Graph API** in the list and click **Set Up** next to it.

---

## Step 2 — Get your access token

1. Go to **[developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)** — this is Meta's official token generator.

2. In the top right, open the **Meta App** dropdown and select the app you just created.

3. Click the blue **Generate Access Token** button.
   > A pop-up will appear asking you to log in and give permissions.

4. On the permissions screen, make sure these four are turned **ON** (they may already be checked):
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_read_engagement`
   - `pages_show_list`

5. Click **Continue** → **Save** → close the pop-up.
   > You'll see a long string of letters and numbers appear in the Access Token box. It starts with `EAA...`. That's your token.

6. Click the **Copy** icon next to the token to copy it. Keep this tab open — you'll need it in a moment.

---

## Step 3 — Make your token last longer

The token from Step 2 expires in 1 hour. You need to extend it to 60 days.

1. In the same Explorer page, look for a small **info icon (ⓘ)** right next to your token. Click it.
   > A panel opens showing your token details.

2. Click **"Open in Access Token Debugger"**.
   > A new page opens at developers.facebook.com/tools/debug.

3. Near the bottom of that page, click the blue **"Extend Access Token"** button.
   > A new long token appears below it.

4. Copy that new token. This is your **long-lived token** — it lasts 60 days and auto-renews when used regularly.

---

## Step 4 — Save your token to the config file (don't paste it in chat)

Your token is sensitive — treat it like a password. **Don't paste it into the Claude conversation.** Instead, save it directly to a local file that only your machine can see.

1. In your Satori folder, find the file called `config.yaml.example`.

2. Make a copy of it and name the copy `config.yaml`.
   - On Mac: right-click the file → Duplicate, then rename it.
   - Or in terminal: `cp config.yaml.example config.yaml`

3. Open `config.yaml` in any text editor (TextEdit, VS Code, Notepad — anything works).

4. Find the line that says:
   ```
   token: "EAA_PASTE_YOUR_TOKEN_HERE"
   ```
   Replace `EAA_PASTE_YOUR_TOKEN_HERE` with your long-lived token from Step 3. Keep the quotes.

5. Save the file.

6. Come back to your Claude conversation and just say **"I've saved my token to config.yaml"** — don't paste the token itself.

Satori will read the file directly, find your Instagram Account ID automatically, and confirm your connection. Your token never passes through the chat.

---

## That's it

Once Satori confirms your account name, you're connected and ready to go.

---

## If something goes wrong

**"I don't see the Instagram Graph API option in Step 1"**
Go back to your app dashboard and click **Add Product** — you'll find Instagram Graph API there.

**"The permissions aren't showing up in Step 2"**
Make sure you selected your app in the Meta App dropdown before clicking Generate Access Token.

**"I don't see a Facebook Page connected to my Instagram"**
Go to Instagram → Settings → Account → Linked Accounts → Facebook, and connect your account to any Facebook Page. If you don't have a Page, create a free one at facebook.com/pages/create — it doesn't need to be active or public.

**"The Extend Access Token button isn't there"**
Your token may already be long-lived. Check the "Expires" date shown in the debugger. If it's more than 7 days away, you're fine — just use the token as-is.

**"I'm still stuck"**
Just tell Satori what step you're on and what you're seeing. Claude will help you through it.

---

## Token renewal

Your token lasts 60 days and **auto-renews** every time you use Satori within that window. If you use it weekly, it will never expire.

If it does expire: repeat Steps 2, 3, and 4 only. You don't need to create a new app.
