// AI Twin 2.0 - Interactive JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize smooth scrolling
    initSmoothScrolling();
    
    // Initialize navigation
    initNavigation();
    
    // Initialize chat functionality
    initChat();
    
    // Initialize animations
    initAnimations();
    
    // Add typing effect to hero title
    initTypingEffect();
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Navigation functionality
function initNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Mobile menu toggle
    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Active link highlighting on scroll
    window.addEventListener('scroll', () => {
        let current = '';
        const sections = document.querySelectorAll('section[id]');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// Chat functionality
function initChat() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const chatMessages = document.getElementById('chatMessages');
    
    // Send message on Enter key
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Send button click
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
}

// Send message function
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.getElementById('sendButton');
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show loading state
    sendButton.innerHTML = '<div class="loading"></div>';
    sendButton.disabled = true;
    
    try {
        // Send message to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.error) {
            addMessage(`Error: ${data.error}`, 'ai', true);
        } else {
            // Add AI response with typing effect
            addMessage(data.response, 'ai');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessage('Sorry, I encountered an error. Please try again.', 'ai', true);
    } finally {
        // Reset send button
        sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        sendButton.disabled = false;
    }
}

// Add message to chat
function addMessage(content, sender, isError = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarIcon = sender === 'ai' ? 'fas fa-robot' : 'fas fa-user';
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${avatarIcon}"></i>
        </div>
        <div class="message-content ${isError ? 'error' : ''}">
            <p>${content}</p>
            <span class="message-time">${currentTime}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom with smooth animation
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
    
    // Add entrance animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    
    requestAnimationFrame(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    });
}

// Send suggestion message
function sendSuggestion(suggestion) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = suggestion;
    sendMessage();
}

// Clear chat
function clearChat() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="message ai-message">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Chat cleared! I'm ready for a fresh conversation. What would you like to talk about?</p>
                <span class="message-time">Just now</span>
            </div>
        </div>
    `;
}

// Toggle settings (placeholder)
function toggleSettings() {
    alert('Settings panel coming soon! 🚀');
}

// Scroll to demo section
function scrollToDemo() {
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth' });
        
        // Focus on input after scrolling
        setTimeout(() => {
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.focus();
            }
        }, 1000);
    }
}

// Show features section
function showFeatures() {
    const featuresSection = document.getElementById('features');
    if (featuresSection) {
        featuresSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize animations
function initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

// Typing effect for hero title
function initTypingEffect() {
    const titleElement = document.querySelector('.hero-title');
    if (!titleElement) return;
    
    const originalText = titleElement.innerHTML;
    const textParts = originalText.split('<span class="gradient-text">');
    const beforeSpan = textParts[0];
    const spanContent = textParts[1].split('</span>')[0];
    const afterSpan = textParts[1].split('</span>')[1] || '';
    
    titleElement.innerHTML = '';
    
    let i = 0;
    const fullText = beforeSpan + spanContent + afterSpan;
    
    function typeWriter() {
        if (i < beforeSpan.length) {
            titleElement.innerHTML += beforeSpan.charAt(i);
        } else if (i < beforeSpan.length + spanContent.length) {
            if (i === beforeSpan.length) {
                titleElement.innerHTML += '<span class="gradient-text">';
            }
            titleElement.innerHTML = titleElement.innerHTML.slice(0, -1) + spanContent.charAt(i - beforeSpan.length) + '</span>';
        } else if (i < fullText.length) {
            if (i === beforeSpan.length + spanContent.length) {
                titleElement.innerHTML = titleElement.innerHTML.slice(0, -7) + '</span>' + afterSpan.charAt(i - beforeSpan.length - spanContent.length);
            } else {
                titleElement.innerHTML += afterSpan.charAt(i - beforeSpan.length - spanContent.length);
            }
        }
        
        i++;
        if (i <= fullText.length) {
            setTimeout(typeWriter, 100);
        }
    }
    
    // Start typing effect after a delay
    setTimeout(typeWriter, 1000);
}

// Particle system for background (optional enhancement)
function createParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particles';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;
    
    document.body.appendChild(particleContainer);
    
    for (let i = 0; i < 50; i++) {
        createParticle(particleContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(99, 102, 241, 0.3);
        border-radius: 50%;
        animation: float ${Math.random() * 20 + 10}s infinite linear;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
    `;
    
    container.appendChild(particle);
}

// Language detection and response formatting
function formatMultilingualText(text) {
    // Simple detection for Telugu script
    const teluguPattern = /[\u0C00-\u0C7F]/;
    const hasTeluguScript = teluguPattern.test(text);
    
    if (hasTeluguScript) {
        return `<span class="multilingual-text telugu">${text}</span>`;
    }
    
    return text;
}

// Performance monitoring
function logPerformance() {
    if (performance.mark) {
        performance.mark('ai-twin-loaded');
        console.log('🚀 AI Twin 2.0 loaded successfully!');
        console.log('⚡ Performance metrics available in DevTools');
    }
}

// Initialize performance logging
setTimeout(logPerformance, 1000);

// Easter egg - Konami code
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65];

document.addEventListener('keydown', function(e) {
    konamiCode.push(e.keyCode);
    konamiCode = konamiCode.slice(-10);
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        triggerEasterEgg();
    }
});

function triggerEasterEgg() {
    const message = "🎉 You found the secret! AI Twin 2.0 is powered by advanced multilingual AI technology!";
    addMessage(message, 'ai');
    
    // Add some visual flair
    document.body.style.animation = 'rainbow 2s ease-in-out';
    setTimeout(() => {
        document.body.style.animation = '';
    }, 2000);
}

// Add rainbow animation for easter egg
const style = document.createElement('style');
style.textContent = `
    @keyframes rainbow {
        0%, 100% { filter: hue-rotate(0deg); }
        25% { filter: hue-rotate(90deg); }
        50% { filter: hue-rotate(180deg); }
        75% { filter: hue-rotate(270deg); }
    }
    
    .error {
        color: #ef4444 !important;
        border-left: 3px solid #ef4444;
        padding-left: 1rem;
    }
    
    .multilingual-text.telugu {
        font-family: 'Noto Sans Telugu', sans-serif;
        font-weight: 500;
    }
`;
document.head.appendChild(style);
