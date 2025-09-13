# eBetStream - Django Betting & Streaming Platform

## Overview
eBetStream is a comprehensive Django-based betting and streaming platform that allows users to:
- Place bets on various games and matches
- Participate in peer-to-peer challenges
- Join gaming clans and tournaments
- Stream content and watch live events
- Manage user accounts with VIP features
- Create and participate in forums and blogs

## Project Architecture

### Core Technology Stack
- **Backend**: Django 5.2.6 (Python web framework)
- **Database**: SQLite3 (development), PostgreSQL (production)
- **Static Files**: WhiteNoise middleware for static file serving
- **Frontend**: Bootstrap 5.3.5 with crispy forms
- **Cache**: Redis (production)
- **Production Server**: Gunicorn

### Django Apps Structure
- `core` - Main application logic, games, matches, tournaments
- `betting` - Betting system, P2P challenges, bet types
- `streaming` - Video streaming functionality
- `users` - User management, authentication, VIP system
- `gameurs` - Gamer profiles and match requests
- `clans_gaming` - Gaming clans and clan management
- `evenements` - Events and event management
- `partenaires` - Partners and partnerships
- `forum` - Discussion forums
- `blog` - Blog system with articles and comments

### Key Features
- User authentication and profiles
- VIP membership system with special privileges
- Peer-to-peer betting challenges
- Gaming clan creation and management
- Event organization and participation
- Live streaming capabilities
- Forum discussions and blog articles
- Partner integration system

## Development Setup

### Environment Configuration
- Django development server runs on port 5000
- ALLOWED_HOSTS configured for Replit environment
- CSRF trusted origins include Replit domain
- WhiteNoise middleware for static file serving
- Media files served from `/media/` directory

### Database
- SQLite3 database for development
- All migrations applied and working
- Custom user model in `users.User`

### Static Files
- Bootstrap 5.3.5 included locally
- Bootstrap Icons for UI elements
- Logo and game images in media directory
- Static files collected and served via WhiteNoise

## Recent Changes (September 13, 2025)
- Successfully imported from GitHub
- Configured Django settings for Replit environment
- Set up ALLOWED_HOSTS and CSRF trusted origins
- Added WhiteNoise middleware for static file serving
- Applied all database migrations
- Configured workflow for Django development server on port 5000
- Set up deployment configuration with Gunicorn
- Collected static files and verified functionality

## Deployment Configuration
- **Target**: Autoscale deployment
- **Build**: Collects static files with `collectstatic --noinput`
- **Run**: Gunicorn WSGI server on port 5000
- **Static Files**: WhiteNoise serves static files in production

## Current Status
✅ Project successfully set up and running in Replit environment
✅ Django server running on port 5000
✅ Database migrations applied
✅ Static files served correctly
✅ Media files accessible
✅ Ready for development and deployment

## User Preferences
- Language: French (fr-fr)
- Timezone: Europe/Paris
- Template Pack: Bootstrap 5 with crispy forms