# Instagram Lead Generation Tool

A powerful Python tool to scrape and collect Instagram profiles for lead generation using Google Custom Search API and Instagram data enrichment.

## 📋 Overview

This tool helps you find Instagram profiles of professionals (Doctors, Lawyers, E-commerce businesses) in specific locations with filtering capabilities based on follower count and external URLs.

## ✨ Features

- **Multi-API Key Support**: Rotate through multiple Google API keys to bypass daily quota limits
- **Smart Filtering**: Filter profiles by follower count (< 100k) and external URLs
- **Data Enrichment**: Extract follower counts, bios, emails, and external URLs from Instagram
- **Location-based Search**: Target specific cities (Mumbai, Delhi, etc.)
- **Profession-based**: Search for Doctors, Lawyers, E-commerce businesses
- **CSV Export**: Save results in clean CSV format
- **API Quota Tracking**: Monitor API usage to stay within limits

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Cloud Account (for Custom Search API)
- Google Custom Search Engine (CX)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Google API keys and Search Engine ID:
   ```bash
   # For single API key
   GOOGLE_API_KEY=your_api_key_here
   GOOGLE_CX=your_search_engine_id

   # For multiple API keys (recommended)
   GOOGLE_API_KEYS=key1,key2,key3,key4
   GOOGLE_CX_IDS=cx1,cx1,cx1,cx1  # Can use same CX for all
   ```

### Getting API Keys

1. **Google Custom Search API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or use existing)
   - Enable "Custom Search API"
   - Create credentials → API Key
   - Copy the API key

2. **Google Custom Search Engine ID (CX)**:
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Create a new search engine
   - Search the entire web
   - Copy the Search Engine ID (CX)

3. **For Multiple Keys** (Optional but Recommended):
   - Create 2-4 additional Google Cloud projects
   - Enable Custom Search API in each
   - Create API key for each project
   - You can use the same CX for all keys

## 💻 Usage

### Run the Tool

```bash
python main.py
```

### What It Does

1. **Searches Google** for Instagram profiles matching:
   - Professions: Doctor, Physician, Lawyer, Advocate, E-commerce, Online Store
   - Locations: Mumbai, Delhi
   - Multiple query variations for better coverage

2. **Enriches Data** using Instaloader:
   - Follower count
   - Biography
   - Email (if in bio)
   - External URL

3. **Filters Results**:
   - Removes profiles with 100k+ followers
   - Removes profiles with external URLs

4. **Exports to CSV**: `data/instagram_profiles.csv`

### Output Format

The CSV file contains:
- `username` - Instagram username
- `name` - Full name from profile
- `profession` - Profession category
- `link` - Instagram profile URL
- `followers` - Follower count
- `biography` - Bio text
- `email` - Email extracted from bio
- `external_url` - External website URL
- `snippet` - Google search snippet

## 📊 Results

### Expected Output
- **With 1 API Key**: 40-80 profiles per day
- **With 4 API Keys**: 150-200 profiles per day
- **API Quota**: 100 queries per key per day
- **Run Time**: 5-15 minutes depending on profiles found

### Sample Results
```
Total Profiles: 43
- Doctors/Physicians: 6
- Lawyers/Advocates: 24
- E-commerce/Online Stores: 13

API Usage:
- Queries Used: 215
- Remaining Capacity: 165
```

## 🔧 Configuration

### Customize Search Parameters

Edit `main.py` to modify:

**Professions** (line 185):
```python
profession_keywords = {
    "Doctor": ["Doctor", "Physician"],
    "Lawyer": ["Lawyer", "Advocate"],
    "E-commerce": ["E-commerce", "Online Store"]
}
```

**Locations** (line 193):
```python
locations = ["Mumbai", "Delhi"]
# Add more: "Bangalore", "Pune", "Kolkata", etc.
```

**Follower Limit** (line 22):
```python
MAX_FOLLOWERS = 100000  # Change to desired limit
```

**Query Limit** (line 48):
```python
MAX_QUERIES = 95  # Maximum queries per API key
```

## 📁 Project Structure

```
instagram_leadgen_tool/
├── main.py              # Main script with multi-key support
├── config.py            # Configuration loader
├── requirements.txt     # Python dependencies
├── .env                 # Your API keys (not in git)
├── .env.example         # Template for .env
├── data/
│   └── instagram_profiles.csv  # Output file
└── logs/
    └── run.log          # Execution logs
```

## ⚙️ How It Works

1. **Google Search**: Uses Google Custom Search API to find Instagram profile URLs
2. **Username Extraction**: Parses URLs to extract Instagram usernames
3. **Profile Enrichment**: Uses Instaloader to fetch profile details
4. **Smart Filtering**: Applies follower and URL filters
5. **Deduplication**: Removes duplicate profiles
6. **CSV Export**: Saves clean data to CSV

## 🔐 API Limits & Best Practices

### Google Custom Search API
- **Free Tier**: 100 queries/day per key
- **Paid Tier**: $5 per 1,000 queries (10,000/day limit)
- **Reset Time**: Midnight Pacific Time

### Instagram/Instaloader
- **Rate Limiting**: Instagram may block requests if too frequent
- **Best Practice**: Use delays between requests (already implemented)
- **Login Session**: Optional, for better reliability

### Tips for Maximum Results
1. Use 3-4 different API keys for 300-400 queries/day
2. Run during off-peak hours
3. Add delays if hitting Instagram rate limits
4. Create different Google Cloud projects for separate keys
5. Monitor logs for errors

## 🐛 Troubleshooting

### Common Issues

**"429 Too Many Requests"**
- Solution: API quota exhausted, wait 24 hours or use additional API keys

**"401 Unauthorized" from Instagram**
- Solution: Instagram rate limiting, reduce scraping speed or use login session

**"No profiles found"**
- Solution: Check API keys are correct, try different search keywords

**"Missing environment variables"**
- Solution: Ensure `.env` file has correct `GOOGLE_API_KEYS` and `GOOGLE_CX_IDS`

### Check Logs
```bash
# View recent errors
Get-Content logs/run.log -Tail 50
```

## 📝 Legal & Ethical Considerations

- ✅ Uses public Instagram data only
- ✅ Respects Instagram's public API limits
- ⚠️ Follow GDPR/CCPA if applicable
- ⚠️ Use data responsibly
- ⚠️ Respect Instagram Terms of Service
- ⚠️ Don't spam or harass users

## 🎯 Use Cases

- **Lead Generation**: Find potential clients/customers
- **Market Research**: Analyze competitor presence
- **Networking**: Connect with professionals
- **Business Development**: Identify partnership opportunities

## 🔄 Future Enhancements

Potential improvements:
- Add more professions and keywords
- Support for more locations
- Email validation
- Direct Instagram API integration
- Automated follow-up tracking
- Excel export with formatting
- GUI interface

## 📞 Support

For issues or questions:
1. Check logs: `logs/run.log`
2. Verify API keys in `.env`
3. Ensure all dependencies installed
4. Check Google Cloud Console for API status

## 📄 License

This project is for educational and personal use. Ensure compliance with:
- Google API Terms of Service
- Instagram Terms of Service
- Data privacy laws (GDPR, CCPA, etc.)

## 🙏 Acknowledgments

- Google Custom Search API
- Instaloader Library
- Python Community

---

**Made with ❤️ for lead generation automation**

**Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Production Ready ✅
