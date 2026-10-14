# Videod API

yt-dlp ভিত্তিক ভিডিও লিংক এক্সট্রাক্টর API।

## ফোল্ডার স্ট্রাচার

```
videod-api/
├── api/
│   └── index.py          # মূল API কোড
├── vercel.json           # Vercel কনফিগারেশন
├── requirements.txt      # Python প্যাকেজ
└── README.md             # এই ফাইল
```

## ডিপ্লয়মেন্ট গাইড (Vercel)

### ধাপ ১: Vercel CLI ইনস্টল করুন
```bash
npm i -g vercel
```

### ধাপ ২: প্রজেক্ট ফোল্ডারে যান
```bash
cd videod-api
```

### ধাপ ৩: Vercel-এ লগইন করুন
```bash
vercel login
```

### ধাপ ৪: ডিপ্লয় করুন
```bash
vercel --prod
```

ডিপ্লয় শেষে আপনার API URL পাবেন:
```
https://your-project.vercel.app/api
```

## API ব্যবহার

### POST /api

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "success": true,
  "title": "Rick Astley - Never Gonna Give You Up",
  "platform": "youtube",
  "author": "Rick Astley",
  "duration": 213,
  "thumbnail": "https://i.ytimg.com/vi/...",
  "links": {
    "Best Video (1080p)": "https://...",
    "720p Video": "https://...",
    "Best Audio (128kbps)": "https://..."
  }
}
```

## সমর্থিত প্ল্যাটফর্ম

- YouTube
- TikTok
- Instagram (Reels, Posts)
- Facebook (Public videos)
- X / Twitter
- এবং yt-dlp যে সব প্ল্যাটফ্ম সমর্থন করে

## সমস্যা সমাধান

**"Unsupported URL" এরর:**
- লিংকটি পাবলিক কিনা চেক করুন
- সঠিক পোস্ট/ভিডিও URL ব্যবহার করুন (প্রোফাইল URL নয়)

**"Private" এরর:**
- প্রাইভেট পোস্ট ডাউনলোড করা যাবে না

**Vercel টাইমআউট:**
- Vercel-এর ফ্রি প্ল্যানে ১০ সেকেন্ড টাইমআউট আছে
- বড় ভিডিওর জন্য Render বা Railway ব্যবহার করুন

## yt-dlp আপডেট

yt-dlp নিয়মিত আপডেট করতে হয় কারণ YouTube তাদের সিস্টেম পরিবর্তন করে।

`requirements.txt`-এ `yt-dlp==2025.10.14` সংস্করণটি আপডেট করুন এবং পুনরায় ডিপ্লয় করুন।
