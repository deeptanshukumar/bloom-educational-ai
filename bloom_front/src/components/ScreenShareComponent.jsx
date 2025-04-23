import React, { useState, useEffect, useRef } from 'react';
import { screenShareService } from '../services/screenShareService';

export default function ScreenShareComponent() {
    const [isSharing, setIsSharing] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [analysis, setAnalysis] = useState('');
    const videoRef = useRef(null);

    useEffect(() => {
        const handleAnalysis = (event) => {
            setAnalysis(event.detail.analysis);
        };

        window.addEventListener('screenAnalysis', handleAnalysis);
        return () => {
            window.removeEventListener('screenAnalysis', handleAnalysis);
            if (isSharing) {
                screenShareService.stopSharing();
            }
        };
    }, [isSharing]);

    const startSharing = async () => {
        try {
            const stream = await screenShareService.startSharing();
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            setIsSharing(true);
        } catch (error) {
            console.error('Failed to start sharing:', error);
        }
    };

    const stopSharing = () => {
        screenShareService.stopSharing();
        setIsSharing(false);
        setIsRecording(false);
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
    };

    const toggleRecording = () => {
        if (!isRecording) {
            screenShareService.startRecording();
            setIsRecording(true);
        } else {
            screenShareService.stopRecording();
            setIsRecording(false);
        }
    };

    return (
        <div className="screen-share-container">
            <div className="video-container">
                <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="screen-share-video"
                />
            </div>

            <div className="controls">
                <button
                    onClick={isSharing ? stopSharing : startSharing}
                    className={`control-button ${isSharing ? 'stop' : 'start'}`}
                >
                    {isSharing ? 'Stop Sharing' : 'Start Sharing'}
                </button>

                {isSharing && (
                    <button
                        onClick={toggleRecording}
                        className={`control-button ${isRecording ? 'recording' : ''}`}
                    >
                        {isRecording ? 'Stop Recording' : 'Start Recording'}
                    </button>
                )}
            </div>

            {analysis && (
                <div className="analysis-panel">
                    <h3>AI Analysis</h3>
                    <p>{analysis}</p>
                </div>
            )}
        </div>
    );
}