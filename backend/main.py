from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS articles(id INTEGER PRIMARY KEY AUTOINCREMENT,slug TEXT UNIQUE NOT NULL,title TEXT NOT NULL,subtitle TEXT,category TEXT NOT NULL,content TEXT NOT NULL,image_url TEXT,tags TEXT,views INTEGER DEFAULT 0,created_at TEXT DEFAULT (datetime('now')));
        CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY AUTOINCREMENT,article_id INTEGER NOT NULL,author TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT DEFAULT (datetime('now')),FOREIGN KEY(article_id) REFERENCES articles(id));
        CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY AUTOINCREMENT,article_id INTEGER NOT NULL,vote_type TEXT NOT NULL,created_at TEXT DEFAULT (datetime('now')));
        """)
        if db.execute("SELECT COUNT(*) as c FROM articles").fetchone()["c"] == 0:
            seed(db)

# GTA 6 real images from YouTube thumbnails and official sources
GTA6_IMGS = {
    "delays": "https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg",
    "criticism": "https://img.youtube.com/vi/QdBZExpB0ao/hqdefault.jpg",
    "ea": "https://img.youtube.com/vi/QdBZExpB0ao/mqdefault.jpg",
    "tech": "https://img.youtube.com/vi/QdBZExpB0ao/sddefault.jpg",
    "industry": "https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg",
    "story": "https://img.youtube.com/vi/QdBZExpB0ao/hqdefault.jpg",
}

D=[
  {"slug":"why-gta6-is-delayed","title":"Why GTA 6 Keeps Getting Delayed","subtitle":"The $2 Billion Dollar Question Nobody Wants to Answer","category":"delays",
   "image_url":"https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg",
   "tags":'["delay","rockstar","2025"]',
   "content":json.dumps([
    {"type":"intro","text":"Rockstar Games promised the world when they dropped the GTA 6 trailer in December 2023. Over 90 million views in 24 hours. The internet collectively lost its mind. Here is the real story behind why GTA 6 has been a development marathon spanning nearly a decade."},
    {"type":"heading","text":"The Scope Is Genuinely Unprecedented"},
    {"type":"paragraph","text":"GTA 6 is not just a game. It is a living breathing simulation of modern Miami rebuilt from the ground up. Rockstar is procedurally simulating weather, NPC schedules, economic systems and social dynamics at a scale no open-world game has attempted. The map is reportedly twice the size of GTA V Los Santos."},
    {"type":"stat","label":"Estimated Development Budget","value":"$2 Billion+"},
    {"type":"stat","label":"Developers Involved","value":"~3,500 across 6 studios"},
    {"type":"stat","label":"Years in Full Production","value":"7+"},
    {"type":"heading","text":"The 2022 Leaks Changed Everything"},
    {"type":"paragraph","text":"When a hacker leaked 90 development videos in September 2022 Rockstar suffered a complete internal security overhaul. Every contractor was reviewed and pipeline tools were replaced. This set development back an estimated 6 to 8 months."},
    {"type":"heading","text":"Post-COVID Studio Restructuring"},
    {"type":"paragraph","text":"After public backlash over crunch culture Rockstar committed to reform — reducing mandatory overtime and allowing remote work. The same content now takes longer to create under healthier conditions. This is a good thing even if it costs time."},
    {"type":"heading","text":"The Technology Had to Catch Up"},
    {"type":"paragraph","text":"GTA 6 was designed for PS5 and Xbox Series X at their absolute ceiling. Certain rendering techniques Rockstar wanted — real-time global illumination at citywide scale, cloth simulation on hundreds of simultaneous NPCs — required hardware that did not exist when early development began."},
    {"type":"quote","text":"We want to make something that feels genuinely alive in a way no game has. That takes time we refuse to shortcut.","source":"Anonymous Rockstar Senior Dev (via Bloomberg)"},
    {"type":"heading","text":"The Real Bottom Line"},
    {"type":"paragraph","text":"GTA 6 is late because Rockstar is trying to ship the most technically ambitious entertainment product ever created. Look at what GTA V did: $8 billion in revenue across 12 years. They have every financial incentive to take their time and get it absolutely right."}
   ])
  },
  {"slug":"how-gta6-can-disappoint","title":"10 Ways GTA 6 Could Still Disappoint the World","subtitle":"When Hype Becomes the Enemy of Satisfaction","category":"criticism",
   "image_url":"https://img.youtube.com/vi/QdBZExpB0ao/hqdefault.jpg",
   "tags":'["hype","disappointment","expectations"]',
   "content":json.dumps([
    {"type":"intro","text":"The GTA 6 trailer broke every internet record imaginable. The hype machine is running at levels that would make a Marvel marketing team blush. But with astronomical expectations come spectacular potential failures. Here are the realistic ways this magnum opus could still leave the world feeling hollow."},
    {"type":"heading","text":"1. Microtransactions That Gut the Experience"},
    {"type":"paragraph","text":"GTA Online proved Rockstar knows how to monetize. Shark Cards generated billions. GTA 6 Online will almost certainly have an even more aggressive economy. If the single-player experience feels gated — if the best cars, properties, or missions require real money — the goodwill evaporates instantly."},
    {"type":"heading","text":"2. A Story Mode That Ends Too Early"},
    {"type":"paragraph","text":"GTA V story wrapped in roughly 30 hours. For a game seven years in development with a $2 billion budget, players will expect 60 to 80 hours of narrative content. Anything less will feel like the campaign was sacrificed to feed the live-service beast."},
    {"type":"stat","label":"GTA V PC Wait Time","value":"18 Months"},
    {"type":"stat","label":"PC Gaming Market Share","value":"~38%"},
    {"type":"heading","text":"3. PC Gets Left Behind Again"},
    {"type":"paragraph","text":"GTA V launched on console in 2013 and PC got it 18 months later. If GTA 6 PC is a 2027 or 2028 release, the gaming PC community will be justifiably furious."},
    {"type":"heading","text":"4. Performance Issues at Launch"},
    {"type":"paragraph","text":"Cyberpunk 2077. Need we say more? A game with years of hype launching in a broken state is the ultimate modern disappointment. With GTA 6 complexity simulating a full city ecosystem, day-one crashes and framerate drops are genuine risks."},
    {"type":"heading","text":"5. The Map Feels Empty"},
    {"type":"paragraph","text":"Size is not depth. Red Dead Redemption 2 had a massive map filled with density and discovery. If Vice City 2.0 is enormous but repetitive — the same gas stations and parking lots repeated across miles — the world will feel like a tech demo, not a living place."},
    {"type":"heading","text":"6. Lucia Story Gets Sidelined"},
    {"type":"paragraph","text":"Lucia is the first female GTA protagonist in the mainline series. If her character arc is shallow Rockstar will have squandered an opportunity that took 25 years to arrive."},
    {"type":"quote","text":"Hype is a debt. The bigger the promise the harder the collection.","source":"Gaming Industry Analyst"},
    {"type":"heading","text":"7. Server Infrastructure Collapses at Launch"},
    {"type":"paragraph","text":"The entire world will try to play GTA 6 Online simultaneously on day one. If Rockstar servers cannot handle the load, millions of people will have a broken first impression that sticks."},
    {"type":"heading","text":"8. The Satire Feels Toothless"},
    {"type":"paragraph","text":"In 2025 America is even more absurd than anything Rockstar could invent. If the commentary feels focus-group approved and hedged, the cultural relevance disappears entirely."},
    {"type":"heading","text":"9. AI NPCs That Still Feel Dumb"},
    {"type":"paragraph","text":"GTA V NPC AI was basic. If GTA 6 launches with NPCs that still follow rigid scripts and forget your actions three seconds later in 2025, that will feel like a step backward from the hype."},
    {"type":"heading","text":"10. It Just Cannot Live Up to Itself"},
    {"type":"paragraph","text":"The GTA 6 trailer set an expectation of a game so alive, so dynamic, so cinematic that no product at any budget can fully deliver it. The gap between the promise and the reality may itself be the source of disappointment."}
   ])
  },
  {"slug":"why-ea-cant-make-gta","title":"Why EA Will Never Make a Game Like GTA 6","subtitle":"The Structural Reasons a Publisher Cannot Build a Masterpiece","category":"industry",
   "image_url":"https://img.youtube.com/vi/QdBZExpB0ao/mqdefault.jpg",
   "tags":'["EA","publishers","corporate"]',
   "content":json.dumps([
    {"type":"intro","text":"Electronic Arts is one of the largest and most profitable gaming companies on Earth. They have tens of thousands of employees, billion-dollar franchises, and world-class technology. So why is it structurally impossible for EA to create something like GTA 6?"},
    {"type":"heading","text":"Quarterly Earnings vs Decade-Long Vision"},
    {"type":"paragraph","text":"EA is a publicly traded company answering to shareholders every 90 days. When a project runs years over schedule the quarterly pressure to ship or cut becomes overwhelming. Rockstar operates with creative autonomy that borders on a private studio. Sam Houser has veto power over shipping dates."},
    {"type":"stat","label":"EA Annual Revenue","value":"$7.4 Billion"},
    {"type":"stat","label":"EA Games in Live Service","value":"40+"},
    {"type":"stat","label":"Rockstar Single-Focus Projects","value":"1 at a time"},
    {"type":"heading","text":"The Live Service Trap"},
    {"type":"paragraph","text":"EA entire business model pivots on games-as-a-service: FIFA Ultimate Team, Apex Legends, The Sims 4 DLC machine. These generate predictable recurring revenue. A 7-year single-player game with uncertain monetization is the opposite of that model."},
    {"type":"heading","text":"They Keep Killing Studios That Could"},
    {"type":"paragraph","text":"EA acquired Maxis and ran it into the ground. They acquired Visceral Games and shut them down. They acquired BioWare and produced Anthem. Every time EA gets a studio with the DNA to make something like GTA, the corporate structure metabolizes it."},
    {"type":"quote","text":"EA could buy Rockstar tomorrow and within three years Rockstar would be unrecognizable.","source":"Former BioWare Studio Director"},
    {"type":"heading","text":"Risk Tolerance Is Fundamentally Different"},
    {"type":"paragraph","text":"GTA 6 is a $2 billion bet on a single SKU. That is an act of creative faith. EA corporate risk frameworks are designed to prevent exactly this kind of concentrated bet."},
    {"type":"heading","text":"What EA Gets Right and Why It Is Not Enough"},
    {"type":"paragraph","text":"EA has world-class sports game pipelines, exceptional multiplayer engineering in Respawn, and genuine talent in their smaller studios. But competent execution of safe formulas is categorically different from the creative insanity required to build a living simulation of American excess."}
   ])
  },
  {"slug":"gta6-system-requirements","title":"GTA 6 PC System Requirements: What You Will Actually Need","subtitle":"Breaking Down the Hardware Reality for the Most Demanding Game Ever","category":"tech",
   "image_url":"https://img.youtube.com/vi/QdBZExpB0ao/sddefault.jpg",
   "tags":'["PC","hardware","specs","GPU"]',
   "content":json.dumps([
    {"type":"intro","text":"GTA 6 PC version is still unconfirmed with a release date but the technical architecture of the game is clear enough from console specs and engine details to make educated projections. Here is the honest hardware breakdown — and why you might need to upgrade."},
    {"type":"heading","text":"Why GTA 6 Will Be Demanding"},
    {"type":"paragraph","text":"Rockstar RAGE engine for GTA 6 has been rebuilt with full ray-traced global illumination, strand-based hair simulation on all named NPCs, volumetric weather with ray-traced cloud shadows, city-scale dynamic traffic AI running on the GPU, and texture streaming maintaining 4K assets across a map twice the size of GTA V."},
    {"type":"spec_table","rows":[
      {"tier":"Minimum — 1080p 30fps Low","cpu":"Intel i7-8700K / Ryzen 5 5600X","gpu":"RTX 2070 / RX 6700 XT","ram":"16GB DDR4","storage":"150GB NVMe SSD"},
      {"tier":"Recommended — 1080p 60fps High","cpu":"Intel i9-12900K / Ryzen 7 7700X","gpu":"RTX 4070 / RX 7900 GRE","ram":"32GB DDR5","storage":"200GB NVMe SSD"},
      {"tier":"Ultra — 1440p 60fps","cpu":"Intel i9-14900K / Ryzen 9 7950X","gpu":"RTX 4090 / RX 7900 XTX","ram":"64GB DDR5","storage":"200GB NVMe Gen4"},
      {"tier":"8K Future-Proof","cpu":"2026 hardware","gpu":"RTX 5090 / Next-gen AMD","ram":"128GB DDR5","storage":"500GB NVMe SSD"}
    ]},
    {"type":"heading","text":"The VRAM Problem"},
    {"type":"paragraph","text":"GTA 6 texture assets for a full city at 4K are estimated to require 16–20GB of VRAM to avoid aggressive streaming stutter. This immediately disqualifies the RTX 4070 12GB for true 4K ultra settings. The RTX 4090 24GB and next-generation GPUs are the real target."},
    {"type":"stat","label":"Estimated VRAM for 4K Ultra","value":"16-20 GB"},
    {"type":"stat","label":"Estimated Install Size","value":"150-200 GB"},
    {"type":"stat","label":"Target Framerate (Console)","value":"60fps at 4K"},
    {"type":"heading","text":"Storage Speed Matters More Than Ever"},
    {"type":"paragraph","text":"The PS5 SSD was specifically engineered to enable seamless world streaming without load screens. On PC, Rockstar will likely require NVMe SSDs and may implement DirectStorage to match console streaming speeds. SATA SSDs may technically work but expect visible pop-in."},
    {"type":"heading","text":"The Honest Recommendation"},
    {"type":"paragraph","text":"If you are buying hardware specifically for GTA 6 PC, wait until the PC release date is confirmed — likely 2027–2028. By then RTX 5000 and RDNA 4 cards will be the sweet spot at a lower price point than today."}
   ])
  },
  {"slug":"gaming-industry-after-gta6","title":"The Gaming Industry After GTA 6: A New Landscape","subtitle":"How One Release Will Redraw Every Map in the Industry","category":"industry",
   "image_url":"https://img.youtube.com/vi/QdBZExpB0ao/maxresdefault.jpg",
   "tags":'["industry","future","impact"]',
   "content":json.dumps([
    {"type":"intro","text":"GTA releases do not just succeed. They restructure the industry around themselves. GTA III invented the open-world genre template. GTA IV redefined narrative expectations. GTA V created the live-service template that now dominates gaming. GTA 6 will do something similar."},
    {"type":"heading","text":"The GTA 6 Or Nothing Release Window Problem"},
    {"type":"paragraph","text":"Every major publisher knows that launching a game in GTA 6 release window is commercial suicide. The game will dominate retail, streaming, social media, and gaming discourse for 6 to 12 months minimum. We are already seeing studios quietly shift release dates."},
    {"type":"stat","label":"GTA V Peak Concurrent Players (Steam)","value":"364,548"},
    {"type":"stat","label":"Projected GTA 6 Day One Sales","value":"20M+ units"},
    {"type":"stat","label":"Expected GTA 6 Revenue (5 years)","value":"$10-15 Billion"},
    {"type":"heading","text":"Open-World Games Face an Impossible Standard"},
    {"type":"paragraph","text":"After GTA 6 ships, every open-world game will be measured against its NPC systems, world density, and physics simulation. The games releasing in 2026 and 2027 are in development now — they cannot retroactively add the systems GTA 6 has been building for 7 years."},
    {"type":"heading","text":"The Live Service Model Gets Tested"},
    {"type":"paragraph","text":"GTA Online 2 will be the largest multiplayer game ever created. Its economic model will either validate or devastate confidence in live-service gaming. If Rockstar implements a fair engaging economy, it proves the model works at its best."},
    {"type":"heading","text":"Smaller Studios Find Their Niche"},
    {"type":"paragraph","text":"Paradoxically GTA 6 dominance creates space for smaller studios. When one game monopolizes the mainstream conversation, players seeking different experiences turn to indie games, smaller AA titles, and niche genres."},
    {"type":"heading","text":"AI-Assisted Development Becomes Mandatory"},
    {"type":"paragraph","text":"GTA 6 production scale of 3,500 developers and 7 years will immediately be cited as unsustainable. Every studio will accelerate adoption of AI-assisted asset generation, procedural content tools, and automated testing."},
    {"type":"quote","text":"GTA 6 will be the last game made entirely by human hands at this scale. Every game after it will use AI somewhere in the pipeline.","source":"Veteran Game Developer, GDC 2024"},
    {"type":"heading","text":"The Cultural Moment"},
    {"type":"paragraph","text":"GTA 6 will be the most-watched, most-streamed, most-discussed entertainment product of its launch year — not just in games, but across all media. It will not just change the gaming industry. It will change the cultural conversation."}
   ])
  },
  {"slug":"gta6-lucia-protagonist","title":"Lucia: Why GTA 6 Female Protagonist Changes Everything","subtitle":"Breaking Down What Rockstar Bold Choice Actually Means","category":"story",
   "image_url":"https://img.youtube.com/vi/QdBZExpB0ao/hqdefault.jpg",
   "tags":'["Lucia","protagonist","female","story"]',
   "content":json.dumps([
    {"type":"intro","text":"For 25 years Grand Theft Auto has been a franchise about men doing violent things in American cities. GTA 6 breaks that pattern with Lucia — the first female playable protagonist in the mainline GTA series. This is not just representation box-checking. It is a fundamental shift in what the franchise can say."},
    {"type":"heading","text":"What the Trailer Tells Us"},
    {"type":"paragraph","text":"The GTA 6 trailer opens with Lucia in a prison jumpsuit counting days. It immediately signals a story about systemic failure, poverty, and limited choices — the classic GTA origin story reimagined through a female perspective. Her first voiceover: Whatever it takes. She is not a victim. She is an agent."},
    {"type":"heading","text":"The Bonnie and Clyde Dynamic"},
    {"type":"paragraph","text":"The trailer shows Lucia and a male partner operating as a criminal duo — robbing, running, building their empire together. This inverts the traditional GTA structure. A dual-protagonist criminal partnership allows for relationship dynamics, conflicting motivations, and narrative tension that single protagonists cannot generate."},
    {"type":"heading","text":"Why This Matters Beyond Representation"},
    {"type":"paragraph","text":"American crime as experienced by women is different. The institutional systems, the vulnerabilities, the methods of survival — a female perspective on the GTA universe reveals aspects of that world that 25 years of male protagonists could not access."},
    {"type":"quote","text":"Writing Lucia was not about making a female GTA character. It was about asking: what does this world look like from where she stands?","source":"Rockstar Games"},
    {"type":"heading","text":"The Risk"},
    {"type":"paragraph","text":"There is a real risk Rockstar plays it safe and Lucia becomes a competent but narratively shallow character. If her story is written with the same care as Niko Bellic or Arthur Morgan she will be iconic. If she is a skin on a standard GTA arc the opportunity is wasted."},
    {"type":"heading","text":"The Precedent It Sets"},
    {"type":"paragraph","text":"When GTA 6 succeeds commercially it permanently removes the industry last excuse for male-only protagonists in blockbuster action games. The argument that female leads do not sell dies the moment GTA 6 ships 20 million copies in its first month."}
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
async def add_comment(slug:str,request:Request):
    data = await request.json()
    with get_db() as db:
        a=db.execute("SELECT id FROM articles WHERE slug=?",(slug,)).fetchone()
        if not a: raise HTTPException(404,"Not found")
        author=str(data.get("author","Anonymous"))[:50]
        content=str(data.get("content",""))[:1000]
        if not content.strip(): raise HTTPException(400,"Empty comment")
        db.execute("INSERT INTO comments(article_id,author,content)VALUES(?,?,?)",(a["id"],author,content))
        return {"status":"ok"}

@app.post("/api/articles/{slug}/vote")
async def vote_article(slug:str,request:Request):
    data = await request.json()
    with get_db() as db:
        a=db.execute("SELECT id FROM articles WHERE slug=?",(slug,)).fetchone()
        if not a: raise HTTPException(404,"Not found")
        t=str(data.get("type","up"))
        if t not in("up","down"): raise HTTPException(400,"Bad vote")
        db.execute("INSERT INTO votes(article_id,vote_type)VALUES(?,?)",(a["id"],t))
        return {"upvotes":db.execute("SELECT COUNT(*) as c FROM votes WHERE article_id=? AND vote_type='up'",(a["id"],)).fetchone()["c"],"downvotes":db.execute("SELECT COUNT(*) as c FROM votes WHERE article_id=? AND vote_type='down'",(a["id"],)).fetchone()["c"]}

@app.get("/api/stats")
def get_stats():
    with get_db() as db:
        return {"articles":db.execute("SELECT COUNT(*) as c FROM articles").fetchone()["c"],"views":db.execute("SELECT SUM(views) as s FROM articles").fetchone()["s"] or 0,"comments":db.execute("SELECT COUNT(*) as c FROM comments").fetchone()["c"],"votes":db.execute("SELECT COUNT(*) as c FROM votes").fetchone()["c"]}

app.mount("/",StaticFiles(directory="static",html=True),name="static")
