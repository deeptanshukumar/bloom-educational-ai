import axios from 'axios';

class GroqService {
    constructor() {
        this.client = axios.create({
            baseURL: 'http://localhost:5000/api',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add request interceptor to include auth token
        this.client.interceptors.request.use((config) => {
            const token = localStorage.getItem('bloom_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('AI Service Error:', error.response?.data || error.message);
                if (error.response?.status === 401) {
                    localStorage.removeItem('bloom_token');
                    window.location.href = '/login';
                }
                throw error;
            }
        );

        this.currentSessionId = null;
    }

    async generateResponse(prompt, options = {}) {
        try {
            const response = await this.client.post('/ai/analyze', {
                prompt,
                language: options.language || 'English'
            });

            if (!response.data || !response.data.response) {
                throw new Error('Invalid response from AI service');
            }

            return response.data.response;
        } catch (error) {
            console.error('AI Service Error:', error);
            if (!navigator.onLine) {
                throw new Error('No internet connection. Please check your network and try again.');
            }
            throw error;
        }
    }

    async analyzeWithContext(fileContent, fileType, options = {}) {
        try {
            const response = await this.client.post('/ai/analyze-with-context', {
                content: fileContent,
                fileType,
                language: options.language || 'English'
            });

            if (!response.data || !response.data.response) {
                throw new Error('Invalid response from AI service');
            }

            return response.data.response;
        } catch (error) {
            console.error('AI Service Error:', error);
            throw error;
        }
    }

    async processAudio(formData) {
        try {
            const response = await this.client.post('/ai/process-audio', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (!response.data || !response.data.transcription) {
                throw new Error('Invalid response from speech service');
            }

            return response.data;
        } catch (error) {
            console.error('Speech Processing Error:', error);
            throw error;
        }
    }

    async processLanguage(text, targetLanguage) {
        return this.generateResponse(text, { language: targetLanguage });
    }

    async analyzeMathProblem(problem) {
        const prompt = `
            Analyze and solve this math problem step by step:
            ${problem}
            
            Please provide:
            1. Step-by-step solution
            2. Key concepts involved
            3. Similar practice problems
        `;
        return this.generateResponse(prompt);
    }

    async initFileSession() {
        try {
            const response = await this.client.post('/api/file/session/create');
            this.currentSessionId = response.data.session_id;
            return this.currentSessionId;
        } catch (error) {
            console.error('Error creating file session:', error);
            throw error;
        }
    }

    async uploadFiles(files, additionalContext = '') {
        try {
            if (!this.currentSessionId) {
                await this.initFileSession();
            }

            const uploadPromises = files.map(async (file) => {
                // Validate file size
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    throw new Error(`File ${file.name} exceeds maximum size of 16MB`);
                }

                // Validate file type
                const allowedTypes = [
                    'text/plain',
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'image/jpeg',
                    'image/png',
                    'image/gif',
                    'audio/mpeg',
                    'audio/wav'
                ];
                if (!allowedTypes.includes(file.type)) {
                    throw new Error(`File type ${file.type} not supported for ${file.name}`);
                }

                const formData = new FormData();
                formData.append('file', file);

                if (additionalContext.trim()) {
                    formData.append('context', additionalContext.trim());
                }

                try {
                    const response = await this.client.post(
                        `/file/upload/${this.currentSessionId}`,
                        formData,
                        {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            }
                        }
                    );

                    if (response.data.error) {
                        throw new Error(response.data.error);
                    }

                    return {
                        ...response.data,
                        context: additionalContext.trim() || null
                    };
                } catch (error) {
                    return {
                        error: `Failed to upload ${file.name}: ${error.response?.data?.error || error.message}`,
                        file: file.name
                    };
                }
            });

            const results = await Promise.all(uploadPromises);

            // Group successful uploads and errors
            const errors = results.filter(result => result.error);
            const successful = results.filter(result => !result.error);

            if (errors.length > 0) {
                const errorMessages = errors.map(e => e.error).join('\n');
                throw new Error(`Failed to upload some files:\n${errorMessages}`);
            }

            return successful;
        } catch (error) {
            console.error('Error uploading files:', error);
            throw new Error(error.response?.data?.error || error.message || 'Error uploading files');
        }
    }

    async processAudioTranscription(audioBlob) {
        try {
            // Use WebSpeech API for transcription
            const recognition = new window.webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;

            return new Promise((resolve, reject) => {
                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    resolve(transcript);
                };

                recognition.onerror = (error) => {
                    reject(error);
                };

                recognition.start();
            });
        } catch (error) {
            console.error('Error transcribing audio:', error);
            throw error;
        }
    }

    async endFileSession() {
        if (this.currentSessionId) {
            try {
                await this.client.delete(`/api/file/session/${this.currentSessionId}`);
                this.currentSessionId = null;
            } catch (error) {
                console.error('Error ending file session:', error);
                throw error;
            }
        }
    }
}

export const groqService = new GroqService();