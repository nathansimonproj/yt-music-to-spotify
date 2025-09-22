# YouTube Music to Spotify Playlist Migrator

A Flask web application that allows users to migrate their playlists from YouTube Music to Spotify.

## Features

- **OAuth Authentication**: Secure authentication with both YouTube Music and Spotify APIs
- **Playlist Selection**: Browse and select playlists from your YouTube Music library
- **Track Matching**: Automatically searches for matching tracks on Spotify
- **Batch Processing**: Efficiently handles large playlists with batch operations
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Modern UI**: Clean, responsive web interface

## Prerequisites

- Python 3.7 or higher
- YouTube Music account
- Spotify account
- Spotify Developer Account (for API credentials)

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd spotify_api
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Spotify API credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URL=http://localhost:8888/callback
SPOTIFY_API_ENDPOINT=https://api.spotify.com/v1
SPOTIFY_AUTH_TOKEN=your_initial_bearer_token

# YouTube Music credentials (optional)
YT_CLIENT_ID=your_youtube_client_id
YT_CLIENT_SECRET=your_youtube_client_secret
```

### 4. Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:8888/callback` to the redirect URIs
4. Copy your Client ID and Client Secret to the `.env` file

### 5. Run the Application

```bash
python migration.py
```

The application will be available at `http://localhost:8888`

## Usage

1. **Enter YouTube Music User ID**: Enter your YouTube Music channel ID on the home page
2. **Select Playlist**: Choose a playlist from your YouTube Music library
3. **Authenticate with Spotify**: Log in to your Spotify account
4. **Migration**: The application will search for matching tracks and create a new Spotify playlist

## API Endpoints

- `GET /` - Home page with user ID input form
- `POST /save_user` - Save YouTube Music user ID
- `GET /pull_youtube_playlist` - Display available playlists
- `GET /store_playlist` - Extract tracks from selected playlist
- `GET /spotify` - Spotify authentication page
- `GET /login` - Initiate Spotify OAuth flow
- `GET /callback` - Handle Spotify OAuth callback
- `GET /profile` - Fetch Spotify user profile
- `GET /search_tracks` - Search tracks and create Spotify playlist

## File Structure

```
spotify_api/
├── migration.py          # Main Flask application
├── requirements.txt      # Python dependencies
├── templates/
│   └── playlists.html   # Playlist selection template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Error Handling

The application includes comprehensive error handling for:
- Invalid YouTube Music user IDs
- Network connectivity issues
- API rate limiting
- Authentication failures
- Track matching failures

## Security Notes

- Never commit sensitive credentials to version control
- Use environment variables for all API keys and secrets
- The `.gitignore` file is configured to exclude sensitive files
- OAuth tokens are stored in session storage only

## Limitations

- Some tracks may not be found on Spotify due to different catalog availability
- YouTube Music API limitations may affect playlist access
- Rate limiting may apply for large playlists

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational and personal use only. Please respect the terms of service of both YouTube Music and Spotify APIs.