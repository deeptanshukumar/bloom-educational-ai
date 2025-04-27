import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { auth } from './middleware/auth.js';
import authRoutes from './routes/auth.js';
import userRoutes from './routes/user.js';
import aiRoutes from './routes/ai.js';
import i18next from 'i18next';
import Backend from 'i18next-fs-backend';
import middleware from 'i18next-http-middleware';

dotenv.config();

const app = express();

// Initialize i18next
i18next
    .use(Backend)
    .use(middleware.LanguageDetector)
    .init({
        fallbackLng: 'en',
        backend: {
            loadPath: './locales/{{lng}}/{{ns}}.json',
        },
        ns: ['common', 'errors'],
        defaultNS: 'common'
    });

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(middleware.handle(i18next));

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/user', auth, userRoutes);
app.use('/api/ai', auth, aiRoutes);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));