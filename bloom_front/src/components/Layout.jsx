import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function Layout({ children }) {
    const { logout } = useAuth();

    return (
        <div className="app">
            {/* Sidebar */}
            <div className="sidebar">
                <div className="px-2 py-4">
                    <h1 className="text-2xl font-bold text-white mb-4 px-3">Bloom</h1>
                    <button className="new-chat-button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 5v14M5 12h14" />
                        </svg>
                        New chat
                    </button>
                </div>

                {/* Feature Buttons */}
                <div className="px-2 space-y-2">
                    <button className="w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" />
                            <path d="M3 9h18" />
                        </svg>
                        Notebooks
                    </button>
                    <button className="w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5z" />
                            <path d="M2 17l10 5 10-5" />
                            <path d="M2 12l10 5 10-5" />
                        </svg>
                        Subject Models
                    </button>
                    <button className="w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                            <polyline points="10 17 15 12 10 7" />
                            <line x1="15" y1="12" x2="3" y2="12" />
                        </svg>
                        Share Screen
                    </button>
                    <button className="w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                            <polyline points="14 2 14 8 20 8" />
                            <line x1="12" y1="18" x2="12" y2="12" />
                            <line x1="9" y1="15" x2="15" y2="15" />
                        </svg>
                        Upload Files
                    </button>
                </div>

                <div className="flex-1">
                    {/* Chat history items will go here */}
                </div>

                {/* User section */}
                <div className="border-t border-gray-700 p-2 mt-2">
                    <button
                        onClick={logout}
                        className="w-full px-3 py-2 text-left text-sm text-white hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-2"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                            <polyline points="16 17 21 12 16 7" />
                            <line x1="21" y1="12" x2="9" y2="12" />
                        </svg>
                        Log out
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <main className="main-content">
                {children}
            </main>
        </div>
    );
}