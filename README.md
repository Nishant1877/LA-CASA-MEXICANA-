# 🌮 La Casa Mexicana — Restaurant Website

A full-stack Mexican restaurant website with animated 3D elements, built with React (frontend) and Flask + SQLite (backend).

## 🚀 Quick Start

### Frontend Only (Open directly)
Just open `index.html` in any browser — no server needed! All pages work fully offline.

### Full Stack with Backend API
The frontend will automatically connect to the Flask backend if running on port 5000.

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
The Flask server starts at `http://localhost:5000`

## 📁 Project Structure

```
restaurant/
├── index.html              # Complete frontend (React + Three.js)
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   └── restaurant.db       # SQLite database (auto-created)
└── README.md
```

## 🎨 Pages

| Page | Description |
|------|-------------|
| **Home** | Hero with 3D Three.js canvas, restaurant info, features, photo gallery & reviews |
| **Menu** | Full menu with category filtering, spice indicators, photo modal |
| **Chef's Specials** | 3D animated page with chef's curated dishes |
| **Seasonal Menu** | Seasonal offerings with 3D floating elements |
| **Events** | Cultural events, weekly dances, festivals |
| **Reservations** | Full booking form with confirmation |

## 🔌 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/menu` | All menu items |
| GET | `/api/menu/specials` | Chef's specials |
| GET | `/api/menu/seasonal` | Seasonal items |
| GET | `/api/events` | All events |
| GET | `/api/reviews` | Customer reviews |
| POST | `/api/book` | Book a table |
| POST | `/api/reviews` | Submit a review |

## ✨ Features

- **3D Elements**: Three.js geometric shapes, animated floating objects, torus knots
- **Custom Cursor**: Gold ring cursor with blend mode
- **Particle System**: Floating golden particles across all pages
- **Scroll Animations**: Reveal-on-scroll for all content
- **Loading Screen**: Branded loading animation
- **Sticky Nav**: Glass-morphism navbar on scroll
- **Color Palette**: Terracotta, deep gold, cream, sage — authentic Mexican warmth
- **Typography**: Playfair Display + Cormorant Garamond + Josefin Sans
