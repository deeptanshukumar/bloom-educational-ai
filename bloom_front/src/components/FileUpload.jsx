import React, { useState, useRef } from 'react';

const ALLOWED_TYPES = [
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

const MAX_FILE_SIZE = 16 * 1024 * 1024; // 16MB

const FileIcon = ({ type }) => {
    // Define icon based on file type
    const getIcon = () => {
        if (type.startsWith('image/')) {
            return (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            );
        } else if (type.startsWith('audio/')) {
            return (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            );
        } else if (type.includes('pdf')) {
            return (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            );
        }
        return (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        );
    };

    return (
        <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {getIcon()}
        </svg>
    );
};

export default function FileUpload({ onFileSelect, onCancel }) {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [additionalText, setAdditionalText] = useState('');
    const [errors, setErrors] = useState([]);
    const fileInputRef = useRef(null);

    const validateFile = (file) => {
        if (!ALLOWED_TYPES.includes(file.type)) {
            return `File type ${file.type} not supported for ${file.name}`;
        }
        if (file.size > MAX_FILE_SIZE) {
            return `File ${file.name} exceeds maximum size of 16MB`;
        }
        return null;
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    };

    const handleFileInput = (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    };

    const handleFiles = (files) => {
        const newErrors = [];
        const validFiles = files.filter(file => {
            const error = validateFile(file);
            if (error) {
                newErrors.push(error);
                return false;
            }
            return true;
        });

        setErrors(newErrors);
        setSelectedFiles(prevFiles => [...prevFiles, ...validFiles]);
    };

    const removeFile = (index) => {
        setSelectedFiles(files => files.filter((_, i) => i !== index));
    };

    const handleSubmit = () => {
        if (selectedFiles.length > 0) {
            setErrors([]);
            onFileSelect(selectedFiles, additionalText);
        }
    };

    const clearErrors = () => {
        setErrors([]);
    };

    return (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-xl w-full mx-4">
                <div className="mb-4 flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-900">Add files</h3>
                    <button
                        onClick={onCancel}
                        className="text-gray-400 hover:text-gray-500"
                    >
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {errors.length > 0 && (
                    <div className="mb-4 p-4 bg-red-50 rounded-md">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <h3 className="text-sm font-medium text-red-800">
                                    There were {errors.length} errors with your submission
                                </h3>
                                <div className="mt-2 text-sm text-red-700">
                                    <ul className="list-disc pl-5 space-y-1">
                                        {errors.map((error, index) => (
                                            <li key={index}>{error}</li>
                                        ))}
                                    </ul>
                                </div>
                                <div className="mt-4">
                                    <button
                                        type="button"
                                        onClick={clearErrors}
                                        className="text-sm font-medium text-red-800 hover:text-red-600"
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div
                    className={`border-2 border-dashed rounded-lg p-6 mb-4 text-center
                        ${dragActive ? 'border-purple-500 bg-purple-50' : 'border-gray-300'}
                        ${selectedFiles.length > 0 ? 'border-solid' : 'border-dashed'}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        className="hidden"
                        accept={ALLOWED_TYPES.join(',')}
                        onChange={handleFileInput}
                    />

                    {selectedFiles.length === 0 ? (
                        <div className="space-y-4">
                            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M24 8v24M8 24h24" />
                            </svg>
                            <div className="text-sm text-gray-600">
                                <button
                                    type="button"
                                    onClick={() => fileInputRef.current?.click()}
                                    className="text-purple-600 hover:text-purple-500 font-medium"
                                >
                                    Click to upload
                                </button>
                                {" or drag and drop"}
                            </div>
                            <p className="text-xs text-gray-500">Up to 16 MB per file</p>
                            <p className="text-xs text-gray-500">Supported formats: PDF, Word, Text, Images (JPEG, PNG, GIF), Audio (MP3, WAV)</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {selectedFiles.map((file, index) => (
                                <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded">
                                    <div className="flex items-center space-x-3">
                                        <FileIcon type={file.type} />
                                        <div>
                                            <span className="text-sm text-gray-700">{file.name}</span>
                                            <p className="text-xs text-gray-500">
                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => removeFile(index)}
                                        className="text-gray-400 hover:text-gray-500"
                                    >
                                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                            ))}
                            <button
                                type="button"
                                onClick={() => fileInputRef.current?.click()}
                                className="text-sm text-purple-600 hover:text-purple-500"
                            >
                                Add more files
                            </button>
                        </div>
                    )}
                </div>

                <div className="mb-4">
                    <label htmlFor="additionalText" className="block text-sm font-medium text-gray-700 mb-2">
                        Additional Context or Notes
                    </label>
                    <textarea
                        id="additionalText"
                        rows="3"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-purple-500 focus:border-purple-500"
                        placeholder="Add any additional context or notes about the files..."
                        value={additionalText}
                        onChange={(e) => setAdditionalText(e.target.value)}
                    />
                </div>

                <div className="flex justify-end space-x-3">
                    <button
                        onClick={onCancel}
                        className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-300 rounded-md"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={selectedFiles.length === 0}
                        className={`px-4 py-2 text-sm font-medium text-white rounded-md
                            ${selectedFiles.length > 0
                                ? 'bg-purple-600 hover:bg-purple-700'
                                : 'bg-gray-300 cursor-not-allowed'}`}
                    >
                        Upload
                    </button>
                </div>
            </div>
        </div>
    );
}