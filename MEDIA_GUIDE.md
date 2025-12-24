# Media Integration Guide - Adding Audio & Video to Survey

## Overview

The scenario page now supports immersive multimedia elements including ambient sounds, phone ringing effects, and background videos to enhance participant engagement.

## What's Been Added

### 1. Audio Elements
- **Ambient Fire Sound**: Looping background audio of fire/emergency
- **Phone Ringing**: Realistic phone ring that plays repeatedly
- **Emergency Alert**: Optional siren/alert sound

### 2. Video Elements
- **Background Video**: Optional fire/smoke footage playing behind the scenario

### 3. Controls
- **Sound Toggle**: Turn audio on/off
- **Video Toggle**: Turn video on/off (shows only if video is available)
- **Visual Feedback**: Buttons change appearance when active

## How to Add Media Files

### Step 1: Create Media Directory

```bash
cd /Users/tzhang/projects/a2i2_survey/a2i2_chatbot/frontend
mkdir media
```

### Step 2: Add Your Media Files

Place your audio/video files in the `media/` directory:

```
frontend/
└── media/
    ├── fire-ambient.mp3      # Background fire sound
    ├── phone-ring.mp3        # Phone ringing sound
    ├── emergency-alert.mp3   # Optional alert sound
    └── fire-smoke.mp4        # Optional background video
```

### Step 3: Update HTML

Uncomment and update the source paths in `scenario.html`:

```html
<!-- Ambient fire sound -->
<audio id="ambientSound" loop>
  <source src="media/fire-ambient.mp3" type="audio/mpeg">
</audio>

<!-- Phone ringing -->
<audio id="phoneRinging">
  <source src="media/phone-ring.mp3" type="audio/mpeg">
</audio>

<!-- Background video (optional) -->
<video id="backgroundVideo" class="background-video" loop muted playsinline>
  <source src="media/fire-smoke.mp4" type="video/mp4">
</video>
```

## Where to Find Free Media

### Free Sound Effects

1. **Freesound.org** (https://freesound.org/)
   - Search: "fire crackling", "phone ringing", "emergency siren"
   - License: Creative Commons (check attribution requirements)

2. **Zapsplat** (https://www.zapsplat.com/)
   - Free sound effects library
   - Requires free account

3. **BBC Sound Effects** (https://sound-effects.bbcrewind.co.uk/)
   - Free for research and education
   - High quality recordings

### Free Video Footage

1. **Pexels Videos** (https://www.pexels.com/videos/)
   - Search: "fire", "smoke", "wildfire"
   - License: Free to use

2. **Pixabay Videos** (https://pixabay.com/videos/)
   - Free stock footage
   - No attribution required

3. **Videvo** (https://www.videvo.net/)
   - Free stock video
   - Some require attribution

## Recommended Media Specifications

### Audio Files

**Ambient Fire Sound:**
- Format: MP3 or OGG
- Duration: 30-60 seconds (will loop)
- Volume: Low intensity (forest fire ambiance)
- File size: < 2MB

**Phone Ringing:**
- Format: MP3 or OGG
- Duration: 2-4 seconds per ring
- Volume: Clear and distinct
- File size: < 500KB

### Video Files

**Background Fire/Smoke:**
- Format: MP4 (H.264 codec)
- Resolution: 1920x1080 or 1280x720
- Duration: 30-60 seconds (will loop)
- Frame rate: 30fps
- File size: < 10MB (compress for web)
- Style: Subtle, not too intense (backdrop only)

## User Experience Flow

### Default State (No Media)
1. Participant arrives at scenario page
2. Sees animated phone icon (CSS animation only)
3. Reads scenario text
4. Selects character
5. Proceeds to chat

### With Media Enabled
1. Participant arrives at scenario page
2. Sees media control buttons (bottom right)
3. Can click "🔊 Sound On" to enable audio
4. Ambient fire sound plays (low volume)
5. Phone ringing starts after 2 seconds
6. Phone icon animates more intensely when ringing
7. Optional: Click "🎥 Video On" for background video
8. Immersive experience enhances engagement

## Features

### Sound System
✅ **Ambient Fire Loop**: Continuous low-volume background
✅ **Phone Ringing**: Repeats every 3 seconds while enabled
✅ **Volume Control**: Pre-set to appropriate levels
✅ **Visual Sync**: Phone icon animates with ring sound
✅ **Browser Compatible**: Falls back gracefully if autoplay blocked

### Video System
✅ **Background Video**: Subtle fire/smoke footage
✅ **Blur Effect**: 2px blur for backdrop effect
✅ **Low Opacity**: 40% opacity to not overwhelm text
✅ **Muted**: No competing audio
✅ **Smooth Loop**: Seamless repeat

### Controls
✅ **Toggle Buttons**: Easy on/off for sound and video
✅ **Persistent State**: Stays on/off until user changes
✅ **Visual Feedback**: Icons change when active
✅ **Responsive**: Works on mobile and desktop
✅ **Accessible**: Clear labels and controls

## Technical Details

### Audio Implementation

```javascript
// Ambient sound
ambientSound.volume = 0.3;  // 30% volume
ambientSound.loop = true;   // Continuous
ambientSound.play();

// Phone ringing (repeating)
function playPhoneRinging() {
  phoneRinging.volume = 0.5;  // 50% volume
  phoneRinging.play();
  
  // Play again after sound ends + 3 second pause
  phoneRinging.onended = () => {
    setTimeout(playPhoneRinging, 3000);
  };
}
```

### Video Implementation

```javascript
// Background video
backgroundVideo.muted = true;     // No audio
backgroundVideo.loop = true;       // Continuous
backgroundVideo.style.opacity = 0.4;  // 40% visible
backgroundVideo.style.filter = 'blur(2px)';  // Slight blur
```

### Browser Autoplay Policies

Modern browsers block autoplay with sound. The system handles this by:
1. Media starts muted/paused by default
2. User must click toggle button to enable
3. This counts as user interaction → allows playback
4. Graceful fallback if still blocked

## Styling

### Media Controls Button
```css
.media-btn {
  background: rgba(44, 62, 80, 0.9);  /* Semi-transparent */
  backdrop-filter: blur(10px);         /* Frosted glass effect */
  position: fixed;
  bottom: 2rem;
  right: 2rem;
}
```

### Phone Icon Ringing Animation
```css
@keyframes phoneRingIntense {
  0%, 100% { transform: rotate(-15deg) scale(1); }
  25% { transform: rotate(15deg) scale(1.05); }
  50% { transform: rotate(-15deg) scale(1); }
  75% { transform: rotate(15deg) scale(1.05); }
}
```

## Performance Considerations

### File Sizes
- Total media < 15MB recommended
- Compress audio to 128kbps MP3
- Compress video using H.264 with medium quality
- Consider lazy loading for large files

### Loading Strategy
```javascript
// Preload media after page load
window.addEventListener('load', () => {
  ambientSound.load();
  phoneRinging.load();
  backgroundVideo.load();
});
```

### Mobile Optimization
- Smaller file sizes for mobile
- Option to disable video on small screens
- Touch-friendly controls
- Responsive button placement

## Testing Checklist

### Desktop
- [ ] Ambient sound plays when enabled
- [ ] Phone ringing works and repeats
- [ ] Video plays in background (if enabled)
- [ ] Toggle buttons work
- [ ] Visual animations sync with audio
- [ ] Volume levels appropriate
- [ ] Works in Chrome, Firefox, Safari

### Mobile
- [ ] Controls visible and accessible
- [ ] Touch targets large enough
- [ ] Sound plays on iOS/Android
- [ ] Video doesn't overwhelm small screen
- [ ] Performance is smooth
- [ ] Battery drain acceptable

### Accessibility
- [ ] Controls have clear labels
- [ ] Can be used with keyboard
- [ ] Screen readers announce buttons
- [ ] Visual alternatives to audio cues
- [ ] Option to disable all media

## Example Media Setup

### Quick Test (Using Public URLs)

For quick testing without downloading files:

```html
<!-- Use royalty-free sample files -->
<audio id="ambientSound" loop>
  <source src="https://www.example.com/fire-ambient.mp3" type="audio/mpeg">
</audio>

<audio id="phoneRinging">
  <source src="https://www.example.com/phone-ring.mp3" type="audio/mpeg">
</audio>
```

### Production Setup

```bash
# 1. Create directory
mkdir frontend/media

# 2. Add your files
cp ~/Downloads/fire-ambient.mp3 frontend/media/
cp ~/Downloads/phone-ring.mp3 frontend/media/
cp ~/Downloads/fire-video.mp4 frontend/media/

# 3. Optimize files
# Use ffmpeg to compress:
ffmpeg -i fire-video.mp4 -vcodec h264 -acodec none fire-video-optimized.mp4
```

## Troubleshooting

### Sound Not Playing
1. Check browser console for errors
2. Verify file paths are correct
3. Ensure files are in supported format (MP3/OGG)
4. Check browser autoplay policy
5. Try clicking sound button again

### Video Not Showing
1. Verify video file exists
2. Check file format (MP4 with H.264)
3. Ensure video toggle button is visible
4. Check browser console for errors
5. Try different browser

### Performance Issues
1. Reduce video file size
2. Lower video resolution
3. Compress audio files
4. Disable video on mobile
5. Use lazy loading

## Future Enhancements

Possible additions:
- [ ] Volume sliders for fine control
- [ ] Different ambient sounds per character
- [ ] Emergency radio chatter
- [ ] Helicopter sounds
- [ ] Fire truck sirens (distant)
- [ ] Wind/weather effects

## Summary

The multimedia system is **ready to use** once you add media files. The infrastructure is in place—just drop in your audio/video files and update the source paths!

**Key Benefits:**
- ✅ Increases immersion
- ✅ Enhances realism
- ✅ Improves engagement
- ✅ Optional (doesn't interfere if not used)
- ✅ User-controlled
- ✅ Mobile-friendly

---

**Status**: 🎬 Ready for media files  
**Required**: Audio/video files (see recommendations above)  
**Optional**: All media features work without files (graceful degradation)

