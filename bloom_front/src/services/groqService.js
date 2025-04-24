import axios from 'axios';

class GroqService {
    constructor() {
        this.client = axios.create({
            baseURL: 'http://localhost:5000/api',  // Restore original URL
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 120000, // Increase timeout to 120 seconds for large files
            // Enhanced retry logic
            retry: 3,
            retryDelay: (retryCount) => {
                return Math.min(1000 * Math.pow(2, retryCount), 10000); // Exponential backoff with max 10s
            }
        });

        // Add request interceptor for auth
        this.client.interceptors.request.use((config) => {
            const token = localStorage.getItem('bloom_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });

        // Enhanced response interceptor
        this.client.interceptors.response.use(
            response => response,
            async error => {
                const { config, response } = error;

                // Don't retry on specific error codes
                const skipRetry = response?.status === 401 ||
                    response?.status === 403 ||
                    response?.status === 422;

                // If network error or 5xx and retries left, retry the request
                if (!skipRetry && (!response || response.status >= 500) && config.retry > 0) {
                    config.retry -= 1;
                    const retryCount = 3 - config.retry;
                    const delayMs = config.retryDelay(retryCount);
                    await new Promise(resolve => setTimeout(resolve, delayMs));
                    return this.client(config);
                }

                if (response?.status === 401) {
                    localStorage.removeItem('bloom_token');
                    window.location.href = '/login';
                    throw new Error('Session expired. Please log in again.');
                }

                // Extract the most meaningful error message
                let errorMessage;
                if (!navigator.onLine) {
                    errorMessage = 'No internet connection. Please check your network and try again.';
                } else if (error.code === 'ECONNABORTED') {
                    errorMessage = 'Request timed out. Please try again.';
                } else if (!response) {
                    errorMessage = 'Network error. Please check your connection and try again.';
                } else {
                    errorMessage = response.data?.error ||
                        response.data?.message ||
                        error.message ||
                        'An unexpected error occurred';
                }

                throw new Error(errorMessage);
            }
        );

        this.currentSessionId = null;
        this.pendingUploads = new Set();
    }

    async generateResponse(prompt, options = {}) {
        try {
            if (!prompt?.trim()) {
                throw new Error('Please enter a message to send.');
            }

            const response = await this.client.post('/ai/analyze', {
                prompt: prompt.trim(),
                language: options.language || 'English'
            });

            if (!response.data) {
                throw new Error('Invalid response from AI service');
            }

            if (response.data.error) {
                throw new Error(response.data.error);
            }

            return response.data.response;

        } catch (error) {
            console.error('AI Service Error:', error);
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
            const response = await this.client.post('file/session/create');  // Removed leading slash
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
                // Skip if already uploading
                if (this.pendingUploads.has(file.name)) {
                    throw new Error(`File ${file.name} is already being uploaded`);
                }

                try {
                    this.pendingUploads.add(file.name);

                    // Validate file
                    if (!file) {
                        throw new Error('Invalid file object');
                    }

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

                    if (additionalContext?.trim()) {
                        formData.append('context', additionalContext.trim());
                    }

                    const response = await this.client.post(
                        `file/upload/${this.currentSessionId}`,  // Removed leading slash
                        formData,
                        {
                            headers: {
                                'Content-Type': 'multipart/form-data'
                            },
                            // Progress tracking
                            onUploadProgress: (progressEvent) => {
                                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                                console.log(`Upload progress for ${file.name}: ${percentCompleted}%`);
                            }
                        }
                    );

                    if (response.data.error) {
                        throw new Error(response.data.error);
                    }

                    return {
                        ...response.data,
                        context: additionalContext?.trim() || null
                    };
                } finally {
                    this.pendingUploads.delete(file.name);
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

            // Enhance error message for network issues
            if (!navigator.onLine) {
                throw new Error('No internet connection. Please check your network and try again.');
            } else if (error.code === 'ECONNABORTED') {
                throw new Error('Upload timed out. Please try with a smaller file or check your connection.');
            } else if (!error.response) {
                throw new Error('Network error occurred. Please try again.');
            }

            throw error;
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
                await this.client.delete(`file/session/${this.currentSessionId}`);  // Removed leading slash
                this.currentSessionId = null;
            } catch (error) {
                console.error('Error ending file session:', error);
                throw error;
            }
        }
    }
}

export const groqService = new GroqService();