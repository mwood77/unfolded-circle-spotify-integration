# Spotify Integration for Unfolded Circle Remote 2/3

Control Spotify playback directly from your Unfolded Circle Remote 2 or Remote 3 with **full media control**, **Spotify Connect device switching**, and **real-time playback updates** with album artwork.

This project is a disconnected fork of `uc-intg-spotify` by @mase1981. The original project was written without without hardware testing or any kind of validation. This meant a number of usability regressions (bugs) entered each release. The author wasn't receptive to feedback and shadowbanned me from his repositories. Hence, this fork.

**_Development in this repository is active and welcomes all feedback and feature requests._ Have you found a bug or want a feature? Submit it here:**
- [unfolded-circle-spotify-integration/issues](https://github.com/mwood77/unfolded-circle-spotify-integration/issues)

## Core Features

### Remote Controls (Physical and GUI)

- **Physical Button Mapping** — Play/Pause, Next, Previous, Volume Up/Down (touch slider), Mute, 
- **Custom UI Page (GUI)** — Tap the artwork to play/pause, swipe left/right to skip or restart tracks, shuffle toggle, and repeat.

### Entities

#### Spotify Media Player

- **UI Playback Controls** — Play/Pause, Next, Previous, Seek, Shuffle, Repeat
- **Media Browser Button** — Open Spotify library browsing from the Spotify Player UI
- **Volume Management** — Slider volume control
- **Media Metadata** — Title, artist, album artwork, and playback position.
- **Spotify Connect Quick Switch** — Switch active playback devices from the Spotify Player UI or Spotify Active Device entity
- **Real-time Updates** — 10-second polling with optimistic state updates

### Media Browser & Media Search

> [!IMPORTANT]
> Media browsing and Search requires Unfolded Circle remote firmware `2.9.5` or newer. At the time of publication, this is only available in BETA firmware.

Browse and play your Spotify library directly from the Remote's media browser:

- **Playlists** — All your playlists with artwork
- **Saved Albums** — Your album library
- **Liked Songs** — Saved tracks collection
- **Top Tracks** — Your most-played tracks
- **Top Artists** — Your most-listened artists with paged discography browsing
- **Followed Artists** — Artists you follow
- **Recently Played** — Recent listening history
- **Search** — Full-text search across tracks, albums, artists, and playlists

Spotify removed the public Browse Categories, New Releases, and Artist Top Tracks
endpoints for Development Mode apps in 2026, so those surfaces are intentionally
not exposed by this integration.


#### Sensor Entities

- **Now Playing** — Current track title and artist as text
- **Active Device** — Currently active Spotify Connect playback device

#### Spotify Connect Entity

- **Active Device** — Browse and switch between all discovered Spotify Connect devices with next/previous cycling

## Prerequisites

- **Spotify Premium required**
  - Spotify updated their developer application and public API in February/March of 2026. These changes reduced some functionality granted to developer applications and introduced a mandatory Spotify Premium account.
- **This integration will not work without a Spotify Premium account(s)**
- **Remote firmware `2.9.5` or newer required for media browsing and search**
  - At the time of publishing, `2.9.5` is currently in BETA.
  - The integration supports mainline firmware, but the media browsing and search will be disabled.
- **You must create a Spotify Developer Application during setup**
  - This is free.

### Spotify Developer App Setup

**BEFORE INSTALLATION:** Create a Spotify Developer App (free, 5 minutes):

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your **Premium** Spotify account
3. Click **Create app**
    - If that button isn't visible, click on your account name, then click **Dashboard**. If prompted accept Spotify's Developer Terms.
  - If you had to accept their Deve
4. Fill in:
   - **App Name**: `UC Remote Integration` (or any name)
   - **App Description**: `Unfolded Circle Remote integration`
   - **Redirect URI**: `https://example.com/callback` 
      - *You must fill this in exactly as specified above, and click the "Add" button*
   - **Which API/SDKs are you planning to use?:**
      - Select **Web API**. Leave the rest unselected
5. Click **"Save"**
6. On the next screen, you'll see a **Client ID** and **Client Secret** (click "View client secret"). Write these values down as you'll need them during the installation setup.

## Installation

### 1. Remote Web Interface (Recommended)
1. Navigate to the [**Releases**](https://github.com/mwood77/unfolded-circle-spotify-integration/releases) page
2. Download the latest `unfolded-circle-spotify-integration-<version>-aarch64.tar.gz` file
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

### 2: Docker (Advanced Users)

**Image**: `ghcr.io/mwood77/unfolded-circle-spotify-integration:latest`

**Docker Compose:**
```yaml
services:
  unfolded-circle-spotify-integration:
    image: ghcr.io/mwood77/unfolded-circle-spotify-integration:latest
    container_name: unfolded-circle-spotify-integration
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name=unfolded-circle-spotify-integration --network host -v </local/path>:/data -e UC_CONFIG_HOME=/data -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app --restart unless-stopped ghcr.io/mwood77/unfolded-circle-spotify-integration:latest
```

## Configuration

### Step 1: Enter App Credentials

1. After installation, go to **Settings** → **Integrations** → **Spotify**
2. Click **"Configure"**
3. Enter your **Spotify Client ID**
4. Enter your **Spotify Client Secret**
5. Click **Next**

### Step 2: Authentication

1. Click the Spotify authorization URL displayed on screen
2. Log into your Spotify account and click **Agree**
3. Browser shows "page not found" — **this is normal!**
4. Copy the `code=...` value from the browser address bar (or paste the entire URL)
5. Paste into setup form and click **Finish**

### Step 3: Completion

Five entities are created automatically:
- **Spotify (<account>) Player** — Media Player with browse, search, and playback control
- **Spotify (<account>) Remote** — Remote entity with button mappings and custom UI
- **Spotify (<account>) Active Device** — Select entity for device switching
- **Spotify (<account>) Now Playing** — Sensor showing current track
- **Spotify (<account>) Active Device** — Sensor showing active playback device

### Multiple Spotify Accounts

To add another Spotify account, run the integration setup again and authenticate in Spotify as the other user. Each account is stored as its own configured device with separate OAuth tokens and account-specific entities. This is a workaround so you can have multiple Spotify accounts controllable from your remote.

## Contributing

- Please fork this project and open PRs against it.

## Local Builds

To speed up local development, I've added a simple build script. To test the release on your Unfolded Circle Remote, you'll need to generate a build. To do so, run the following command from the project root:
- `./scripts/build-local.sh <YOUR_VERSION>`

After the build is complete, you'll find your tarball. Simply install it like any regular Custom Integration for Unfolded Circle Remotes.

## License

This project is licensed under the MPL-2.0 License - see LICENSE file for details.

Originally derived from [`uc-intg-spotify`](https://github.com/mase1981/uc-intg-spotify) by [`mase1981`](https://github.com/mase1981).

## Legal Disclaimer

This is an **independent, unofficial project** using Spotify's public Web API. Not sponsored, endorsed, or affiliated with Spotify AB.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mwood77/unfolded-circle-spotify-integration/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [mwood77](https://github.com/mwood77)
- **Spotify Support**: [Official Spotify Support](https://support.spotify.com/)
