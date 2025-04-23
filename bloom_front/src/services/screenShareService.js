import { groqService } from './groqService';

export class ScreenShareService {
    constructor() {
        this.stream = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.isRecording = false;
        this.analysisInterval = null;
    }

    async startSharing() {
        try {
            this.stream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    cursor: "always",
                    frameRate: { ideal: 30 }
                },
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });

            this.setupRecording();
            this.startScreenAnalysis();
            return this.stream;
        } catch (error) {
            console.error('Error starting screen share:', error);
            throw error;
        }
    }

    setupRecording() {
        this.mediaRecorder = new MediaRecorder(this.stream, {
            mimeType: 'video/webm;codecs=vp9'
        });

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.recordedChunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = () => {
            const blob = new Blob(this.recordedChunks, {
                type: 'video/webm'
            });
            this.saveRecording(blob);
            this.recordedChunks = [];
        };
    }

    startRecording() {
        if (this.mediaRecorder && !this.isRecording) {
            this.mediaRecorder.start();
            this.isRecording = true;
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
        }
    }

    async startScreenAnalysis() {
        this.analysisInterval = setInterval(async () => {
            const canvas = document.createElement('canvas');
            const video = document.createElement('video');
            video.srcObject = this.stream;

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            const imageData = canvas.toDataURL('image/jpeg', 0.8);

            try {
                const analysis = await groqService.generateResponse(
                    `Analyze this screen content and provide suggestions: ${imageData}`
                );
                this.onAnalysis(analysis);
            } catch (error) {
                console.error('Screen analysis error:', error);
            }
        }, 5000); // Analyze every 5 seconds
    }

    stopSharing() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.analysisInterval) {
            clearInterval(this.analysisInterval);
            this.analysisInterval = null;
        }
        if (this.isRecording) {
            this.stopRecording();
        }
    }

    saveRecording(blob) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        document.body.appendChild(a);
        a.style = 'display: none';
        a.href = url;
        a.download = `screen-recording-${new Date().toISOString()}.webm`;
        a.click();
        URL.revokeObjectURL(url);
    }

    getStream() {
        return this.stream;
    }

    onAnalysis(analysis) {
        // Dispatch custom event with analysis results
        const event = new CustomEvent('screenAnalysis', {
            detail: { analysis }
        });
        window.dispatchEvent(event);
    }
}

export const screenShareService = new ScreenShareService();