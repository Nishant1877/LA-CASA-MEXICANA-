from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
 
app = Flask(__name__)
CORS(app)
 
DB_PATH = os.path.join(os.path.dirname(__file__), 'restaurant.db')
 
# ─────────────────────────────────────────────
#  EMAIL CONFIGURATION
#  Set these via environment variables, or
#  replace the fallback strings directly.
#
#  For Gmail:
#    1. Enable 2-Step Verification on your Google account
#    2. Go to https://myaccount.google.com/apppasswords
#    3. Create an App Password (select "Mail" + "Other")
#    4. Use that 16-char password as SMTP_PASSWORD
#
#  Run the server with env vars like this:
#    SMTP_USER=you@gmail.com SMTP_PASSWORD=xxxx python app.py
# ─────────────────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "465"))   # 465 = SSL
SMTP_USER     = os.getenv("SMTP_USER",     "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password_here")
FROM_NAME     = "La Casa Mexicana"
FROM_ADDR     = SMTP_USER
 
 
# ─────────────────────────────────────────────
#  EMAIL SENDER
# ─────────────────────────────────────────────
 
def send_confirmation_email(booking: dict) -> bool:
    """Build and send a beautifully styled HTML confirmation email."""
 
    name     = booking["name"]
    email    = booking["email"]
    date     = booking["date"]
    time_str = booking["time"]
    guests   = booking["guests"]
    requests = booking.get("special_requests", "").strip() or "None"
 
    ref     = f"LCM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    year    = datetime.now().year
    subject = f"Reservation Confirmed — La Casa Mexicana ({date} at {time_str})"
 
    # ── Plain-text fallback ──────────────────
    plain = f"""
Hola {name},
 
Your table reservation at La Casa Mexicana is confirmed!
 
Booking Reference : {ref}
Date              : {date}
Time              : {time_str}
Guests            : {guests}
Special Requests  : {requests}
 
Address : 123 Calle Fiesta, City Center
Phone   : +1 (555) 123-4567
Hours   : Mon-Thu 12pm-10pm | Fri-Sat 12pm-12am | Sun 11am-9pm
 
To modify or cancel, call us at least 2 hours before your booking.
 
We look forward to welcoming you!
Hasta pronto!
 
— The La Casa Mexicana Team
"""
 
    # ── HTML email ───────────────────────────
    # Build detail rows separately to keep the f-string clean
    detail_rows = ""
    for icon, label, value in [
        ("📅", "Date",              date),
        ("🕐", "Time",              time_str),
        ("👥", "Guests",            f"{guests} {'Guest' if str(guests) == '1' else 'Guests'}"),
        ("💬", "Special Requests",  requests),
    ]:
        detail_rows += f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px;">
          <tr>
            <td style="width:36px;vertical-align:middle;font-size:20px;">{icon}</td>
            <td style="padding-left:12px;vertical-align:middle;">
              <span style="display:block;font-size:10px;letter-spacing:3px;text-transform:uppercase;
                           color:#C4622D;margin-bottom:2px;">{label}</span>
              <span style="font-size:16px;color:#FAF3E0;font-weight:bold;">{value}</span>
            </td>
          </tr>
        </table>
        """
 
    expect_cols = ""
    for emoji, title, desc in [
        ("🌮", "Authentic Flavors",   "Recipes passed down through generations"),
        ("💃", "Cultural Evenings",   "Live Mariachi &amp; Folklorico every Friday"),
        ("✨", "Warm Hospitality",    "All-Mexican staff, immaculate spaces"),
    ]:
        expect_cols += f"""
        <td style="width:33%;vertical-align:top;text-align:center;padding:0 8px;">
          <p style="font-size:24px;margin:0 0 8px;">{emoji}</p>
          <p style="font-size:11px;letter-spacing:2px;text-transform:uppercase;
                    color:#C4622D;margin:0 0 4px;">{title}</p>
          <p style="font-size:12px;color:#E8D5A3;line-height:1.6;margin:0;">{desc}</p>
        </td>
        """
 
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Reservation Confirmed — La Casa Mexicana</title>
</head>
<body style="margin:0;padding:0;background:#1A0A00;font-family:Georgia,serif;">
 
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1A0A00;padding:40px 0;">
  <tr><td align="center">
  <table width="600" cellpadding="0" cellspacing="0"
         style="background:#1A0A00;border:1px solid #D4A853;max-width:600px;width:100%;">
 
    <!-- HEADER -->
    <tr>
      <td style="background:#3D1F00;padding:48px 40px;text-align:center;border-bottom:3px solid #D4A853;">
        <p style="margin:0 0 6px;font-size:11px;letter-spacing:5px;text-transform:uppercase;color:#D4A853;">
          Authentic Mexican Cuisine
        </p>
        <h1 style="margin:0;font-size:40px;font-weight:900;color:#FAF3E0;line-height:1.1;">
          La Casa<br/><span style="color:#D4A853;font-style:italic;">Mexicana</span>
        </h1>
        <p style="margin:16px 0 0;font-size:13px;letter-spacing:3px;text-transform:uppercase;color:#E8D5A3;">
          &#127790; &nbsp;Table Reservation Confirmed&nbsp; &#127790;
        </p>
      </td>
    </tr>
 
    <!-- GREETING -->
    <tr>
      <td style="padding:40px 40px 0;text-align:center;">
        <h2 style="margin:0 0 12px;font-size:26px;color:#FAF3E0;">Hola, {name}! &#128075;</h2>
        <p style="margin:0;font-size:16px;color:#E8D5A3;line-height:1.8;">
          Your reservation has been confirmed. We are thrilled to welcome you<br/>
          and cannot wait to share the warmth of Mexico with you.
        </p>
      </td>
    </tr>
 
    <!-- BOOKING CARD -->
    <tr>
      <td style="padding:32px 40px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:#3D1F00;border:1px solid rgba(212,168,83,0.3);">
          <tr>
            <td style="padding:28px 32px;">
              <!-- Reference -->
              <p style="margin:0 0 20px;text-align:center;">
                <span style="font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#C4622D;">
                  Booking Reference
                </span><br/>
                <span style="font-family:'Courier New',monospace;font-size:20px;color:#D4A853;
                             font-weight:bold;letter-spacing:2px;">{ref}</span>
              </p>
              <hr style="border:none;border-top:1px solid rgba(212,168,83,0.2);margin:0 0 24px;"/>
              {detail_rows}
            </td>
          </tr>
        </table>
      </td>
    </tr>
 
    <!-- WHAT TO EXPECT -->
    <tr>
      <td style="padding:0 40px 32px;">
        <h3 style="margin:0 0 20px;font-size:18px;color:#D4A853;text-align:center;letter-spacing:1px;">
          What Awaits You &#10024;
        </h3>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>{expect_cols}</tr>
        </table>
      </td>
    </tr>
 
    <!-- LOCATION -->
    <tr>
      <td style="padding:0 40px 32px;">
        <table width="100%" cellpadding="0" cellspacing="0"
               style="background:rgba(196,98,45,0.1);border-left:3px solid #C4622D;padding:20px 24px;">
          <tr>
            <td>
              <p style="margin:0 0 8px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#C4622D;">
                Find Us
              </p>
              <p style="margin:0 0 4px;font-size:15px;color:#FAF3E0;">
                &#128205; 123 Calle Fiesta, City Center
              </p>
              <p style="margin:0 0 4px;font-size:15px;color:#E8D5A3;">
                &#128222; +1 (555) 123-4567
              </p>
              <p style="margin:0;font-size:13px;color:#E8D5A3;opacity:0.7;">
                Mon&ndash;Thu 12pm&ndash;10pm &nbsp;|&nbsp;
                Fri&ndash;Sat 12pm&ndash;12am &nbsp;|&nbsp;
                Sun 11am&ndash;9pm
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
 
    <!-- CANCEL NOTE -->
    <tr>
      <td style="padding:0 40px 32px;text-align:center;">
        <p style="margin:0;font-size:13px;color:#E8D5A3;opacity:0.6;line-height:1.8;">
          Need to modify or cancel?<br/>
          Call <strong>+1 (555) 123-4567</strong> or email
          <strong>hola@lacasamexicana.com</strong> at least 2 hours before your booking.
        </p>
      </td>
    </tr>
 
    <!-- FOOTER -->
    <tr>
      <td style="background:#0D0500;border-top:1px solid rgba(212,168,83,0.2);
                  padding:28px 40px;text-align:center;">
        <p style="margin:0 0 8px;font-size:20px;font-weight:900;color:#D4A853;">La Casa Mexicana</p>
        <p style="margin:0 0 16px;font-size:12px;color:#E8D5A3;opacity:0.5;font-style:italic;">
          Where every meal is a celebration of tradition
        </p>
        <p style="margin:0;font-size:11px;color:#E8D5A3;opacity:0.35;">
          &copy; {year} La Casa Mexicana &middot; 123 Calle Fiesta, City Center
        </p>
      </td>
    </tr>
 
  </table>
  </td></tr>
</table>
</body>
</html>"""
 
    # ── Assemble MIME ────────────────────────
    msg             = MIMEMultipart("alternative")
    msg["Subject"]  = subject
    msg["From"]     = f"{FROM_NAME} <{FROM_ADDR}>"
    msg["To"]       = email
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))
 
    # ── Send ────────────────────────────────
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_ADDR, [email], msg.as_string())
        print(f"[EMAIL] Confirmation sent to {email}")
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] Could not send to {email}: {exc}")
        return False
 
 
# ─────────────────────────────────────────────
#  DATABASE HELPERS
# ─────────────────────────────────────────────
 
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_db():
    conn = get_db()
    c = conn.cursor()
 
    c.execute('''CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, description TEXT,
        price REAL NOT NULL, category TEXT NOT NULL,
        image_url TEXT, is_special INTEGER DEFAULT 0,
        is_seasonal INTEGER DEFAULT 0, spice_level INTEGER DEFAULT 1
    )''')
 
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL, description TEXT,
        event_date TEXT NOT NULL, event_time TEXT,
        image_url TEXT, category TEXT
    )''')
 
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, email TEXT NOT NULL,
        phone TEXT NOT NULL, date TEXT NOT NULL,
        time TEXT NOT NULL, guests INTEGER NOT NULL,
        special_requests TEXT,
        email_sent INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
 
    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, rating INTEGER NOT NULL,
        comment TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
 
    c.execute("SELECT COUNT(*) FROM menu_items")
    if c.fetchone()[0] == 0:
        items = [
            ("Tacos al Pastor","Marinated pork with pineapple, cilantro & onion on soft corn tortillas",14.99,"Tacos","https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400",0,0,2),
            ("Enchiladas Rojas","Corn tortillas filled with chicken, topped with red chili sauce & cheese",16.99,"Mains","https://images.unsplash.com/photo-1534352956036-cd81e27dd615?w=400",0,0,2),
            ("Guacamole Fresco","Hand-mashed avocado with lime, cilantro, tomato & jalapeño",9.99,"Starters","https://images.unsplash.com/photo-1551191372-2d88a36a2b70?w=400",0,0,1),
            ("Chiles Rellenos","Poblano peppers stuffed with cheese, battered & fried in tomato sauce",18.99,"Mains","https://images.unsplash.com/photo-1582564286939-400a311013a2?w=400",1,0,2),
            ("Pozole Rojo","Traditional hominy soup with slow-cooked pork in rich red chile broth",15.99,"Soups","https://images.unsplash.com/photo-1607116667981-ff148a9c0154?w=400",1,0,3),
            ("Tamales de Rajas","Corn masa stuffed with roasted peppers & cheese, wrapped in corn husks",13.99,"Mains","https://images.unsplash.com/photo-1600891964092-4316c288032e?w=400",0,1,1),
            ("Mole Poblano","Chicken in rich dark mole sauce with 30+ ingredients including chocolate",22.99,"Mains","https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",1,0,2),
            ("Churros con Chocolate","Crispy cinnamon churros with warm dark chocolate dipping sauce",8.99,"Desserts","https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400",0,0,0),
            ("Michelada","Beer with lime juice, hot sauce, Worcestershire & chili salt rim",7.99,"Drinks","https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400",0,0,2),
            ("Horchata","Traditional rice milk with cinnamon, vanilla & a hint of almond",5.99,"Drinks","https://images.unsplash.com/photo-1499638673689-79a0b5115d87?w=400",0,0,0),
            ("Sopa de Lima","Yucatán-style lime chicken soup with crispy tortilla strips",13.99,"Soups","https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400",0,1,1),
            ("Camarones a la Diabla","Spicy shrimp in fiery red chile sauce served with Mexican rice",24.99,"Mains","https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400",0,1,4),
            ("Elote Callejero","Street-style corn with mayo, cotija cheese, lime & chili powder",6.99,"Starters","https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400",0,0,1),
            ("Tres Leches","Light sponge cake soaked in three milks, topped with whipped cream",7.99,"Desserts","https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400",0,0,0),
            ("Margarita Clásica","Premium tequila with fresh lime juice & triple sec, salted rim",10.99,"Drinks","https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400",0,0,0),
        ]
        c.executemany("INSERT INTO menu_items (name,description,price,category,image_url,is_special,is_seasonal,spice_level) VALUES (?,?,?,?,?,?,?,?)", items)
 
    c.execute("SELECT COUNT(*) FROM events")
    if c.fetchone()[0] == 0:
        events = [
            ("Día de los Muertos Fiesta","Celebrate the Day of the Dead with traditional altar, marigolds, special menu & live Mariachi music","2024-11-01","7:00 PM","https://images.unsplash.com/photo-1604608672516-5a9b86e4a569?w=400","Cultural"),
            ("Cinco de Mayo Grand Celebration","Our biggest night! Live Mariachi, traditional dances, unlimited margaritas & festive food specials","2025-05-05","6:00 PM","https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400","Seasonal"),
            ("Mexican Dance Night — Folklorico","Every Friday: Witness the beauty of traditional Folklorico dancers in full costume","2024-12-06","8:00 PM","https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400","Weekly"),
            ("Tequila Tasting Evening","Guided tasting of 10 premium tequilas with food pairings from our Chef","2024-12-15","7:30 PM","https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400","Special"),
            ("Posadas — Christmas Season","Traditional Mexican Posadas celebration with candles, piñatas & seasonal menu","2024-12-16","6:00 PM","https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=400","Seasonal"),
            ("Chef's Mole Masterclass","Learn the secrets of authentic Mole Poblano from our Head Chef in our open kitchen","2025-01-18","3:00 PM","https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400","Workshop"),
        ]
        c.executemany("INSERT INTO events (title,description,event_date,event_time,image_url,category) VALUES (?,?,?,?,?,?)", events)
 
    c.execute("SELECT COUNT(*) FROM reviews")
    if c.fetchone()[0] == 0:
        reviews = [
            ("Sofia R.",5,"Absolutely magical evening! The Mole Poblano was divine and the Folklorico dancers took my breath away.","2024-11-20"),
            ("James T.",5,"Cleanest restaurant I've ever visited. The ambiance is so peaceful and the staff is incredibly warm.","2024-11-18"),
            ("Priya M.",4,"The Pozole Rojo warmed my soul on a cold evening. Beautiful cultural decor!","2024-11-15"),
            ("Carlos V.",5,"As a Mexican myself, I was skeptical but the authenticity is real. Abuela-level cooking.","2024-11-10"),
            ("Emma L.",5,"Came for the Cinco de Mayo celebration and stayed for the food. All world-class. 10/10!","2024-11-05"),
        ]
        c.executemany("INSERT INTO reviews (name,rating,comment,created_at) VALUES (?,?,?,?)", reviews)
 
    conn.commit()
    conn.close()
 
 
# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
 
@app.route('/api/menu', methods=['GET'])
def get_menu():
    conn = get_db()
    items = conn.execute("SELECT * FROM menu_items ORDER BY category, name").fetchall()
    conn.close()
    return jsonify([dict(i) for i in items])
 
@app.route('/api/menu/specials', methods=['GET'])
def get_specials():
    conn = get_db()
    items = conn.execute("SELECT * FROM menu_items WHERE is_special=1").fetchall()
    conn.close()
    return jsonify([dict(i) for i in items])
 
@app.route('/api/menu/seasonal', methods=['GET'])
def get_seasonal():
    conn = get_db()
    items = conn.execute("SELECT * FROM menu_items WHERE is_seasonal=1").fetchall()
    conn.close()
    return jsonify([dict(i) for i in items])
 
@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    events = conn.execute("SELECT * FROM events ORDER BY event_date").fetchall()
    conn.close()
    return jsonify([dict(e) for e in events])
 
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    conn = get_db()
    reviews = conn.execute("SELECT * FROM reviews ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in reviews])
 
@app.route('/api/book', methods=['POST'])
def book_table():
    data = request.json
    required = ['name', 'email', 'phone', 'date', 'time', 'guests']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400
 
    # 1 — Save to DB
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO bookings (name,email,phone,date,time,guests,special_requests,email_sent) VALUES (?,?,?,?,?,?,?,?)",
        (data['name'], data['email'], data['phone'], data['date'],
         data['time'], data['guests'], data.get('special_requests', ''), 0)
    )
    booking_id = cursor.lastrowid
    conn.commit()
 
    # 2 — Send email
    email_sent = send_confirmation_email(data)
 
    # 3 — Update flag
    conn.execute("UPDATE bookings SET email_sent=? WHERE id=?", (1 if email_sent else 0, booking_id))
    conn.commit()
    conn.close()
 
    return jsonify({
        'success':    True,
        'email_sent': email_sent,
        'message': (
            f"Table reserved for {data['name']} on {data['date']} at {data['time']}. "
            + (f"Confirmation sent to {data['email']}." if email_sent
               else "Note: confirmation email could not be delivered — please contact us if needed.")
        )
    })
 
@app.route('/api/reviews', methods=['POST'])
def post_review():
    data = request.json
    conn = get_db()
    conn.execute("INSERT INTO reviews (name,rating,comment) VALUES (?,?,?)",
                 (data['name'], data['rating'], data.get('comment', '')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
 
 
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
 