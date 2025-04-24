import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const validateToken = async () => {
            const token = localStorage.getItem('bloom_token');
            if (token) {
                try {
                    const response = await axios.get('http://localhost:5000/api/auth/profile', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (response.status === 200) {
                        setUser(response.data);
                    } else {
                        localStorage.removeItem('bloom_token');
                        setUser(null);
                    }
                } catch (error) {
                    console.error('Token validation error:', error);
                    localStorage.removeItem('bloom_token');
                    setUser(null);
                }
            }
            setLoading(false);
        };

        validateToken();
    }, []);

    const login = async (email, password) => {
        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_URL}/api/auth/login`,
                { email, password },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    withCredentials: true
                }
            );

            const data = response.data;

            if (response.status !== 200) {
                throw new Error(data.error || 'Login failed');
            }

            if (data.access_token) {
                localStorage.setItem('bloom_token', data.access_token);
                setUser(data.user);
                return true;
            }
            throw new Error('No access token received');
        } catch (error) {
            console.error('Login error details:', error.response?.data);
            throw new Error(error.response?.data?.message || 'Invalid credentials');
        }
    };

    const logout = async () => {
        try {
            const token = localStorage.getItem('bloom_token');
            if (token) {
                await axios.post('http://localhost:5000/api/auth/logout', null, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    withCredentials: true
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('bloom_token');
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);