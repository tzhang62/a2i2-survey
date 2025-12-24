# How to Add Audio/Video to the Scenario Page

## Current Status

✅ **System is ready** - Infrastructure is in place  
⚠️ **No media files yet** - Controls are hidden until you add files  
🎯 **Easy to enable** - Just 3 steps below

## Quick Setup (3 Steps)

### Step 1: Create Media Folder

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend
mkdir media
```

### Step 2: Add Your Media Files

Download free media and place in `media/` folder:

```
frontend/media/
├── fire-ambient.mp3    (optional - background fire sound)
├── phone-ring.mp3      (optional - phone ringing)
└── fire-smoke.mp4      (optional - background video)
```

### Step 3: Update scenario.html

Open `frontend/scenario.html` and **uncomment** the lines you want to use:

**For ambient fire sound:**
```html
<audio id="ambientSound" loop style="display: none;">
  <source src="media/fire-ambient.mp3" type="audio/mpeg">  <!-- Remove the comment tags -->
</audio>
```

**For phone ringing:**
```html
<audio id="phoneRinging" style="display: none;">
  <source src="media/phone-ring.mp3" type="audio/mpeg">  <!-- Remove the comment tags -->
</audio>
```

**For background video:**
```html
<video id="backgroundVideo" class="background-video" loop muted playsinline style="display: none;">
  <source src="media/fire-smoke.mp4" type="video/mp4">  <!-- Remove the comment tags -->
</video>
```

## Where to Get Free Media

### 🎵 Free Sound Effects

**Freesound.org** (Recommended)
1. Go to https://freesound.org/
2. Search "fire crackling ambient" for background sound
3. Search "phone ringing" for phone sound
4. Download MP3 format
5. Rename to `fire-ambient.mp3` and `phone-ring.mp3`

**Other sources:**
- Zapsplat.com (free account required)
- BBC Sound Effects (free for research)
- YouTube Audio Library

### 🎥 Free Video Footage

**Pexels.com** (Recommended)
1. Go to https://www.pexels.com/videos/
2. Search "wildfire smoke"
3. Download 1920x1080 MP4
4. Rename to `fire-smoke.mp4`

**Other sources:**
- Pixabay.com/videos
- Videvo.net

## Recommended Specifications

### Audio
- **Format**: MP3 or OGG
- **Fire ambient**: 30-60 seconds (loops automatically)
- **Phone ring**: 2-4 seconds per ring
- **File size**: < 2MB each

### Video
- **Format**: MP4 (H.264 codec)
- **Resolution**: 1920x1080 or 1280x720
- **Duration**: 30-60 seconds (loops automatically)
- **File size**: < 10MB (compress if needed)

## What Happens When You Add Media

### Before (No Media Files)
- Scenario page works normally
- Only CSS animations (phone shaking)
- No control buttons visible
- Clean, simple experience

### After (With Media Files)
- Control buttons appear (bottom-right corner)
- Participants can click "🔊 Sound On"
- Ambient fire plays in background (low volume)
- Phone rings repeatedly (more immersive)
- Optional video background
- Highly engaging experience

## Testing

1. Add at least one media file
2. Uncomment the corresponding `<source>` line
3. Refresh the scenario page
4. You should see control button(s) appear
5. Click to enable sound/video
6. Verify playback works

## File Structure

```
a2i2_chatbot/
└── frontend/
    ├── scenario.html
    ├── js/
    │   └── scenario.js
    ├── styles/
    │   └── scenario.css
    └── media/              ← Create this folder
        ├── fire-ambient.mp3
        ├── phone-ring.mp3
        └── fire-smoke.mp4
```

## Example: Adding Phone Ring Only

1. **Get audio file:**
   - Download phone ring from Freesound.org
   - Save as `phone-ring.mp3`

2. **Place in folder:**
   ```bash
   mv ~/Downloads/phone-ring.mp3 frontend/media/
   ```

3. **Edit scenario.html:**
   Find this section:
   ```html
   <audio id="phoneRinging" style="display: none;">
     <!-- To enable: Add your audio file and uncomment the line below -->
     <!-- <source src="media/phone-ring.mp3" type="audio/mpeg"> -->
   </audio>
   ```
   
   Change to:
   ```html
   <audio id="phoneRinging" style="display: none;">
     <source src="media/phone-ring.mp3" type="audio/mpeg">
   </audio>
   ```

4. **Test:**
   - Refresh scenario page
   - Sound button appears
   - Click "🔊 Sound On"
   - Phone rings!

## Troubleshooting

**Controls don't appear:**
- Check file paths are correct
- Verify files are in `frontend/media/` folder
- Make sure you uncommented the `<source>` line
- Refresh browser (hard refresh: Cmd+Shift+R / Ctrl+Shift+F5)

**Sound doesn't play:**
- Check browser console for errors
- Try clicking the sound button again
- Some browsers block autoplay - button click enables it
- Verify file format is MP3 or OGG

**Video doesn't show:**
- Verify MP4 format with H.264 codec
- Check file isn't too large (>10MB)
- Try a different browser
- Check browser console for errors

## Tips

✅ **Start simple**: Add just phone-ring.mp3 first  
✅ **Test incrementally**: Add one file at a time  
✅ **Keep files small**: Compress for faster loading  
✅ **Mobile friendly**: Works on phones/tablets  
✅ **Optional**: Participants can still complete survey without media

## Current Behavior

**Right now (no media files):**
- ✅ Scenario page works perfectly
- ✅ Personalized scenario text appears
- ✅ Character selection works
- ✅ No errors
- ⚪ No media controls visible (by design)

**After adding media:**
- ✅ Everything above still works
- ✅ Media controls appear
- ✅ Participants can enable/disable
- ✅ More immersive experience

---

**Status**: 🎬 Ready for your media files  
**Required**: None (optional feature)  
**Time to setup**: 5-10 minutes

