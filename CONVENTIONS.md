# Conventions: How to Read & Customize This Toolkit

> [!IMPORTANT]
> **Every value you must change for YOUR environment is marked the same way everywhere in this repo.**
> If you only learn one thing before running anything, learn the **CHANGE-ME convention** below.

This single page explains the symbols, colours, and tokens used across all docs and scripts so
that anyone — even a non-developer — can tell *exactly* what to edit before running a script.

---

## 1. The CHANGE-ME convention (read this first)

Plain GitHub Markdown cannot truly colour text **inside** a code block, so this toolkit uses a
convention that works everywhere and is impossible to miss: a **sentinel token** plus a **trailing comment**.

Wherever a script needs a real value from your environment, you will see this pattern:

```powershell
# vvv  CHANGE ME  vvv -------------------------------------------------
$SmtpServer = "<<CHANGE_ME: smtp.yourcompany.local>>"      # CHANGE ME
$FromAddress = "<<CHANGE_ME: grc-bot@yourcompany.local>>"  # CHANGE ME
$EvidenceRoot = "<<CHANGE_ME: \\fileserver\GRC\Evidence>>" # CHANGE ME
# ^^^  CHANGE ME  ^^^ -------------------------------------------------
```

Three signals point at the same thing so you cannot miss it:

| Signal | What it looks like | What to do |
|--------|--------------------|------------|
| **Sentinel token** | `<<CHANGE_ME: example value>>` | Replace the **whole token including the angle brackets** with your real value. Keep the surrounding quotes. |
| **Trailing comment** | `# CHANGE ME` (or `// CHANGE ME`) | Marks the exact line that needs editing. |
| **Banner block** | `# vvv CHANGE ME vvv` ... `# ^^^ CHANGE ME ^^^` | Groups all the values you must edit at the top of a script. |

> [!TIP]
> **Find every value to change in seconds.** Open the script and press `Ctrl+F`, then search for
> `CHANGE_ME` (scripts) or `CHANGE ME` (comments). Editors like **VS Code** and **Notepad++** will
> highlight every hit. In VS Code you can also install the *TODO Highlight* extension and add
> `CHANGE_ME` to its keyword list to render every token in **bright orange/red** automatically.

### Make it literally a colour (optional, recommended)

If you want the replaceable parts to actually appear in a **different colour** while you edit:

1. Open the script in **VS Code** (free).
2. Install the extension **TODO Highlight** (`Gruntfuggly.todo-highlight`) or **Better Comments**.
3. Add `CHANGE_ME` and `CHANGE ME` to the keyword list in settings.
4. Every replaceable value now renders in a bold colour of your choice, so editing is foolproof.

A ready-to-paste VS Code setting is provided in [`.vscode/settings.json`](.vscode/settings.json) in this repo —
open the repo folder in VS Code and the colours turn on automatically.

---

## 2. Token vocabulary

You will see a small, fixed set of token names. Each always means the same thing:

| Token | Meaning | Example real value |
|-------|---------|--------------------|
| `<<CHANGE_ME: ...>>` | A value unique to your environment that you MUST set | a path, server, email |
| `<<PATH: ...>>` | A folder or file path on your shared drive / OneDrive | `\\fileserver\GRC` |
| `<<EMAIL: ...>>` | A mailbox or distribution list | `grc@company.local` |
| `<<SERVER: ...>>` | A hostname (SMTP, file server, SharePoint site) | `smtp.company.local` |
| `<<OWNER: ...>>` | A person/team name used in registers | `Risk Manager` |
| `<<OPTIONAL: ...>>` | A value you MAY change but a sensible default exists | reminder day count |

Anything **not** wrapped in `<<...>>` is safe to leave as-is unless a comment says otherwise.

---

## 3. Markdown callouts used in the docs

The guides use GitHub's native coloured alert boxes so important notes stand out visually:

> [!NOTE]
> Background / context — nice to know.

> [!TIP]
> A shortcut or best-practice that saves you time.

> [!IMPORTANT]
> Do not skip this — the outcome depends on it.

> [!WARNING]
> A safety / governance boundary. Usually means *a human must approve*, never automate.

> [!CAUTION]
> Risk of data loss or an irreversible action. Stop and double-check.

---

## 4. The golden governance rule (applies to every script)

> [!WARNING]
> **Automation in this toolkit only REPORTS, COLLECTS, TRACKS, and NOTIFIES.**
> It must never delete, disable, deprovision, change permissions, accept risk, approve exceptions,
> or send external/breach notifications on its own. Every irreversible or judgement-based action
> stays **human-approved**. If a script seems to do otherwise, treat it as a bug.

---

## 5. Where to go next

- New here? Start with the **[DIY-GUIDE.md](DIY-GUIDE.md)** — granular, click-by-click steps for every task.
- Want the big picture? See the **[README.md](README.md)**.
- Looking for a specific pillar? Browse **[docs/](docs/)** (01–21).
- Ready to run code? See **[scripts/](scripts/)** and edit the `CHANGE_ME` values first.
