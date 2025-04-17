import React, { useState } from 'react';
import './App.css';

function App() {
    const [searchInput, setSearchInput] = useState('Multilingual voice');

    return (
        <div className="app">
            {/* Sidebar */}
            <div className="sidebar">
                <h1 className="text-3xl font-bold text-navy-900 mb-10">Bloom</h1>

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

                <div className="mt-auto">
                    <div className="flex items-center">
                        <div className="account-circle"></div>
                        <span className="ml-3">Account Name</span>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="main-content">
                <div className="content-wrapper">
                    <h1 className="main-heading">What do you want to learn today?</h1>

                    {/* Search Input */}
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
                        />
                        <button className="search-button">
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" strokeWidth="2">
                                <circle cx="11" cy="11" r="8" />
                                <path d="M21 21l-4.35-4.35" />
                            </svg>
                        </button>
                    </div>

                    {/* Option Buttons */}
                    <div className="options-grid">
                        <button className="option-button">
                            <div className="option-title">Use canvas</div>
                        </button>
                        <button className="option-button">
                            <div className="option-title">Screen share</div>
                            <div className="option-subtitle">Share a screen with sound guidance</div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;