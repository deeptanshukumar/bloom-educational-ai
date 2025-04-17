import { useState } from 'react';

export default function BloomInterface() {
    const [searchInput, setSearchInput] = useState('Multilingual voice');

    return (
        <div className="flex h-screen bg-white">
            {/* Sidebar */}
            <div className="w-64 bg-slate-50 flex flex-col">
                <div className="p-6 flex flex-col h-full">
                    <h1 className="text-3xl font-bold text-navy-900 mb-10">Bloom</h1>

                    <div className="mb-8">
                        <h2 className="text-lg font-medium mb-4">Notebooks</h2>
                        <button className="bg-slate-100 hover:bg-slate-200 text-gray-700 w-full py-2 rounded-lg flex items-center justify-center">
                            <span className="mr-1 text-lg">+</span> Add
                        </button>
                    </div>

                    <div className="mb-8">
                        <h2 className="text-lg font-medium mb-4">Subject models</h2>
                        <button className="bg-slate-100 hover:bg-slate-200 text-gray-700 w-full py-2 rounded-lg flex items-center justify-center">
                            <span className="mr-1 text-lg">+</span> Add
                        </button>
                    </div>

                    <div className="mt-auto">
                        <div className="flex items-center">
                            <div className="w-10 h-10 rounded-full bg-slate-200"></div>
                            <span className="ml-3 text-gray-600">Account Name</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col p-8">
                <div className="max-w-3xl mx-auto w-full pt-16">
                    <h1 className="text-4xl font-bold text-center mb-12">What do you want to learn today?</h1>

                    {/* Search Input */}
                    <div className="relative rounded-xl border border-gray-200 mb-8">
                        <div className="flex items-center">
                            <div className="p-3">
                                <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
                                    <svg viewBox="0 0 24 24" width="24" height="24" className="text-navy-900">
                                        <circle cx="12" cy="10" r="4" fill="none" stroke="currentColor" strokeWidth="2"/>
                                        <path d="M6 21v-2a6 6 0 0112 0v2" fill="none" stroke="currentColor" strokeWidth="2"/>
                                    </svg>
                                </div>
                            </div>
                            <input
                                type="text"
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                                className="flex-1 py-4 px-2 outline-none"
                            />
                            <button className="bg-blue-500 text-white p-4 rounded-tr-xl rounded-br-xl hover:bg-blue-600">
                                <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" strokeWidth="2">
                                    <circle cx="11" cy="11" r="8" />
                                    <path d="M21 21l-4.35-4.35" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    {/* Option Buttons */}
                    <div className="grid grid-cols-2 gap-4">
                        <button className="text-center py-6 px-4 rounded-xl border border-gray-200 hover:bg-slate-50 transition">
                            <div className="font-semibold">Use canvas</div>
                        </button>
                        <button className="text-center py-4 px-4 rounded-xl border border-gray-200 hover:bg-slate-50 transition">
                            <div className="font-semibold mb-1">Screen share</div>
                            <div className="text-sm text-gray-600">Share a screen with sound guidance</div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}