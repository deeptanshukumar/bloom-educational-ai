import React, { useState, useRef } from 'react';
import './App.css';
import { FaMicrophone } from 'react-icons/fa'; // Import a microphone icon

function App() {
    const [searchInput, setSearchInput] = useState('Multilingual voice');
    const [isSharing, setIsSharing] = useState(false); // State to track screen sharing
    const [stream, setStream] = useState(null); // State to hold the media stream
    const fileInputRef = useRef(null); // Ref for the file input

    const handleScreenShare = async () => {
        // ... (rest of your handleScreenShare function remains the same)
        if (isSharing && stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
            setIsSharing(false);
            console.log("Screen sharing stopped.");
        } else {
            try {
                const displayStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { cursor: "always" },
                    audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 44100 }
                });
                setStream(displayStream);
                setIsSharing(true);
                console.log("Screen sharing started:", displayStream);

                displayStream.getTracks().forEach(track => {
                    track.onended = () => {
                        console.log("Screen sharing ended by user.");
                        setStream(null);
                        setIsSharing(false);
                    };
                });

            } catch (err) {
                console.error("Error starting screen share:", err);
                setIsSharing(false);
                setStream(null);
            }
        }
    };

    const handleUploadButtonClick = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click(); // Programmatically trigger the file input
        }
    };

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            console.log("Selected file:", selectedFile);
            // TODO: Implement your file upload logic here
        }
    };

    return (
        <div className="app">
            <div className="sidebar">
                <h1 className="text-3xl font-bold text-navy-900 mb-10">Bloom</h1>
                <div className="sidebar-middle">
                    <div className="mb-8">
                        <h2 className="text-xl mb-4">Notebooks</h2>
                        <button className="add-button">
                            <span className="mr-2">+</span> Add
                        </button>
                    </div>

                    <div className="mb-8">
                        <h2 className="text-xl mb-4">Subject models</h2>
                        <button className="add-button">
                            <span className="mr-2">+</span> Add
                        </button>
                    </div>
                </div>
                <div className="flex items-center mt-auto pt-4">
                    <div className="account-circle"></div>
                    <span className="ml-3">Account Name</span>
                </div>
            </div>

            <div className="main-content">
                <div className="content-wrapper">
                    <h1 className="main-heading">What do you want to learn today?</h1>

                    <div className="search-container">
                        <div className="avatar-container">
                            <div className="avatar-circle">
                                <svg viewBox="0 0 24 24" width="24" height="24" className="avatar-icon">
                                    <circle cx="12" cy="10" r="4" fill="none" stroke="currentColor" strokeWidth="2"/>
                                    <path d="M6 21v-2a6 6 0 0112 0v2" fill="none" stroke="currentColor" strokeWidth="2"/>
                                </svg>
                            </div>
                        </div>
                        <input
                            type="text"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            className="search-input"
                            placeholder="Ask or search..."
                        />
                        <button className="search-button mic-button">
                             <FaMicrophone />
                        </button>
                        <button className="search-button search-action-button">
                            Search
                        </button>
                    </div>

                     <button className="option-button" onClick={handleScreenShare}>
                        <div className="option-title">{isSharing ? 'Stop Sharing' : 'Screen share'}</div>
                        <div className="option-subtitle">Share a screen with sound guidance</div>
                    </button>

                    {/* Upload File Button */}
                    <div className="mt-5 text-center">
                        <button className="upload-button" onClick={handleUploadButtonClick}>
                            Or upload a file
                        </button>
                        <input
                            id="file-upload"
                            type="file"
                            className="sr-only"
                            onChange={handleFileChange}
                            ref={fileInputRef}
                        />
                    </div>

                </div>
            </div>
        </div>
    );
}

export default App;