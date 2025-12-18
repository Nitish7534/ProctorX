// script.js
// Common utility functions

// Toggle Password Visibility
function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Form Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

// Show/Hide Loading
function showLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    button.disabled = true;
    return originalText;
}

function hideLoading(button, originalText) {
    button.innerHTML = originalText;
    button.disabled = false;
}

// API Calls
const API_BASE_URL = 'http://localhost:5000';

async function makeRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        const result = await response.json();

        // 🔴 THIS WAS MISSING
        if (!response.ok) {
            console.error('Backend error:', result);
            return {
                success: false,
                message: result.message || 'Server error'
            };
        }

        return result;

    } catch (error) {
        console.error('API Error:', error);
        return {
            success: false,
            message: 'Network error. Please try again.'
        };
    }
}


// Webcam Functions
let webcamStream = null;

async function startWebcam(videoElementId) {
    try {
        const video = document.getElementById(videoElementId);
        webcamStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 },
            audio: false
        });
        video.srcObject = webcamStream;
        return true;
    } catch (error) {
        console.error('Webcam error:', error);
        alert('Cannot access webcam. Please check permissions.');
        return false;
    }
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
}

function capturePhoto(videoElementId, canvasElementId) {
    const video = document.getElementById(videoElementId);
    const canvas = document.getElementById(canvasElementId);
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    return canvas.toDataURL('image/jpeg');
}

// Exam Timer
class ExamTimer {
    constructor(durationInMinutes, displayElementId) {
        this.duration = durationInMinutes * 60; // Convert to seconds
        this.displayElement = document.getElementById(displayElementId);
        this.timeLeft = this.duration;
        this.interval = null;
    }
    
    start() {
        this.updateDisplay();
        this.interval = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                this.stop();
                alert('Time is up!');
                // Auto-submit exam
                if (typeof submitExam === 'function') {
                    submitExam();
                }
            }
        }, 1000);
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.displayElement.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add current year to footer
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});