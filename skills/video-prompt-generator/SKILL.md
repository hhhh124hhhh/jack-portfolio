---
name: video-prompt-generator
description: Generate high-quality video prompts with 10+ styles and Grok Imagine API integration. Features history management, search/filter, export to JSON/Markdown, and web UI with direct video generation. Supports landscape, product, tech, emotional, urban, food, sports, ancient Chinese, anime, and abstract art styles with automatic enhancement and batch generation.
metadata:
  {
    "clawdbot":
      {
        "emoji": "🎬",
        "requires": { "bins": ["python3"], "env": ["XAI_API_KEY"] },
        "primaryEnv": "XAI_API_KEY",
      },
  }
---

# Video Prompt Generator

Generate high-quality video prompts with 10+ creative styles and one-click video generation using Grok Imagine API.

**New in v2.0:**
- 📚 History management with localStorage
- 🔍 Real-time search and filter
- 📄 Export to JSON and Markdown
- 🌐 Full-featured web UI
- 🎬 Direct video generation from web interface

## Overview

A powerful video prompt generator that creates professional prompts for various video styles, with optional direct video generation through xAI's Grok Imagine API.

## Features

### Core Features
- 🎬 **10+ Video Styles** - Landscape, product, tech, emotional, urban, food, sports, ancient Chinese, anime, abstract
- ⚡ **Grok Imagine API** - One-click video generation with XAI
- 🎨 **Prompt Enhancement** - Automatic lighting, camera, mood, and technical details
- 🔄 **Batch Generation** - Generate multiple prompts at once
- 💡 **Interactive & CLI** - User-friendly menu or command-line interface
- 📊 **JSON Export** - Easy integration with other tools

### New Features (v2.0)
- 📚 **History Management** - All prompts saved to localStorage
- 🔍 **Search & Filter** - Real-time search by keywords and categories
- 📄 **Export Options** - JSON and Markdown formats
- 🌐 **Web UI** - Full-featured browser interface
- 🎬 **Video Generation** - Generate videos directly from web UI
- ⚙️ **Video Parameters** - Duration (1-15s), aspect ratio (16:9, 4:3, 1:1, 9:16), resolution (720p, 480p)

## Quick Start

### Installation

1. Install Grok Imagine API dependency:
   ```bash
   cd /root/clawd/skills/grok-imagine
   pip install -r requirements.txt
   ```

2. Set up API key:
   ```bash
   export XAI_API_KEY="your_xai_api_key"
   ```

### Using the Web UI (Recommended)

1. Start the API server:
   ```bash
   node generate.js --server --port 3000
   ```

2. Open the test page in your browser:
   ```
   file:///tmp/hhhh124hhhh.github.io/video-prompt-generator.html
   ```

3. Generate prompts and create videos directly from the interface!

### Interactive CLI Mode

```bash
node generate.js --interactive
```

Follow the prompts:
1. Enter your video topic
2. Select category or all
3. Add enhancements (lighting, camera, mood, technical)
4. Save prompts (optional)
5. Generate video with Grok Imagine (optional)

### Command Line Mode

```bash
# Generate all prompts for a topic
node generate.js --topic "cat playing" --all

# Generate for specific categories
node generate.js --topic "sunset" --categories "landscape,emotional"

# Generate with enhancements
node generate.js --topic "product showcase" \
  --lighting "golden hour" \
  --camera "slow zoom" \
  --mood "cinematic"

# Generate video directly
node generate.js --topic "cat playing" \
  --style "Serene Mountain Sunrise" \
  --generate-video \
  --duration 10 \
  --aspect-ratio 16:9
```

## Web UI Features

### 1. Generate Prompts
- Enter your topic in the input field
- Select one or more categories
- Add optional enhancements
- Click "Generate Prompts" to create prompts

### 2. History Management
- All generated prompts are automatically saved to localStorage
- Click any history item to reload it
- Search through history using the search box
- Filter by category using the filter tabs
- Clear history with the trash button

### 3. Video Generation
- Click "Generate Video" on any prompt card
- Configure video parameters:
  - Duration: 3, 5, 10, or 15 seconds
  - Aspect Ratio: 16:9 (landscape), 4:3 (standard), 1:1 (square), 9:16 (portrait)
  - Resolution: 720p or 480p
- Click "Start Generation" to create the video
- View the video URL when generation completes

### 4. Export Options

#### Export Current Prompts
- **JSON**: Structured data for programmatic use
- **Markdown**: Human-readable format with formatting

#### Export History
- **JSON**: All history records in structured format
- **Markdown**: Complete history with all prompts

### 5. Copy Functions
- Copy individual prompts with the "Copy" button
- Copy all prompts at once with "Copy All"

## Video Categories

### 1. 🌄 Landscape Scenery
Natural and scenic video styles:
- **Serene Mountain Sunrise** - Misty mountains at golden hour
- **Ocean Sunset Drone Shot** - Aerial ocean sunset view
- **Forest Canopy Walkthrough** - First-person forest walk
- **Urban City Timelapse** - Day-to-night city transition
- **Seasonal Cherry Blossom** - Spring flower scene

### 2. 📦 Product Showcase
Professional product video styles:
- **Cinematic Product Reveal** - Slow 360° showcase
- **Lifestyle Product Usage** - Authentic product in action
- **E-commerce Flat Lay** - Clean floating product shot
- **Exploded View Animation** - 3D component assembly
- **Unboxing Experience** - First-person unboxing

### 3. 🤖 Tech Future
Futuristic technology styles:
- **Cyberpunk Neon City** - Neon-lit cyberpunk cityscape
- **AI Digital Interface** - Holographic AI interface
- **Space Station View** - Zero gravity space scene
- **Digital Glitch Art** - Tech-forward glitch effects
- **Futuristic Laboratory** - High-tech research lab

### 4. 💖 Emotional Story
Emotional and narrative styles:
- **Romantic Moonlight Scene** - Intimate romantic moment
- **Nostalgic Vintage Film** - Sepia nostalgic feeling
- **Inspiring Journey** - Motivational growth story
- **Bittersweet Goodbye** - Emotional farewell scene
- **Celebration and Joy** - Pure happiness moment

### 5. 🏙 Urban Life
Urban and city lifestyle styles:
- **Street Cafe Morning** - Bustling cafe scene
- **Modern Office Workspace** - Stylish home office
- **Night City Walking** - Neon-lit urban walk
- **Subway Commute** - Authentic daily commute
- **Rooftop City View** - Aspiring skyline view

### 6. 🍜 Food Cooking
Food and culinary styles:
- **Food Preparation Close-up** - Sharp ingredient prep
- **Cooking Process** - Chef in modern kitchen
- **Plating Presentation** - Elegant fine dining
- **Farm to Table** - Fresh organic journey
- **Food Porn Aesthetic** - Appetizing slow-motion

### 7. 🏃 Sports Fitness
Sports and fitness styles:
- **Dynamic Sports Action** - Fast athletic movement
- **Gym Workout Routine** - Dedicated fitness session
- **Outdoor Adventure** - Nature-based activity
- **Yoga and Meditation** - Calm wellness practice
- **Team Spirit** - Celebratory team moment

### 8. 🏛️ Ancient Chinese
Traditional Chinese styles:
- **Traditional Chinese Garden** - Serene ancient garden
- **Hanfu Costume Showcase** - Elegant traditional dress
- **Ink Wash Painting Style** - Brush stroke aesthetic
- **Ancient Architecture** - Historic cultural buildings
- **Wuxia Martial Arts** - Heroic martial arts scene

### 9. 🎨 Anime Style
Anime and animation styles:
- **Anime Opening Style** - Vibrant action sequences
- **Kawaii Chibi Character** - Cute adorable design
- **Fantasy School Life** - Magical slice of life
- **Mecha Robot Battle** - Epic sci-fi combat
- **Magical Girl Transformation** - Sparkle and magic effects

### 10. 🎭 Abstract Art
Abstract and artistic styles:
- **Liquid Abstract Art** - Morphing organic shapes
- **Geometric Patterns** - Clean mathematical beauty
- **Particle Explosion** - Dynamic burst of energy
- **Ink in Water** - Artistic organic diffusion
- **Fractal Zoom** - Mesmerizing infinite detail

## Prompt Enhancement

Add automatic enhancements to prompts:

### Lighting
- **Golden Hour** - Warm, soft sunlight
- **Soft Lighting** - Gentle diffused light
- **Dramatic Shadows** - High contrast lighting
- **Neon Lights** - Colorful artificial lighting

### Camera Movement
- **Slow Zoom** - Gradual zoom in/out
- **Pan Left/Right** - Horizontal camera movement
- **Drone Shot** - Aerial perspective
- **Tracking Shot** - Following subject movement

### Mood
- **Cinematic** - Movie-quality composition
- **Dreamy** - Ethereal and surreal
- **Energetic** - Dynamic and vibrant
- **Mysterious** - Enigmatic and intriguing

### Technical Specs
- **4K Quality** - Ultra-high definition
- **8K Quality** - Extreme resolution
- **Slow Motion** - Time-stretching effect
- **Hyper-detailed** - Intricate textures

## Grok Imagine API Integration

### Requirements

1. **XAI API Key** - Get from https://x.ai
   ```bash
   export XAI_API_KEY="your_api_key_here"
   ```

2. **Grok Imagine Skill** - Install dependencies:
   ```bash
   cd /root/clawd/skills/grok-imagine
   pip install httpx
   ```

### Video Generation Options

| Option | Default | Description |
|---------|----------|-------------|
| `--duration` | 5 | Video duration in seconds (1-15) |
| `--aspect-ratio` | 16:9 | Aspect ratio (16:9, 4:3, 1:1, 9:16) |
| `--resolution` | 720p | Resolution (720p, 480p) |

### Examples

#### Generate a 10-second 16:9 video
```bash
node generate.js --topic "cat playing in garden" \
  --style "Serene Mountain Sunrise" \
  --generate-video \
  --duration 10 \
  --aspect-ratio 16:9 \
  --resolution 720p
```

#### Generate a square video
```bash
node generate.js --topic "product showcase" \
  --style "Cinematic Product Reveal" \
  --generate-video \
  --duration 5 \
  --aspect-ratio 1:1
```

## API Server

The API server provides endpoints for web UI integration:

### Start Server
```bash
node generate.js --server --port 3000
```

### Endpoints

#### POST /api/generate-video
Generate a video using Grok Imagine API.

**Request:**
```json
{
  "prompt": "Your video prompt",
  "duration": 5,
  "aspectRatio": "16:9",
  "resolution": "720p"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://video-url-here",
  "prompt": "...",
  "duration": 5,
  "aspectRatio": "16:9",
  "resolution": "720p"
}
```

#### GET /api/status
Check service status.

**Response:**
```json
{
  "status": "running",
  "service": "Video Prompt Generator API",
  "version": "2.0.0",
  "features": ["prompt-generation", "video-generation", "history", "search", "export"]
}
```

## Output Formats

### JSON Export
```bash
node generate.js --topic "sunset" --all --output prompts.json
```

Output structure:
```json
{
  "topic": "sunset",
  "categories": ["landscape", "product"],
  "generatedAt": "2026-02-04T00:00:00.000Z",
  "promptCount": 10,
  "prompts": [
    {
      "category": "landscape",
      "style": "Serene Mountain Sunrise",
      "prompt": "Cinematic video of sunset at sunrise over misty mountains..."
    }
  ]
}
```

### Markdown Export
Formatted markdown with:
- Topic and generation info
- Each prompt in code blocks
- Proper heading hierarchy
- Separators between prompts

### Console Output
Color-coded terminal output with:
- Category and style names
- Full generated prompt
- Enhancement details
- Video generation status

## Advanced Usage

### Generate Multiple Variants
```bash
# Generate 3 variations
node generate.js --topic "cat playing" --variants 3
```

### Custom Category Selection
```bash
# Select specific categories
node generate.js --topic "product" --categories "product,urban"
```

### Batch Processing
```bash
# Generate for all topics in a file
for topic in $(cat topics.txt); do
  node generate.js --topic "$topic" --all --output "prompts_$topic.json"
done
```

### History Management (Web UI)
- All prompts automatically saved to browser localStorage
- Search by topic or category
- Filter by category tabs
- Click to reload any history item
- Clear all history with one click

## Examples by Use Case

### Social Media Content
```bash
# Instagram Reel (9:16)
node generate.js --topic "outfit showcase" \
  --style "Lifestyle Product Usage" \
  --lighting "golden hour" \
  --camera "slow zoom" \
  --generate-video \
  --aspect-ratio 9:16 \
  --duration 15
```

### Product Advertisement
```bash
# E-commerce product video
node generate.js --topic "smartphone" \
  --style "Cinematic Product Reveal" \
  --mood "premium" \
  --technical "4K quality" \
  --generate-video \
  --aspect-ratio 16:9 \
  --duration 10
```

### Storytelling Video
```bash
# Emotional narrative
node generate.js --topic "growing up" \
  --style "Inspiring Journey" \
  --lighting "warm soft" \
  --mood "cinematic" \
  --generate-video \
  --duration 15
```

### Artistic Project
```bash
# Abstract art video
node generate.js --topic "liquid art" \
  --style "Liquid Abstract Art" \
  --technical "slow motion" \
  --mood "dreamy" \
  --generate-video
```

## Troubleshooting

### Grok Imagine API Not Working

**Check:**
1. `XAI_API_KEY` is set correctly
2. Grok Imagine dependencies are installed: `pip install httpx`
3. Network connection to x.ai
4. API server is running if using web UI

**Test:**
```bash
# Test Grok Imagine directly
cd /root/clawd/skills/grok-imagine
python3 grok-imagine.py video "test prompt" --duration 5
```

### Prompt Generation Issues

**Common problems:**
- Topic too generic → Be more specific
- Style mismatch → Choose appropriate category
- Enhancement overload → Keep enhancements simple

### Video Generation Fails

**Possible causes:**
1. API rate limits → Wait and retry
2. Invalid prompt → Check prompt format
3. Insufficient credits → Check x.ai account
4. Server not running → Start API server

**Web UI Video Generation:**
- Ensure API server is running: `node generate.js --server`
- Check browser console for errors
- Verify network connectivity to localhost:3000

### History Not Saving

**Web UI:**
- Check browser supports localStorage
- Verify cookies/localStorage not blocked
- Try clearing browser cache

## Best Practices

1. **Be Specific** - Use detailed topics (e.g., "cat playing with red ball" vs "cat")
2. **Match Style to Topic** - Choose appropriate category for your subject
3. **Enhance Sparingly** - Add 2-3 enhancements maximum
4. **Test Variations** - Generate multiple versions and pick best
5. **Review Prompt** - Read generated prompt before generating video
6. **Use History** - Save and reuse successful prompts
7. **Export for Backup** - Export history regularly

## API Costs

Grok Imagine API pricing (as of 2026):
- **Video Generation**: ~$0.04-0.08 per second
- **Resolution**: 720p base, 1080p premium
- **Audio**: Included (synchronized with video)

Check current pricing at: https://x.ai/docs/models

## Integration with Other Skills

This skill integrates with:
- **Grok Imagine** - `/root/clawd/skills/grok-imagine` - Video generation API
- **ad-creative-generator** - `/root/clawd/skills/ad-creative-generator` - Original ad prompts
- **prompt-craft** - `/root/clawd/skills/prompt-craft` - Prompt optimization

## Contributing

Contributions welcome! Feel free to:
- Add new video styles
- Improve prompt templates
- Add enhancement options
- Fix bugs
- Enhance web UI

## License

MIT License

## Version History

### v2.0.0 (2026-02-04)
- ✅ History management with localStorage
- ✅ Real-time search and filter
- ✅ Export to JSON and Markdown
- ✅ Full-featured web UI
- ✅ Direct video generation from web UI
- ✅ API server for backend integration
- ✅ Video parameter configuration
- ✅ Copy individual and all prompts

### v1.0.0 (2026-02-04)
- ✅ Initial release
- ✅ 10 video categories with 5 styles each
- ✅ Grok Imagine API integration
- ✅ Interactive and CLI modes
- ✅ Prompt enhancement system
- ✅ JSON export support
- ✅ Batch generation

## Contact & Support

For issues or questions:
- Check documentation in this SKILL.md
- Test Grok Imagine API separately
- Review generated prompts before video generation
- Check browser console for web UI issues

---

**Made with ❤️ by Momo**
