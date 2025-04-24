import React, { useState, useRef, useEffect } from 'react';
import { useVoiceRecording } from '../hooks/useVoiceRecording';
import { groqService } from '../services/groqService';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import FileUpload from './FileUpload';

export default function AIChatInterface() {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [hasStartedChat, setHasStartedChat] = useState(false);
    const [showFileUpload, setShowFileUpload] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const { isRecording, startRecording, stopRecording } = useVoiceRecording();
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null);
    const [shouldAutoScroll, setShouldAutoScroll] = useState(true);

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    };

    useEffect(() => {
        if (shouldAutoScroll) {
            scrollToBottom();
        }
    }, [messages, shouldAutoScroll]);

    const handleScroll = (e) => {
        const messageContainer = e.currentTarget;
        const isAtBottom = messageContainer.scrollHeight - messageContainer.scrollTop <= messageContainer.clientHeight + 100;
        setShouldAutoScroll(isAtBottom);
    };

    const adjustTextareaHeight = () => {
        try {
            const textarea = textareaRef.current;
            if (textarea) {
                const currentValue = textarea.value;
                textarea.style.height = '0px';
                const scrollHeight = textarea.scrollHeight;
                textarea.style.height = Math.min(scrollHeight, 200) + 'px';
                // Ensure value is preserved
                textarea.value = currentValue;
            }
        } catch (error) {
            console.error('Error in adjustTextareaHeight:', error);
        }
    };

    // Modify the resize observer implementation
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            let rafId;
            const resizeObserver = new ResizeObserver((entries) => {
                // Use requestAnimationFrame to throttle the resize callback
                cancelAnimationFrame(rafId);
                rafId = requestAnimationFrame(() => {
                    try {
                        adjustTextareaHeight();
                    } catch (error) {
                        console.error('Error adjusting textarea height:', error);
                    }
                });
            });

            resizeObserver.observe(textarea);
            return () => {
                cancelAnimationFrame(rafId);
                resizeObserver.disconnect();
            };
        }
    }, []);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleFileSelect = async (files) => {
        try {
            setIsProcessing(true);
            setShowFileUpload(false);

            // Create file preview message with a loading indicator
            const filePreviewMessage = {
                role: 'user',
                content: `📄 Analyzing files:\n${files.map(f => `- ${f.name}`).join('\n')}`,
                files: files.map(f => ({
                    name: f.name,
                    type: f.type,
                    size: f.size
                }))
            };
            setMessages(prev => [...prev, filePreviewMessage]);

            // Upload files and get analysis
            try {
                const results = await groqService.uploadFiles(files, inputText);
                setInputText(''); // Clear any additional context

                // Add AI response for each file
                for (const result of results) {
                    let content;
                    if (result.error) {
                        content = `⚠️ Error processing ${result.original_name}: ${result.error}`;
                        if (result.error_details) {
                            content += `\n\nDetails: ${result.error_details}`;
                        }
                    } else {
                        content = result.analysis || `File ${result.original_name} was uploaded successfully.`;
                    }

                    const aiMessage = {
                        role: 'assistant',
                        content: content,
                        fileId: result.file_id
                    };
                    setMessages(prev => [...prev, aiMessage]);
                }

                setUploadedFiles(prev => [...prev, ...files]);
            } catch (error) {
                console.error('File processing error:', error);
                let errorMessage;

                if (!navigator.onLine) {
                    errorMessage = '📶 No internet connection. Please check your network and try again.';
                } else if (error.message.includes('exceeds maximum size')) {
                    errorMessage = '📦 One or more files exceed the maximum size limit of 16MB.';
                } else if (error.message.includes('not supported')) {
                    errorMessage = '❌ One or more files have an unsupported type. Supported types include text, PDF, Word documents, images, and audio files.';
                } else if (error.message.includes('already exists')) {
                    errorMessage = '🔄 One or more files with the same name already exist in this session.';
                } else if (error.message.includes('Failed to upload')) {
                    errorMessage = `⚠️ ${error.message}`; // Use the detailed error message from the service
                } else {
                    errorMessage = `❌ ${error.message || 'An unexpected error occurred while processing your files.'}`;
                }

                // Remove the loading message and add error message
                setMessages(prev => [...prev.slice(0, -1), {
                    role: 'assistant',
                    content: errorMessage
                }]);
            }
        } catch (error) {
            console.error('Error handling files:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '❌ An unexpected error occurred. Please try again.'
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleVoiceRecordingComplete = async (audioBlob) => {
        if (!audioBlob) return;

        try {
            setIsProcessing(true);
            // Use WebSpeech API for transcription directly in the browser
            const transcription = await groqService.processAudioTranscription(audioBlob);

            // Add transcription as user message
            const userMessage = {
                role: 'user',
                content: `🎤 "${transcription}"`
            };
            setMessages(prev => [...prev, userMessage]);

            // Get AI response
            const response = await groqService.generateResponse(transcription);
            const aiMessage = { role: 'assistant', content: response };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error processing voice:', error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error processing your voice message.'
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    // Cleanup file session on unmount
    useEffect(() => {
        return () => {
            groqService.endFileSession();
        };
    }, []);

    const handleSend = async () => {
        if (!inputText.trim() || isProcessing) return;

        try {
            setIsProcessing(true);
            setHasStartedChat(true);

            // Add user message immediately
            const userMessage = { role: 'user', content: inputText };
            setMessages(prev => [...prev, userMessage]);

            // Store and clear input text
            const messageToSend = inputText.trim();
            setInputText('');

            // Get AI response
            const response = await groqService.generateResponse(messageToSend);

            // Add AI response
            const aiMessage = {
                role: 'assistant',
                content: response || 'I apologize, but I was unable to generate a response. Please try again.'
            };
            setMessages(prev => [...prev, aiMessage]);

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = error.message.includes('network') || error.message.includes('connection')
                ? '📶 Network error occurred. Please check your internet connection and try again.'
                : `❌ ${error.message || 'Sorry, I encountered an error processing your request. Please try again.'}`;

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: errorMessage
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            {!hasStartedChat ? (
                <div className="welcome-screen">
                    <div className="text-center">
                        <h1 className="welcome-title">
                            What do you want to learn today?
                        </h1>
                        <p className="welcome-subtitle">
                            Start a conversation with Bloom to begin your learning journey
                        </p>
                    </div>
                </div>
            ) : (
                <>
                    <div className="messages-container" onScroll={handleScroll}>
                        {messages.map((msg, index) => (
                            <div key={index} className={`message ${msg.role}`}>
                                <div className="w-8 h-8 flex-shrink-0">
                                    {msg.role === 'assistant' ? (
                                        <div className="w-full h-full rounded-full bg-purple-600 flex items-center justify-center text-white">
                                            B
                                        </div>
                                    ) : (
                                        <div className="w-full h-full rounded-full bg-gray-500 flex items-center justify-center text-white">
                                            U
                                        </div>
                                    )}
                                </div>
                                <div className="message-content prose prose-purple max-w-none">
                                    {msg.files ? (
                                        <div className="files-preview">
                                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                                            <div className="flex flex-wrap gap-2 mt-2">
                                                {msg.files.map((file, fileIndex) => (
                                                    <div
                                                        key={fileIndex}
                                                        className="flex items-center bg-gray-100 rounded-lg p-2 text-sm"
                                                    >
                                                        <svg className="w-5 h-5 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                        </svg>
                                                        <span>{file.name}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {msg.content}
                                        </ReactMarkdown>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isProcessing && (
                            <div className="message assistant">
                                <div className="w-8 h-8 flex-shrink-0">
                                    <div className="w-full h-full rounded-full bg-purple-600 flex items-center justify-center text-white">
                                        B
                                    </div>
                                </div>
                                <div className="message-content">
                                    <div className="loading"></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </>
            )}

            {/* Always show input container regardless of hasStartedChat */}
            <div className="input-container">
                <div className="input-box relative">
                    <textarea
                        ref={textareaRef}
                        value={inputText}
                        onChange={(e) => {
                            setInputText(e.target.value);
                            adjustTextareaHeight();
                        }}
                        onKeyDown={handleKeyDown}
                        placeholder="Message Bloom..."
                        className="chat-input"
                        rows="1"
                    />

                    <div className="absolute right-2 bottom-2 flex items-center gap-2">
                        <button
                            onClick={() => setShowFileUpload(true)}
                            className="send-button"
                            title="Upload files"
                            disabled={isProcessing}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                <polyline points="17 8 12 3 7 8" />
                                <line x1="12" y1="3" x2="12" y2="15" />
                            </svg>
                        </button>
                        <button
                            onClick={isRecording ? async () => {
                                const blob = await stopRecording();
                                if (blob) handleVoiceRecordingComplete(blob);
                            } : startRecording}
                            className="send-button"
                            disabled={isProcessing}
                            title={isRecording ? "Stop recording" : "Start voice recording"}
                        >
                            {isRecording ? (
                                <div className="w-5 h-5 rounded-full bg-red-500 animate-pulse" />
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                                    <line x1="12" y1="19" x2="12" y2="22" />
                                </svg>
                            )}
                        </button>
                        <button
                            onClick={handleSend}
                            className="send-button"
                            disabled={!inputText.trim() || isProcessing}
                            title="Send message"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M22 2L11 13" />
                                <path d="M22 2l-7 20-4-9-9-4 20-7z" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {showFileUpload && (
                <FileUpload
                    onFileSelect={handleFileSelect}
                    onCancel={() => setShowFileUpload(false)}
                    allowedTypes=".txt,.pdf,.doc,.docx,image/*,audio/*"
                />
            )}
        </div>
    );
}