import streamlit as st
import streamlit.components.v1 as components
import html
import json

def render_dot_avatar(emotion_data: dict, speaking_intensity: float = 0.5, message_length: int = 0):
    """Fixed dot matrix avatar with proper display and smooth animations"""
    
    emotion = emotion_data.get('dominant_emotion', 'neutral').lower()
    confidence = emotion_data.get('confidence', 0.5)
    crisis_level = emotion_data.get('crisis_level', 'low')
    
    # Enhanced emotional patterns
    emotional_patterns = {
        'joy': {
            'eyes': [[4, 4], [11, 4]],
            'mouth': [[6, 10], [7, 10], [8, 10], [9, 10], [7, 11], [8, 11]],
            'extra': [[3, 3], [12, 3], [2, 5], [13, 5]],
            'color': 'rgba(255, 220, 60, 0.95)',
            'mouth_color': 'rgba(255, 100, 80, 0.95)',
            'animation': 'bounce',
            'blink_speed': 120
        },
        'sadness': {
            'eyes': [[4, 4], [11, 4], [4, 5], [11, 5]],
            'mouth': [[7, 12], [8, 12], [9, 12], [6, 11], [10, 11]],
            'extra': [],
            'color': 'rgba(100, 150, 255, 0.85)',
            'mouth_color': 'rgba(80, 120, 220, 0.95)',
            'animation': 'pulse_slow',
            'blink_speed': 150
        },
        'anger': {
            'eyes': [[3, 4], [4, 3], [11, 4], [12, 3]],
            'mouth': [[6, 11], [7, 12], [8, 12], [9, 12], [10, 11]],
            'extra': [[2, 2], [13, 2]],
            'color': 'rgba(255, 80, 60, 0.95)',
            'mouth_color': 'rgba(255, 60, 40, 0.95)',
            'animation': 'flicker',
            'blink_speed': 80
        },
        'fear': {
            'eyes': [[4, 4], [11, 4], [4, 5], [11, 5]],
            'mouth': [[7, 11], [8, 12], [9, 11]],
            'extra': [[3, 2], [12, 2]],
            'color': 'rgba(180, 180, 255, 0.9)',
            'mouth_color': 'rgba(120, 120, 220, 0.9)',
            'animation': 'tremble',
            'blink_speed': 60
        },
        'surprise': {
            'eyes': [[4, 3], [4, 4], [11, 3], [11, 4]],
            'mouth': [[7, 11], [8, 11], [9, 11], [7, 12], [8, 12], [9, 12]],
            'extra': [],
            'color': 'rgba(255, 200, 100, 0.9)',
            'mouth_color': 'rgba(255, 120, 80, 0.9)',
            'animation': 'pulse_fast',
            'blink_speed': 100
        },
        'neutral': {
            'eyes': [[4, 4], [11, 4]],
            'mouth': [[6, 11], [7, 11], [8, 11], [9, 11], [10, 11]],
            'extra': [],
            'color': 'rgba(200, 200, 200, 0.9)',
            'mouth_color': 'rgba(180, 180, 180, 0.9)',
            'animation': 'gentle',
            'blink_speed': 90
        }
    }
    
    pattern = emotional_patterns.get(emotion, emotional_patterns['neutral'])
    
    # Create the HTML and JavaScript for the avatar
    avatar_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .avatar-container {{
                position: relative;
                width: 512px;
                height: 512px;
            }}
            canvas {{
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                background: rgba(255,255,255,0.05);
            }}
        </style>
    </head>
    <body>
        <div class="avatar-container">
            <canvas id="emotionalAvatar" width="512" height="512"></canvas>
        </div>
        
        <script>
            // Emotional Avatar Class
            class EmotionalAvatar {{
                constructor() {{
                    this.canvas = document.getElementById('emotionalAvatar');
                    this.ctx = this.canvas.getContext('2d');
                    this.GRID = 16;
                    this.W = this.canvas.width;
                    this.H = this.canvas.height;
                    this.cw = this.W / this.GRID;
                    this.ch = this.H / this.GRID;
                    
                    // Emotional data
                    this.emotion = "{emotion}";
                    this.confidence = {confidence};
                    this.crisisLevel = "{crisis_level}";
                    this.speakingIntensity = {speaking_intensity};
                    
                    // Pattern data
                    this.pattern = {json.dumps(pattern)};
                    
                    // Animation state
                    this.t = 0;
                    this.particles = [];
                    this.animationId = null;
                    this.isRunning = true;
                    
                    this.startAnimation();
                }}
                
                getCrisisColor() {{
                    switch(this.crisisLevel) {{
                        case 'high': return 'rgba(255, 80, 80, 0.1)';
                        case 'medium': return 'rgba(255, 180, 60, 0.08)';
                        default: return 'rgba(60, 60, 80, 0.05)';
                    }}
                }}
                
                // Animation effects
                bounceEffect(phase) {{
                    return Math.sin(phase) * 0.25 + 0.75;
                }}
                
                pulseSlowEffect(phase) {{
                    return (Math.sin(phase * 0.2) * 0.15) + 0.85;
                }}
                
                flickerEffect(phase) {{
                    return 0.8 + Math.random() * 0.2;
                }}
                
                trembleEffect(phase) {{
                    return 0.85 + Math.sin(phase * 10) * 0.15;
                }}
                
                pulseFastEffect(phase) {{
                    return (Math.sin(phase * 1.5) * 0.2) + 0.8;
                }}
                
                gentleEffect(phase) {{
                    return 0.95 + Math.sin(phase * 0.5) * 0.05;
                }}
                
                getAnimationEffect() {{
                    const effects = {{
                        'bounce': (phase) => this.bounceEffect(phase),
                        'pulse_slow': (phase) => this.pulseSlowEffect(phase),
                        'flicker': (phase) => this.flickerEffect(phase),
                        'tremble': (phase) => this.trembleEffect(phase),
                        'pulse_fast': (phase) => this.pulseFastEffect(phase),
                        'gentle': (phase) => this.gentleEffect(phase)
                    }};
                    return effects[this.pattern.animation] || effects['gentle'];
                }}
                
                createParticle(x, y, color) {{
                    return {{
                        x: x * this.cw + this.cw/2,
                        y: y * this.ch + this.ch/2,
                        vx: (Math.random() - 0.5) * 2.5,
                        vy: (Math.random() - 0.5) * 2 - 0.5,
                        life: 1,
                        maxLife: 1.5,
                        color: color
                    }};
                }}
                
                drawGrid() {{
                    this.ctx.fillStyle = this.getCrisisColor();
                    this.ctx.fillRect(0, 0, this.W, this.H);
                    
                    for(let y = 0; y < this.GRID; y++) {{
                        for(let x = 0; x < this.GRID; x++) {{
                            this.ctx.beginPath();
                            this.ctx.fillStyle = 'rgba(80, 80, 100, 0.1)';
                            this.ctx.arc(x * this.cw + this.cw/2, y * this.ch + this.ch/2, 
                                        Math.min(this.cw, this.ch) * 0.1, 0, Math.PI * 2);
                            this.ctx.fill();
                        }}
                    }}
                }}
                
                drawEyes(animationEffect, intensity) {{
                    this.pattern.eyes.forEach(([x, y]) => {{
                        // Natural blinking
                        const blinkPhase = (this.t % this.pattern.blink_speed) / this.pattern.blink_speed;
                        const blink = blinkPhase > 0.95 ? Math.max(0.1, 1 - (blinkPhase - 0.95) * 20) : 1.0;
                        
                        this.ctx.beginPath();
                        this.ctx.fillStyle = this.pattern.color;
                        this.ctx.arc(
                            x * this.cw + this.cw/2, 
                            y * this.ch + this.ch/2, 
                            Math.min(this.cw, this.ch) * 0.3 * intensity * blink, 
                            0, 
                            Math.PI * 2
                        );
                        this.ctx.fill();
                    }});
                }}
                
                drawMouth(animationEffect, intensity) {{
                    const mouthScale = 0.6 + this.speakingIntensity * (0.6 + 0.3 * Math.sin(this.t/2));
                    this.pattern.mouth.forEach(([x, y]) => {{
                        this.ctx.beginPath();
                        this.ctx.fillStyle = this.pattern.mouth_color;
                        this.ctx.arc(
                            x * this.cw + this.cw/2, 
                            y * this.ch + this.ch/2, 
                            Math.min(this.cw, this.ch) * 0.2 * mouthScale * intensity, 
                            0, 
                            Math.PI * 2
                        );
                        this.ctx.fill();
                    }});
                }}
                
                drawExtraElements(intensity) {{
                    this.pattern.extra.forEach(([x, y]) => {{
                        this.ctx.beginPath();
                        this.ctx.fillStyle = this.pattern.color;
                        this.ctx.arc(
                            x * this.cw + this.cw/2, 
                            y * this.ch + this.ch/2, 
                            Math.min(this.cw, this.ch) * 0.15 * intensity, 
                            0, 
                            Math.PI * 2
                        );
                        this.ctx.fill();
                    }});
                }}
                
                updateParticles() {{
                    this.particles = this.particles.filter(p => {{
                        p.x += p.vx;
                        p.y += p.vy;
                        p.life -= 0.015;
                        p.vy += 0.05; // gentle gravity
                        
                        if(p.life > 0) {{
                            const alpha = p.life / p.maxLife;
                            this.ctx.beginPath();
                            const colored = p.color.replace('0.95', alpha.toFixed(2));
                            this.ctx.fillStyle = colored;
                            this.ctx.arc(p.x, p.y, Math.min(this.cw, this.ch) * 0.06 * p.life, 0, Math.PI * 2);
                            this.ctx.fill();
                            return true;
                        }}
                        return false;
                    }});
                    
                    // Add new particles for high emotion intensity
                    if(this.confidence > 0.6 && this.t % 20 === 0 && this.particles.length < 6) {{
                        const sourceX = this.pattern.eyes[0] ? this.pattern.eyes[0][0] : 8;
                        const sourceY = this.pattern.eyes[0] ? this.pattern.eyes[0][1] : 4;
                        this.particles.push(this.createParticle(sourceX, sourceY, this.pattern.color));
                    }}
                }}
                
                draw() {{
                    if (!this.isRunning) return;
                    
                    this.drawGrid();
                    
                    const animationEffect = this.getAnimationEffect();
                    const intensity = animationEffect(this.t / 8);
                    
                    this.drawEyes(animationEffect, intensity);
                    this.drawMouth(animationEffect, intensity);
                    this.drawExtraElements(intensity);
                    this.updateParticles();
                    
                    this.t += 1;
                    this.animationId = requestAnimationFrame(() => this.draw());
                }}
                
                startAnimation() {{
                    this.isRunning = true;
                    this.draw();
                }}
                
                stopAnimation() {{
                    this.isRunning = false;
                    if (this.animationId) {{
                        cancelAnimationFrame(this.animationId);
                    }}
                }}
            }}
            
            // Initialize avatar when page loads
            document.addEventListener('DOMContentLoaded', function() {{
                window.emotionalAvatar = new EmotionalAvatar();
            }});
            
            // Cleanup
            window.addEventListener('beforeunload', function() {{
                if (window.emotionalAvatar) {{
                    window.emotionalAvatar.stopAnimation();
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(avatar_html, height=550, scrolling=False)

def render_emotional_indicator(emotion_data: dict):
    """Enhanced emotional state indicator"""
    emotion = emotion_data.get('dominant_emotion', 'neutral')
    confidence = emotion_data.get('confidence', 0)
    crisis_level = emotion_data.get('crisis_level', 'low')
    
    emotion_emojis = {
        'joy': '😊',
        'sadness': '😢', 
        'anger': '😠',
        'fear': '😨',
        'surprise': '😲',
        'disgust': '😖',
        'neutral': '😐'
    }
    
    emoji = emotion_emojis.get(emotion.lower(), '😐')
    crisis_color = {'high': '#ff4444', 'medium': '#ffaa00', 'low': '#44aa44'}[crisis_level]
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <h4 style="margin: 0 0 8px 0; color: white;">Current Emotional State</h4>
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 2em;">{emoji}</span>
            <div>
                <div style="font-weight: bold; font-size: 1.1em;">{emotion.title()}</div>
                <div style="font-size: 0.9em; opacity: 0.9;">
                    Confidence: {confidence:.0%} • 
                    <span style="color: {crisis_color}; font-weight: bold;">{crisis_level.upper()}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)