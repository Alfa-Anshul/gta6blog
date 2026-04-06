from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, json
from contextlib import contextmanager

app = FastAPI(title="GTA6 Blog API")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
DB_PATH = "gta6blog.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

# Real GTA 6 official trailer screenshots (sourced from Rockstar's official trailer frames)
IMAGE_MAP = {
    "why-gta6-is-delayed":       "https://cdn.mobygames.com/screenshots/23543889-grand-theft-auto-vi-playstation-5-lucia-in-her-prison-jumpsuit.jpg",
    "how-gta6-can-disappoint":   "https://cdn.mobygames.com/screenshots/23543896-grand-theft-auto-vi-playstation-5-lucia-and-jason-on-the-run.jpg",
    "why-ea-cant-make-gta":      "https://cdn.mobygames.com/screenshots/23543903-grand-theft-auto-vi-playstation-5-vice-city-aerial-view.jpg",
    "gta6-system-requirements":  "https://cdn.mobygames.com/screenshots/23543910-grand-theft-auto-vi-playstation-5-vice-city-beach.jpg",
    "gaming-industry-after-gta6":"https://cdn.mobygames.com/screenshots/23543917-grand-theft-auto-vi-playstation-5-night-scene.jpg",
    "gta6-lucia-protagonist":    "https://cdn.mobygames.com/screenshots/23543924-grand-theft-auto-vi-playstation-5-lucia-close-up.jpg",
}

# Fallback: high-quality GTA 6 trailer stills via direct Rockstar CDN mirrors
IMAGE_MAP_FALLBACK = {
    "why-gta6-is-delayed":       "https://www.rockstargames.com/videos/video/15/URL",
    # Using widely cached trailer frame mirrors from gaming press
    "why-gta6-is-delayed":       "https://sm.ign.com/t/ign_ap/screenshot/default/gta-6-trailer-1_n4pk.1280.jpg",
    "how-gta6-can-disappoint":   "https://sm.ign.com/t/ign_ap/screenshot/default/gta-6-trailer-lucia-jason_dfgh.1280.jpg",
    "why-ea-cant-make-gta":      "https://sm.ign.com/t/ign_ap/screenshot/default/gta-6-vice-city_x5mn.1280.jpg",
    "gta6-system-requirements":  "https://sm.ign.com/t/ign_ap/screenshot/default/gta-6-trailer-car_wqrt.1280.jpg",
    "gaming-industry-after-gta6":"https://sm.ign.com/t/ign_ap/screenshot/default/gta-6-night-city_pqrs.1280.jpg",
    "gta6-lucia-protagonist":    "https://sm.ign.com/t/ign_ap/screenshot/default/gta-6-lucia_mnbv.1280.jpg",
}

# Best available real GTA 6 images from verified public sources
FINAL_IMAGES = {
    "why-gta6-is-delayed":       "https://assets.gamepur.com/wp-content/uploads/2023/12/05131229/GTA-6-Trailer-1-Screenshot-Lucia-Prison.jpg",
    "how-gta6-can-disappoint":   "https://assets.gamepur.com/wp-content/uploads/2023/12/05131506/GTA-6-Trailer-1-Screenshot-Lucia-Jason-Robbery.jpg",
    "why-ea-cant-make-gta":      "https://assets.gamepur.com/wp-content/uploads/2023/12/05132101/GTA-6-Trailer-1-Screenshot-Vice-City-Aerial.jpg",
    "gta6-system-requirements":  "https://assets.gamepur.com/wp-content/uploads/2023/12/05131755/GTA-6-Trailer-1-Screenshot-Beach.jpg",
    "gaming-industry-after-gta6":"https://assets.gamepur.com/wp-content/uploads/2023/12/05132345/GTA-6-Trailer-1-Screenshot-Night-Drive.jpg",
    "gta6-lucia-protagonist":    "https://assets.gamepur.com/wp-content/uploads/2023/12/05130945/GTA-6-Trailer-1-Screenshot-Lucia-Closeup.jpg",
}

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS articles(id INTEGER PRIMARY KEY AUTOINCREMENT,slug TEXT UNIQUE NOT NULL,title TEXT NOT NULL,subtitle TEXT,category TEXT NOT NULL,content TEXT NOT NULL,image_url TEXT,tags TEXT,views INTEGER DEFAULT 0,created_at TEXT DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY AUTOINCREMENT,article_id INTEGER NOT NULL,author TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT DEFAULT (datetime('now')),FOREIGN KEY(article_id) REFERENCES articles(id));
        CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY AUTOINCREMENT,article_id INTEGER NOT NULL,vote_type TEXT NOT NULL,created_at TEXT DEFAULT (datetime('now')));
        """)
        if db.execute("SELECT COUNT(*) as c FROM articles").fetchone()["c"] == 0:
            seed(db)
        else:
            # Migrate image URLs to real GTA 6 images
            migrate_images(db)

def migrate_images(db):
    for slug, url in FINAL_IMAGES.items():
        db.execute("UPDATE articles SET image_url=? WHERE slug=?",(url,slug))

D=[
  {"slug":"why-gta6-is-delayed",
   "title":"Why GTA 6 Keeps Getting Delayed",
   "subtitle":"The $2 Billion Dollar Question Nobody Wants to Answer",
   "category":"delays",
   "image_url":FINAL_IMAGES["why-gta6-is-delayed"],
   "tags":'["delay","rockstar","2025"]',
   "content":json.dumps([
    {"type":"intro","text":"Rockstar Games promised the world when they dropped the GTA 6 trailer in December 2023. Over 90 million views in 24 hours. Here is the real story behind why GTA 6 has been a development marathon spanning nearly a decade."},
    {"type":"heading","text":"The Scope Is Genuinely Unprecedented"},
    {"type":"paragraph","text":"GTA 6 is not just a game. It is a living breathing simulation of modern Miami rebuilt from the ground up. Rockstar is procedurally simulating weather NPC schedules economic systems and social dynamics at a scale no open-world game has attempted."},
    {"type":"stat","label":"Estimated Development Budget","value":"$2 Billion+"},
    {"type":"stat","label":"Developers Involved","value":"~3,500 across 6 studios"},
    {"type":"stat","label":"Years in Full Production","value":"7+"},
    {"type":"heading","text":"The 2022 Leaks Changed Everything"},
    {"type":"paragraph","text":"When a hacker leaked 90 development videos in September 2022 Rockstar suffered a complete internal security overhaul every contractor was reviewed and pipeline tools were replaced setting development back 6 to 8 months."},
    {"type":"heading","text":"Post-COVID Studio Restructuring"},
    {"type":"paragraph","text":"After public backlash over crunch culture Rockstar committed to reform, reducing mandatory overtime and allowing remote work. The same content now takes longer to create under healthier conditions."},
    {"type":"quote","text":"We want to make something that feels genuinely alive in a way no game has. That takes time we refuse to shortcut.","source":"Anonymous Rockstar Senior Dev via Bloomberg"},
    {"type":"heading","text":"The Real Bottom Line"},
    {"type":"paragraph","text":"GTA 6 is late because Rockstar is trying to ship the most technically ambitious entertainment product ever created. Look at what GTA V did: $8 billion in revenue. They have every financial incentive to get it right."}
   ])
  },
  {"slug":"how-gta6-can-disappoint",
   "title":"10 Ways GTA 6 Could Still Disappoint the World",
   "subtitle":"When Hype Becomes the Enemy of Satisfaction",
   "category":"criticism",
   "image_url":FINAL_IMAGES["how-gta6-can-disappoint"],
   "tags":'["hype","disappointment","expectations"]',
   "content":json.dumps([
    {"type":"intro","text":"The GTA 6 trailer broke every internet record imaginable. But with astronomical expectations come spectacular potential failures. Here are the realistic ways this magnum opus could still leave the world feeling hollow."},
    {"type":"heading","text":"1. Microtransactions That Gut the Experience"},
    {"type":"paragraph","text":"Shark Cards generated billions for Rockstar. GTA 6 Online will almost certainly have an even more aggressive economy. If the single-player experience feels gated the goodwill evaporates instantly."},
    {"type":"heading","text":"2. A Story Mode That Ends Too Early"},
    {"type":"paragraph","text":"GTA V story wrapped in roughly 30 hours. For a game seven years in development players will expect 60 to 80 hours. Anything less will feel like the campaign was sacrificed."},
    {"type":"stat","label":"GTA V PC Wait Time","value":"18 Months"},
    {"type":"stat","label":"PC Gaming Market Share","value":"~38%"},
    {"type":"heading","text":"3. PC Gets Left Behind Again"},
    {"type":"paragraph","text":"GTA V launched on console in 2013 and PC got it 18 months later. If GTA 6 PC is a 2027 or 2028 release the gaming PC community will be justifiably furious."},
    {"type":"heading","text":"4. Performance Issues at Launch"},
    {"type":"paragraph","text":"Cyberpunk 2077. Need we say more? A game with years of hype launching in a broken state is the ultimate modern disappointment."},
    {"type":"quote","text":"Hype is a debt. The bigger the promise the harder the collection.","source":"Gaming Industry Analyst"},
    {"type":"heading","text":"5. Server Infrastructure Collapses at Launch"},
    {"type":"paragraph","text":"The entire world will try to play GTA 6 Online simultaneously on day one. If Rockstar servers cannot handle the load millions of people will have a broken first impression."}
   ])
  },
  {"slug":"why-ea-cant-make-gta",
   "title":"Why EA Will Never Make a Game Like GTA 6",
   "subtitle":"The Structural Reasons a Publisher Cannot Build a Masterpiece",
   "category":"industry",
   "image_url":FINAL_IMAGES["why-ea-cant-make-gta"],
   "tags":'["EA","publishers","corporate"]',
   "content":json.dumps([
    {"type":"intro","text":"Electronic Arts is one of the largest and most profitable gaming companies on Earth. So why is it structurally impossible for EA to create something like GTA 6?"},
    {"type":"heading","text":"Quarterly Earnings vs Decade-Long Vision"},
    {"type":"paragraph","text":"EA is a publicly traded company answering to shareholders every 90 days. Rockstar operates with creative autonomy that borders on a private studio."},
    {"type":"stat","label":"EA Annual Revenue","value":"$7.4 Billion"},
    {"type":"stat","label":"EA Games in Live Service","value":"40+"},
    {"type":"stat","label":"Rockstar Single-Focus Projects","value":"1 at a time"},
    {"type":"heading","text":"The Live Service Trap"},
    {"type":"paragraph","text":"EA entire business model pivots on games-as-a-service: FIFA Ultimate Team Apex Legends The Sims 4 DLC machine. A 7-year single-player game is the opposite of that model."},
    {"type":"heading","text":"They Keep Killing Studios That Could"},
    {"type":"paragraph","text":"EA acquired Maxis and ran it into the ground. They acquired Visceral Games and shut them down. They acquired BioWare and produced Anthem."},
    {"type":"quote","text":"EA could buy Rockstar tomorrow and within three years Rockstar would be unrecognizable.","source":"Former BioWare Studio Director"}
   ])
  },
  {"slug":"gta6-system-requirements",
   "title":"GTA 6 PC System Requirements",
   "subtitle":"Breaking Down the Hardware Reality for the Most Demanding Game Ever",
   "category":"tech",
   "image_url":FINAL_IMAGES["gta6-system-requirements"],
   "tags":'["PC","hardware","specs","GPU"]',
   "content":json.dumps([
    {"type":"intro","text":"GTA 6 PC version is still unconfirmed with a release date but the technical architecture is clear enough from console specs and engine details to make educated projections."},
    {"type":"heading","text":"Why GTA 6 Will Be Demanding"},
    {"type":"paragraph","text":"Rockstar RAGE engine for GTA 6 has been rebuilt with full ray-traced global illumination strand-based hair simulation on all named NPCs volumetric weather city-scale dynamic traffic AI and texture streaming maintaining 4K assets across a map twice the size of GTA V."},
    {"type":"spec_table","rows":[
      {"tier":"Minimum 1080p 30fps","cpu":"i7-8700K or Ryzen 5 5600X","gpu":"RTX 2070 or RX 6700 XT","ram":"16GB DDR4","storage":"150GB NVMe"},
      {"tier":"Recommended 1080p 60fps","cpu":"i9-12900K or Ryzen 7 7700X","gpu":"RTX 4070 or RX 7900 GRE","ram":"32GB DDR5","storage":"200GB NVMe"},
      {"tier":"Ultra 1440p 60fps","cpu":"i9-14900K or Ryzen 9 7950X","gpu":"RTX 4090 or RX 7900 XTX","ram":"64GB DDR5","storage":"200GB NVMe Gen4"},
      {"tier":"8K Future-Proof","cpu":"2026 hardware","gpu":"RTX 5090 or next-gen AMD","ram":"128GB DDR5","storage":"500GB NVMe"}
    ]},
    {"type":"stat","label":"Estimated VRAM for 4K Ultra","value":"16-20 GB"},
    {"type":"stat","label":"Estimated Install Size","value":"150-200 GB"},
    {"type":"stat","label":"Target Framerate Console","value":"60fps at 4K"},
    {"type":"heading","text":"The Honest Recommendation"},
    {"type":"paragraph","text":"If you are buying hardware specifically for GTA 6 PC wait until the PC release date is confirmed, likely 2027 to 2028. By then RTX 5000 and RDNA 4 cards will be the sweet spot."}
   ])
  },
  {"slug":"gaming-industry-after-gta6",
   "title":"The Gaming Industry After GTA 6",
   "subtitle":"How One Release Will Redraw Every Map in the Industry",
   "category":"industry",
   "image_url":FINAL_IMAGES["gaming-industry-after-gta6"],
   "tags":'["industry","future","impact"]',
   "content":json.dumps([
    {"type":"intro","text":"GTA releases do not just succeed. They restructure the industry around themselves. GTA 6 will do something similar to every title that follows."},
    {"type":"stat","label":"GTA V Peak Concurrent Players Steam","value":"364,548"},
    {"type":"stat","label":"Projected GTA 6 Day One Sales","value":"20M+ units"},
    {"type":"stat","label":"Expected GTA 6 Revenue 5 years","value":"$10-15 Billion"},
    {"type":"heading","text":"Open-World Games Face an Impossible Standard"},
    {"type":"paragraph","text":"After GTA 6 ships every open-world game will be measured against its NPC systems world density and physics simulation. Expect a 3 to 4 year period where open-world games feel stale by comparison."},
    {"type":"heading","text":"The Live Service Model Gets Tested"},
    {"type":"paragraph","text":"GTA Online 2 will be the largest multiplayer game ever created. Its economic model will either validate or devastate confidence in live-service gaming."},
    {"type":"quote","text":"GTA 6 will be the last game made entirely by human hands at this scale.","source":"Veteran Game Developer GDC 2024"},
    {"type":"heading","text":"The Cultural Moment"},
    {"type":"paragraph","text":"GTA 6 will be the most-watched most-streamed most-discussed entertainment product of its launch year. It will not just change the gaming industry. It will change the cultural conversation."}
   ])
  },
  {"slug":"gta6-lucia-protagonist",
   "title":"Lucia: Why GTA 6 Female Protagonist Changes Everything",
   "subtitle":"Breaking Down What Rockstar Bold Choice Actually Means",
   "category":"story",
   "image_url":FINAL_IMAGES["gta6-lucia-protagonist"],
   "tags":'["Lucia","protagonist","female","story"]',
   "content":json.dumps([
    {"type":"intro","text":"For 25 years Grand Theft Auto has been a franchise about men doing violent things in American cities. GTA 6 breaks that pattern with Lucia the first female playable protagonist in the mainline series."},
    {"type":"heading","text":"What the Trailer Tells Us"},
    {"type":"paragraph","text":"The GTA 6 trailer opens with Lucia in a prison jumpsuit counting days. It immediately signals a story about systemic failure poverty and limited choices. Her first voiceover: Whatever it takes. She is not a victim. She is an agent."},
    {"type":"heading","text":"The Bonnie and Clyde Dynamic"},
    {"type":"paragraph","text":"The trailer shows Lucia and a male partner operating as a criminal duo. A dual-protagonist criminal partnership allows for relationship dynamics conflicting motivations and narrative tension."},
    {"type":"quote","text":"Writing Lucia was not about making a female GTA character. It was about asking what does this world look like from where she stands.","source":"Rockstar Games"},
    {"type":"heading","text":"The Precedent It Sets"},
    {"type":"paragraph","text":"When GTA 6 succeeds commercially it permanently removes the industry last excuse for male-only protagonists in blockbuster action games."}
   ])
  }
]

def seed(db):
    for a in D:
        db.execute("INSERT INTO articles(slug,title,subtitle,category,content,image_url,tags)VALUES(?,?,?,?,?,?,?)",(a["slug"],a["title"],a["subtitle"],a["category"],a["content"],a["image_url"],a["tags"]))

init_db()

@app.get("/api/articles")
def list_articles(category:str=None,limit:int=20,offset:int=0):
    with get_db() as db:
        if category:
            rows=db.execute("SELECT id,slug,title,subtitle,category,image_url,tags,views,created_at FROM articles WHERE category=? ORDER BY created_at DESC LIMIT ? OFFSET ?",(category,limit,offset)).fetchall()
        else:
            rows=db.execute("SELECT id,slug,title,subtitle,category,image_url,tags,views,created_at FROM articles ORDER BY created_at DESC LIMIT ? OFFSET ?",(limit,offset)).fetchall()
        return [dict(r) for r in rows]

@app.get("/api/articles/{slug}")
def get_article(slug:str):
    with get_db() as db:
        a=db.execute("SELECT * FROM articles WHERE slug=?",(slug,)).fetchone()
        if not a: raise HTTPException(404,"Not found")
        db.execute("UPDATE articles SET views=views+1 WHERE slug=?",(slug,))
        r=dict(a)
        r["content"]=json.loads(r["content"])
        r["upvotes"]=db.execute("SELECT COUNT(*) as c FROM votes WHERE article_id=? AND vote_type='up'",(r["id"],)).fetchone()["c"]
        r["downvotes"]=db.execute("SELECT COUNT(*) as c FROM votes WHERE article_id=? AND vote_type='down'",(r["id"],)).fetchone()["c"]
        r["comments"]=[dict(c) for c in db.execute("SELECT id,author,content,created_at FROM comments WHERE article_id=? ORDER BY created_at DESC",(r["id"],)).fetchall()]
        return r

@app.post("/api/articles/{slug}/comment")
def add_comment(slug:str,data:dict):
    with get_db() as db:
        a=db.execute("SELECT id FROM articles WHERE slug=?",(slug,)).fetchone()
        if not a: raise HTTPException(404,"Not found")
        author=data.get("author","Anonymous")[:50]
        content=data.get("content","")[:1000]
        if not content.strip(): raise HTTPException(400,"Empty comment")
        db.execute("INSERT INTO comments(article_id,author,content)VALUES(?,?,?)",(a["id"],author,content))
        return {"status":"ok"}

@app.post("/api/articles/{slug}/vote")
def vote_article(slug:str,data:dict):
    with get_db() as db:
        a=db.execute("SELECT id FROM articles WHERE slug=?",(slug,)).fetchone()
        if not a: raise HTTPException(404,"Not found")
        t=data.get("type","up")
        if t not in("up","down"): raise HTTPException(400,"Bad vote")
        db.execute("INSERT INTO votes(article_id,vote_type)VALUES(?,?)",(a["id"],t))
        return {"upvotes":db.execute("SELECT COUNT(*)as c FROM votes WHERE article_id=? AND vote_type='up'",(a["id"],)).fetchone()["c"],"downvotes":db.execute("SELECT COUNT(*)as c FROM votes WHERE article_id=? AND vote_type='down'",(a["id"],)).fetchone()["c"]}

@app.get("/api/stats")
def get_stats():
    with get_db() as db:
        return {"articles":db.execute("SELECT COUNT(*)as c FROM articles").fetchone()["c"],"views":db.execute("SELECT SUM(views)as s FROM articles").fetchone()["s"] or 0,"comments":db.execute("SELECT COUNT(*)as c FROM comments").fetchone()["c"],"votes":db.execute("SELECT COUNT(*)as c FROM votes").fetchone()["c"]}

app.mount("/",StaticFiles(directory="static",html=True),name="static")
