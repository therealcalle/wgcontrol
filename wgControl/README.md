# wgControl

Local webapp for controlling Philips Hue lights in a shared apartment (WG). Two predefined users, each with their own assigned room lights plus shared lights for common areas.

## Features

- **User profiles** with PIN login (local network only)
- **Per-user light assignment** — room lamps exclusive to each user
- **Shared lights** — hallway, living room, etc. visible to both users
- **On/Off toggle** per light
- **Brightness slider** (dimming)
- **Color picker wheel** for RGB-capable lights (auto-detected)
- **Scenes/presets** — save & apply light configurations with one click
- **User-defined groups** — control multiple lights together
- **Real-time sync** — changes from Hue app, switches, etc. reflected instantly via EventStream (SSE)
- **Settings UI** — assign lights, rename them, manage groups, change PINs (no config files to edit manually)
- **First-run setup wizard** — auto-discovers and pairs with Hue Bridge

## Tech Stack

- **Backend**: Python / FastAPI
- **Frontend**: Svelte 4 (compiled via Vite, served as static files)
- **Bridge API**: Philips Hue CLIP v2
- **Real-time**: Hue EventStream → FastAPI SSE → Svelte stores

## Prerequisites

- **Arch Linux** (or any Linux system)
- **Python 3.11+**
- **Node.js 18+** and **npm**
- **Philips Hue Bridge** on the same local network

## Quick Start

### 1. Install Python dependencies

```bash
cd /path/to/wgControl
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Build the frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

This compiles the Svelte app into `backend/static/`.

### 3. Run the server

```bash
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm run dev
```

Open `http://<your-ip>:8000` in a browser.

### 4. First-time setup

The app will show a setup wizard on first launch:
1. **Discover** your Hue Bridge (or enter IP manually)
2. **Press the button** on the Hue Bridge when prompted
3. **Create two user profiles** with names and PINs
4. **Assign lights** — click each light to cycle between User 1 / User 2 / Shared / Unassigned

After setup, you'll be taken to the login screen.

## Development

Run backend and frontend in parallel for hot-reloading:

**Terminal 1 — Backend:**
```bash
source venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend (dev server with hot reload):**
```bash
cd frontend
npm run dev
```

The Vite dev server runs on `:5173` and proxies `/api/*` to the FastAPI backend on `:8000`.

## Project Structure

```
wgControl/
├── backend/
│   ├── main.py              # FastAPI app, lifespan, static serving
│   ├── config.py            # YAML config loader/saver
│   ├── hue.py               # Hue Bridge CLIP v2 client
│   ├── models.py            # Pydantic models
│   ├── sse.py               # SSE manager (broadcast to frontend clients)
│   ├── state.py             # Shared app state (bridge, SSE manager)
│   └── routes/
│       ├── auth.py           # Login/PIN verification
│       ├── bridge.py         # Bridge discovery & pairing
│       ├── config_routes.py  # Config CRUD (users, assignments, groups)
│       ├── events.py         # SSE endpoint for frontend
│       ├── lights.py         # Light state get/set
│       └── scenes.py         # Scene CRUD & apply
├── frontend/
│   ├── src/
│   │   ├── App.svelte        # Root component (routing)
│   │   ├── stores/            # Svelte stores (lights, user, toast, api)
│   │   ├── utils/color.js     # Color conversions (RGB/HSV/CIE xy)
│   │   └── lib/               # UI components
│   │       ├── LoginPage.svelte
│   │       ├── SetupWizard.svelte
│   │       ├── Dashboard.svelte
│   │       ├── LampCard.svelte
│   │       ├── ColorPicker.svelte
│   │       ├── BrightnessSlider.svelte
│   │       ├── SceneManager.svelte
│   │       ├── GroupControl.svelte
│   │       ├── Settings.svelte
│   │       ├── LightAssignment.svelte
│   │       ├── GroupEditor.svelte
│   │       ├── Navbar.svelte
│   │       └── Toast.svelte
│   ├── package.json
│   └── vite.config.js
├── config.yaml               # Auto-generated at runtime
├── requirements.txt
└── README.md
```

## Configuration

The `config.yaml` file is created and managed automatically through the UI. You never need to edit it manually, but it's human-readable YAML if you want to inspect it.