import { useState, useCallback } from 'react';

export function useVoiceRecording() {
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState(null);
    const [audioChunks, setAudioChunks] = useState([]);

    const startRecording = useCallback(async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);

            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    setAudioChunks(chunks => [...chunks, e.data]);
                }
            };

            recorder.onstop = () => {
                stream.getTracks().forEach(track => track.stop());
            };

            setMediaRecorder(recorder);
            setAudioChunks([]);
            recorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Could not access microphone. Please ensure you have granted permission.');
        }
    }, []);

    const stopRecording = useCallback(async () => {
        if (!mediaRecorder) return null;

        return new Promise((resolve) => {
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                setAudioChunks([]);
                setIsRecording(false);
                resolve(audioBlob);
            };

            mediaRecorder.stop();
        });
    }, [mediaRecorder, audioChunks]);

    return {
        isRecording,
        startRecording,
        stopRecording
    };
}